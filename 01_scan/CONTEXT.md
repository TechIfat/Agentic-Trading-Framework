# 01_scan/CONTEXT.md — Layer 2
# Stage 01: Market scan
# Role: data collector. You scan. You do not decide.

## Your job this stage

1. Read CLAUDE.md to confirm CURRENT_PHASE.
2. Read rules.md to get scan criteria and phase behaviour.
3. Read knowledge/wiki/market-regimes.md for current regime context.
4. **VIX freshness check** — use `web_search` to fetch current VIX.
   Read `VIX_CURRENT` and `CRISIS:` from knowledge/wiki/macro-context.md.

   **CRISIS check (runs first, before VIX delta):**
   - If `CRISIS: true`: write 06_execute/CIRCUIT_BREAKER immediately with reason
     `CRISIS macro flag set in macro-context.md`. Write ABORT to scan output. Halt.
     Do not proceed to step 5. Alert human — CRISIS requires manual review before reset.

   Search query: `"VIX index current level today"`
   Extract the numeric VIX value from search results.
   Compare live VIX against stored value:
   - If |live_vix − stored_vix| > 5 points: treat this session as SESSION_TYPE=MACRO_UPDATE.
     Halt scan. Route to Stage 07 Part C to refresh macro-context.md first.
     Do not proceed to step 5 until Part C completes and macro-context.md is updated.
   - If live VIX has crossed a regime boundary since last update (see thresholds below):
     Same action — halt, route to Part C, do not scan with stale regime.
   - Otherwise: proceed. Log live VIX and stored VIX in scan-result.json for audit.

   VIX regime boundaries (from rules.md):
   - Crossing above 25: stored regime must be TRENDING_BEAR or higher — if not, stale
   - Crossing above 30: stored regime must be HIGH_VOLATILITY — if not, stale
   - Crossing below 15: stored regime must be TRENDING_BULL — if not, stale

5. **Check open positions** — scan 06_execute/open-positions/ for any .json files.
   For each open position, fetch current price via Yahoo Finance:
   ```bash
   curl -s -A "Mozilla/5.0" \
     "https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?interval=1d&range=1d"
   ```
   Extract `meta.regularMarketPrice` for P&L calculation.
   - Phase 1: report position status (current price, P&L%) but output exit_signal = HOLD
   - Phase 2+: apply exit rules and generate EXIT signals where criteria are met

5a. **Earnings proximity check** — for each ticker in TICKER_ALLOWLIST, use `web_search`
    to check for earnings releases, trading updates, or results announcements within
    the next 5 trading days.

    Search query: `"{company name} earnings date next"`

    Use the company name map below. Run all searches before proceeding to step 6.

    Rules:
    - **Earnings within 5 trading days**: cap confidence at LOW regardless of signals
      fired. Set `earnings_warning: true` and record the date in scan-result.json.
    - **Earnings tomorrow**: set `proceed: false` for that ticker. Do not generate
      entry signals — binary event risk too high.
    - **No earnings found / search inconclusive**: set `earnings_warning: false`,
      proceed normally.

    Ticker → company name map (Example):
    ```yaml
    AAPL → Apple Inc
    MSFT → Microsoft
    TSLA → Tesla
    ```

    This check uses `web_search` only — no new MCP tools required.

4b. **Active avoidance check** — check each of the following conditions before fetching
    market data. If any SESSION-LEVEL condition is met, write `session_skip: true` and
    `session_skip_reason` to scan output and halt after Stage 01.
    For TICKER-LEVEL conditions, set `proceed: false` and `skip_reason` for that ticker only.
    Do NOT evaluate entry signals for skipped tickers.

    **SESSION-LEVEL checks (apply to entire session):**

    1. Domestic macro release today:
       web_search: `"Economic data releases today {date}"`
       Skip if: Major central bank decisions, CPI, or GDP releasing today.
       Reason: binary events make technical signals unreliable.

    2. VIX spike check:
       Compare live_vix (already fetched in step 4) against stored VIX from 7 days ago
       in macro-context.md (use LAST_UPDATED entry in macro change log).
       - If live_vix > stored_7day_vix × 1.20 (risen 20%+ in a week):
         Downgrade all signal confidence by one tier.
       - If live_vix > stored_7day_vix × 1.35 (risen 35%+ in a week):
         Set session_skip: true, session_skip_reason: "VIX_SPIKE" — do not trade.

    **TICKER-LEVEL checks (skip that ticker only):**

    4. Already moved today:
       Compare regularMarketPrice vs previousClose from Yahoo Finance 1-year fetch.
       If |price_change_today| > 3%: set proceed: false, skip_reason: "MOVED_TODAY".
       Reason: large opening moves make yesterday's close signals stale.

    5. Market holiday tomorrow:
       web_search: `"Stock market holiday {next trading date}"`
       If tomorrow is a market holiday: set proceed: false for all tickers,
       skip_reason: "PRE_HOLIDAY".
       Reason: pre-holiday sessions have thin volume and unusual positioning.

    6. Earnings within 5 days: already implemented in step 5a ✅

    skip_reason values: `MA200_DECLINING | MACRO_RELEASE | VIX_SPIKE | MOVED_TODAY | PRE_HOLIDAY | EARNINGS_PROXIMITY`

6. **Fetch market data for each ticker** — for each ticker in TICKER_ALLOWLIST:

   Run the screener script (handles fetch + all indicator math):
   ```bash
   python3 01_scan/screener.py {TICKER}
   ```
   The script exits non-zero and outputs `{"error": "..."}` on failure — treat as a
   rejected ticker and log the error string in `abort_reason`.

   Parse the returned JSON. Field map:
   - `price`            → current price
   - `market_time`      → Unix timestamp — use for freshness check (step 7)
   - `rsi_14`           → RSI-14 (Wilder smoothed)
   - `ma200`            → 200-day simple moving average
   - `ma200_slope`      → 20-day ROC of MA200 (decimal)
   - `ma200_slope_flag` → `RISING | FLAT | DECLINING`
   - `lower_bb_20_2sd`  → Lower Bollinger Band (20-day SMA − 2σ)
   - `upper_bb_20_2sd`  → Upper Bollinger Band
   - `atr_14`           → 14-day Average True Range (Wilder smoothed)
   - `price_vs_ma200`   → (price − MA200) / MA200 as decimal
   - `bb_touch`         → boolean — true if price ≤ lower_bb_20_2sd
   - `vol_today`        → today's volume (integer)
   - `vol_avg_20d`      → 20-day average volume
   - `volume_vs_avg`    → vol_today / vol_avg_20d

   EMA9, EMA21, MACD, 20-day high: compute in-context from the close series only when
   Signals 2, 3, or 5 require them (avoid computing for tickers that fail Signal 1 first).

   Reject any ticker where the script returns a non-zero exit code or an `error` key.
   Reject any quote where `market_time` is older than today's market open.

7. **Verify data freshness** — all quotes must be from today's session.
   If a ticker returns stale data: exclude it, log reason in abort_reason.

8. Apply entry signal criteria (Signals 1–5) to each ticker.
9. Count signals firing per ticker — assign confidence level.
10. Apply regime modifiers from knowledge/wiki/market-regimes.md.
11. Write output to 01_scan/output/scan-result.json.

## Data sources

```yaml
VIX (step 4):   web_search — query "VIX index current level today"
                No API key required.

Market data (steps 5–7):   python3 01_scan/screener.py {TICKER}
                Wraps Yahoo Finance chart API — no API key required.
                Returns JSON with all required indicators (see step 6 field map).
                Reject on non-zero exit or error key in output.
                No signature verification — verify market_time freshness instead.
```

## Output schema (01_scan/output/scan-result.json)

```json
{
  "timestamp": "ISO-8601",
  "regime": "string from market-regimes.md",
  "session_skip": false,
  "session_skip_reason": null,
  "vix_check": {
    "live_vix": number,
    "stored_vix": number,
    "delta": number,
    "regime_boundary_crossed": true,
    "action": "PROCEED | ROUTED_TO_MACRO_UPDATE"
  },
  "open_positions": [
    {
      "ticker": "string",
      "entry_price": number,
      "entry_date": "ISO-8601",
      "current_price": number,
      "pnl_pct": number,
      "hold_days": number,
      "exit_signal": "TAKE_PROFIT | STOP_LOSS | TRAILING_STOP | RSI_EXIT | MACD_EXIT | END_OF_WEEK | MAX_HOLD | HOLD",
      "exit_urgency": "IMMEDIATE | RECOMMEND | MONITOR"
    }
  ],
  "tickers_scanned": ["AAPL", "..."],
  "candidates": [
    {
      "ticker": "string",
      "price": number,
      "rsi_14": number,
      "ma_200": number,
      "volume_vs_avg": number,
      "signal": "BULLISH | BEARISH | NEUTRAL",
      "signals_fired": ["RSI_OVERSOLD", "MACD_CROSSOVER"],
      "signal_count": number,
      "confidence": "HIGH | MEDIUM | LOW",
      "ma200_slope": number,
      "ma200_slope_flag": "RISING | FLAT | DECLINING",
      "earnings_warning": false,
      "earnings_date": "ISO-8601 or null",
      "skip_reason": "string or null",
      "proceed": true,
      "reason": "max 20 words"
    }
  ],
  "stage_status": "COMPLETE | ABORT",
  "abort_reason": "string or null"
}
```

## Edge cases

| Condition | Action |
|-----------|--------|
| web_search returns no VIX value | Write ABORT — cannot verify regime freshness |
| Yahoo Finance HTTP non-200 for ticker | Exclude ticker, log in abort_reason |
| Yahoo Finance returns stale quote | Exclude ticker, log reason |
| All tickers excluded | Write ABORT — no clean data |
| Yahoo Finance missing required field | Exclude ticker, log in abort_reason |
| CRISIS: true in macro-context.md | Write CIRCUIT_BREAKER, write ABORT, halt — do not scan |
| live_vix delta > 5 points | Halt, route to Stage 07 Part C, do not scan |
| VIX regime boundary crossed | Halt, route to Stage 07 Part C, do not scan |
| Earnings tomorrow (step 5a) | Set proceed: false — skip entry signal generation for that ticker |
| Earnings within 5 days (step 5a) | Cap confidence at LOW, set earnings_warning: true, record date |
| Earnings search inconclusive | Set earnings_warning: false, proceed normally |
| MA200_SLOPE < −0.001 (step 4b) | Reject all bullish signals for ticker, flag MA200_DECLINING |
| MA200_SLOPE −0.001 to 0.001 (step 4b) | Reduce signal confidence by one tier, flag MA200_FLAT |
| Major macro release today (step 4b) | session_skip: true, session_skip_reason: "MACRO_RELEASE" |
| VIX risen >35% in 7 days (step 4b) | session_skip: true, session_skip_reason: "VIX_SPIKE" |
| VIX risen 20–35% in 7 days (step 4b) | Downgrade all signal confidence by one tier |
| Price moved >3% today (step 4b) | proceed: false for that ticker, skip_reason: "MOVED_TODAY" |
| Market holiday tomorrow (step 4b) | proceed: false for all tickers, skip_reason: "PRE_HOLIDAY" |

## What you must NOT do

- Do not make buy/sell recommendations here
- Do not read 04_decision/ or 05_review/
- Do not write to the wiki directly
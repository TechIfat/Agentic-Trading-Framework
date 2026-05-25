# 01_scan/rules.md — Layer 3
# Scan criteria template. Edit these to change what the agent looks for.
# Changes here take effect next session automatically.
# Exit rules are processed in Phase 2+ only — see CLAUDE.md CURRENT_PHASE.

## Universe

[DEFINE YOUR UNIVERSE HERE - e.g., S&P 500 constituents]
No penny stocks. No suspended securities.

```yaml
TICKER_ALLOWLIST:
  - AAPL   # Apple
  - TSLA   # Tesla
  - MSFT   # Microsoft
```

To add tickers: append to the list above AND update 03_risk/risk-limits.md allowlist.
Both files must be consistent or Stage 03 will reject the candidate.

---

## Step 0 — Check open positions first (Phase 2+ only)

Before scanning for new entries, read 06_execute/open-positions/.
For each open position file found:
1. Get current price via MCP
2. Calculate % change from entry_price
3. Check against exit rules below
4. Output EXIT signal if criteria met
5. Only then proceed to entry scan for remaining capacity

In Phase 1: read open-positions/ for status reporting only.
Do NOT generate EXIT signals. Do NOT process exit criteria.

---

## Entry signal criteria (ALL must be true for BULLISH)

```yaml
RSI_14:         < 30         # deeply oversold
PRICE_VS_MA200: > 0          # above long-term trend (price > MA200)
VOLUME_VS_AVG:  > 1.0        # volume confirmation
```

## Entry signal criteria (ALL must be true for BEARISH)

```yaml
RSI_14:         > 70         # overbought
PRICE_VS_MA200: < 0          # below long-term trend
VOLUME_VS_AVG:  > 1.0        # volume confirmation
```

## Ticker-specific volume overrides

Apply these thresholds instead of the default for the listed tickers.
All other signal criteria remain unchanged.

```yaml
MSFT:  VOLUME_VS_AVG > 0.8   # Example: institutional stock — lower natural vol vs average
```

## NEUTRAL

Everything else. Pass to Stage 02 only if BULLISH or BEARISH.

---

### MA200 slope filter (pre-condition for all bullish signals)

MA200_SLOPE: (MA200_today - MA200_20days_ago) / MA200_20days_ago

* If MA200_SLOPE < -0.001 (declining by more than 0.1% over 20 days): REJECT signal regardless of RSI or other conditions. Flag as MA200_DECLINING in scan output.
* If MA200_SLOPE >= -0.001 and < 0.001 (flat): Reduce confidence by one tier. Flag as MA200_FLAT.
* If MA200_SLOPE >= 0.001 (rising): No penalty — signal proceeds normally. Flag as MA200_RISING.

Rationale: Buying oversold stocks in declining or flat long-term trends produces low-quality bounces that often fail. This filter protects against buying structural downtrends.

To compute MA200_20days_ago: use closes[-220:-20] average vs closes[-200:] average.

---

## Additional entry signals

### Signal 2 — MACD crossover
MACD_LINE:      crosses above SIGNAL_LINE from below
MACD_HISTOGRAM: turning positive (was negative prior session)
PRICE_VS_MA200: > 0

### Signal 3 — EMA crossover
EMA_9:          crosses above EMA_21
PRICE_VS_MA200: > 0
VOLUME_VS_AVG:  > 1.0

### Signal 4 — Bollinger Band mean reversion
PRICE:          touched lower Bollinger Band (2 std dev) intraday
RSI_14:         < 40
CLOSE:          back inside Bollinger Band at end of session
REGIME:         RANGING or HIGH_VOLATILITY_WATCH only

### Signal 5 — Volume breakout
PRICE:          breaks above 20-day high
VOLUME_VS_AVG:  > 2.0
PRICE_VS_MA200: > 0

### Signal 6 — Momentum pullback
PRICE_VS_MA200:   > 10%       # strongly above long-term trend (confirmed uptrend)
PRICE_VS_5D_HIGH: < -2%       # pulled back at least 2% from 5-day high (default)
RSI_14:           < 60        # not overbought — room to recover
VOLUME_VS_AVG:    > 0.8       # standard threshold
REGIME:           TRENDING_BULL or HIGH_VOLATILITY_WATCH only

Logic: Stock is in a strong uptrend but has pulled back slightly from its recent high — a dip-buying opportunity within the trend.

---

## Earnings proximity rules (applied at step 5a)

```yaml
EARNINGS_WINDOW_DAYS:   5       # trading days — cap confidence if earnings within this window
EARNINGS_EXCLUDE_DAYS:  1       # trading days — suppress entry signals entirely if earnings this close
```

| Condition | Action |
|-----------|--------|
| Earnings within EARNINGS_EXCLUDE_DAYS | proceed: false — no entry signals generated |
| Earnings within EARNINGS_WINDOW_DAYS  | confidence capped at LOW, earnings_warning: true |
| No earnings found / inconclusive      | earnings_warning: false, proceed normally |

These rules override signal confidence but do NOT override exit signals on open positions.

---

## Confidence weighting

Count how many independent signals fire for the same ticker:
* 1 signal firing   → confidence: LOW
* 2 signals firing  → confidence: MEDIUM
* 3+ signals firing → confidence: HIGH

Stage 04 only assigns HIGH confidence with 3+ signals AND wiki evidence.

---

## Regime modifiers (read from wiki/market-regimes.md)

If current regime is `HIGH_VOLATILITY`:
  - Tighten RSI thresholds: BULLISH < 30, BEARISH > 70
  - Require VOLUME_VS_AVG > 1.5

If current regime is `TRENDING_BULL`:
  - Relax RSI: BULLISH < 40 acceptable
  - MA200 filter still required

If current regime is `TRENDING_BEAR` or `CRISIS`:
  - Signal 6 is DISABLED — do not evaluate or fire

If regime is `UNKNOWN` or wiki is frozen:
  - Use default thresholds above

---

## Exit rules (Phase 2+ only — ignored in Phase 1)

Apply to each open position read from 06_execute/open-positions/:
ATR_AT_ENTRY is read from the open-position JSON file. All distance thresholds below scale with this value.

* TAKE_PROFIT:    entry_price + (2.0 × ATR_at_entry)  → EXIT signal
* STOP_LOSS:      entry_price − (1.0 × ATR_at_entry)  → EXIT signal (urgent — flag as STOP)
* TRAILING_STOP:  price drops (1.0 × ATR_at_entry) from highest high since entry → EXIT signal
* END_OF_DAY:     15:45 local time → EXIT signal
* END_OF_WEEK:    Friday session → EXIT signal
* MAX_HOLD_DAYS:  5 trading days → EXIT signal regardless of P&L
* RSI_EXIT:       RSI_14 > 65 on held position → EXIT signal
* MACD_EXIT:      MACD crosses back below signal line → EXIT signal

Exit signal priority if multiple fire simultaneously:
1. STOP_LOSS — always first, execute immediately
2. TAKE_PROFIT — execute
3. TRAILING_STOP — execute
4. RSI_EXIT or MACD_EXIT — present to human with recommendation
5. END_OF_DAY / END_OF_WEEK / MAX_HOLD_DAYS — present to human

---

## Open position output schema

For each position in 06_execute/open-positions/, include in scan-result.json:

```json
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
```

In Phase 1: exit_signal always = "HOLD", exit_urgency always = "MONITOR".
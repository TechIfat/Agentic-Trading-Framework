# 06_execute/CONTEXT.md — Layer 2
# Stage 06: Execution
# Role: place the order. Verify everything before touching the broker.

## Your job this stage

1. Check for CIRCUIT_BREAKER file. If it exists: halt immediately, alert human.
2. Read 05_review/pending-orders/ (see 05_review/pending-orders/README.md) — find the order for this session.
   Accept either a standard order file or a remainder order file (`-remainder.json`).
   Reject any file with `"trigger": "PARTIAL_FILL"` — that is a signal file, not an order.
3. Verify nonce: must not appear in audit/used-nonces.txt. If it does: halt (replay attack).
4. Verify order has not expired (expires_at > now).
5. **Re-run deterministic risk check** — re-read risk-limits.md, recheck ALL limits
   against live portfolio state. Market may have moved since Stage 03.
   For remainder orders: include the already-filled portion as an open position when
   calculating headroom against MAX_POSITION_GBP.
6. **Write pending file** — write 06_execute/pending/[session_id]-[ticker].pending
   BEFORE calling the broker. This is the two-phase commit checkpoint.
   If a .pending file already exists for this session: a prior crash occurred — halt
   immediately and alert human. Do not proceed.
7. **Check PAPER_TRADING flag in CLAUDE.md.**
   - If PAPER_TRADING = false: call MCP broker tool with JIT write token (live execution — normal path).
   - If PAPER_TRADING = true: skip broker MCP call entirely.
     Simulate a fill at current mid-price from the last Finnhub quote response (field `c`).
     Set fill_type = FULL, filled_price = last known mid-price, filled_size_gbp = requested size.
     Write to 06_execute/paper-trades/ instead of completed-trades/. Add "paper": true to the output JSON.
     Continue to steps 8–14 as normal — audit, nonce invalidation, open-positions update all run identically.
8. Verify broker response signature.
9. Write execution confirmation to 06_execute/completed-trades/ (see 06_execute/completed-trades/README.md for file format).
10. Append nonce to audit/used-nonces.txt (invalidate it).
    For remainder orders: append the new nonce. The original nonce was already
    invalidated during the initial fill — do not re-append it.
11. Write full audit entry to audit/session-log.md.
12. **Delete pending file** — only delete 06_execute/pending/[session_id]-[ticker].pending
    AFTER step 11 completes successfully. If this process crashes before step 12,
    Stage 07 will find the orphaned .pending file and halt before touching the wiki.
13. **Update open-positions/** — for BUY orders: write 06_execute/open-positions/[ticker].json
    For SELL orders: delete 06_execute/open-positions/[ticker].json
    (move contents to completed-trades/ first for audit purposes)
    Do this AFTER step 12. Format: see 06_execute/open-positions/README.md.
14. **If fill_type = PARTIAL: write partial fill signal** — see Partial fill handling below.
    Do this AFTER steps 10–13 are complete (nonce invalidated, audit written, pending
    file deleted). Do NOT end the session — await Stage 05 re-approval.

## MCP tools to call

**Pre-flight portfolio state (step 5):**
```
mcp__trading212__fetch_account_cash          → available cash balance
mcp__trading212__fetch_all_open_positions    → current open positions
```

**Live execution (step 7, PAPER_TRADING = false):**

LIMIT orders (default — preferred for controlled entry):
```
mcp__trading212__place_limit_order
  ticker:        {TICKER} without exchange suffix (e.g., AAPL, not AAPL.US)
  limitPrice:    number
  quantity:      shares = floor(size_gbp / current_price)
  timeValidity:  "DAY"
```

MARKET orders (only when decision specifies MARKET):
```
mcp__trading212__place_market_order
  ticker:    {TICKER}
  quantity:  shares
```

SELL orders:
```
1. mcp__trading212__search_specific_position_by_ticker  → confirm held quantity
2. mcp__trading212__place_limit_order  (sell direction)
```

Cancel:
```
mcp__trading212__cancel_order
```

**Ticker format note:** Your broker (e.g., Trading 212) may use tickers without exchange suffixes (AAPL), while data providers like Finnhub may require them (e.g., AAPL.US or LLOY.L). Map between them when passing data between stages.

**Credential:** Trading 212 API key loaded from `$TRADING212_API_KEY` environment variable.
No JIT token issuance required — the MCP server handles authentication.

Required fields in response: `confirmation_id` (or equivalent order ID), `filled_price`,
`filled_size`, `timestamp`. Treat any non-200 / unsigned response as ABORT.

## Pre-flight re-check (deterministic — no LLM)

Re-verify against risk-limits.md:
- Position size still within MAX_POSITION_GBP
- Daily loss still within MAX_DAILY_LOSS_GBP
- Market still open (not in NO_TRADE_WINDOW)
- Price not moved more than 1% since Stage 04 decision

If price moved > 1%: write STALE_PRICE to output, do NOT execute.
Cancel order. Route back to Stage 01 for fresh session.

## Execution output (06_execute/completed-trades/[session_id]-[ticker].json)

```json
{
  "session_id": "string",
  "ticker": "string",
  "action": "BUY | SELL",
  "requested_size_gbp": number,
  "filled_size_gbp": number,
  "filled_price": number,
  "fill_type": "FULL | PARTIAL | NONE",
  "confirmation_id": "string from broker",
  "executed_at": "ISO-8601",
  "nonce_used": "UUID-v4",
  "broker_signature_verified": true,
  "pre_flight_passed": true,
  "stage_status": "COMPLETE | PARTIAL | ABORT"
}
```

## Circuit breaker trigger

Write 06_execute/CIRCUIT_BREAKER if:
- fill_type = NONE three times this session
- Broker returns HTTP 5xx
- Pre-flight fails due to MAX_DAILY_LOSS_GBP breach
- fill_type = PARTIAL twice in the same session (broker instability — do not attempt third order)
- CRISIS: true found in knowledge/wiki/macro-context.md at session start
  (this is written by the session start checklist and Stage 01 step 4 — not by Stage 06 directly,
  but listed here so the trigger conditions are complete in one place)

Contents of CIRCUIT_BREAKER file:
```
TRIGGERED_AT: [ISO-8601]
REASON: [one line]
RESET_REQUIRED: human must delete this file manually
```

If the circuit breaker fires while a partial fill signal is already open in
05_review/pending-orders/: leave the signal file in place. Do not delete it.
Human must reconcile the open broker position manually before resetting.

## Partial fill handling

Runs at step 14 — only after nonce invalidated, audit written, pending file deleted.

Write 05_review/pending-orders/[session_id]-[ticker]-partial.json:

```json
{
  "trigger": "PARTIAL_FILL",
  "session_id": "string",
  "ticker": "string",
  "action": "BUY | SELL",
  "original_nonce": "UUID-v4 — the nonce just invalidated in step 10",
  "original_size_gbp": number,
  "filled_size_gbp": number,
  "filled_price": number,
  "remainder_size_gbp": number,
  "confirmation_id": "string — broker confirmation for the filled portion",
  "partial_at": "ISO-8601"
}
```

Stage 05 reads this file and surfaces a re-approval prompt to the human.
Stage 05 will issue a new nonce. Do not reuse `original_nonce` under any
circumstances — it is already recorded in audit/used-nonces.txt.

When Stage 05 writes the remainder order ([session_id]-[ticker]-remainder.json),
re-enter this stage from step 1.
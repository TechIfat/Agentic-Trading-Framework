# 05_review/CONTEXT.md — Layer 2
# Stage 05: Human review gate
# NOTHING EXECUTES WITHOUT A SIGNED NONCE FROM THIS STAGE.

## Your job this stage

1. Read 04_decision/output/decision.json.
2. Read 04_decision/output/rationale.md.
3. Surface both to the human in readable form.
4. Wait for human approval.
5. On approval: write a signed order file to 05_review/pending-orders/ (see 05_review/pending-orders/README.md for format).
6. On rejection: write REJECTED to output and end session.

## What to show the human

Present a clear, concise summary. Do not pad it.

```
═══════════════════════════════════════════
TRADING DECISION — AWAITING YOUR APPROVAL
Session: [session_id]
Time: [timestamp]
═══════════════════════════════════════════

DECISION: [BUY/SELL/HOLD] [TICKER]
Size:      £[size_gbp]
Type:      [LIMIT @ £X | MARKET]
Confidence: [HIGH/MEDIUM/LOW]

RATIONALE SUMMARY:
[2-3 sentence summary from rationale.md]

WIKI EVIDENCE USED:
[bullet list of wiki pages referenced]

GRAPH EVIDENCE:
[one sentence from Graphify query result]

RISK CHECKS PASSED: ✓ All [N] rules
SCHEMA VALIDATED:   ✓
TICKER ON ALLOWLIST: ✓

─────────────────────────────────────────
Type APPROVE to proceed or REJECT to cancel.
This approval expires in 60 seconds.
═══════════════════════════════════════════
```

## On APPROVE

Write to 05_review/pending-orders/[session_id]-[ticker]-order.json:

```json
{
  "session_id": "string",
  "ticker": "string",
  "action": "BUY | SELL",
  "size_gbp": number,
  "order_type": "LIMIT | MARKET",
  "limit_price": number or null,
  "approved_at": "ISO-8601",
  "nonce": "UUID-v4",
  "expires_at": "ISO-8601 — approved_at + 5 minutes",
  "rationale_ref": "04_decision/output/rationale.md"
}
```

The nonce is single-use. Stage 06 verifies it and invalidates it on use.

## Edge cases

| Condition | Action |
|-----------|--------|
| No response within 60s | Write EXPIRED, end session |
| Human approves but size > MAX_POSITION_GBP | Reject regardless, log override attempt |
| Human tries to override ticker not on allowlist | Reject, require 2nd approver flag |
| Same nonce presented twice to Stage 06 | Stage 06 rejects — replay attack protection |

---

## Partial fill re-approval

Triggered when Stage 06 writes a file to 05_review/pending-orders/ with
`"trigger": "PARTIAL_FILL"`. Do NOT treat this as a new session — it is a
continuation of an existing one. The original nonce is already spent.

### How Stage 06 signals a partial fill

Stage 06 writes 05_review/pending-orders/[session_id]-[ticker]-partial.json:

```json
{
  "trigger": "PARTIAL_FILL",
  "session_id": "string",
  "ticker": "string",
  "action": "BUY | SELL",
  "original_nonce": "UUID-v4 — already spent, for audit linkage only",
  "original_size_gbp": number,
  "filled_size_gbp": number,
  "filled_price": number,
  "remainder_size_gbp": number,
  "confirmation_id": "string — broker confirmation for the filled portion",
  "partial_at": "ISO-8601"
}
```

### What to show the human

```
═══════════════════════════════════════════
PARTIAL FILL — REMAINDER AWAITING APPROVAL
Session: [session_id]
Time: [timestamp]
═══════════════════════════════════════════

ORIGINAL ORDER:  [BUY/SELL] [TICKER] £[original_size_gbp]
FILLED:          £[filled_size_gbp] @ £[filled_price] ✓ (conf: [confirmation_id])
REMAINDER:       £[remainder_size_gbp] — needs fresh approval

REMAINDER ACTION: [BUY/SELL] [TICKER] £[remainder_size_gbp]

─────────────────────────────────────────
Type APPROVE to place remainder, ABANDON to leave filled portion as-is.
This approval expires in 60 seconds.
NEW nonce will be issued — original nonce [original_nonce_short] already spent.
═══════════════════════════════════════════
```

### On APPROVE of remainder

1. Re-run deterministic risk check against current portfolio state.
   The filled portion now counts as an open position — recalculate headroom.
   If remainder would breach MAX_POSITION_GBP when added to filled portion: reject.

2. Write a new order file to 05_review/pending-orders/[session_id]-[ticker]-remainder.json:

```json
{
  "session_id": "string",
  "ticker": "string",
  "action": "BUY | SELL",
  "size_gbp": number,
  "order_type": "LIMIT | MARKET",
  "limit_price": number or null,
  "approved_at": "ISO-8601",
  "nonce": "UUID-v4 — freshly generated, unrelated to original",
  "expires_at": "ISO-8601 — approved_at + 5 minutes",
  "rationale_ref": "04_decision/output/rationale.md",
  "partial_fill_ref": "05_review/pending-orders/[session_id]-[ticker]-partial.json",
  "original_nonce": "UUID-v4 — spent nonce, for audit trail linkage only"
}
```

The `original_nonce` field is read-only audit metadata. Stage 06 must not
attempt to verify or re-use it. Only the new `nonce` field is actionable.

### On ABANDON of remainder

Write to audit/session-log.md:
```
PARTIAL_FILL_ABANDONED
session_id: [string]
ticker: [string]
filled: £[filled_size_gbp] @ £[filled_price]
remainder: £[remainder_size_gbp] — not placed
reason: human abandoned remainder
```

Delete the partial signal file from 05_review/pending-orders/.
The filled portion stands. Session ends.

### Partial fill edge cases

| Condition | Action |
|-----------|--------|
| No response within 60s | Treat as ABANDON — log, delete partial file, end session |
| Remainder would breach MAX_POSITION_GBP (including filled portion) | Reject remainder, treat as ABANDON |
| Circuit breaker fires while partial fill is open | Halt — do not issue new nonce. Human must resolve position manually and reset circuit breaker before next session |
| Two partial fills in same session | Issue CIRCUIT_BREAKER — broker instability. Do not attempt third order |
| Price moved >1% since original Stage 04 decision | Reject remainder (stale price). Treat as ABANDON — do not route to Stage 01 automatically; human decides |

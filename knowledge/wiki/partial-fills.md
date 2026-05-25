# knowledge/wiki/partial-fills.md
# Partial fill outcomes: recording rules and resolution states.
# Written by Stage 07 after any session where fill_type = PARTIAL.
# All entries are EXTRACTED from confirmed trade data unless marked INFERRED.

## What is a partial fill

A partial fill occurs when the broker executes only part of the requested order size.
Stage 06 records `fill_type: PARTIAL` in the completed-trades JSON and signals Stage 05
to seek fresh human approval for the remainder.

Three resolution states are possible, each requiring a distinct entry in trade-outcomes.md
and a distinct treatment in signal-performance.md.

---

## Resolution states

### REMAINDER_FILLED

The human approved the remainder and Stage 06 filled it successfully.

**Trade outcome entry** (append two linked entries to trade-outcomes.md):

```markdown
### [DATE] [TICKER] [BUY/SELL] $[TOTAL_SIZE] — PARTIAL FILL (REMAINDER_FILLED)

**Initial fill:**    $[filled_size] @ $[filled_price] (conf: [confirmation_id])
**Remainder fill:**  $[remainder_size] @ $[remainder_price] (conf: [remainder_confirmation_id])
**Blended price:**   $[weighted_avg_price]
**Outcome:**         [OPEN | WIN $X | LOSS $X | FLAT]
**Hold days:**       [N]
**Signal:**          [signal name]
**Regime at entry:** [regime]
**Sentiment at entry:** [POSITIVE | NEUTRAL | NEGATIVE]
**Nonces:**          [original_nonce] (initial) / [remainder_nonce] (remainder)
**Rationale ref:**   04_decision/output/rationale.md (session [ID])
**Source:**          EXTRACTED — 06_execute/completed-trades/[session_id]-[ticker].json
                     EXTRACTED — 06_execute/completed-trades/[session_id]-[ticker]-remainder.json
```

**Signal-performance.md treatment:**
Count as one trade. Use blended price as fill price. Apply to the signal's win rate table
in the normal way once the position closes. Mark with `(partial — remainder filled)` in
the Notes column so the blended execution cost is visible during review.

---

### ABANDONED

The human declined the remainder (or the 60-second re-approval window expired).
Only the initial fill stands.

**Trade outcome entry** (append to trade-outcomes.md):

```markdown
### [DATE] [TICKER] [BUY/SELL] $[INITIAL_FILL_SIZE] — PARTIAL FILL (ABANDONED)

**Filled at:**       $[filled_price] @ $[filled_size] (conf: [confirmation_id])
**Remainder:**       $[remainder_size] — not placed (human abandoned)
**Outcome:**         [OPEN | WIN $X | LOSS $X | FLAT] — based on filled portion only
**Hold days:**       [N]
**Signal:**          [signal name]
**Regime at entry:** [regime]
**Sentiment at entry:** [POSITIVE | NEUTRAL | NEGATIVE]
**Nonce:**           [original_nonce]
**Rationale ref:**   04_decision/output/rationale.md (session [ID])
**Source:**          EXTRACTED — 06_execute/completed-trades/[session_id]-[ticker].json
**Note:**            Position is smaller than originally signalled. See signal-performance.md
                     for size-adjustment notation.
```

**Signal-performance.md treatment:**
Count as one trade at the reduced size. Add a `(partial — abandoned, [filled_size]
of [original_size] placed)` note in the Notes column. Do not adjust the win/loss
calculation — the signal is still evaluated on outcome, not on size. However, if the
regime-specific notes section accumulates 3+ abandoned partials for the same signal,
add an INFERRED observation flagging execution risk in that regime.

---

### CIRCUIT_BREAKER_OPEN

The circuit breaker fired while the partial fill was unresolved (either before the
remainder could be approved, or on the second partial fill of the session).
The position is open and unresolved. Human must reconcile manually.

Circuit breaker triggers that can produce this state:
- Second partial fill in the same session (broker instability)
- Broker returns HTTP 5xx during remainder execution
- `CRISIS: true` set in macro-context.md (written by session start checklist — see macro-context.md § Macro regime flags)

**Trade outcome entry** (append to trade-outcomes.md):

```markdown
### [DATE] [TICKER] [BUY/SELL] $[INITIAL_FILL_SIZE] — PARTIAL FILL (CIRCUIT_BREAKER_OPEN)

**Filled at:**       $[filled_price] @ $[filled_size] (conf: [confirmation_id])
**Remainder:**       $[remainder_size] — unresolved at circuit breaker trigger
**Outcome:**         OPEN — MANUAL RESOLUTION REQUIRED
**Circuit breaker:** TRIGGERED_AT [ISO-8601] REASON: [one line from CIRCUIT_BREAKER file]
**Signal:**          [signal name]
**Regime at entry:** [regime]
**Nonce:**           [original_nonce]
**Rationale ref:**   04_decision/output/rationale.md (session [ID])
**Source:**          EXTRACTED — 06_execute/completed-trades/[session_id]-[ticker].json
**Status:**          PENDING — update this entry after manual resolution
```

**Signal-performance.md treatment:**
Do not count this trade in win rate calculations until the entry is marked resolved.
Add a `(circuit breaker — pending manual resolution)` note in the Notes column.
Once the human resolves the position and updates this entry to WIN/LOSS/FLAT,
Stage 07 should update signal-performance.md in the same session.

**After manual resolution**, replace `PENDING` with the resolution and add:

```markdown
**Resolved at:**     [ISO-8601]
**Resolution:**      [REMAINDER_FILLED manually | POSITION_CLOSED | POSITION_HELD]
**Final outcome:**   [WIN $X | LOSS $X | FLAT]
**Resolved by:**     human
```

---

## Cross-reference rules (signal-performance.md)

| Resolution state | Count in win rate | Notes column tag |
|------------------|-------------------|-----------------|
| REMAINDER_FILLED | Yes — on close, blended price | `(partial — remainder filled)` |
| ABANDONED | Yes — on close, reduced size | `(partial — abandoned, X of Y placed)` |
| CIRCUIT_BREAKER_OPEN | No — until manually resolved | `(circuit breaker — pending)` |

If any signal accumulates a partial fill rate > 30% in a given regime, Stage 04 should
treat that signal's confidence as one tier lower than the raw win rate suggests.
Stage 07 is responsible for computing this rate and adding it as an INFERRED observation
to the signal's regime table. Source the observation from this page.

---

## Writing rules

1. Always append — never modify existing entries.
2. CIRCUIT_BREAKER_OPEN entries must be updated when the position is manually resolved.
   Write the update immediately below the original entry, do not overwrite it.
3. All monetary values to 2 decimal places.
4. Nonce fields are audit metadata only — one nonce per fill leg.
5. If fill_type = PARTIAL appears in completed-trades JSON but no partial-fill entry
   exists here, treat as a data integrity gap. Flag in the weekly wiki integrity audit.
# knowledge/wiki/market-regimes.md
# Market regime classifications. Updated by Stage 07 after each session.

## Current regime

```text
REGIME:          UNKNOWN
SET_DATE:        [not yet set — update after first session]
EVIDENCE:        [populate after first session]
CONFIDENCE:      LOW
```

---

## Regime definitions

| Regime | Description | Key signals | Macro flag trigger |
|--------|-------------|-------------|-------------------|
| TRENDING_BULL | Sustained uptrend, breadth wide | Benchmark Index > 200-day MA, VIX < 15, advancers > decliners | — |
| TRENDING_BEAR | Sustained downtrend | Benchmark Index < 200-day MA, VIX > 25, decliners dominant | — |
| RANGING | Sideways, mean-reverting | Price oscillating within 5% band, RSI extremes more reliable | — |
| HIGH_VOLATILITY | Sharp intraday moves, unpredictable | VIX > 30, large daily ranges, news-driven | — |
| CRISIS | Systemic stress | Circuit breakers triggering, correlation spikes, liquidity thin | `CRISIS: true` in `macro-context.md` — must be set in sync |
| UNKNOWN | Insufficient data | Fewer than 5 sessions of data — use conservative defaults | — |

**CRISIS automatic enforcement:** setting `CRISIS: true` in `macro-context.md` causes the session start checklist to write `06_execute/CIRCUIT_BREAKER` on the next session. No scan runs. No positions are opened. To resume trading: investigate the crisis condition, set `CRISIS: false`, delete `06_execute/CIRCUIT_BREAKER`, recompute checksums if risk-limits.md was changed, then run SESSION_TYPE: AUDIT_ONLY before returning to DAILY_TRADING.

The CRISIS regime and the `CRISIS` macro flag in `macro-context.md` define the same
condition. Setting one without the other is a data integrity error. Stage 07 must update
both in the same wiki update session. See: `knowledge/wiki/macro-context.md` § Macro regime flags.

VIX thresholds in the Key signals column above are interpreted against `VIX_CURRENT`
in `macro-context.md` § Current macro snapshot. The reading and the thresholds live in
separate files — Stage 07 is responsible for comparing them when updating the regime.
If `VIX_CURRENT` crosses a boundary (< 15, > 25, > 30), regime must be re-evaluated.
See: `knowledge/wiki/macro-context.md` § Current macro snapshot.

---

## Regime history

| Date | Regime | Duration | Notes |
|------|--------|----------|-------|
| [populated by Stage 07] | | | |

---

## Regime-specific scan modifier summary

```text
RANGING:          RSI signals more reliable. Tighten to < 30 / > 70.
HIGH_VOLATILITY:  Increase volume threshold to 1.5x average.
TRENDING_BULL:    Relax RSI buy threshold to < 40. MA filter still required.
TRENDING_BEAR:    Only BEARISH signals. No longs.
CRISIS:           No new positions. Existing positions: alert human.
```
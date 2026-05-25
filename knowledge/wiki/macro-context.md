# knowledge/wiki/macro-context.md
# Current macro environment. Updated by Stage 07 weekly or on significant macro events.
# Stage 02 reads this before scoring sentiment.

## Current macro snapshot

LAST_UPDATED:     2026-05-20
BASE_RATE:        5.00%
INFLATION_CPI:    3.0%
CURRENCY_PAIR:    1.2500
INDEX_YTD:        5000.00
VIX_CURRENT:      18.50
MACRO_REGIME:     UNKNOWN

---

## Macro regime flags

Set these manually or by Stage 07 when conditions are met.
Stage 02 reads these to apply macro overrides to sentiment scoring.

RATE_HIKE_CYCLE:      false   # Example: Central bank paused hikes
RATE_CUT_CYCLE:       false
COMMODITY_SHOCK:      false   # Example: Oil prices stable
CURRENCY_STRESS:      false   
CRISIS:               false

When CRISIS: true is set here, Stage 07 must also:
1. Set REGIME: CRISIS in market-regimes.md
2. Set MACRO_REGIME: CRISIS in the snapshot above
The session start checklist in CLAUDE.md will detect CRISIS: true and write 06_execute/CIRCUIT_BREAKER automatically.

---

## Sector context

| Sector | Current view | Basis | Last updated |
|--------|-------------|-------|--------------|
| Technology | NEUTRAL | Rates stabilizing, but valuations stretched. | 2026-05-20 |
| Energy | POSITIVE | Supply constraints supportive of pricing. | 2026-05-20 |
| Financials | CAUTIOUS | Yield curve inversion pressuring margins. | 2026-05-20 |

---

## Key upcoming events

Central Bank decision: **[DATE]** 
CPI release: **[DATE]** 

---

## Macro change log

| Date | Change | Impact |
|------|--------|--------|
| 2026-05-20 | Template initialized. | Baseline established. |
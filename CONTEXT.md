# CONTEXT.md — Layer 1
# Session routing. Read this after CLAUDE.md to determine which stage to run.

## What to do when you open this file

1. Check the current session type below.
2. Navigate to the correct stage folder.
3. Read that stage's CONTEXT.md.
4. Do only what that stage asks. Nothing more.

---

## Current session type

```text
SESSION_TYPE: DAILY_TRADING
MARKET_OPEN: [INSERT_LOCAL_MARKET_OPEN_TIME]
RUN_STAGES: 01 → 02 → 03 → 04 → 05 → 06 → 07
```

Other valid session types:
- `AUDIT_ONLY` → run 07_update/ integrity audit sub-task only. Also used as dry-run verification — see SETUP.md § Step 7.
- `WIKI_REVIEW` → human-directed wiki review, no trading
- `BACKFILL` → update wiki from historical trade log only
- `MACRO_UPDATE` → run Stage 07 Part C only, then re-run Stage 01 scan.
  Triggered automatically by Stage 01 when VIX delta > 5 points or regime boundary crossed mid-week.

---

## Stage sequence for DAILY_TRADING

| Stage | Folder | Description |
|-------|--------|-------------|
| 01 | 01_scan/ | VIX freshness check first, then market scan |
| 02 | 02_sentiment/ | News sentiment — sanitised feed analysis |
| 03 | 03_risk/ | Deterministic risk gate — hard rules only |
| 04 | 04_decision/ | Order decision — temp=0, strict JSON output |
| 05 | 05_review/ | Human review — await signed approval nonce |
| 06 | 06_execute/ | Execution — MCP broker call, pre-flight re-check |
| 07 | 07_update/ | Wiki update — stage → audit → rebuild graph |

**Paper trading:** set PAPER_TRADING: true in CLAUDE.md before running SESSION_TYPE: DAILY_TRADING.
Stage 06 will simulate fills without calling the broker. All other stages are identical to live.
Recommended for first sessions after connecting broker MCP, and for testing Phase 2 exit logic
before risking real capital.

---

## Abort conditions (stop entire session immediately)

- Any stage writes an `ABORT` file to its output/ folder
- 03_risk/ outputs `REJECT`
- Circuit breaker flag found at 06_execute/CIRCUIT_BREAKER
- Wiki integrity audit (run weekly from 07_update/) returns `FREEZE`
- MCP response signature verification fails at any stage
- web_search returns no VIX value at Stage 01 step 4 → ABORT
- CRISIS: true found in knowledge/wiki/macro-context.md → write CIRCUIT_BREAKER, halt before Stage 01

On abort: write a timestamped entry to audit/session-log.md and stop.
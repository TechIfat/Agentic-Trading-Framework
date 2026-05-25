# audit/README.md
# WORM append-only audit log directory.
# Never delete or modify entries. Add only.

## Files in this directory

| File | Purpose |
|------|---------|
| session-log.md | Timestamped record of every session: stages run, decisions made, outcomes |
| used-nonces.txt | Single-use nonce registry — Stage 06 appends here after each execution |
| wiki-audit-log.md | Weekly integrity audit results |

## session-log.md format

Each session appends one block:

```markdown
---
SESSION: [session_id]
DATE: [ISO-8601]
STAGES_RUN: [01, 02, 03, 04, 05, 06, 07]
CANDIDATES_SCANNED: [N]
CANDIDATES_TO_DECISION: [N]
DECISIONS: [BUY TICKER £X | SELL TICKER £X | HOLD]
EXECUTIONS: [COMPLETE | PARTIAL | ABORT]
CIRCUIT_BREAKER: [not triggered | TRIGGERED — reason]
WIKI_UPDATES: [N entries committed]
INTEGRITY_AUDIT: [CLEAN | FROZEN | not run]
ABORT_REASON: [null | reason]
---
```

## used-nonces.txt format

One nonce per line, appended by Stage 06:
```
[UUID-v4] [session_id] [ticker] [ISO-8601]
```

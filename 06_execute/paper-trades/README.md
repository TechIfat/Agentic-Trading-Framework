# 06_execute/paper-trades/README.md
# Paper trade records. Written by Stage 06 when PAPER_TRADING: true.
# Identical schema to completed-trades/ with "paper": true added.
# Stage 07 reads these for wiki updates — signal performance and
# trade outcomes compound from paper trades exactly as from live trades.
# This means paper trading genuinely improves Stage 04 confidence
# calibration even before real money is involved.

## File format

Same as 06_execute/completed-trades/ plus one field:
  "paper": true

## How to use

1. Set PAPER_TRADING: true in CLAUDE.md
2. Run SESSION_TYPE: DAILY_TRADING normally
3. Review paper-trades/ after each session
4. When satisfied the pipeline works correctly:
   - Set PAPER_TRADING: false
   - Run SESSION_TYPE: AUDIT_ONLY to verify clean state
   - Next DAILY_TRADING session is live

## Current paper trades

None yet.

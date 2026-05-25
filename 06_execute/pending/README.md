# 06_execute/pending/README.md
# Two-phase commit checkpoint folder.
#
# .pending files are written BEFORE broker calls and deleted AFTER audit log confirms.
# Any .pending file found here at session start = a prior crash occurred mid-trade.
#
# Stage 07 Part 0 scans this folder before doing anything.
# If a file is found: session halts, human must investigate.
#
# To resolve manually:
# 1. Check broker account — did the trade actually execute?
# 2. If YES: manually write the completed-trade JSON and audit entry, then delete .pending
# 3. If NO:  simply delete the .pending file and restart
# Never delete a .pending file without first checking the broker.

# knowledge/sources/README.md
# Layer 4 — Raw immutable inputs.
# Files here are NEVER modified. The wiki is derived from these.
# If you need to re-derive the wiki from scratch, sources are the ground truth.

## What belongs here

- Raw exchange announcements (saved as PDFs or markdown, e.g., SEC EDGAR filings)
- Broker execution confirmations (copied from 06_execute/completed-trades/)
- Analyst reports ingested as reference material
- Economic data downloads (e.g., Central Bank or Labour department releases)
- Any external document that informed a wiki entry

## Naming convention

```text
[YYYY-MM-DD]-[ticker]-[type]-[source].md
Examples:
  2026-05-08-AAPL-10Q-SEC.md
  2026-05-08-macro-fed-rate-decision.md
  2026-05-08-MSFT-earnings-bloomberg.md
```

## Provenance rule

Every wiki entry tagged EXTRACTED must have a corresponding source file here.
Every wiki entry tagged INFERRED must reference at least one EXTRACTED entry.

The integrity audit checks this graph. Missing source files will be flagged.
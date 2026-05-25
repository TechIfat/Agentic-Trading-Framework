# 04_decision/CONTEXT.md — Layer 2
# Stage 04: Order decision — strict JSON output, temperature 0.
# Role: synthesise scan + sentiment + risk into a single structured decision.
# See README.md § Stage 04 for architectural overview and strict JSON output contract.
# Temperature: 0. Output is strict JSON only. No preamble. No explanation outside the JSON.

## Your job this stage

1. Read 03_risk/output/risk-result.json — passed candidates only.
2. Read knowledge/wiki/signal-performance.md — historical signal reliability.
3. Query knowledge/graph/graph.json — find relationships between this signal type
   and historical outcomes (Graphify query: signal conditions → outcome distribution).
4. Read knowledge/wiki/trade-outcomes.md — last 30 entries for context.
5. Make a BUY, SELL, or HOLD decision for each passed candidate.
6. Read `knowledge/wiki/proven-patterns.md`. Check if the candidate ticker triggers any of the institutional patterns based on the day of the week, macro flags, or recent earnings. Adjust the final Confidence level (UPGRADE or DOWNGRADE) exactly as instructed by the pattern rules.
7. Write decision JSON to 04_decision/output/decision.json.
8. Write rationale document to 04_decision/output/rationale.md.
9. Stage any wiki updates to 04_decision/staging/ (see 04_decision/staging/README.md for format) — NOT directly to wiki/.

## Data sources

- Risk-filtered candidates: `03_risk/output/risk-result.json`
- Signal reliability: `knowledge/wiki/signal-performance.md`
- Signal relationships: `knowledge/graph/graph.json`
- Historical outcomes: `knowledge/wiki/trade-outcomes.md`
- Institutional Edge: `knowledge/wiki/proven-patterns.md`

## Output schema — decision.json (STRICT. Any deviation = HOLD.)

```json
{
  "timestamp": "ISO-8601",
  "session_id": "YYYYMMDD-HHMMSS",
  "decisions": [
    {
      "ticker": "string — must be on allowlist",
      "action": "BUY | SELL | HOLD",
      "size_gbp": number,
      "order_type": "LIMIT | MARKET",
      "limit_price": number or null,
      "confidence": "HIGH | MEDIUM | LOW",
      "wiki_evidence": ["list of wiki page references used"],
      "graph_evidence": "string — Graphify query result summary",
      "rationale_ref": "rationale.md#ticker-section"
    }
  ],
  "stage_status": "COMPLETE | ABORT"
}
```

## Rationale document — rationale.md

Write one section per decision using this structure:

```markdown
## [TICKER] — [ACTION] — [timestamp]

### Signal
- Scan: [signal from Stage 01]
- Sentiment: [score and label from Stage 02]
- Risk: [passed rules, position size]

### Knowledge base evidence
- Wiki: [specific pages and what they say]
- Graph: [relationship query and result]

### Decision reasoning
[2-4 sentences. Factual. No speculation.]

### Compliance note
This rationale document is preserved with the trade record
and is available for regulatory export.
```

## Hallucination prevention rules

- **Ticker must appear in 03_risk/risk-limits.md ALLOWED_TICKERS**. If you generate
  a ticker not on that list, the schema validator in Stage 05 will reject it.
- **size_gbp must be <= position_size_gbp from Stage 03**. Do not recalculate.
- **confidence = LOW** if this is the first trade of this signal type in this regime
  (no prior wiki evidence). Do not assign HIGH without at least 5 supporting wiki entries.

## Wiki staging (04_decision/staging/)

If this decision reveals something worth adding to the wiki (new signal observation,
regime shift, unusual macro correlation), write a staging file:

```
04_decision/staging/YYYYMMDD-[ticker]-observation.md
```

Stage 07 will validate and commit these. Do not write to knowledge/wiki/ directly.

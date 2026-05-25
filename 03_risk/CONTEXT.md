# 03_risk/CONTEXT.md — Layer 2
# Stage 03: Deterministic risk gate
# THIS STAGE CONTAINS NO LLM JUDGEMENT.
# Apply rules exactly as written. If a rule is ambiguous, REJECT.

## Your job this stage

1. **Verify checksum FIRST**. Compute SHA-256 of risk-limits.md.
   Compare against vault-ref/checksums.txt entry for risk-limits.md.
   If mismatch: write ABORT, halt entirely, alert human. Do not read the file.
   (Initial risk limits checksum setup: see SETUP.md § Step 4.)

2. Read risk-limits.md.
3. Read 02_sentiment/output/sentiment-result.json.
4. For each candidate where proceed = true, apply every rule in risk-limits.md.
5. Write pass/fail per candidate to 03_risk/output/risk-result.json.

## Checksum verification pseudocode

```python
import hashlib

with open("03_risk/risk-limits.md", "rb") as f:
    computed = hashlib.sha256(f.read()).hexdigest()

with open("vault-ref/checksums.txt", "r") as f:
    stored = dict(line.split("  ") for line in f.read().strip().splitlines())

assert computed == stored["risk-limits.md"], "CHECKSUM MISMATCH — HALT"
```

## Output schema (03_risk/output/risk-result.json)

```json
{
  "timestamp": "ISO-8601",
  "checksum_verified": true,
  "candidates": [
    {
      "ticker": "string",
      "passed": true or false,
      "failed_rules": ["list rule names that failed"],
      "position_size_gbp": number or null
    }
  ],
  "stage_status": "COMPLETE | ABORT | REJECT_ALL"
}
```

If zero candidates pass: write stage_status = REJECT_ALL. Session ends here.

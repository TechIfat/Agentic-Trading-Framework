# SETUP.md — First-time setup guide

Follow these steps before running any trading session.
Estimated time: 2–3 hours for a careful first setup.

---

## Step 1 — Prerequisites

Install these tools:

```bash
# Python 3.10+
python3 --version

# Graphify (Use pipx for isolated CLI environments)
pipx install graphifyy

# Claude Code (for running the agent)
npm install -g @anthropic-ai/claude-code

# Verify checksum utility exists
shasum --version   # Mac/Linux standard
```

---

## Step 2 — Set up your broker MCP connection

This workspace is designed to work with any broker that exposes an MCP server.
Tested with: Alpaca, Trading 212, Interactive Brokers.

Example for a local MCP server:
```bash
# Add to vault-ref/mcp-allowlist.txt
echo "uvx my-broker-mcp-server" >> vault-ref/mcp-allowlist.txt
```

---

## Step 3 — Configure your vault

Choose one of:
- **Local (development only):** store secrets in a `.env` file (never commit this to git).
- **Production:** HashiCorp Vault, Azure Key Vault, or 1Password Secrets Automation.

Minimum secrets required:
```text
BROKER_API_KEY         # execution access (loaded as environment variable)
ANTHROPIC_API_KEY      # Claude API
AES256_KEY             # optional: for encrypting wiki/graph/audit at rest
```

---

## Step 4 — Compute and store the risk-limits.md checksum

After reviewing and accepting `03_risk/risk-limits.md`:

```bash
# On Mac/Linux:
shasum -a 256 03_risk/risk-limits.md > vault-ref/checksums.txt

# If using a production vault, copy the output hash into your vault under key: checksums/risk-limits-md
```

**Repeat this every time you edit risk-limits.md.**

---

## Step 5 — Customise your ticker universe and risk limits

Edit these files to match your account size and preferences:

- `01_scan/rules.md` — tickers, RSI thresholds, volume filters, and ATR multipliers.
- `03_risk/risk-limits.md` — position caps, daily loss limit, drawdown %.
- `02_sentiment/sentiment-criteria.md` — source trust tiers and macro overrides.

**After editing risk-limits.md, recompute the checksum (Step 4).**

---

## Step 6 — Populate macro-context.md

Open `knowledge/wiki/macro-context.md` and fill in the current values manually to establish a baseline:
- Central Bank base rate
- Current local CPI
- Primary Currency Pair (e.g., EUR/USD)
- Any active macro regime flags

*(Note: Once connected to a macro data provider, Stage 07 Part C can automate this on Mondays).*

---

## Step 7 — Run a dry-run session

Run an audit-only session to verify the workspace architecture and checksums without scanning the market.

```bash
claude --system-file CLAUDE.md "Run SESSION_TYPE: AUDIT_ONLY. Do not trade. Verify the workspace is configured correctly."
```

Expected output: a clean session log entry in `audit/session-log.md` with no errors.

---

## Step 8 — First Paper Trading session

Before risking real capital, ensure `PAPER_TRADING: true` is set in `CLAUDE.md`. This will simulate fills using live market data without calling the broker.

```bash
claude --system-file CLAUDE.md "Run SESSION_TYPE: DAILY_TRADING. Market is open. Run all stages."
```

Watch for Stage 05 — the agent will pause and ask for your APPROVE / REJECT.

---

## Ongoing maintenance

| Task | Frequency | How |
|------|-----------|-----|
| Update macro-context.md | Weekly or on macro events | Manual edit (if not using MCP macro tool) |
| Review wiki integrity audit | Weekly | Check 07_update/output/audit-result.md |
| Add new tickers to allowlist | As needed | Edit rules.md AND risk-limits.md, recompute checksum |
| Clear CIRCUIT_BREAKER | After investigating | Delete 06_execute/CIRCUIT_BREAKER manually |
| Set CRISIS: true | When macro crisis detected | Edit macro-context.md, set CRISIS: true AND REGIME: CRISIS in market-regimes.md together. Next session auto-writes CIRCUIT_BREAKER and halts. |
| Clear CRISIS state | After crisis resolves | Set CRISIS: false, set REGIME back to appropriate value, delete 06_execute/CIRCUIT_BREAKER, run AUDIT_ONLY before next DAILY_TRADING. |
| Review staged wiki entries | After each session | Check 04_decision/staging/ before Stage 07 commits |

---

## VSCode recommended extensions

- **YAML** — for structured output files
- **Markdown All in One** — for reading wiki pages
- **GitLens** — for tracking wiki change history (commit wiki folder to git)
- **Thunder Client** — for testing API endpoints directly
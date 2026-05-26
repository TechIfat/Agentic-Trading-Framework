# Agentic Trading Framework (ICM + LLM-Wiki)

A secure, deterministic, and interpretable framework for building autonomous financial agents using Large Language Models (LLMs). 

> **⚠️ DISCLAIMER:** This is an architectural framework and template. It is provided for educational and developmental purposes only. It does **not** contain financial advice, proprietary trading logic, or API keys. You are solely responsible for any financial risk incurred by deploying automated trading systems.

---

## The Architecture Problem This Solves

LLMs are incredible reasoning engines, but they are probabilistic. In financial execution, probability is dangerous. You cannot afford an LLM hallucinating a position size or forgetting a risk limit.

This framework solves the "Agentic Safety Problem" by separating probabilistic reasoning from deterministic execution. It utilises:

1. **Interpretable Context Methodology (ICM):** Replaces brittle Python orchestration loops (like LangChain/AutoGen) with a 7-stage Markdown folder hierarchy. The agent's state machine is 100% readable by compliance teams in plain English.
2. **Deterministic Guardrails:** The LLM is not allowed to do complex maths. A local Python script calculates indicators (ATR, Bollinger Bands). The LLM is not allowed to bypass risk limits; cryptographic SHA-256 checksums verify risk rules before API execution.
3. **Compounding Memory (LLM-Wiki):** AI agents usually suffer from amnesia, starting fresh every session. This framework implements a compounding Wiki. After every trade, the agent logs outcomes and updates a centralised Wiki, effectively writing its own textbook and adjusting future confidence scores based on past performance.
4. **Graphify Dependency Mapping:** The entire folder structure is mapped into a queryable knowledge graph, ensuring that safety gates (like Circuit Breakers) are mathematically linked to execution modules.

---

## The 7-Stage Pipeline

The agent routes through seven isolated folders per session. Stages communicate only through strict JSON outputs. 

| Stage | Role | Description |
|-------|------|-------------|
| **01_scan** | Data Collection | Triggers Python screener, evaluates technical signals, and filters out declining macro trends. |
| **02_sentiment** | News Analysis | Fetches latest news via web search, runs injection-attack sanitisation, and scores sentiment. |
| **03_risk** | Deterministic Gate | SHA-256 checksum verification. Hard limits on position sizing and drawdown. No LLM judgement allowed. |
| **04_decision** | Order Proposal | Reads the compounding Wiki. Outputs strict JSON order proposal and a compliance rationale document. |
| **05_review** | Human-in-the-Loop | Halts and awaits human approval. If approved, issues a single-use cryptographic Nonce. |
| **06_execute** | Two-Phase Commit | Verifies the Nonce. Writes a `.pending` file, calls the Broker via MCP, and updates local open-positions. |
| **07_update** | Memory & Audit | Checks for orphaned trades. Updates the Wiki with trade outcomes. Rebuilds the knowledge graph. |

---

## Enterprise-Grade Security Features

*   **Two-Phase Commit Protocol:** Before calling the broker API, the agent writes a local `.pending` file. If the system crashes during the API call, the next session will detect the orphaned `.pending` file and halt immediately.
*   **Cryptographic Checksums:** Risk limits are hard-coded in markdown. The agent must verify the SHA-256 hash of this file against a secure vault before it is allowed to execute. Any unauthorised change halts the system.
*   **Active Avoidance Layer:** The agent autonomously checks for major macroeconomic releases (e.g., Central Bank days) or market holidays, proactively skipping sessions to avoid binary event volatility.
*   **Model Context Protocol (MCP):** Connects safely to external Broker APIs using the open-source MCP standard, isolating execution logic from LLM prompt generation.

---

## Getting Started

### 1. Prerequisites
*   [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) CLI installed.
*   Python 3.10+ installed.
*   A Model Context Protocol (MCP) compatible broker server (e.g., Trading 212, Alpaca).

### 2. Setup the Framework
Clone the repository and set up your local environment:
```bash
git clone https://github.com/TechIfat/Agentic-Trading-Framework.git
cd Agentic-Trading-Framework
```

Initialise your risk limits checksum (Mac/Linux):
```bash
shasum -a 256 03_risk/risk-limits.md > vault-ref/checksums.txt
```

### 3. Run a Paper Trading Session
Ensure `PAPER_TRADING: true` is set in `CLAUDE.md`, then trigger Claude Code:
```bash
claude --system-file CLAUDE.md
```
Prompt the agent:
> "Run SESSION_TYPE: DAILY_TRADING. Market is open. PAPER_TRADING is true. Run all stages."

---

## Customisation

This framework is a skeleton. To make it trade your specific strategy:
1.  **Define your Edge:** Edit the `01_scan/rules.md` file to set your own RSI, MACD, or custom technical thresholds.
2.  **Define your Universe:** Update the `TICKER_ALLOWLIST` in `rules.md` and `risk-limits.md`.
3.  **Inject Institutional Knowledge:** Edit `knowledge/wiki/proven-patterns.md` to feed the agent your statistical edge for Stage 04 to read.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact & Consulting

**Ifat Noreen**  
*Principal Agentic AI Architect | Founder, Shift AI Systems Ltd*

* **LinkedIn:** [linkedin.com/in/ifat-noreen](https://www.linkedin.com/in/ifat-noreen)
* **GitHub:** [@TechIfat](https://github.com/TechIfat)
* **Web:** [shiftaiconsulting.co.uk](https://shiftaiconsulting.co.uk)
# 06_execute/open-positions/README.md
# Active positions. Read by Stage 01 at start of every session.
# Updated by Stage 06 when a trade executes.

## How this folder works

One JSON file per open position, named: [ticker].json
When a position is closed (sold), Stage 06 moves the file to completed-trades/
and writes the final outcome.

Stage 01 reads every .json file here at the start of each session.
In Phase 1: reports P&L status only, no exit signals generated.
In Phase 2+: checks exit criteria and generates EXIT signals.

---

## File format

```json
{
  "ticker": "AAPL",
  "action": "BUY",
  "entry_price": 2482,
  "entry_date": "2026-05-12T09:15:00Z",
  "size_gbp": 200,
  "shares": 8,
  "session_id": "20260512-091500",
  "confirmation_id": "string from broker",
  "hold_overnight": false,
  "notes": "RSI oversold bounce + MACD crossover. Energy sector positive."
}
```

---

## How to add a position manually (Phase 1 testing)

If you want to test position monitoring without a live trade,
create a file manually using the format above.
Next session Stage 01 will report current P&L against your entry.

---

## Current open positions

None yet. Files will appear here after first executed trade.

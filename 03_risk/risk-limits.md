# 03_risk/risk-limits.md — Layer 3 (DETERMINISTIC)
# These rules are applied exactly. No interpretation. No exceptions.
# Any edit to this file invalidates the checksum in vault-ref/checksums.txt.
# Update the checksum after every edit or Stage 03 will halt.

## Hard position limits

```
MAX_POSITION_GBP:        100       # single position cap
MAX_DAILY_LOSS_GBP:      1000      # total realised loss today before session halts
MAX_DRAWDOWN_PCT:        2.0       # unrealised drawdown vs account value
MAX_SINGLE_STOCK_PCT:    10.0      # single stock as % of total portfolio value
MAX_OPEN_POSITIONS:      5         # concurrent open positions
```

## Timing restrictions

```
NO_TRADE_WINDOW_OPEN_MIN:   30    # no new trades in first 30 min after market open
NO_TRADE_WINDOW_CLOSE_MIN:  30    # no new trades in last 30 min before market close
NO_TRADE_DAYS: Saturday, Sunday   # weekends
```

## Ticker allowlist

Only tickers on this list may be traded. Any candidate not on this list: REJECT.

```
ALLOWED_TICKERS:
  - AAPL
  - TSLA
  - MSFT
```

## Position sizing formula

```
position_size_gbp = min(
    account_value_gbp * 0.02,   # risk 2% of account per trade
    MAX_POSITION_GBP             # hard cap
)
```

## Circuit breaker trigger conditions

Write 06_execute/CIRCUIT_BREAKER file if ANY of:
- Daily loss >= MAX_DAILY_LOSS_GBP
- 3 consecutive execution failures
- Broker MCP returns HTTP 5xx three times in one session
- Drawdown >= MAX_DRAWDOWN_PCT on any single position

Once CIRCUIT_BREAKER file exists, no further trading until human deletes it manually.

## File integrity

```
CHECKSUM_FILE: vault-ref/checksums.txt
CHECKSUM_ALGO: SHA-256
LAST_UPDATED:  2026-05-21
UPDATED_BY:    your_name
```

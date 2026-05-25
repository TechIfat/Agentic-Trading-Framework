# 02_sentiment/sentiment-criteria.md — Layer 3
# Sentiment scoring reference. Static. Edit deliberately.

## Source trust tiers

```yaml
TIER_1 (weight x1.5):
  - Reuters
  - Bloomberg
  - Financial Times
  - Primary Exchange Announcements (e.g., SEC EDGAR, RNS)

TIER_2 (weight x1.0):
  - Major National Business News (e.g., BBC, WSJ, CNBC)
  - Morningstar

TIER_3 (weight x0.5 — treat with caution):
  - Twitter/X financial accounts
  - Reddit / Stocktwits
  - Unknown or aggregated sources

UNTRUSTED (discard entirely):
  - Anonymous blogs
  - Paywalled content with summary only
  - Any source not reachable via https://
```

## Macro override rules

If wiki/macro-context.md contains any of these regime flags,
apply the override before scoring individual tickers:

```yaml
MACRO_REGIME: RATE_HIKE_CYCLE
  → Apply -1 to all BULLISH candidates in rate-sensitive sectors
  → Sectors: real estate, utilities, financials (when not banks)

MACRO_REGIME: COMMODITY_SHOCK
  → Apply +1 to energy and mining tickers regardless of individual news

MACRO_REGIME: CURRENCY_STRESS
  → Apply -1 to domestic-revenue-dependent companies
  → Apply +1 to foreign-revenue earners (multinationals)
```

## Conflicted signal handling

A ticker is CONFLICTED when:
- Scan signal is BULLISH but sentiment_score <= -1
- Scan signal is BEARISH but sentiment_score >= +1

CONFLICTED tickers: set proceed = false.
Log the conflict in the output. Do not attempt to resolve it.
Stage 04 never sees a CONFLICTED ticker.
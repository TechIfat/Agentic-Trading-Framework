#!/usr/bin/env python3
"""
01_scan/screener.py — Technical indicator calculator for Stage 01 scanning.
Fetches 1y daily OHLCV from Yahoo Finance and prints JSON to stdout.
Usage: python3 01_scan/screener.py TICKER   (e.g. AAPL, MSFT, TSLA)
"""
import sys
import json
import math
import urllib.request

# Removed the hardcoded .L suffix to support generic global tickers
YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{}?interval=1d&range=1y"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_chart(ticker):
    req = urllib.request.Request(YAHOO_URL.format(ticker), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def wilder_rsi(closes, period=14):
    """Wilder smoothed RSI using all available closes."""
    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains   = [max(c, 0) for c in changes]
    losses  = [max(-c, 0) for c in changes]
    ag = sum(gains[:period]) / period
    al = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        ag = (ag * (period - 1) + gains[i]) / period
        al = (al * (period - 1) + losses[i]) / period
    rs = ag / al if al else float("inf")
    return 100 - 100 / (1 + rs)

def wilder_atr(highs, lows, closes, period=14):
    """Wilder smoothed ATR."""
    trs = [
        max(highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i]  - closes[i - 1]))
        for i in range(1, len(closes))
    ]
    atr = sum(trs[:period]) / period
    for i in range(period, len(trs)):
        atr = (atr * (period - 1) + trs[i]) / period
    return atr

def slope_flag(slope):
    if slope >= 0.001:
        return "RISING"
    if slope < -0.001:
        return "DECLINING"
    return "FLAT"

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: screener.py TICKER"}))
        sys.exit(1)

    ticker = sys.argv[1].upper()

    try:
        data = fetch_chart(ticker)
    except Exception as e:
        print(json.dumps({"error": f"fetch failed: {e}", "ticker": ticker}))
        sys.exit(1)

    try:
        result = data["chart"]["result"][0]
        meta   = result["meta"]
        quote  = result["indicators"]["quote"][0]

        raw_rows = zip(
            quote.get("close",  []),
            quote.get("high",   []),
            quote.get("low",    []),
            quote.get("volume", []),
        )
        rows = [(c, h, l, v) for c, h, l, v in raw_rows if None not in (c, h, l, v)]

        if len(rows) < 220:
            print(json.dumps({
                "error": f"insufficient data: {len(rows)} rows (need 220)",
                "ticker": ticker,
            }))
            sys.exit(1)

        closes  = [r[0] for r in rows]
        highs   = [r[1] for r in rows]
        lows    = [r[2] for r in rows]
        volumes = [r[3] for r in rows]

        price = meta.get("regularMarketPrice", closes[-1])
        market_time = meta.get("regularMarketTime")

        # ── MA200 & slope ───────────────────────────────────────────────
        ma200        = sum(closes[-200:]) / 200
        ma200_20ago  = sum(closes[-220:-20]) / 200
        ma200_slope  = (ma200 - ma200_20ago) / ma200_20ago

        # ── RSI-14 ──────────────────────────────────────────────────────
        rsi_14 = wilder_rsi(closes)

        # ── Bollinger Bands (20-day, 2σ) ────────────────────────────────
        bb_window = closes[-20:]
        ma20      = sum(bb_window) / 20
        std20     = math.sqrt(sum((x - ma20) ** 2 for x in bb_window) / 20)
        lower_bb  = ma20 - 2 * std20
        upper_bb  = ma20 + 2 * std20

        # ── ATR-14 ──────────────────────────────────────────────────────
        atr_14 = wilder_atr(highs, lows, closes)

        # ── Volume ──────────────────────────────────────────────────────
        vol_today    = meta.get("regularMarketVolume", volumes[-1])
        vol_avg_20   = sum(volumes[-20:]) / 20
        volume_vs_avg = round(vol_today / vol_avg_20, 4) if vol_avg_20 else None

        output = {
            "ticker":           ticker,
            "price":            round(price, 4),
            "market_time":      market_time,
            "rsi_14":           round(rsi_14, 2),
            "ma200":            round(ma200, 4),
            "ma200_slope":      round(ma200_slope, 6),
            "ma200_slope_flag": slope_flag(ma200_slope),
            "lower_bb_20_2sd":  round(lower_bb, 4),
            "upper_bb_20_2sd":  round(upper_bb, 4),
            "ma20":             round(ma20, 4),
            "atr_14":           round(atr_14, 4),
            "price_vs_ma200":   round((price - ma200) / ma200, 4),
            "bb_touch":         price <= lower_bb,
            "vol_today":        int(vol_today),
            "vol_avg_20d":      round(vol_avg_20, 0),
            "volume_vs_avg":    volume_vs_avg,
        }

        print(json.dumps(output, indent=2))

    except (KeyError, IndexError, TypeError, ZeroDivisionError) as e:
        print(json.dumps({"error": f"parse failed: {e}", "ticker": ticker}))
        sys.exit(1)

if __name__ == "__main__":
    main()
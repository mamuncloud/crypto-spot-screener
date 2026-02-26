"""
screener/rising3methods.py

Strategy: Rising Three Methods (Bullish Continuation Pattern)
--------------------------------------------------------------
Criteria (classic candlestick pattern):
  1. First candle  : Large bullish candle (body >= threshold % of range)
  2. Candles 2-4   : Three small candles that stay within the body of candle 1
                     (each close is above candle 1's open, each close is below candle 1's close)
  3. Fifth candle  : Large bullish candle that closes ABOVE candle 1's close

This is a classic bullish continuation pattern typically found in uptrends.
"""

import ccxt
from typing import Optional


# Minimum body ratio to qualify as a "large" candle (20% of candle range)
LARGE_CANDLE_BODY_RATIO = 0.6

# Small candle body must be less than this ratio relative to candle 1's body
SMALL_CANDLE_MAX_BODY_RATIO = 0.5


def is_bullish(candle: list) -> bool:
    """Return True if candle is bullish (close > open)."""
    return candle[4] > candle[1]  # close > open


def body_size(candle: list) -> float:
    """Return absolute body size of candle."""
    return abs(candle[4] - candle[1])  # |close - open|


def candle_range(candle: list) -> float:
    """Return high - low range of candle."""
    return candle[2] - candle[3]  # high - low


def analyze(ohlcv: list) -> Optional[dict]:
    """
    Detect the Rising Three Methods pattern on the last 5 candles.

    Args:
        ohlcv: List of candles [[timestamp, open, high, low, close, volume], ...]
               Must have at least 5 candles.

    Returns:
        dict with signal info if pattern detected, else None.
    """
    if len(ohlcv) < 5:
        return None

    # Last 5 candles
    c1, c2, c3, c4, c5 = ohlcv[-5], ohlcv[-4], ohlcv[-3], ohlcv[-2], ohlcv[-1]

    c1_open  = c1[1]
    c1_close = c1[4]
    c5_close = c5[4]

    # --- Check candle 1: large bullish candle ---
    if not is_bullish(c1):
        return None

    c1_body = body_size(c1)
    c1_range = candle_range(c1)

    if c1_range == 0:
        return None

    if (c1_body / c1_range) < LARGE_CANDLE_BODY_RATIO:
        return None

    # --- Check candles 2, 3, 4: small candles inside candle 1's body ---
    for cx in (c2, c3, c4):
        cx_open  = cx[1]
        cx_close = cx[4]

        # Close must stay within candle 1's body range
        if cx_close <= c1_open or cx_close >= c1_close:
            return None

        # Open must stay within candle 1's body range
        if cx_open <= c1_open or cx_open >= c1_close:
            return None

        # Body must be small relative to candle 1's body
        if c1_body > 0 and (body_size(cx) / c1_body) > SMALL_CANDLE_MAX_BODY_RATIO:
            return None

    # --- Check candle 5: large bullish candle closing above candle 1's close ---
    if not is_bullish(c5):
        return None

    c5_body = body_size(c5)
    c5_range = candle_range(c5)

    if c5_range > 0 and (c5_body / c5_range) < LARGE_CANDLE_BODY_RATIO:
        return None

    if c5_close <= c1_close:
        return None

    # Pattern matched!
    return {
        "signal": "RISING_3_METHODS",
        "close": c5_close,
        "volume": c5[5],
        "c1_close": c1_close,
        "c5_close": c5_close,
    }


def run(
    exchange: ccxt.okx,
    symbols: list[str],
    timeframe: str,
    limit: int,
) -> list[dict]:
    """
    Run the Rising Three Methods screener across all given symbols.

    Args:
        exchange: Initialized CCXT OKX exchange instance.
        symbols: List of trading pair symbols to screen.
        timeframe: Candle timeframe string (e.g., "4H", "1D").
        limit: Number of candles to fetch (minimum 5 required).

    Returns:
        List of dicts for symbols that match the Rising Three Methods pattern.
    """
    results = []
    total = len(symbols)

    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i:>4}/{total}] Checking {symbol:<20}", end="\r", flush=True)

        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

            if not ohlcv:
                continue

            result = analyze(ohlcv)
            if result:
                result["symbol"] = symbol
                results.append(result)
                print(
                    f"  [+] MATCH: {symbol:<20} | "
                    f"Close: {result['close']:.4f} | "
                    f"Signal: {result['signal']}"
                )

        except ccxt.NetworkError as e:
            print(f"\n  [!] Network error for {symbol}: {e}")
        except ccxt.ExchangeError as e:
            print(f"\n  [!] Exchange error for {symbol}: {e}")
        except Exception as e:
            print(f"\n  [!] Unexpected error for {symbol}: {e}")

    print()  # Clear the progress line
    return results

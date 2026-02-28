"""
screener/buyonbreakout.py

Strategy: Buy on Breakout
--------------------------
Criteria:
  - Current close price breaks ABOVE the highest close of the previous 20 candles.
  - Volume on the breakout candle is above the average volume of the previous 20 candles.

This is a momentum/breakout strategy: we look for symbols that have just
broken out of their 20-period high with above-average volume confirmation.
"""

import ccxt
from typing import Optional


def analyze(ohlcv: list) -> Optional[dict]:
    """
    Analyze OHLCV data for a 20-day breakout pattern.

    Args:
        ohlcv: List of candles [[timestamp, open, high, low, close, volume], ...]
               Must have at least 22 candles to be valid.

    Returns:
        dict with signal info if breakout detected, else None.
    """
    # Need at least 21 candles (20 lookback + 1 current)
    if len(ohlcv) < 22:
        return None

    # Extract close prices and volumes
    closes = [c[4] for c in ohlcv]
    volumes = [c[5] for c in ohlcv]

    current_close = closes[-1]
    current_volume = volumes[-1]

    # Lookback window: previous 20 candles (excluding current)
    lookback_closes = closes[-21:-1]
    lookback_volumes = volumes[-21:-1]

    highest_close = max(lookback_closes)
    avg_volume = sum(lookback_volumes) / len(lookback_volumes)

    # Breakout condition
    price_breakout = current_close > highest_close
    volume_confirmation = current_volume > avg_volume

    if price_breakout and volume_confirmation:
        return {
            "signal": "BUY_ON_BREAKOUT",
            "close": current_close,
            "volume": current_volume,
            "prev_high": highest_close,
            "avg_volume": avg_volume,
            "vol_ratio": round(current_volume / avg_volume, 2),
        }

    return None


def run(
    exchange: ccxt.okx,
    symbols: list[str],
    timeframe: str,
    limit: int,
) -> list[dict]:
    """
    Run the 20-day breakout screener across all given symbols.

    Args:
        exchange: Initialized CCXT OKX exchange instance.
        symbols: List of trading pair symbols to screen.
        timeframe: Candle timeframe string (e.g., "4H", "1D").
        limit: Number of candles to fetch (minimum 22 recommended).

    Returns:
        List of dicts for symbols that match the breakout criteria.
    """
    results = []
    total = len(symbols)

    for i, symbol in enumerate(symbols, 1):
        print(f"  [{i:>4}/{total}] Checking {symbol:<20}", end="\r", flush=True)

        try:
            # Fetch candle data
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
                    f"Vol Ratio: {result['vol_ratio']}x"
                )

        except ccxt.NetworkError as e:
            print(f"\n  [!] Network error for {symbol}: {e}")
        except ccxt.ExchangeError as e:
            print(f"\n  [!] Exchange error for {symbol}: {e}")
        except Exception as e:
            print(f"\n  [!] Unexpected error for {symbol}: {e}")

    print()  # Clear the progress line
    return results

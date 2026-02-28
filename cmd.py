"""
cmd.py - Command dispatcher for crypto screener strategies.

Loads the appropriate screener module based on the strategy name
and runs the screening logic.
"""

import sys
import ccxt
from typing import Optional


def get_exchange() -> ccxt.okx:
    """Initialize and return the OKX exchange instance."""
    exchange = ccxt.okx({
        "enableRateLimit": True,
        # Add API keys below if needed for private endpoints:
        # "apiKey": "YOUR_API_KEY",
        # "secret": "YOUR_SECRET",
        # "password": "YOUR_PASSPHRASE",
    })
    return exchange


def fetch_spot_symbols(exchange: ccxt.okx, quote: str = "USDT") -> list[str]:
    """
    Fetch all spot trading symbols from OKX filtered by quote currency.

    Args:
        exchange: CCXT OKX exchange instance.
        quote: Quote currency to filter (e.g., "USDT").

    Returns:
        List of symbol strings (e.g., ["BTC/USDT", "ETH/USDT", ...])
    """
    print(f"[*] Loading markets from OKX...")
    markets = exchange.load_markets()

    symbols = [
        symbol for symbol, market in markets.items()
        if market.get("spot") is True
        and market.get("active") is True
        and market.get("quote") == quote
    ]

    print(f"[*] Found {len(symbols)} active {quote} spot pairs.")
    return sorted(symbols)


def fetch_ohlcv(
    exchange: ccxt.okx,
    symbol: str,
    timeframe: str,
    limit: int,
) -> list:
    """
    Fetch OHLCV candle data for a given symbol.

    Args:
        exchange: CCXT OKX exchange instance.
        symbol: Trading pair symbol (e.g., "BTC/USDT").
        timeframe: Candle timeframe (e.g., "4H", "1D").
        limit: Number of candles to fetch.

    Returns:
        List of OHLCV candles: [[timestamp, open, high, low, close, volume], ...]
    """
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        return ohlcv
    except Exception as e:
        print(f"  [!] Error fetching {symbol}: {e}")
        return []


def run_screener(
    strategy: str,
    timeframe: str,
    limit: int = 100,
    quote: str = "USDT",
    top_n: Optional[int] = None,
) -> None:
    """
    Main dispatcher: loads the requested strategy and runs the screener.

    Args:
        strategy: Strategy name (e.g., "buyonbreakout", "rising3methods").
        timeframe: OHLCV timeframe (e.g., "4H", "1D").
        limit: Number of candles to fetch.
        quote: Quote currency filter.
        top_n: If set, only screen top N symbols by volume.
    """
    # Dynamically load the strategy module
    strategy_map = {
        "buyonbreakout": _run_buyonbreakout,
        "rising3methods": _run_rising3methods,
    }

    runner = strategy_map.get(strategy)
    if runner is None:
        print(f"[!] Unknown strategy: {strategy}")
        sys.exit(1)

    # Initialize exchange
    exchange = get_exchange()

    # Fetch available symbols
    symbols = fetch_spot_symbols(exchange, quote=quote)

    if top_n:
        symbols = symbols[:top_n]
        print(f"[*] Screening top {top_n} symbols.")

    print(f"[*] Running strategy: {strategy} on {len(symbols)} symbols...")
    print()

    # Run strategy
    results = runner(exchange, symbols, timeframe, limit)

    # Print results
    print_results(results, strategy, timeframe)


def _run_buyonbreakout(
    exchange: ccxt.okx,
    symbols: list[str],
    timeframe: str,
    limit: int,
) -> list[dict]:
    """Wrapper to call the buyonbreakout screener."""
    from screener.buyonbreakout import run as breakout_run
    return breakout_run(exchange, symbols, timeframe, limit)


def _run_rising3methods(
    exchange: ccxt.okx,
    symbols: list[str],
    timeframe: str,
    limit: int,
) -> list[dict]:
    """Wrapper to call the rising3methods screener."""
    from screener.rising3methods import run as rising_run
    return rising_run(exchange, symbols, timeframe, limit)


def print_results(results: list[dict], strategy: str, timeframe: str) -> None:
    """
    Print screening results to the console in a formatted table.

    Args:
        results: List of result dicts returned by the strategy.
        strategy: Strategy name (for display).
        timeframe: Timeframe used (for display).
    """
    print()
    print("=" * 60)
    print(f"  Results: {strategy.upper()} | TF: {timeframe}")
    print("=" * 60)

    if not results:
        print("  No symbols matched the criteria.")
    else:
        print(f"  {'Symbol':<20} {'Signal':<20} {'Close':>10} {'Volume':>15}")
        print(f"  {'-'*20} {'-'*20} {'-'*10} {'-'*15}")
        for r in results:
            print(
                f"  {r.get('symbol', ''):<20} "
                f"{r.get('signal', ''):<20} "
                f"{r.get('close', 0):>10.4f} "
                f"{r.get('volume', 0):>15.2f}"
            )

    print("=" * 60)
    print(f"  Total matches: {len(results)}")
    print("=" * 60)

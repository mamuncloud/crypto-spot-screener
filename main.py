#!/usr/bin/env python3
"""
Crypto Spot Screener - OKX
Usage:
    python main.py --strategy breakout_20day --tf 4H
    python main.py --strategy breakout_20day --tf 1D
    python main.py --strategy rising3methods --tf 1D
"""

import argparse
import sys
from cmd import run_screener


VALID_STRATEGIES = [
    "breakout_20day",
    "rising3methods",
]

VALID_TIMEFRAMES = [
    "1m", "3m", "5m", "15m", "30m",
    "1H", "2H", "4H", "6H", "12H",
    "1D", "3D", "1W", "1M",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Crypto Spot Screener for OKX",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--strategy",
        type=str,
        required=True,
        choices=VALID_STRATEGIES,
        help=(
            "Screening strategy to use.\n"
            "Available strategies:\n"
            "  breakout_20day  - 20-day breakout strategy\n"
            "  rising3methods  - Rising Three Methods candlestick pattern\n"
        ),
    )
    parser.add_argument(
        "--tf",
        type=str,
        required=True,
        choices=VALID_TIMEFRAMES,
        help=(
            "Timeframe for OHLCV data.\n"
            "Examples: 1m, 5m, 15m, 1H, 4H, 1D, 1W\n"
        ),
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Number of candles to fetch per symbol (default: 100)",
    )
    parser.add_argument(
        "--quote",
        type=str,
        default="USDT",
        help="Quote currency to filter pairs (default: USDT)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Only screen top N symbols by volume (default: all)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("  OKX Crypto Spot Screener")
    print("=" * 60)
    print(f"  Strategy  : {args.strategy}")
    print(f"  Timeframe : {args.tf}")
    print(f"  Quote     : {args.quote}")
    print(f"  Limit     : {args.limit} candles")
    if args.top:
        print(f"  Top N     : {args.top} symbols")
    print("=" * 60)
    print()

    run_screener(
        strategy=args.strategy,
        timeframe=args.tf,
        limit=args.limit,
        quote=args.quote,
        top_n=args.top,
    )


if __name__ == "__main__":
    main()

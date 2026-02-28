#!/usr/bin/env python3
"""
Crypto Spot Screener - OKX
Usage:
    python main.py --strategy buyonbreakout --tf 4H
    python main.py --strategy buyonbreakout --tf 1D
    python main.py --strategy rising3methods --tf 1D
"""

import argparse
import sys
from cmd import run_screener


VALID_STRATEGIES = [
    "buyonbreakout",
    "rising3methods",
]

VALID_TIMEFRAMES = [
    "1m", "3m", "5m", "15m"
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
            "  buyonbreakout  - Buy on Breakout strategy\n"
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
    parser.add_argument(
        "--webhook",
        type=str,
        default=None,
        metavar="URL",
        help=(
            "Discord Webhook URL for notifications.\n"
            "Falls back to DISCORD_WEBHOOK_URL env variable if not set.\n"
            "Use --webhook '' to disable notifications entirely."
        ),
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
    webhook_display = args.webhook or "(from DISCORD_WEBHOOK_URL env)"
    print(f"  Notify    : Discord {webhook_display}")
    print("=" * 60)
    print()

    run_screener(
        strategy=args.strategy,
        timeframe=args.tf,
        limit=args.limit,
        quote=args.quote,
        top_n=args.top,
        webhook_url=args.webhook,
    )


if __name__ == "__main__":
    main()

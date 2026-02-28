"""
notification.py - Discord notification module for Crypto Spot Screener.

Sends screening results to a Discord channel via Webhook using rich embeds.

Usage:
    from notification import DiscordNotifier

    notifier = DiscordNotifier(webhook_url="https://discord.com/api/webhooks/...")
    notifier.send_results(results, strategy="rising3methods", timeframe="1D")

Environment:
    Set DISCORD_WEBHOOK_URL in your environment or .env file to avoid
    hardcoding the webhook URL in your code.
"""

import os
import json
import time
import logging
from datetime import datetime, timezone
from typing import Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Embed color palette (Discord uses decimal int)
# ──────────────────────────────────────────────
class Color:
    GREEN   = 0x2ECC71   # success / bullish
    RED     = 0xE74C3C   # failure / bearish
    GOLD    = 0xF1C40F   # warning / info
    BLUE    = 0x3498DB   # neutral info
    PURPLE  = 0x9B59B6   # highlight
    GREY    = 0x95A5A6   # empty result


# ──────────────────────────────────────────────
# Strategy metadata for prettier messages
# ──────────────────────────────────────────────
STRATEGY_META = {
    "buyonbreakout": {
        "label": "Buy on Breakout 📈",
        "description": "Breakout above 20-day high with volume confirmation",
        "emoji": "🚀",
    },
    "rising3methods": {
        "label": "Rising Three Methods 🕯️",
        "description": "Classic bullish continuation candlestick pattern",
        "emoji": "📊",
    },
}


def _default_strategy_meta(strategy: str) -> dict:
    return {
        "label": strategy.upper(),
        "description": "Custom screening strategy",
        "emoji": "🔍",
    }


class DiscordNotifier:
    """
    Sends Crypto Screener results to Discord via Webhook.

    Args:
        webhook_url: Discord Webhook URL. If None, reads from
                     DISCORD_WEBHOOK_URL environment variable.
        username:    Display name of the bot in Discord.
        avatar_url:  Optional avatar image URL for the bot.
        timeout:     HTTP request timeout in seconds.
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        username: str = "Crypto Screener 🤖",
        avatar_url: Optional[str] = None,
        timeout: int = 10,
    ):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL", "")
        self.username = username
        self.avatar_url = avatar_url
        self.timeout = timeout

        if not self.webhook_url:
            logger.warning(
                "Discord webhook URL not set. "
                "Pass webhook_url= or set DISCORD_WEBHOOK_URL env variable."
            )

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def send_results(
        self,
        results: list[dict],
        strategy: str,
        timeframe: str,
        quote: str = "USDT",
    ) -> bool:
        """
        Send screening results to Discord.

        Splits into multiple messages if there are many results
        (Discord embed field limit = 25).

        Args:
            results:   List of result dicts from the screener.
            strategy:  Strategy name.
            timeframe: Timeframe string (e.g. "1D", "4H").
            quote:     Quote currency (default: USDT).

        Returns:
            True if all messages sent successfully, False otherwise.
        """
        if not self.webhook_url:
            logger.error("No webhook URL configured. Skipping Discord notification.")
            return False

        meta = STRATEGY_META.get(strategy, _default_strategy_meta(strategy))
        now_utc = datetime.now(timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M UTC")

        # ── Header message ──────────────────────────────────
        header_embed = self._build_header_embed(
            meta=meta,
            strategy=strategy,
            timeframe=timeframe,
            quote=quote,
            result_count=len(results),
            timestamp=timestamp,
            now_utc=now_utc,
        )
        success = self._post_embed(header_embed)

        if not results:
            return success

        # ── Result chunks (max 20 symbols per embed) ────────
        chunk_size = 20
        chunks = [results[i:i + chunk_size] for i in range(0, len(results), chunk_size)]

        for chunk_index, chunk in enumerate(chunks):
            result_embed = self._build_results_embed(
                chunk=chunk,
                chunk_index=chunk_index,
                total_chunks=len(chunks),
                meta=meta,
                timeframe=timeframe,
                now_utc=now_utc,
            )
            ok = self._post_embed(result_embed)
            success = success and ok

            # Small delay to avoid Discord rate limiting
            if chunk_index < len(chunks) - 1:
                time.sleep(0.5)

        return success

    def send_error(self, message: str, strategy: str = "", timeframe: str = "") -> bool:
        """
        Send an error/alert message to Discord.

        Args:
            message:  Error description.
            strategy: Strategy that produced the error (optional).
            timeframe: Timeframe (optional).

        Returns:
            True if sent successfully.
        """
        if not self.webhook_url:
            return False

        now_utc = datetime.now(timezone.utc)
        embed = {
            "title": "⚠️ Screener Error",
            "description": f"```{message}```",
            "color": Color.RED,
            "timestamp": now_utc.isoformat(),
            "footer": {"text": "Crypto Screener | Error Report"},
        }
        if strategy:
            embed["fields"] = [
                {"name": "Strategy", "value": strategy, "inline": True},
                {"name": "Timeframe", "value": timeframe or "—", "inline": True},
            ]
        return self._post_embed(embed)

    # ──────────────────────────────────────────
    # Embed builders (private)
    # ──────────────────────────────────────────

    def _build_header_embed(
        self,
        meta: dict,
        strategy: str,
        timeframe: str,
        quote: str,
        result_count: int,
        timestamp: str,
        now_utc: datetime,
    ) -> dict:
        color = Color.GREEN if result_count > 0 else Color.GREY

        description_lines = [
            f"> {meta['description']}",
            "",
            f"**📅 Scan Time:** `{timestamp}`",
            f"**⏱️ Timeframe:** `{timeframe}`",
            f"**💱 Quote Currency:** `{quote}`",
            f"**📌 Matches Found:** `{result_count}`",
        ]

        embed = {
            "title": f"{meta['emoji']} {meta['label']}",
            "description": "\n".join(description_lines),
            "color": color,
            "timestamp": now_utc.isoformat(),
            "footer": {
                "text": "Crypto Screener | OKX Spot  •  Do Your Own Research! ⚠️"
            },
        }

        if result_count == 0:
            embed["description"] += "\n\n*No symbols matched the criteria this scan.*"

        return embed

    def _build_results_embed(
        self,
        chunk: list[dict],
        chunk_index: int,
        total_chunks: int,
        meta: dict,
        timeframe: str,
        now_utc: datetime,
    ) -> dict:
        fields = []

        for r in chunk:
            symbol   = r.get("symbol", "?")
            signal   = r.get("signal", "—")
            close    = r.get("close", 0)
            volume   = r.get("volume", 0)

            # Format ticker-only label (e.g. "BTC" from "BTC/USDT")
            ticker = symbol.split("/")[0] if "/" in symbol else symbol

            # Build field value
            value_lines = [
                f"Signal: `{signal}`",
                f"Close:  `{close:.4f}`",
                f"Vol:    `{volume:,.2f}`",
            ]

            fields.append({
                "name": f"🪙 {ticker}",
                "value": "\n".join(value_lines),
                "inline": True,
            })

        title_suffix = (
            f" (Part {chunk_index + 1}/{total_chunks})"
            if total_chunks > 1
            else ""
        )

        embed = {
            "title": f"📋 Matched Symbols{title_suffix}",
            "color": Color.GREEN,
            "fields": fields,
            "timestamp": now_utc.isoformat(),
            "footer": {
                "text": f"{meta['label']} | {timeframe}  •  DYOR ⚠️"
            },
        }

        return embed

    # ──────────────────────────────────────────
    # HTTP transport (no external deps)
    # ──────────────────────────────────────────

    def _post_embed(self, embed: dict) -> bool:
        """
        POST a single embed dict to the Discord webhook.

        Returns:
            True on success (2xx), False otherwise.
        """
        payload = {
            "username": self.username,
            "embeds": [embed],
        }
        if self.avatar_url:
            payload["avatar_url"] = self.avatar_url

        data = json.dumps(payload).encode("utf-8")
        req = Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                if status in (200, 204):
                    logger.info("Discord notification sent (HTTP %s).", status)
                    return True
                else:
                    logger.warning("Unexpected HTTP status from Discord: %s", status)
                    return False

        except HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            logger.error("Discord HTTP error %s: %s", e.code, body)
            return False

        except URLError as e:
            logger.error("Discord URL error: %s", e.reason)
            return False

        except Exception as e:
            logger.error("Discord unexpected error: %s", e)
            return False

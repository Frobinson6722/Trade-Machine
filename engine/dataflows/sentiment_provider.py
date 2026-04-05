"""Crypto sentiment data provider."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from engine.dataflows.interface import SentimentProvider
from engine.dataflows.config import DATA_CONFIG

logger = logging.getLogger(__name__)


class CryptoSentimentProvider(SentimentProvider):
    """Fetches sentiment data from Alternative.me Fear & Greed and other sources."""

    def __init__(self):
        self.fng_url = DATA_CONFIG["fear_greed"]["base_url"]

    async def get_fear_greed_index(self) -> dict[str, Any]:
        """Fetch the crypto Fear & Greed Index."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.fng_url,
                    params={"limit": 7},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        return {"value": 50, "label": "Neutral", "error": True}
                    data = await resp.json()

            entries = data.get("data", [])
            if not entries:
                return {"value": 50, "label": "Neutral", "error": True}

            current = entries[0]
            history = [
                {
                    "value": int(e.get("value", 50)),
                    "label": e.get("value_classification", "Neutral"),
                    "timestamp": e.get("timestamp", ""),
                }
                for e in entries
            ]

            return {
                "value": int(current.get("value", 50)),
                "label": current.get("value_classification", "Neutral"),
                "history": history,
                "trend": self._calculate_trend(history),
            }
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed index: {e}")
            return {"value": 50, "label": "Neutral", "error": True}

    async def get_social_sentiment(self, pair: str) -> dict[str, Any]:
        """Fetch social media sentiment metrics.

        Uses free endpoints to gather sentiment signals.
        """
        # Aggregate from Fear & Greed as primary sentiment source
        fng = await self.get_fear_greed_index()

        return {
            "pair": pair,
            "fear_greed": fng,
            "overall_score": fng.get("value", 50),
            "interpretation": self._interpret_score(fng.get("value", 50)),
        }

    @staticmethod
    def _calculate_trend(history: list[dict]) -> str:
        """Determine if sentiment is improving, worsening, or stable."""
        if len(history) < 2:
            return "stable"
        recent = sum(h["value"] for h in history[:3]) / min(3, len(history))
        older = sum(h["value"] for h in history[3:]) / max(1, len(history) - 3)
        diff = recent - older
        if diff > 5:
            return "improving"
        elif diff < -5:
            return "worsening"
        return "stable"

    @staticmethod
    def _interpret_score(score: int) -> str:
        """Interpret a 0-100 sentiment score."""
        if score <= 20:
            return "Extreme Fear — potential contrarian buy signal"
        elif score <= 40:
            return "Fear — market is cautious"
        elif score <= 60:
            return "Neutral — no strong sentiment signal"
        elif score <= 80:
            return "Greed — market is optimistic, watch for overextension"
        else:
            return "Extreme Greed — potential contrarian sell signal"

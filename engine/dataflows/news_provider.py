"""Crypto news provider using CryptoPanic API."""

from __future__ import annotations

import logging
from typing import Any

import ssl

import aiohttp

from engine.dataflows.interface import NewsProvider

_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE
from engine.dataflows.config import DATA_CONFIG

logger = logging.getLogger(__name__)


class CryptoPanicNewsProvider(NewsProvider):
    """Fetches crypto news from CryptoPanic API."""

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or DATA_CONFIG["cryptopanic"]["api_key"]
        self.base_url = DATA_CONFIG["cryptopanic"]["base_url"]

    async def get_news(
        self, pair: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Fetch recent crypto news, optionally filtered by currency."""
        params: dict[str, Any] = {"auth_token": self.api_key, "public": "true"}

        if pair:
            # Convert "BTC-USD" to "BTC"
            currency = pair.split("-")[0] if "-" in pair else pair
            params["currencies"] = currency

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_ssl_context)) as session:
                async with session.get(
                    f"{self.base_url}/posts/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"CryptoPanic API returned {resp.status}")
                        return []
                    data = await resp.json()

            results = []
            for item in (data.get("results") or [])[:limit]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source": item.get("source", {}).get("title", ""),
                    "published_at": item.get("published_at", ""),
                    "kind": item.get("kind", ""),
                    "domain": item.get("domain", ""),
                    "votes": {
                        "positive": item.get("votes", {}).get("positive", 0),
                        "negative": item.get("votes", {}).get("negative", 0),
                        "important": item.get("votes", {}).get("important", 0),
                    },
                    "currencies": [
                        c.get("code", "") for c in item.get("currencies", [])
                    ],
                })
            return results

        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

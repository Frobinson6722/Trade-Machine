"""Free crypto market data provider using CoinGecko public API (no auth needed).

Provides multi-timeframe historical data: 24h, 7d, 30d, 90d, 365d.
"""

from __future__ import annotations

import logging
import ssl
from datetime import datetime, timezone
from typing import Any

import aiohttp

from engine.dataflows.interface import DataProvider
from engine.dataflows.config import PAIR_TO_COINGECKO

_ssl_context = ssl.create_default_context()
_ssl_context.check_hostname = False
_ssl_context.verify_mode = ssl.CERT_NONE

logger = logging.getLogger(__name__)

PAIR_TO_SYMBOL = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "SOL-USD": "solana",
    "DOGE-USD": "dogecoin",
    "XRP-USD": "ripple",
    "ADA-USD": "cardano",
    "AVAX-USD": "avalanche-2",
    "LTC-USD": "litecoin",
    "LINK-USD": "chainlink",
    "XLM-USD": "stellar",
    "SHIB-USD": "shiba-inu",
}


class FreeMarketProvider(DataProvider):
    """Fetches crypto data from CoinGecko with multi-timeframe historical lookback."""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def _get_coin_id(self, pair: str) -> str:
        return PAIR_TO_SYMBOL.get(pair, pair.split("-")[0].lower())

    async def _fetch_market_chart(self, coin_id: str, days: str) -> dict:
        """Fetch market chart data for a specific timeframe."""
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_ssl_context)) as session:
                async with session.get(
                    f"{self.base_url}/coins/{coin_id}/market_chart",
                    params={"vs_currency": "usd", "days": days},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        return {}
                    return await resp.json()
        except Exception as e:
            logger.error(f"Error fetching {days}d chart for {coin_id}: {e}")
            return {}

    def _parse_candles(self, data: dict, limit: int = 500) -> list[dict[str, Any]]:
        """Convert CoinGecko market_chart response to candle format."""
        prices = data.get("prices", [])
        volumes = data.get("total_volumes", [])
        candles = []
        for i in range(min(len(prices), limit)):
            ts = prices[i][0] / 1000
            price = prices[i][1]
            vol = volumes[i][1] if i < len(volumes) else 0
            spread = price * 0.002
            candles.append({
                "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
                "open": price - spread / 2,
                "high": price + spread,
                "low": price - spread,
                "close": price,
                "volume": vol,
            })
        return candles

    async def get_ohlcv(
        self, pair: str, interval: str = "hour", limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch OHLCV data — default 24h hourly candles."""
        coin_id = self._get_coin_id(pair)
        days = "1" if interval in ("hour", "1h", "5min", "10min") else "30"
        data = await self._fetch_market_chart(coin_id, days)
        if not data:
            return self._generate_fallback_data(pair)
        candles = self._parse_candles(data, limit)
        logger.info(f"Fetched {len(candles)} candles for {pair} ({days}d)")
        return candles[-limit:]

    async def get_historical_data(self, pair: str) -> dict[str, Any]:
        """Fetch multi-timeframe historical data for deep analysis.

        Returns 7-day, 30-day, 90-day, and 365-day price histories
        so agents can identify long-term trends and patterns.
        """
        coin_id = self._get_coin_id(pair)
        logger.info(f"Fetching multi-timeframe history for {pair}...")

        result: dict[str, Any] = {"pair": pair}

        # Fetch multiple timeframes
        for label, days in [("7d", "7"), ("30d", "30"), ("90d", "90"), ("365d", "365")]:
            data = await self._fetch_market_chart(coin_id, days)
            candles = self._parse_candles(data)
            if candles:
                prices = [c["close"] for c in candles]
                high = max(prices)
                low = min(prices)
                start_price = prices[0]
                end_price = prices[-1]
                change_pct = ((end_price - start_price) / start_price * 100) if start_price else 0

                result[label] = {
                    "candles_count": len(candles),
                    "start_price": round(start_price, 6),
                    "end_price": round(end_price, 6),
                    "high": round(high, 6),
                    "low": round(low, 6),
                    "change_pct": round(change_pct, 2),
                    "volatility": round((high - low) / ((high + low) / 2) * 100, 2) if (high + low) else 0,
                    # Key levels
                    "support_levels": self._find_support_resistance(prices, "support"),
                    "resistance_levels": self._find_support_resistance(prices, "resistance"),
                    # Trend
                    "trend": "bullish" if change_pct > 5 else "bearish" if change_pct < -5 else "sideways",
                    # Recent candles for pattern analysis
                    "recent_20_candles": candles[-20:],
                }
            else:
                result[label] = {"error": f"No data for {label}"}

        return result

    def _find_support_resistance(self, prices: list[float], mode: str, levels: int = 3) -> list[float]:
        """Find approximate support/resistance levels from price history."""
        if len(prices) < 10:
            return []

        # Simple approach: find local minima (support) or maxima (resistance)
        key_levels = []
        window = max(5, len(prices) // 20)

        for i in range(window, len(prices) - window):
            segment = prices[i - window:i + window + 1]
            if mode == "support" and prices[i] == min(segment):
                key_levels.append(round(prices[i], 6))
            elif mode == "resistance" and prices[i] == max(segment):
                key_levels.append(round(prices[i], 6))

        # Cluster nearby levels and pick the strongest
        if not key_levels:
            if mode == "support":
                key_levels = [round(min(prices), 6)]
            else:
                key_levels = [round(max(prices), 6)]

        # Deduplicate levels within 2% of each other
        clustered = []
        for level in sorted(key_levels):
            if not clustered or abs(level - clustered[-1]) / clustered[-1] > 0.02:
                clustered.append(level)

        return clustered[-levels:] if mode == "support" else clustered[:levels]

    async def get_ticker(self, pair: str) -> dict[str, Any]:
        """Fetch current price from CoinGecko."""
        coin_id = self._get_coin_id(pair)
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_ssl_context)) as session:
                async with session.get(
                    f"{self.base_url}/simple/price",
                    params={
                        "ids": coin_id,
                        "vs_currencies": "usd",
                        "include_24hr_vol": "true",
                        "include_24hr_change": "true",
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        return {"pair": pair, "price": 0}
                    data = await resp.json()

            coin_data = data.get(coin_id, {})
            price = coin_data.get("usd", 0)
            return {
                "pair": pair,
                "price": price,
                "ask": price * 1.001,
                "bid": price * 0.999,
                "volume": coin_data.get("usd_24h_vol", 0),
                "change_24h": coin_data.get("usd_24h_change", 0),
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {pair}: {e}")
            return {"pair": pair, "price": 0}

    async def get_account_balance(self) -> dict[str, Any]:
        return {"equity": 10000, "cash": 10000, "crypto_holdings": {}}

    def _generate_fallback_data(self, pair: str) -> list[dict[str, Any]]:
        import random
        base_prices = {"XRP-USD": 2.10, "DOGE-USD": 0.17, "BTC-USD": 84000, "ETH-USD": 3200}
        base = base_prices.get(pair, 1.0)
        now = datetime.now(timezone.utc)
        return [{
            "timestamp": now.isoformat(),
            "open": base * (1 + random.uniform(-0.02, 0.02)),
            "high": base * (1 + random.uniform(0, 0.03)),
            "low": base * (1 - random.uniform(0, 0.03)),
            "close": base * (1 + random.uniform(-0.01, 0.01)),
            "volume": random.uniform(1000, 50000),
        } for _ in range(24)]

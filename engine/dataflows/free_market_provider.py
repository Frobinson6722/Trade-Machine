"""Free crypto market data provider using CoinGecko public API (no auth needed)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import aiohttp

from engine.dataflows.interface import DataProvider
from engine.dataflows.config import PAIR_TO_COINGECKO

logger = logging.getLogger(__name__)

# Map pairs to simple symbols
PAIR_TO_SYMBOL = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "SOL-USD": "solana",
    "DOGE-USD": "dogecoin",
    "ADA-USD": "cardano",
    "AVAX-USD": "avalanche-2",
    "LTC-USD": "litecoin",
    "LINK-USD": "chainlink",
    "XLM-USD": "stellar",
    "SHIB-USD": "shiba-inu",
}


class FreeMarketProvider(DataProvider):
    """Fetches crypto data from free public APIs (CoinGecko). No API key needed."""

    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"

    def _get_coin_id(self, pair: str) -> str:
        return PAIR_TO_SYMBOL.get(pair, pair.split("-")[0].lower())

    async def get_ohlcv(
        self, pair: str, interval: str = "hour", limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch OHLCV data from CoinGecko."""
        coin_id = self._get_coin_id(pair)

        # CoinGecko market_chart gives us price/volume over time
        # days=1 gives hourly, days=7 gives ~4h, days=30 gives daily
        days = "1" if interval in ("hour", "1h", "5min", "10min") else "30"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/coins/{coin_id}/market_chart",
                    params={"vs_currency": "usd", "days": days},
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status != 200:
                        logger.warning(f"CoinGecko returned {resp.status} for {pair}")
                        return self._generate_fallback_data(pair)
                    data = await resp.json()

            prices = data.get("prices", [])
            volumes = data.get("total_volumes", [])

            candles = []
            for i in range(min(len(prices), limit)):
                ts = prices[i][0] / 1000  # Convert ms to seconds
                price = prices[i][1]
                vol = volumes[i][1] if i < len(volumes) else 0

                # Simulate OHLCV from price points (CoinGecko free doesn't give true OHLCV)
                spread = price * 0.002  # 0.2% spread simulation
                candles.append({
                    "timestamp": datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(),
                    "open": price - spread / 2,
                    "high": price + spread,
                    "low": price - spread,
                    "close": price,
                    "volume": vol,
                })

            logger.info(f"Fetched {len(candles)} candles for {pair} from CoinGecko")
            return candles[-limit:]

        except Exception as e:
            logger.error(f"Error fetching OHLCV for {pair}: {e}")
            return self._generate_fallback_data(pair)

    async def get_ticker(self, pair: str) -> dict[str, Any]:
        """Fetch current price from CoinGecko."""
        coin_id = self._get_coin_id(pair)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/simple/price",
                    params={
                        "ids": coin_id,
                        "vs_currencies": "usd",
                        "include_24hr_vol": "true",
                        "include_24hr_change": "true",
                        "include_last_updated_at": "true",
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
        """Paper trading doesn't need real account balance."""
        return {"equity": 10000, "cash": 10000, "crypto_holdings": {}}

    def _generate_fallback_data(self, pair: str) -> list[dict[str, Any]]:
        """Generate minimal fallback data if API fails."""
        logger.warning(f"Using fallback data for {pair}")
        base_prices = {"BTC-USD": 84000, "ETH-USD": 3200, "SOL-USD": 130, "DOGE-USD": 0.17}
        base = base_prices.get(pair, 100)
        now = datetime.now(timezone.utc)
        candles = []
        for i in range(24):
            import random
            noise = base * random.uniform(-0.01, 0.01)
            p = base + noise
            candles.append({
                "timestamp": now.isoformat(),
                "open": p * 0.999,
                "high": p * 1.005,
                "low": p * 0.995,
                "close": p,
                "volume": random.uniform(1000, 50000),
            })
        return candles

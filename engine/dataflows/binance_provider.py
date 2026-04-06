"""Real-time crypto data from Binance public API (no auth needed).

Provides 1-minute and 5-minute klines for accurate short-term trading.
Free tier: 1200 requests/minute — more than enough for 60-second cycles.
"""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)

# Map our pair format to Binance symbols
PAIR_TO_BINANCE = {
    "XRP-USD": "XRPUSDT",
    "DOGE-USD": "DOGEUSDT",
    "BTC-USD": "BTCUSDT",
    "ETH-USD": "ETHUSDT",
    "SOL-USD": "SOLUSDT",
    "ADA-USD": "ADAUSDT",
    "AVAX-USD": "AVAXUSDT",
    "LTC-USD": "LTCUSDT",
    "LINK-USD": "LINKUSDT",
    "XLM-USD": "XLMUSDT",
    "SHIB-USD": "SHIBUSDT",
}


class BinanceProvider:
    """Real-time crypto data from Binance — free, no API key needed.

    Uses REST API for klines (candlesticks) and ticker price.
    Rate limit: 1200 req/min (we use ~2 per cycle = ~120/hr).
    """

    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self._ticker_cache: dict[str, dict] = {}
        self._ticker_cache_ttl = 5  # Cache ticker for 5 seconds

    def _get_symbol(self, pair: str) -> str:
        return PAIR_TO_BINANCE.get(pair, pair.replace("-", ""))

    async def get_ohlcv(
        self, pair: str, interval: str = "1m", limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch real-time klines from Binance.

        Default: 100 x 1-minute candles = last ~1.5 hours of data.
        This gives RSI/MACD/Bollinger accurate, up-to-the-minute readings.
        """
        symbol = self._get_symbol(pair)

        # Map interval names
        binance_interval = {
            "1m": "1m", "5m": "5m", "15m": "15m",
            "1h": "1h", "hour": "1h", "4h": "4h",
            "1d": "1d", "day": "1d",
        }.get(interval, "1m")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/klines",
                    params={
                        "symbol": symbol,
                        "interval": binance_interval,
                        "limit": str(limit),
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.warning(f"Binance returned {resp.status}: {text[:200]}")
                        return []
                    data = await resp.json()

            candles = []
            for k in data:
                candles.append({
                    "timestamp": datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc).isoformat(),
                    "open": float(k[1]),
                    "high": float(k[2]),
                    "low": float(k[3]),
                    "close": float(k[4]),
                    "volume": float(k[5]),
                })

            logger.info(f"Binance: {len(candles)} x {binance_interval} candles for {pair}")
            return candles

        except asyncio.TimeoutError:
            logger.warning(f"Binance timeout for {pair} klines")
            return []
        except Exception as e:
            logger.error(f"Binance klines error for {pair}: {e}")
            return []

    async def get_ticker(self, pair: str) -> dict[str, Any]:
        """Fetch real-time price from Binance."""
        symbol = self._get_symbol(pair)

        # Quick cache to avoid hammering
        now = time.time()
        cached = self._ticker_cache.get(pair)
        if cached and now - cached["ts"] < self._ticker_cache_ttl:
            return cached["data"]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/ticker/24hr",
                    params={"symbol": symbol},
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status != 200:
                        return {"pair": pair, "price": 0}
                    data = await resp.json()

            price = float(data.get("lastPrice", 0))
            result = {
                "pair": pair,
                "price": price,
                "ask": float(data.get("askPrice", price)),
                "bid": float(data.get("bidPrice", price)),
                "volume": float(data.get("volume", 0)),
                "change_24h": float(data.get("priceChangePercent", 0)),
            }

            self._ticker_cache[pair] = {"data": result, "ts": now}
            return result

        except Exception as e:
            logger.error(f"Binance ticker error for {pair}: {e}")
            return {"pair": pair, "price": 0}

    async def get_historical_data(self, pair: str) -> dict[str, Any]:
        """Fetch multi-timeframe data for deeper analysis."""
        result: dict[str, Any] = {"pair": pair}

        for label, interval, limit in [
            ("1h", "1m", 60),     # Last hour, 1-min candles
            ("4h", "5m", 48),     # Last 4 hours, 5-min candles
            ("1d", "15m", 96),    # Last day, 15-min candles
            ("7d", "1h", 168),    # Last week, hourly candles
        ]:
            candles = await self.get_ohlcv(pair, interval=interval, limit=limit)
            if candles:
                prices = [c["close"] for c in candles]
                high = max(prices)
                low = min(prices)
                result[label] = {
                    "candles_count": len(candles),
                    "start_price": prices[0],
                    "end_price": prices[-1],
                    "high": high,
                    "low": low,
                    "change_pct": round(((prices[-1] - prices[0]) / prices[0]) * 100, 2) if prices[0] else 0,
                }
            await asyncio.sleep(0.1)  # Gentle rate limiting

        return result

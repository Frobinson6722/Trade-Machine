"""On-chain data provider using DeFiLlama and free APIs."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

from engine.dataflows.interface import OnchainProvider
from engine.dataflows.config import DATA_CONFIG, PAIR_TO_COINGECKO

logger = logging.getLogger(__name__)


class DefiLlamaOnchainProvider(OnchainProvider):
    """Fetches on-chain data from DeFiLlama (free, no auth)."""

    def __init__(self):
        self.base_url = DATA_CONFIG["defillama"]["base_url"]

    async def get_tvl(self, protocol: str | None = None) -> dict[str, Any]:
        """Fetch Total Value Locked data."""
        try:
            async with aiohttp.ClientSession() as session:
                if protocol:
                    url = f"{self.base_url}/protocol/{protocol}"
                else:
                    url = f"{self.base_url}/protocols"

                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        return {"tvl": 0, "error": True}
                    data = await resp.json()

            if protocol:
                return {
                    "protocol": protocol,
                    "tvl": data.get("currentChainTvls", {}),
                    "total_tvl": sum(
                        v for v in data.get("currentChainTvls", {}).values()
                        if isinstance(v, (int, float))
                    ),
                    "chains": data.get("chains", []),
                }
            else:
                # Return top protocols by TVL
                top = sorted(data, key=lambda x: x.get("tvl", 0), reverse=True)[:20]
                return {
                    "top_protocols": [
                        {
                            "name": p.get("name", ""),
                            "tvl": p.get("tvl", 0),
                            "change_1d": p.get("change_1d", 0),
                            "change_7d": p.get("change_7d", 0),
                            "chains": p.get("chains", []),
                        }
                        for p in top
                    ]
                }
        except Exception as e:
            logger.error(f"Error fetching TVL data: {e}")
            return {"tvl": 0, "error": True}

    async def get_token_metrics(self, symbol: str) -> dict[str, Any]:
        """Fetch token-level metrics using CoinGecko-compatible free APIs."""
        coingecko_id = PAIR_TO_COINGECKO.get(symbol, symbol.lower())

        try:
            async with aiohttp.ClientSession() as session:
                # Use CoinGecko free API for basic token data
                async with session.get(
                    f"https://api.coingecko.com/api/v3/coins/{coingecko_id}",
                    params={
                        "localization": "false",
                        "tickers": "false",
                        "community_data": "true",
                        "developer_data": "true",
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        return {"symbol": symbol, "error": True}
                    data = await resp.json()

            market = data.get("market_data", {})
            community = data.get("community_data", {})
            developer = data.get("developer_data", {})

            return {
                "symbol": symbol,
                "market_cap": market.get("market_cap", {}).get("usd", 0),
                "market_cap_rank": data.get("market_cap_rank", 0),
                "total_supply": market.get("total_supply", 0),
                "circulating_supply": market.get("circulating_supply", 0),
                "ath": market.get("ath", {}).get("usd", 0),
                "ath_change_pct": market.get("ath_change_percentage", {}).get("usd", 0),
                "price_change_24h_pct": market.get("price_change_percentage_24h", 0),
                "price_change_7d_pct": market.get("price_change_percentage_7d", 0),
                "price_change_30d_pct": market.get("price_change_percentage_30d", 0),
                "community": {
                    "reddit_subscribers": community.get("reddit_subscribers", 0),
                    "reddit_active": community.get("reddit_accounts_active_48h", 0),
                    "twitter_followers": community.get("twitter_followers", 0),
                },
                "developer": {
                    "forks": developer.get("forks", 0),
                    "stars": developer.get("stars", 0),
                    "commits_4w": developer.get("commit_count_4_weeks", 0),
                },
            }
        except Exception as e:
            logger.error(f"Error fetching token metrics for {symbol}: {e}")
            return {"symbol": symbol, "error": True}

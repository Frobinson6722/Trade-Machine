"""Configuration for data providers."""

import os

DATA_CONFIG = {
    "robinhood": {
        "username": os.getenv("ROBINHOOD_USERNAME", ""),
        "password": os.getenv("ROBINHOOD_PASSWORD", ""),
        "mfa_code": os.getenv("ROBINHOOD_MFA_CODE", ""),
    },
    "cryptopanic": {
        "api_key": os.getenv("CRYPTOPANIC_API_KEY", ""),
        "base_url": "https://cryptopanic.com/api/free/v1",
    },
    "fear_greed": {
        "base_url": "https://api.alternative.me/fng/",
    },
    "defillama": {
        "base_url": "https://api.llama.fi",
    },
    "cache_ttl_seconds": {
        "ohlcv": 60,
        "ticker": 15,
        "news": 300,
        "sentiment": 300,
        "onchain": 600,
    },
}

# Map common pair names to Robinhood symbols
PAIR_TO_ROBINHOOD = {
    "BTC-USD": "BTC",
    "ETH-USD": "ETH",
    "DOGE-USD": "DOGE",
    "SOL-USD": "SOL",
    "ADA-USD": "ADA",
    "AVAX-USD": "AVAX",
    "SHIB-USD": "SHIB",
    "LTC-USD": "LTC",
    "LINK-USD": "LINK",
    "XLM-USD": "XLM",
}

# Map pairs to CoinGecko IDs for on-chain data
PAIR_TO_COINGECKO = {
    "BTC-USD": "bitcoin",
    "ETH-USD": "ethereum",
    "DOGE-USD": "dogecoin",
    "SOL-USD": "solana",
    "ADA-USD": "cardano",
    "AVAX-USD": "avalanche-2",
    "SHIB-USD": "shiba-inu",
    "LTC-USD": "litecoin",
    "LINK-USD": "chainlink",
    "XLM-USD": "stellar",
}

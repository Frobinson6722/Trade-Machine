"""Abstract data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class DataProvider(ABC):
    """Protocol that all data providers must implement."""

    @abstractmethod
    async def get_ohlcv(
        self, pair: str, interval: str = "1h", limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch OHLCV candle data."""
        ...

    @abstractmethod
    async def get_ticker(self, pair: str) -> dict[str, Any]:
        """Fetch current ticker (price, volume, 24h change)."""
        ...

    @abstractmethod
    async def get_account_balance(self) -> dict[str, Any]:
        """Fetch account balances."""
        ...


class NewsProvider(ABC):
    """Protocol for news data providers."""

    @abstractmethod
    async def get_news(
        self, pair: str | None = None, limit: int = 20
    ) -> list[dict[str, Any]]:
        """Fetch recent crypto news."""
        ...


class SentimentProvider(ABC):
    """Protocol for sentiment data providers."""

    @abstractmethod
    async def get_fear_greed_index(self) -> dict[str, Any]:
        """Fetch the crypto Fear & Greed index."""
        ...

    @abstractmethod
    async def get_social_sentiment(self, pair: str) -> dict[str, Any]:
        """Fetch social media sentiment metrics."""
        ...


class OnchainProvider(ABC):
    """Protocol for on-chain data providers."""

    @abstractmethod
    async def get_tvl(self, protocol: str | None = None) -> dict[str, Any]:
        """Fetch Total Value Locked data."""
        ...

    @abstractmethod
    async def get_token_metrics(self, symbol: str) -> dict[str, Any]:
        """Fetch token-level on-chain metrics."""
        ...

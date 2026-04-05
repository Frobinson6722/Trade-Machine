"""Robinhood data provider for crypto market data and account info."""

from __future__ import annotations

import logging
from typing import Any

from engine.dataflows.interface import DataProvider
from engine.dataflows.config import PAIR_TO_ROBINHOOD

logger = logging.getLogger(__name__)


def _get_rh():
    """Lazy import robin_stocks to avoid import errors when not configured."""
    import robin_stocks.robinhood as rh
    return rh


class RobinhoodProvider(DataProvider):
    """Fetches crypto data and manages orders via Robinhood API."""

    def __init__(self, username: str, password: str, mfa_code: str = ""):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self._logged_in = False

    def _ensure_login(self) -> None:
        """Log in to Robinhood if not already authenticated."""
        if self._logged_in:
            return
        rh = _get_rh()
        try:
            rh.login(
                self.username,
                self.password,
                mfa_code=self.mfa_code if self.mfa_code else None,
                store_session=True,
            )
            self._logged_in = True
            logger.info("Successfully logged in to Robinhood")
        except Exception as e:
            logger.error(f"Robinhood login failed: {e}")
            raise

    def _get_symbol(self, pair: str) -> str:
        """Convert pair name to Robinhood symbol."""
        return PAIR_TO_ROBINHOOD.get(pair, pair.split("-")[0])

    async def get_ohlcv(
        self, pair: str, interval: str = "hour", limit: int = 100
    ) -> list[dict[str, Any]]:
        """Fetch historical crypto price data from Robinhood."""
        self._ensure_login()
        rh = _get_rh()
        symbol = self._get_symbol(pair)

        interval_map = {
            "5min": ("day", "5minute"),
            "10min": ("week", "10minute"),
            "hour": ("month", "hour"),
            "1h": ("month", "hour"),
            "day": ("year", "day"),
            "1d": ("year", "day"),
            "week": ("5year", "week"),
        }
        span, rh_interval = interval_map.get(interval, ("month", "hour"))

        try:
            historicals = rh.crypto.get_crypto_historicals(
                symbol, interval=rh_interval, span=span
            )
            candles = []
            for h in (historicals or [])[-limit:]:
                candles.append({
                    "timestamp": h.get("begins_at", ""),
                    "open": float(h.get("open_price", 0)),
                    "high": float(h.get("high_price", 0)),
                    "low": float(h.get("low_price", 0)),
                    "close": float(h.get("close_price", 0)),
                    "volume": float(h.get("volume", 0)),
                })
            return candles
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {pair}: {e}")
            return []

    async def get_ticker(self, pair: str) -> dict[str, Any]:
        """Fetch current crypto ticker from Robinhood."""
        self._ensure_login()
        rh = _get_rh()
        symbol = self._get_symbol(pair)

        try:
            quote = rh.crypto.get_crypto_quote(symbol)
            if not quote:
                return {}
            return {
                "pair": pair,
                "price": float(quote.get("mark_price", 0)),
                "ask": float(quote.get("ask_price", 0)),
                "bid": float(quote.get("bid_price", 0)),
                "high": float(quote.get("high_price", 0)),
                "low": float(quote.get("low_price", 0)),
                "volume": float(quote.get("volume", 0)),
            }
        except Exception as e:
            logger.error(f"Error fetching ticker for {pair}: {e}")
            return {}

    async def get_account_balance(self) -> dict[str, Any]:
        """Fetch Robinhood crypto account balances."""
        self._ensure_login()
        rh = _get_rh()
        try:
            profile = rh.profiles.load_portfolio_profile()
            crypto_positions = rh.crypto.get_crypto_positions()

            holdings = {}
            for pos in crypto_positions or []:
                currency = pos.get("currency", {})
                code = currency.get("code", "")
                quantity = float(pos.get("quantity", 0))
                if quantity > 0:
                    holdings[code] = {
                        "quantity": quantity,
                        "cost_basis": float(pos.get("cost_bases", [{}])[0].get("direct_cost_basis", 0)),
                    }

            return {
                "equity": float(profile.get("equity", 0)) if profile else 0,
                "cash": float(profile.get("withdrawable_amount", 0)) if profile else 0,
                "crypto_holdings": holdings,
            }
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            return {"equity": 0, "cash": 0, "crypto_holdings": {}}

    def logout(self) -> None:
        """Log out from Robinhood."""
        if self._logged_in:
            rh = _get_rh()
            rh.logout()
            self._logged_in = False

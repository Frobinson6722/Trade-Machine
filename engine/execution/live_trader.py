"""Live trader — executes real trades via Robinhood Crypto API."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import robin_stocks.robinhood as rh

from engine.dataflows.config import PAIR_TO_ROBINHOOD

logger = logging.getLogger(__name__)


class LiveTrader:
    """Executes real crypto trades via Robinhood."""

    def __init__(self, username: str, password: str, mfa_code: str = ""):
        self.username = username
        self.password = password
        self.mfa_code = mfa_code
        self._logged_in = False
        self.trade_history: list[dict[str, Any]] = []

    def _ensure_login(self) -> None:
        if self._logged_in:
            return
        rh.login(
            self.username,
            self.password,
            mfa_code=self.mfa_code if self.mfa_code else None,
            store_session=True,
        )
        self._logged_in = True
        logger.info("Logged in to Robinhood for live trading")

    def _get_symbol(self, pair: str) -> str:
        return PAIR_TO_ROBINHOOD.get(pair, pair.split("-")[0])

    async def place_order(
        self,
        pair: str,
        side: str,
        size_usd: float,
        current_price: float,
        stop_loss: float | None = None,
        take_profit: float | None = None,
    ) -> dict[str, Any]:
        """Place a real crypto order on Robinhood."""
        self._ensure_login()
        symbol = self._get_symbol(pair)
        order_id = str(uuid.uuid4())[:8]

        try:
            if side == "BUY":
                result = rh.orders.order_buy_crypto_by_price(
                    symbol, size_usd, timeInForce="gtc"
                )
            elif side == "SELL":
                # Calculate quantity from USD amount at current price
                quantity = size_usd / current_price if current_price > 0 else 0
                result = rh.orders.order_sell_crypto_by_quantity(
                    symbol, quantity, timeInForce="gtc"
                )
            else:
                return {"success": False, "reason": f"Unknown side: {side}"}

            if not result or "id" not in result:
                error_msg = result.get("detail", "Unknown error") if result else "No response"
                logger.error(f"Order failed for {pair}: {error_msg}")
                return {"success": False, "reason": error_msg}

            trade_record = {
                "order_id": result.get("id", order_id),
                "pair": pair,
                "side": side,
                "price": current_price,
                "size_usd": size_usd,
                "status": result.get("state", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "robinhood_response": result,
            }
            self.trade_history.append(trade_record)

            logger.info(f"[LIVE] {side} {pair}: ${size_usd:.2f} @ ~${current_price:,.2f}")
            return {"success": True, "trade": trade_record}

        except Exception as e:
            logger.error(f"Live order failed for {pair}: {e}")
            return {"success": False, "reason": str(e)}

    async def get_open_orders(self) -> list[dict[str, Any]]:
        """Fetch open crypto orders from Robinhood."""
        self._ensure_login()
        try:
            orders = rh.orders.get_all_open_crypto_orders()
            return orders or []
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order."""
        self._ensure_login()
        try:
            result = rh.orders.cancel_crypto_order(order_id)
            return bool(result)
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

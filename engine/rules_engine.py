"""Rules-based trading engine — no LLM needed for trade decisions.

Pure math: RSI, MACD, Bollinger Bands, Volume.
Trades execute instantly based on signals. No API costs for decisions.
Claude is only used for nightly learning review (~$0.05/day).
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from engine.config import DEFAULT_CONFIG
from engine.dataflows.free_market_provider import FreeMarketProvider
from engine.dataflows.technical_indicators import compute_indicators
from engine.execution.paper_trader import PaperTrader
from engine.execution.position_manager import PositionManager
from engine.execution.stage_manager import StageManager
from engine.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)


class RulesEngine:
    """Pure rules-based trading — no LLM calls for decisions."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        on_trade: Callable | None = None,
        on_agent_log: Callable | None = None,
        on_status: Callable | None = None,
    ):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.on_trade = on_trade
        self.on_agent_log = on_agent_log
        self.on_status = on_status

        self.running = False
        self.paused = False
        self._task: asyncio.Task | None = None
        self._last_prices: dict[str, float] = {}

        self.memory = MemoryManager()
        self.stage_manager = StageManager(self.config)
        self.paper_trader = PaperTrader(self.config["stages"]["paper"]["initial_balance"])
        self.position_manager = PositionManager()
        self.data_provider = FreeMarketProvider()

        # Executor reference for compatibility
        self.executor = type('obj', (object,), {'mode': 'paper', 'paper_trader': self.paper_trader})()

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.paused = False
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Rules engine started")
        if self.on_status:
            await self.on_status("running")

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Rules engine stopped")
        if self.on_status:
            await self.on_status("stopped")

    async def pause(self) -> None:
        self.paused = True
        if self.on_status:
            await self.on_status("paused")

    async def resume(self) -> None:
        self.paused = False
        if self.on_status:
            await self.on_status("running")

    async def _run_loop(self) -> None:
        interval = self.config["cycle_interval_seconds"]

        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(5)
                    continue

                for pair in self.config["trading_pairs"]:
                    if not self.running or self.paused:
                        break
                    await self._run_cycle(pair)

                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Loop error: {e}", exc_info=True)
                await asyncio.sleep(30)

    async def _run_cycle(self, pair: str) -> None:
        cycle_id = str(uuid.uuid4())[:8]

        try:
            if self.on_agent_log:
                await self.on_agent_log("system", f"Cycle {cycle_id}: Fetching {pair} data...")

            # 1. Get price data
            candles = await self.data_provider.get_ohlcv(pair)
            if not candles or len(candles) < 20:
                if self.on_agent_log:
                    await self.on_agent_log("system", f"Cycle {cycle_id}: Not enough data for {pair}")
                return

            ticker = await self.data_provider.get_ticker(pair)
            current_price = ticker.get("price", 0)
            if not current_price:
                return

            # 2. Check open positions first
            await self._check_position(pair, current_price, cycle_id)

            # 3. Compute indicators
            indicators = compute_indicators(candles)
            if "error" in indicators:
                if self.on_agent_log:
                    await self.on_agent_log("system", f"Cycle {cycle_id}: Indicator error: {indicators['error']}")
                return

            # 4. Generate signal from rules
            signal = self._evaluate_rules(pair, current_price, indicators)

            if self.on_agent_log:
                await self.on_agent_log("system",
                    f"Cycle {cycle_id}: {pair} @ ${current_price:.6f} | "
                    f"RSI: {signal['rsi']:.0f} | MACD: {signal['macd_signal']} | "
                    f"Signal: {signal['action']} ({signal['reason']})")

            # 5. Execute if signal says BUY and we don't have a position
            if signal["action"] == "BUY" and pair not in self.paper_trader.positions:
                size_pct = 8.0
                size_usd = self.paper_trader.cash_balance * (size_pct / 100)

                if size_usd > 1:
                    stop_loss = current_price * 0.995    # 0.5% stop
                    take_profit = current_price * 1.003  # 0.3% take profit

                    result = await self.paper_trader.place_order(
                        pair=pair, side="BUY", size_usd=size_usd,
                        current_price=current_price,
                        stop_loss=stop_loss, take_profit=take_profit,
                    )

                    if result.get("success"):
                        self.position_manager.update_position(pair, {
                            "cycle_id": cycle_id,
                            "entry_price": current_price,
                            "quantity": size_usd / current_price,
                            "side": "long",
                            "stop_loss": stop_loss,
                            "take_profit": take_profit,
                        })

                        self.memory.record_trade_entry(
                            pair=pair, action="BUY", entry_price=current_price,
                            size_usd=size_usd, stop_loss=stop_loss,
                            take_profit=take_profit,
                            agent_reasoning={"signal": signal["reason"], "rsi": signal["rsi"]},
                            stage=self.stage_manager.get_current_stage(),
                            cycle_id=cycle_id,
                        )

                        if self.on_agent_log:
                            await self.on_agent_log("system",
                                f"TRADE: BUY {pair} @ ${current_price:.6f} | "
                                f"Size: ${size_usd:.2f} | Stop: ${stop_loss:.6f} | Target: ${take_profit:.6f}")

                        if self.on_trade:
                            await self.on_trade({
                                "cycle_id": cycle_id, "pair": pair, "action": "BUY",
                                "price": current_price, "size_usd": size_usd,
                                "stop_loss": stop_loss, "take_profit": take_profit,
                                "stage": self.stage_manager.get_current_stage(),
                                "mode": "paper", "reason": signal["reason"],
                            })

        except Exception as e:
            logger.error(f"Cycle {cycle_id} failed: {e}", exc_info=True)
            if self.on_agent_log:
                await self.on_agent_log("system", f"Cycle {cycle_id} error: {str(e)[:100]}")

    def _evaluate_rules(self, pair: str, price: float, indicators: dict) -> dict[str, Any]:
        """Pure rules-based signal generation. No LLM. Just math."""

        rsi = indicators.get("rsi", {})
        rsi_value = rsi.get("value", 50) if isinstance(rsi, dict) else 50

        macd = indicators.get("macd", {})
        macd_crossover = macd.get("crossover", "neutral") if isinstance(macd, dict) else "neutral"

        bollinger = indicators.get("bollinger", {})
        bb_position = bollinger.get("position", "") if isinstance(bollinger, dict) else ""

        volume = indicators.get("volume", {})
        vol_ratio = volume.get("ratio", 1) if isinstance(volume, dict) else 1

        # ── RULE SET ──
        action = "HOLD"
        reason = "No clear signal"
        score = 0

        # RSI oversold = buy signal
        if rsi_value < 35:
            score += 2
            reason = f"RSI oversold at {rsi_value:.0f}"
        elif rsi_value < 45:
            score += 1

        # MACD bullish crossover = buy signal
        if macd_crossover in ("bullish_crossover", "bullish"):
            score += 2
            reason = f"MACD {macd_crossover}"

        # Price near lower Bollinger Band = buy signal
        if "below_lower" in bb_position:
            score += 2
            reason = f"Price below lower Bollinger Band"

        # High volume confirms the signal
        if vol_ratio > 1.3:
            score += 1

        # RSI overbought = don't buy
        if rsi_value > 70:
            score -= 3
            reason = f"RSI overbought at {rsi_value:.0f} — avoid"

        # Bearish MACD = don't buy
        if macd_crossover in ("bearish_crossover", "bearish"):
            score -= 1

        # Decision
        if score >= 3:
            action = "BUY"
            if not reason or reason == "No clear signal":
                reason = f"Multiple bullish signals (score: {score})"
        elif score >= 2:
            action = "BUY"
            reason = f"Moderate buy signal (score: {score}): {reason}"

        return {
            "action": action,
            "reason": reason,
            "score": score,
            "rsi": rsi_value,
            "macd_signal": macd_crossover,
            "bb_position": bb_position,
            "vol_ratio": vol_ratio,
        }

    async def _check_position(self, pair: str, current_price: float, cycle_id: str) -> None:
        """Check if open position should be closed."""
        pos = self.position_manager.get_position(pair)
        if not pos:
            return

        entry = pos.get("entry_price", 0)
        if not entry:
            return

        pnl_pct = ((current_price / entry) - 1) * 100
        sl = pos.get("stop_loss")
        tp = pos.get("take_profit")

        should_close = False
        trigger = "manual"

        # Take profit first (we want to close winners fast)
        if tp and current_price >= tp:
            should_close = True
            trigger = "take_profit"
        elif pnl_pct >= 0.3:
            should_close = True
            trigger = "auto_take_profit"
        elif sl and current_price <= sl:
            should_close = True
            trigger = "stop_loss"
        elif pnl_pct <= -0.5:
            should_close = True
            trigger = "auto_stop_loss"

        if should_close:
            old_cycle = pos.get("cycle_id", cycle_id)
            result = await self.paper_trader.place_order(
                pair=pair, side="SELL", size_usd=0, current_price=current_price
            )
            if result.get("success"):
                trade = result.get("trade", {})
                pnl = trade.get("pnl", 0)
                pnl_pct_actual = trade.get("pnl_pct", pnl_pct)

                self.position_manager.close_position(pair)
                self.memory.record_trade_exit(
                    cycle_id=old_cycle, exit_price=current_price,
                    pnl=pnl, pnl_pct=pnl_pct_actual, trigger=trigger,
                )
                self.stage_manager.record_trade(pnl)

                emoji = "WIN" if pnl > 0 else "LOSS"
                if self.on_agent_log:
                    await self.on_agent_log("system",
                        f"CLOSED {pair} ({trigger}): {emoji} ${pnl:+.2f} ({pnl_pct_actual:+.1f}%)")

                if self.on_trade:
                    await self.on_trade({
                        "cycle_id": old_cycle, "pair": pair, "action": "SELL",
                        "price": current_price, "pnl": pnl, "pnl_pct": pnl_pct_actual,
                        "trigger": trigger, "stage": self.stage_manager.get_current_stage(),
                    })
            return

        # Log unrealized P&L
        if self.on_agent_log:
            qty = pos.get("quantity", 0)
            unrealized = (current_price - entry) * qty
            await self.on_agent_log("system",
                f"Open {pair}: ${entry:.6f} → ${current_price:.6f} | P&L: ${unrealized:+.2f} ({pnl_pct:+.1f}%)")

    def get_status(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "paused": self.paused,
            "mode": "paper",
            "stage": self.stage_manager.get_status(),
            "positions": self.position_manager.get_all_positions(),
            "stats": self.memory.get_trading_stats(),
        }

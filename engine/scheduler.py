"""Main 24/7 scheduler — runs analysis cycles on configurable intervals."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from engine.config import DEFAULT_CONFIG
from engine.graph.trading_graph import TradeMachineGraph
from engine.execution.executor import OrderExecutor
from engine.execution.paper_trader import PaperTrader
from engine.execution.live_trader import LiveTrader
from engine.execution.position_manager import PositionManager
from engine.execution.stage_manager import StageManager
from engine.memory.memory_manager import MemoryManager
from engine.dataflows.free_market_provider import FreeMarketProvider
from engine.dataflows.news_provider import CryptoPanicNewsProvider
from engine.dataflows.sentiment_provider import CryptoSentimentProvider
from engine.dataflows.onchain_provider import DefiLlamaOnchainProvider
from engine.dataflows.technical_indicators import compute_indicators

logger = logging.getLogger(__name__)


class TradingScheduler:
    """Main scheduler that runs the trading engine 24/7."""

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

        # State
        self.running = False
        self.paused = False
        self._task: asyncio.Task | None = None

        # Memory
        self.memory = MemoryManager()

        # Stage management
        self.stage_manager = StageManager(self.config)

        # Execution
        paper = PaperTrader(self.config["stages"]["paper"]["initial_balance"])
        live = None
        if self.config.get("robinhood_username"):
            live = LiveTrader(
                self.config["robinhood_username"],
                self.config["robinhood_password"],
                self.config.get("robinhood_mfa_code", ""),
            )
        self.executor = OrderExecutor(paper, live)
        self.position_manager = PositionManager()

        # Data providers — use free APIs for paper trading
        self.data_provider = FreeMarketProvider()
        self.news_provider = CryptoPanicNewsProvider(self.config.get("cryptopanic_api_key", ""))
        self.sentiment_provider = CryptoSentimentProvider()
        self.onchain_provider = DefiLlamaOnchainProvider()

        # Trading graph
        self.graph = TradeMachineGraph(
            config=self.config,
            on_trade=on_trade,
            on_agent_log=on_agent_log,
        )

    async def start(self) -> None:
        """Start the trading scheduler."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        self.paused = False
        self._task = asyncio.create_task(self._run_loop())
        logger.info("Trading scheduler started")
        await self._emit_status("running")

    async def stop(self) -> None:
        """Stop the trading scheduler."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Trading scheduler stopped")
        await self._emit_status("stopped")

    async def pause(self) -> None:
        """Pause the scheduler (keeps running but skips cycles)."""
        self.paused = True
        logger.info("Trading scheduler paused")
        await self._emit_status("paused")

    async def resume(self) -> None:
        """Resume from paused state."""
        self.paused = False
        logger.info("Trading scheduler resumed")
        await self._emit_status("running")

    async def _run_loop(self) -> None:
        """Main loop — runs trading cycles at configured intervals."""
        interval = self.config["cycle_interval_seconds"]
        nightly_hour = self.config.get("nightly_learn_hour_utc", 0)
        last_nightly = None

        while self.running:
            try:
                if self.paused:
                    await asyncio.sleep(5)
                    continue

                # Check for nightly learning
                now = datetime.now(timezone.utc)
                if now.hour == nightly_hour and last_nightly != now.date():
                    last_nightly = now.date()
                    await self._run_nightly_learning()

                # Run a cycle for each trading pair
                for pair in self.config["trading_pairs"]:
                    if not self.running or self.paused:
                        break
                    await self._run_single_cycle(pair)

                # Wait for next cycle
                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(30)  # Brief cooldown on error

    async def _run_single_cycle(self, pair: str) -> None:
        """Run a complete trading cycle for one pair."""
        cycle_id = str(uuid.uuid4())[:8]
        logger.info(f"Starting cycle {cycle_id} for {pair}")

        try:
            # 1. Fetch data
            market_data_raw = await self.data_provider.get_ohlcv(pair)
            indicators = compute_indicators(market_data_raw)
            market_data = {"candles": market_data_raw[-20:], "indicators": indicators}

            news_data = await self.news_provider.get_news(pair)
            sentiment_data = await self.sentiment_provider.get_social_sentiment(pair)
            onchain_data = await self.onchain_provider.get_token_metrics(pair)

            # 2. Get memory context
            memory_context = self.memory.get_context_for_pair(pair)

            # 3. Run the analysis graph
            result = await self.graph.run_cycle(
                pair=pair,
                market_data=market_data,
                news_data=news_data,
                sentiment_data=sentiment_data,
                onchain_data=onchain_data,
                memory_context=memory_context,
            )

            # 4. Execute if approved
            decision = result.get("final_decision")
            if decision and hasattr(decision, "approved") and decision.approved:
                ticker = await self.data_provider.get_ticker(pair)
                current_price = ticker.get("price", 0)

                if current_price > 0:
                    trade_size = self.stage_manager.get_trade_size_usd()
                    balance = self.executor.paper_trader.cash_balance

                    exec_result = await self.executor.execute(
                        decision, current_price, balance, trade_size
                    )

                    if exec_result.get("executed"):
                        # Record in journal
                        agent_reasoning = {
                            "market": result.get("market_report", "")[:200],
                            "news": result.get("news_report", "")[:200],
                            "sentiment": result.get("sentiment_report", "")[:200],
                            "fundamentals": result.get("fundamentals_report", "")[:200],
                            "research_verdict": result.get("research_verdict", "")[:200],
                        }
                        self.memory.record_trade_entry(
                            pair=pair,
                            action=decision.action,
                            entry_price=current_price,
                            size_usd=trade_size or (balance * decision.size_pct / 100),
                            stop_loss=decision.stop_loss,
                            take_profit=decision.take_profit,
                            agent_reasoning=agent_reasoning,
                            stage=self.stage_manager.get_current_stage(),
                            cycle_id=cycle_id,
                        )

                        # Position tracking
                        self.position_manager.update_position(pair, {
                            "cycle_id": cycle_id,
                            "entry_price": current_price,
                            "quantity": (trade_size or (balance * decision.size_pct / 100)) / current_price,
                            "side": "long" if decision.action == "BUY" else "short",
                            "stop_loss": decision.stop_loss,
                            "take_profit": decision.take_profit,
                        })

                        if self.on_trade:
                            await self.on_trade({
                                "cycle_id": cycle_id,
                                "pair": pair,
                                "action": decision.action,
                                "price": current_price,
                                "stage": self.stage_manager.get_current_stage(),
                            })

            # 5. Check existing position stops
            await self._check_stops(pair)

            logger.info(f"Cycle {cycle_id} for {pair} completed")

        except Exception as e:
            logger.error(f"Cycle {cycle_id} for {pair} failed: {e}", exc_info=True)

    async def _check_stops(self, pair: str) -> None:
        """Check if any stops have been triggered for a pair."""
        ticker = await self.data_provider.get_ticker(pair)
        current_price = ticker.get("price", 0)
        if not current_price:
            return

        triggered = self.position_manager.check_stops({pair: current_price})
        for t in triggered:
            result = await self.executor.check_stops(t["pair"], t["price"])
            if result and result.get("success"):
                trade = result.get("trade", {})
                pnl = trade.get("pnl", 0)
                pnl_pct = trade.get("pnl_pct", 0)

                pos = self.position_manager.close_position(pair)
                cycle_id = pos.get("cycle_id", "") if pos else ""

                self.memory.record_trade_exit(
                    cycle_id=cycle_id,
                    exit_price=t["price"],
                    pnl=pnl,
                    pnl_pct=pnl_pct,
                    trigger=t["trigger"],
                )
                self.stage_manager.record_trade(pnl)

                # Trigger reflection for closed trades
                await self._reflect_on_trade(cycle_id, pair, pnl, pnl_pct)

    async def _reflect_on_trade(
        self, cycle_id: str, pair: str, pnl: float, pnl_pct: float
    ) -> None:
        """Run reflection on a closed trade."""
        try:
            journal_entry = None
            for e in reversed(self.memory.journal.entries):
                if e.get("cycle_id") == cycle_id:
                    journal_entry = e
                    break

            if not journal_entry:
                return

            reflection_result = await self.graph.reflect(
                pair=pair,
                action=journal_entry.get("action", ""),
                entry_price=journal_entry.get("entry_price", 0),
                exit_price=journal_entry.get("exit_price", 0),
                pnl=pnl,
                pnl_pct=pnl_pct,
                duration="N/A",
                agent_reasoning=str(journal_entry.get("agent_reasoning", "")),
                market_conditions="Current market conditions",
            )

            # Store reflection
            outcome = "win" if pnl > 0 else "loss"
            tags = [pair, outcome, self.stage_manager.get_current_stage()]
            self.memory.store_reflection(
                pair, reflection_result["reflection"], tags, outcome
            )

            # Store hypotheses for losses
            if pnl < 0 and reflection_result.get("hypotheses"):
                self.memory.store_hypotheses(
                    pair, cycle_id, reflection_result["hypotheses"]
                )

            self.memory.journal.add_reflection(cycle_id, reflection_result["reflection"])

        except Exception as e:
            logger.error(f"Reflection failed for {cycle_id}: {e}")

    async def _run_nightly_learning(self) -> None:
        """Run the nightly learning review."""
        logger.info("Running nightly learning review...")
        try:
            result = await self.memory.nightly_learner.run_nightly_review(
                self.graph.deep_llm
            )
            logger.info(f"Nightly review result: {result.get('status')}")
        except Exception as e:
            logger.error(f"Nightly learning failed: {e}", exc_info=True)

    async def _emit_status(self, status: str) -> None:
        if self.on_status:
            try:
                await self.on_status(status)
            except Exception:
                pass

    def get_status(self) -> dict[str, Any]:
        """Get current scheduler status for the dashboard."""
        return {
            "running": self.running,
            "paused": self.paused,
            "mode": self.executor.mode,
            "stage": self.stage_manager.get_status(),
            "positions": self.position_manager.get_all_positions(),
            "stats": self.memory.get_trading_stats(),
        }

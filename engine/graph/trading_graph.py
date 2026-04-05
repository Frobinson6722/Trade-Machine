"""TradeMachineGraph — top-level orchestrator for the trading pipeline."""

from __future__ import annotations

import logging
from typing import Any, Callable

from engine.config import DEFAULT_CONFIG
from engine.llm_clients.factory import create_llm_client
from engine.graph.setup import build_trading_graph
from engine.graph.propagation import create_initial_state, invoke_graph
from engine.graph.reflection import reflect_on_trade, generate_hypotheses
from engine.agents.utils.agent_states import FinalDecision

logger = logging.getLogger(__name__)


class TradeMachineGraph:
    """Top-level class that assembles and runs the full trading pipeline."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        on_trade: Callable | None = None,
        on_agent_log: Callable | None = None,
        debug: bool = False,
    ):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.on_trade = on_trade
        self.on_agent_log = on_agent_log
        self.debug = debug

        # Create LLM clients
        self.llm = create_llm_client(
            self.config["llm_provider"],
            self.config.get("quick_think_model"),
        )
        self.deep_llm = create_llm_client(
            self.config["llm_provider"],
            self.config.get("deep_think_model"),
        )

        # Build the graph
        self.graph = build_trading_graph(self.llm, self.deep_llm, self.config)

    async def run_cycle(
        self,
        pair: str,
        market_data: dict[str, Any],
        news_data: list[dict],
        sentiment_data: dict[str, Any],
        onchain_data: dict[str, Any],
        memory_context: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run a single trading analysis cycle for a pair.

        Returns the final state including the decision.
        """
        initial_state = create_initial_state(
            pair=pair,
            market_data=market_data,
            news_data=news_data,
            sentiment_data=sentiment_data,
            onchain_data=onchain_data,
            memory_context=memory_context,
            config=self.config,
        )

        result = await invoke_graph(self.graph, initial_state, self.config)

        # Notify callbacks
        if self.on_agent_log:
            await self._emit_agent_logs(result)

        return result

    async def reflect(
        self,
        pair: str,
        action: str,
        entry_price: float,
        exit_price: float,
        pnl: float,
        pnl_pct: float,
        duration: str,
        agent_reasoning: str,
        market_conditions: str,
    ) -> dict[str, str]:
        """Run post-trade reflection and hypothesis generation for losing trades."""
        reflection = await reflect_on_trade(
            self.deep_llm, pair, action, entry_price, exit_price,
            pnl, pnl_pct, duration, agent_reasoning, market_conditions,
        )

        hypotheses = ""
        if pnl < 0:
            hypotheses = await generate_hypotheses(
                self.deep_llm, pair, action, entry_price, exit_price,
                pnl, pnl_pct, agent_reasoning,
            )

        return {"reflection": reflection, "hypotheses": hypotheses}

    async def _emit_agent_logs(self, state: dict[str, Any]) -> None:
        """Emit agent log callbacks from the pipeline state."""
        if not self.on_agent_log:
            return

        logs = [
            ("market_analyst", state.get("market_report", "")),
            ("news_analyst", state.get("news_report", "")),
            ("sentiment_analyst", state.get("sentiment_report", "")),
            ("fundamentals_analyst", state.get("fundamentals_report", "")),
            ("bull_researcher", state.get("bull_thesis", "")),
            ("bear_researcher", state.get("bear_thesis", "")),
            ("research_manager", state.get("research_verdict", "")),
        ]

        proposal = state.get("trade_proposal")
        if proposal:
            proposal_str = proposal.model_dump_json() if hasattr(proposal, "model_dump_json") else str(proposal)
            logs.append(("trader", proposal_str))

        risk = state.get("risk_debate", {})
        if risk.get("aggressive_view"):
            logs.append(("aggressive_debator", risk["aggressive_view"]))
        if risk.get("conservative_view"):
            logs.append(("conservative_debator", risk["conservative_view"]))
        if risk.get("neutral_view"):
            logs.append(("neutral_debator", risk["neutral_view"]))

        decision = state.get("final_decision")
        if decision:
            decision_str = decision.model_dump_json() if hasattr(decision, "model_dump_json") else str(decision)
            logs.append(("portfolio_manager", decision_str))

        for agent_name, content in logs:
            if content:
                try:
                    await self.on_agent_log(agent_name, content)
                except Exception as e:
                    logger.error(f"Error in agent log callback: {e}")

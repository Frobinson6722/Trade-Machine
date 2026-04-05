"""Nightly learner — reviews the day's trades and updates strategy rules."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.prompts import NIGHTLY_LEARNER_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, parse_json_from_response
from engine.llm_clients.base_client import BaseLLMClient
from engine.memory.trade_journal import TradeJournal
from engine.memory.hypothesis_engine import HypothesisEngine
from engine.memory.strategy_tracker import StrategyTracker

logger = logging.getLogger(__name__)


class NightlyLearner:
    """Runs nightly review of trades and updates strategy parameters."""

    def __init__(
        self,
        journal: TradeJournal,
        hypothesis_engine: HypothesisEngine,
        strategy_tracker: StrategyTracker,
    ):
        self.journal = journal
        self.hypothesis_engine = hypothesis_engine
        self.strategy_tracker = strategy_tracker

    async def run_nightly_review(self, llm: BaseLLMClient) -> dict[str, Any]:
        """Execute the nightly learning cycle.

        1. Review today's trades
        2. Test pending hypotheses
        3. Aggregate lessons
        4. Recommend and apply strategy updates
        """
        logger.info("Starting nightly learning review...")

        # 1. Get today's trades
        todays_trades = self.journal.get_todays_trades()
        if not todays_trades:
            logger.info("No trades today, skipping nightly review")
            return {"status": "skipped", "reason": "no trades today"}

        # 2. Test pending hypotheses against all trade history
        all_trades = self.journal.entries
        validated_hypotheses = []
        for hyp in self.hypothesis_engine.get_pending():
            result = await self.hypothesis_engine.test_hypothesis(
                llm, hyp["id"], all_trades
            )
            if result.get("status") == "validated":
                validated_hypotheses.append(result)

        # 3. Prepare nightly review prompt
        stats = self.journal.get_stats()
        current_strategy = self.strategy_tracker.get_current_parameters()

        trades_summary = ""
        for t in todays_trades:
            trades_summary += (
                f"  {t['pair']} {t['action']}: "
                f"${t.get('entry_price', 0):,.2f} → ${t.get('exit_price', 'open'):} "
                f"(P&L: {t.get('pnl_pct', 'N/A')}%)\n"
            )

        hypotheses_summary = ""
        for h in validated_hypotheses:
            hypotheses_summary += f"  - {h['hypothesis']}\n    Rule change: {h.get('rule_change', 'N/A')}\n"

        prompt = NIGHTLY_LEARNER_PROMPT.format(
            todays_trades=trades_summary,
            current_strategy=str(current_strategy),
            validated_hypotheses=hypotheses_summary or "None",
            win_rate=f"{stats.get('win_rate', 0) * 100:.1f}",
            target_win_rate="55",
            avg_pnl=f"${stats.get('avg_pnl', 0):,.2f}",
        )

        # 4. Get strategy recommendations
        response = await invoke_agent(
            llm, prompt,
            """Produce your strategy adjustments as JSON:
{
    "adjustments": [
        {"parameter": "param_name", "old_value": ..., "new_value": ..., "reason": "..."},
    ],
    "summary": "One paragraph summary of today's learning"
}""",
            temperature=0.3,
        )

        # 5. Apply adjustments
        parsed = parse_json_from_response(response)
        adjustments_applied = []

        if parsed and "adjustments" in parsed:
            for adj in parsed["adjustments"]:
                param = adj.get("parameter", "")
                new_val = adj.get("new_value")
                reason = adj.get("reason", "")

                if param and new_val is not None:
                    self.strategy_tracker.record_update(
                        description=reason,
                        parameter_changes={param: new_val},
                        performance_before=stats,
                    )
                    adjustments_applied.append(adj)

        result = {
            "status": "completed",
            "trades_reviewed": len(todays_trades),
            "hypotheses_tested": len(self.hypothesis_engine.get_pending()) + len(validated_hypotheses),
            "hypotheses_validated": len(validated_hypotheses),
            "adjustments_applied": adjustments_applied,
            "summary": parsed.get("summary", response[:500]) if parsed else response[:500],
        }

        logger.info(
            f"Nightly review complete: {len(adjustments_applied)} adjustments applied"
        )
        return result

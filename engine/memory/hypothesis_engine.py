"""Hypothesis engine — reverse-engineers losses and tests assumptions against history."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from engine.agents.utils.agent_utils import invoke_agent
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


class HypothesisEngine:
    """Forms hypotheses about losing trades and validates them against history."""

    def __init__(self):
        self.hypotheses: list[dict[str, Any]] = []

    def store_hypothesis(
        self,
        pair: str,
        trade_id: str,
        hypothesis_text: str,
        status: str = "pending",
    ) -> dict[str, Any]:
        """Store a new hypothesis for later testing."""
        entry = {
            "id": len(self.hypotheses),
            "pair": pair,
            "trade_id": trade_id,
            "hypothesis": hypothesis_text,
            "status": status,  # pending, validated, rejected
            "test_results": None,
            "rule_change": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tested_at": None,
        }
        self.hypotheses.append(entry)
        logger.info(f"Hypothesis stored for {pair}: {hypothesis_text[:80]}...")
        return entry

    async def test_hypothesis(
        self,
        llm: BaseLLMClient,
        hypothesis_id: int,
        historical_trades: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Test a hypothesis against historical trade data."""
        if hypothesis_id >= len(self.hypotheses):
            return {"error": "Hypothesis not found"}

        hyp = self.hypotheses[hypothesis_id]

        prompt = f"""You are testing a trading hypothesis against historical data.

HYPOTHESIS: {hyp['hypothesis']}

HISTORICAL TRADES ({len(historical_trades)} trades):
"""
        for i, trade in enumerate(historical_trades[-20:]):
            prompt += f"""
Trade {i+1}: {trade.get('pair', 'N/A')} {trade.get('action', 'N/A')}
  Entry: ${trade.get('entry_price', 0):,.2f} → Exit: ${trade.get('exit_price', 0):,.2f}
  P&L: {trade.get('pnl_pct', 0):+.2f}%
  Agent reasoning: {str(trade.get('agent_reasoning', ''))[:200]}
"""

        prompt += """
Analyze whether the hypothesis holds true across these historical trades.
Respond with:
1. VERDICT: VALIDATED or REJECTED
2. EVIDENCE: Specific trades that support or contradict the hypothesis
3. CONFIDENCE: How confident are you (0-100%)
4. RULE_CHANGE: If validated, what specific trading rule should change?
"""

        result = await invoke_agent(llm, prompt, "Test this hypothesis now.", temperature=0.3)

        hyp["status"] = "validated" if "VALIDATED" in result.upper() else "rejected"
        hyp["test_results"] = result
        hyp["tested_at"] = datetime.now(timezone.utc).isoformat()

        if hyp["status"] == "validated":
            # Extract rule change suggestion
            hyp["rule_change"] = result

        logger.info(f"Hypothesis {hypothesis_id} tested: {hyp['status']}")
        return hyp

    def get_pending(self) -> list[dict[str, Any]]:
        return [h for h in self.hypotheses if h["status"] == "pending"]

    def get_validated(self) -> list[dict[str, Any]]:
        return [h for h in self.hypotheses if h["status"] == "validated"]

    def get_all(self) -> list[dict[str, Any]]:
        return list(self.hypotheses)

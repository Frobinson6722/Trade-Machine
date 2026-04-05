"""State propagation — creates initial state and invokes the trading graph."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def create_initial_state(
    pair: str,
    market_data: dict[str, Any],
    news_data: list[dict],
    sentiment_data: dict[str, Any],
    onchain_data: dict[str, Any],
    memory_context: list[str] | None = None,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create the initial state for a trading cycle."""
    cfg = config or {}
    return {
        "messages": [],
        "pair": pair,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market_data": market_data,
        "news_data": news_data,
        "sentiment_data": sentiment_data,
        "onchain_data": onchain_data,
        "market_report": "",
        "news_report": "",
        "sentiment_report": "",
        "fundamentals_report": "",
        "bull_thesis": "",
        "bear_thesis": "",
        "invest_debate": {
            "round_number": 0,
            "max_rounds": cfg.get("max_debate_rounds", 2),
            "bull_arguments": [],
            "bear_arguments": [],
            "verdict": "",
        },
        "research_verdict": "",
        "trade_proposal": None,
        "risk_debate": {
            "round_number": 0,
            "max_rounds": cfg.get("max_risk_discuss_rounds", 2),
            "aggressive_view": "",
            "conservative_view": "",
            "neutral_view": "",
            "consensus": "",
        },
        "final_decision": None,
        "similar_past_trades": memory_context or [],
        "active_reflections": [],
    }


async def invoke_graph(graph, initial_state: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
    """Invoke the compiled LangGraph with the initial state."""
    cfg = config or {}
    recursion_limit = cfg.get("max_recur_limit", 50)

    logger.info(f"Starting trading cycle for {initial_state['pair']}")
    try:
        result = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": recursion_limit},
        )
        logger.info(f"Trading cycle completed for {initial_state['pair']}")
        return result
    except Exception as e:
        logger.error(f"Trading cycle failed for {initial_state['pair']}: {e}")
        raise

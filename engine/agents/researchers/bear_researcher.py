"""Bear Researcher agent — builds the case for caution or short positions."""

from __future__ import annotations

import logging

from engine.agents.utils.prompts import BEAR_RESEARCHER_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_bear_researcher(
    llm: BaseLLMClient,
    pair: str,
    market_report: str,
    news_report: str,
    sentiment_report: str,
    fundamentals_report: str,
    bull_counterpoints: str = "",
    memory_context: list[str] | None = None,
) -> str:
    """Run the bear researcher to build a bearish/cautious thesis."""
    prompt = BEAR_RESEARCHER_PROMPT.format(
        pair=pair,
        market_report=market_report,
        news_report=news_report,
        sentiment_report=sentiment_report,
        fundamentals_report=fundamentals_report,
        bull_counterpoints=f"\nBull counterarguments to address:\n{bull_counterpoints}" if bull_counterpoints else "",
        memory_context=format_memory_context(memory_context or []),
    )

    report = await invoke_agent(llm, prompt, "Build your bearish thesis now.", temperature=0.5)
    logger.info(f"Bear researcher completed thesis for {pair}")
    return report

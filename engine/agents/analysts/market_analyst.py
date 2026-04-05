"""Market Analyst agent — technical analysis of crypto price data."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.prompts import MARKET_ANALYST_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context, format_data_for_prompt
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_market_analyst(
    llm: BaseLLMClient,
    pair: str,
    market_data: dict[str, Any],
    indicators: dict[str, Any],
    memory_context: list[str] | None = None,
) -> str:
    """Run the market analyst agent on technical data.

    Args:
        llm: LLM client for generating analysis
        pair: Trading pair (e.g. "BTC-USD")
        market_data: OHLCV candle data
        indicators: Computed technical indicators
        memory_context: Relevant past reflections

    Returns:
        Analyst report as a string
    """
    prompt = MARKET_ANALYST_PROMPT.format(
        pair=pair,
        memory_context=format_memory_context(memory_context or []),
    )

    user_content = f"""Analyze {pair} using the following data:

## OHLCV Data (recent candles)
{format_data_for_prompt(market_data)}

## Technical Indicators
{format_data_for_prompt(indicators)}

Provide your structured technical analysis."""

    report = await invoke_agent(llm, prompt, user_content, temperature=0.3)
    logger.info(f"Market analyst completed analysis for {pair}")
    return report

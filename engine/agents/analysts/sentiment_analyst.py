"""Sentiment Analyst agent — social sentiment and market psychology."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.prompts import SENTIMENT_ANALYST_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context, format_data_for_prompt
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_sentiment_analyst(
    llm: BaseLLMClient,
    pair: str,
    sentiment_data: dict[str, Any],
    memory_context: list[str] | None = None,
) -> str:
    """Run the sentiment analyst agent on social/market sentiment data."""
    prompt = SENTIMENT_ANALYST_PROMPT.format(
        pair=pair,
        memory_context=format_memory_context(memory_context or []),
    )

    user_content = f"""Analyze sentiment data for {pair}:

## Sentiment Metrics
{format_data_for_prompt(sentiment_data)}

Provide your structured sentiment analysis."""

    report = await invoke_agent(llm, prompt, user_content, temperature=0.3)
    logger.info(f"Sentiment analyst completed analysis for {pair}")
    return report

"""News Analyst agent — crypto news monitoring and impact assessment."""

from __future__ import annotations

import logging
from typing import Any

from engine.agents.utils.prompts import NEWS_ANALYST_PROMPT
from engine.agents.utils.agent_utils import invoke_agent, format_memory_context, format_data_for_prompt
from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


async def run_news_analyst(
    llm: BaseLLMClient,
    pair: str,
    news_data: list[dict[str, Any]],
    memory_context: list[str] | None = None,
) -> str:
    """Run the news analyst agent on recent crypto news."""
    prompt = NEWS_ANALYST_PROMPT.format(
        pair=pair,
        memory_context=format_memory_context(memory_context or []),
    )

    user_content = f"""Analyze recent news for {pair}:

## Recent News Items
{format_data_for_prompt({"articles": news_data})}

Provide your structured news analysis."""

    report = await invoke_agent(llm, prompt, user_content, temperature=0.3)
    logger.info(f"News analyst completed analysis for {pair}")
    return report

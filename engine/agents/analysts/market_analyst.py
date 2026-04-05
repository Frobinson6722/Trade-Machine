"""Market Analyst agent — technical analysis with patterns and historical data."""

from __future__ import annotations

import json
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
    """Run the market analyst with patterns, indicators, and multi-timeframe history."""
    prompt = MARKET_ANALYST_PROMPT.format(
        pair=pair,
        memory_context=format_memory_context(memory_context or []),
    )

    # Build rich data context
    patterns = market_data.get("patterns", [])
    historical = market_data.get("historical", {})

    patterns_text = "No patterns detected."
    if patterns:
        parts = []
        for p in patterns:
            parts.append(
                f"**{p['name']}** ({p['type']})\n"
                f"  Signal: {p['signal']} | Confidence: {p['confidence']*100:.0f}%\n"
                f"  Psychology: {p['psychology']}\n"
                f"  Expected move: {p.get('expected_move_pct', 'N/A')}%"
            )
        patterns_text = "\n\n".join(parts)

    historical_text = "No historical data available."
    if historical:
        parts = []
        for tf in ["7d", "30d", "90d", "365d"]:
            h = historical.get(tf, {})
            if not h or h.get("error"):
                continue
            parts.append(
                f"**{tf} Lookback**: {h.get('trend', 'N/A')} trend | "
                f"Change: {h.get('change_pct', 0):+.1f}% | "
                f"Volatility: {h.get('volatility', 0):.1f}% | "
                f"Range: ${h.get('low', 0):.6f} - ${h.get('high', 0):.6f} | "
                f"Support: {h.get('support_levels', [])} | "
                f"Resistance: {h.get('resistance_levels', [])}"
            )
        if parts:
            historical_text = "\n".join(parts)

    user_content = f"""Analyze {pair} using the following data:

## Current Technical Indicators
{format_data_for_prompt(indicators)}

## Detected Chart Patterns (with crowd psychology)
{patterns_text}

## Multi-Timeframe Historical Analysis
{historical_text}

## Recent OHLCV Candles
{format_data_for_prompt({"candles": market_data.get("candles", [])[-10:]})}

Provide your structured technical analysis."""

    report = await invoke_agent(llm, prompt, user_content, temperature=0.3)
    logger.info(f"Market analyst completed analysis for {pair}")
    return report

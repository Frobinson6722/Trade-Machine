"""Shared utilities for agent construction and response parsing."""

from __future__ import annotations

import json
import logging
from typing import Any

from engine.llm_clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)


def build_messages(
    system_prompt: str,
    user_content: str,
    history: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Build a message list for LLM invocation."""
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_content})
    return messages


async def invoke_agent(
    llm: BaseLLMClient,
    system_prompt: str,
    user_content: str,
    history: list[dict[str, str]] | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    """Invoke an LLM agent and return the text response."""
    messages = build_messages(system_prompt, user_content, history)
    response = await llm.invoke(
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response["content"]


def format_memory_context(reflections: list[str]) -> str:
    """Format past reflections into a memory context block for prompts."""
    if not reflections:
        return ""
    entries = "\n".join(f"- {r}" for r in reflections[-5:])
    return f"\nRelevant lessons from past trades:\n{entries}\n"


def parse_json_from_response(text: str) -> dict[str, Any] | None:
    """Extract JSON from an LLM response that may contain markdown fences."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code blocks
    for marker in ("```json", "```"):
        if marker in text:
            start = text.index(marker) + len(marker)
            end = text.index("```", start)
            try:
                return json.loads(text[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                continue

    logger.warning("Could not parse JSON from LLM response")
    return None


def format_data_for_prompt(data: dict[str, Any], max_length: int = 3000) -> str:
    """Format a data dictionary into a readable string for prompts, truncating if needed."""
    text = json.dumps(data, indent=2, default=str)
    if len(text) > max_length:
        text = text[:max_length] + "\n... (truncated)"
    return text

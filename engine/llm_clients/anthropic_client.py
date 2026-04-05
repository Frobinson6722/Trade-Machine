"""Anthropic Claude LLM client with usage tracking."""

import os
from datetime import datetime, timezone
from typing import Any

from anthropic import AsyncAnthropic

from engine.llm_clients.base_client import BaseLLMClient

# Claude pricing per million tokens (as of 2026)
PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
}
DEFAULT_PRICING = {"input": 3.00, "output": 15.00}


class UsageTracker:
    """Tracks all API calls, tokens, and costs."""

    def __init__(self):
        self.calls: list[dict[str, Any]] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def record(self, model: str, input_tokens: int, output_tokens: int, agent_name: str = ""):
        pricing = PRICING.get(model, DEFAULT_PRICING)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        cost = input_cost + output_cost

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost

        self.calls.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "agent_name": agent_name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(cost, 6),
        })

    def get_summary(self) -> dict[str, Any]:
        # Group by hour for chart data
        hourly: dict[str, float] = {}
        by_agent: dict[str, dict] = {}
        by_model: dict[str, dict] = {}

        for call in self.calls:
            # Hourly
            hour = call["timestamp"][:13]  # "2026-04-05T14"
            hourly[hour] = hourly.get(hour, 0) + call["cost"]

            # By agent
            agent = call.get("agent_name", "unknown")
            if agent not in by_agent:
                by_agent[agent] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0}
            by_agent[agent]["calls"] += 1
            by_agent[agent]["input_tokens"] += call["input_tokens"]
            by_agent[agent]["output_tokens"] += call["output_tokens"]
            by_agent[agent]["cost"] += call["cost"]

            # By model
            model = call["model"]
            if model not in by_model:
                by_model[model] = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost": 0}
            by_model[model]["calls"] += 1
            by_model[model]["input_tokens"] += call["input_tokens"]
            by_model[model]["output_tokens"] += call["output_tokens"]
            by_model[model]["cost"] += call["cost"]

        # Estimate daily cost
        total_calls = len(self.calls)
        if total_calls > 1:
            first = datetime.fromisoformat(self.calls[0]["timestamp"])
            last = datetime.fromisoformat(self.calls[-1]["timestamp"])
            hours_elapsed = max((last - first).total_seconds() / 3600, 0.01)
            cost_per_hour = self.total_cost / hours_elapsed
            estimated_daily = cost_per_hour * 24
        else:
            estimated_daily = self.total_cost * 24

        return {
            "total_calls": total_calls,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost": round(self.total_cost, 4),
            "estimated_daily_cost": round(estimated_daily, 2),
            "cost_per_cycle": round(self.total_cost / max(total_calls / 12, 1), 4),  # ~12 calls per cycle
            "by_agent": {k: {**v, "cost": round(v["cost"], 4)} for k, v in by_agent.items()},
            "by_model": {k: {**v, "cost": round(v["cost"], 4)} for k, v in by_model.items()},
            "hourly_costs": [{"hour": h, "cost": round(c, 4)} for h, c in sorted(hourly.items())],
            "recent_calls": self.calls[-20:],
        }


# Global usage tracker
usage_tracker = UsageTracker()


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models with cost tracking."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", **kwargs: Any):
        super().__init__(model, **kwargs)
        self.client = AsyncAnthropic(
            api_key=kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY"),
        )
        self._current_agent = ""

    def set_agent_name(self, name: str):
        """Set which agent is about to make a call (for cost attribution)."""
        self._current_agent = name

    async def invoke(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        system_msg = ""
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                conversation.append(msg)

        kwargs_api: dict[str, Any] = {
            "model": self.model,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs_api["system"] = system_msg
        if tools:
            kwargs_api["tools"] = [
                {
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "input_schema": t["function"]["parameters"],
                }
                for t in tools
            ]

        response = await self.client.messages.create(**kwargs_api)

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        # Track usage and cost
        usage_tracker.record(self.model, input_tokens, output_tokens, self._current_agent)
        self._current_agent = ""

        content = ""
        tool_calls = None
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                if tool_calls is None:
                    tool_calls = []
                import json
                tool_calls.append({
                    "id": block.id,
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input),
                    },
                })

        return {
            "content": content,
            "tool_calls": tool_calls,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        }

    async def invoke_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        system_msg = ""
        conversation = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                conversation.append(msg)

        kwargs_api: dict[str, Any] = {
            "model": self.model,
            "messages": conversation,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_msg:
            kwargs_api["system"] = system_msg

        async with self.client.messages.stream(**kwargs_api) as stream:
            async for text in stream.text_stream:
                yield text

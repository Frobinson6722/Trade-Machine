"""OpenAI LLM client implementation."""

import os
from typing import Any

from openai import AsyncOpenAI

from engine.llm_clients.base_client import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    """Client for OpenAI GPT models."""

    def __init__(self, model: str = "gpt-4o", **kwargs: Any):
        super().__init__(model, **kwargs)
        self.client = AsyncOpenAI(
            api_key=kwargs.get("api_key") or os.getenv("OPENAI_API_KEY"),
            base_url=kwargs.get("base_url"),
        )

    async def invoke(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        tool_calls = None
        if choice.message.tool_calls:
            tool_calls = [
                {
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in choice.message.tool_calls
            ]

        return {
            "content": choice.message.content or "",
            "tool_calls": tool_calls,
            "usage": {
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
            },
        }

    async def invoke_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

"""Google Gemini LLM client implementation."""

import os
from typing import Any

from engine.llm_clients.base_client import BaseLLMClient


class GoogleClient(BaseLLMClient):
    """Client for Google Gemini models."""

    def __init__(self, model: str = "gemini-2.0-flash", **kwargs: Any):
        super().__init__(model, **kwargs)
        self.api_key = kwargs.get("api_key") or os.getenv("GOOGLE_API_KEY")

    async def invoke(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: list[dict] | None = None,
    ) -> dict[str, Any]:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)

        # Convert messages to Gemini format
        gemini_messages = []
        system_instruction = None
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        if system_instruction:
            model = genai.GenerativeModel(
                self.model, system_instruction=system_instruction
            )

        response = await model.generate_content_async(
            gemini_messages,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
        )

        return {
            "content": response.text or "",
            "tool_calls": None,
            "usage": {
                "input_tokens": getattr(response.usage_metadata, "prompt_token_count", 0),
                "output_tokens": getattr(response.usage_metadata, "candidates_token_count", 0),
            },
        }

    async def invoke_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ):
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)

        system_instruction = None
        gemini_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_messages.append({"role": "model", "parts": [msg["content"]]})

        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_instruction,
        )

        response = await model.generate_content_async(
            gemini_messages,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            ),
            stream=True,
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text

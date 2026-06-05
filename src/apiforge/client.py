"""OpenAI-compatible HTTP client for APIForge.

Works with any provider that speaks the OpenAI ``/chat/completions`` protocol
(OpenAI, OpenRouter, Ollama, llama.cpp, Xiaomi MiMo Token Plan, ...). The auth
header style (bearer vs api-key) comes from the config's provider preset.
"""

from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Any
import httpx
from .config import APIForgeConfig


@dataclass
class CompletionResponse:
    content: str = ""
    reasoning_content: str = ""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = ""
    latency_ms: float = 0.0


class LLMClient:
    def __init__(self, config: APIForgeConfig | None = None) -> None:
        self.config = config or APIForgeConfig.from_env()
        self._http: httpx.AsyncClient | None = None
        self._request_count: int = 0
        self._total_tokens: int = 0

    @property
    def base_url(self) -> str:
        return self.config.mimo_base_url.rstrip("/")

    @property
    def headers(self) -> dict[str, str]:
        return self.config.headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=httpx.Timeout(120.0))
        return self._http

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> CompletionResponse:
        client = await self._get_client()
        payload = {
            "model": model or self.config.mimo_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        start = time.monotonic()
        resp = await client.post(
            f"{self.base_url}/chat/completions", headers=self.headers, json=payload
        )
        resp.raise_for_status()
        data = resp.json()
        elapsed = (time.monotonic() - start) * 1000
        self._request_count += 1
        usage = data.get("usage", {})
        tokens = usage.get("total_tokens", 0)
        self._total_tokens += tokens
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        return CompletionResponse(
            content=msg.get("content", ""),
            reasoning_content=msg.get("reasoning_content", ""),
            model=data.get("model", ""),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=tokens,
            finish_reason=choice.get("finish_reason", ""),
            latency_ms=round(elapsed, 2),
        )

    async def close(self) -> None:
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    @property
    def stats(self) -> dict[str, Any]:
        return {
            "request_count": self._request_count,
            "total_tokens": self._total_tokens,
        }


# Backward-compatible alias. New code should use LLMClient.
MiMoClient = LLMClient

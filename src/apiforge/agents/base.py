"""Base agent for APIForge."""
from __future__ import annotations
import time
from abc import ABC, abstractmethod
from typing import Any
from ..client import CompletionResponse, MiMoClient
from ..config import APIForgeConfig
from ..token_tracker import TokenTracker


class BaseAgent(ABC):
    name: str = "base"

    def __init__(self, client: MiMoClient | None = None, config: APIForgeConfig | None = None,
                 tracker: TokenTracker | None = None) -> None:
        self.config = config or APIForgeConfig.from_env()
        self.client = client or MiMoClient(self.config)
        self.tracker = tracker or TokenTracker()

    def _build_system_prompt(self) -> str:
        return f"You are {self.name}, a specialized agent in the APIForge API scaffolding pipeline."

    async def _call_mimo(self, user_prompt: str, *, system_prompt: str | None = None, **kwargs: Any) -> CompletionResponse:
        messages = [{"role": "system", "content": system_prompt or self._build_system_prompt()},
                    {"role": "user", "content": user_prompt}]
        start = time.monotonic()
        response = await self.client.chat_completion(messages, **kwargs)
        elapsed = (time.monotonic() - start) * 1000
        self.tracker.record(agent_name=self.name, prompt_tokens=response.prompt_tokens,
                            completion_tokens=response.completion_tokens, latency_ms=elapsed)
        return response

    @abstractmethod
    async def run(self, **kwargs: Any) -> Any: ...

    def __repr__(self) -> str: return f"<{self.__class__.__name__} agent={self.name!r}>"

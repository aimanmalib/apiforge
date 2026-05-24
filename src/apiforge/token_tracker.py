"""Token usage tracking for APIForge."""
from __future__ import annotations
import json, time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentUsage:
    agent_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    timestamp: float = field(default_factory=time.time)


class TokenTracker:
    DAILY_ESTIMATES: dict[str, float] = {
        "parser": 0.30, "schema": 0.50, "router": 0.45,
        "model": 0.35, "auth": 0.20, "test_gen": 0.40,
        "doc_gen": 0.25, "validator": 0.15,
    }

    def __init__(self) -> None:
        self._records: list[AgentUsage] = []
        self._session_start: float = time.time()

    def record(self, agent_name: str, prompt_tokens: int, completion_tokens: int, latency_ms: float = 0.0) -> AgentUsage:
        usage = AgentUsage(agent_name=agent_name, prompt_tokens=prompt_tokens,
                           completion_tokens=completion_tokens, total_tokens=prompt_tokens + completion_tokens,
                           latency_ms=latency_ms)
        self._records.append(usage)
        return usage

    def by_agent(self) -> dict[str, dict[str, Any]]:
        agg: dict[str, dict[str, Any]] = defaultdict(lambda: {"calls": 0, "prompt": 0, "completion": 0, "total": 0})
        for r in self._records:
            agg[r.agent_name]["calls"] += 1
            agg[r.agent_name]["prompt"] += r.prompt_tokens
            agg[r.agent_name]["completion"] += r.completion_tokens
            agg[r.agent_name]["total"] += r.total_tokens
        return dict(agg)

    def total_tokens(self) -> int: return sum(r.total_tokens for r in self._records)
    def total_calls(self) -> int: return len(self._records)

    def summary(self) -> dict[str, Any]:
        return {"total_calls": self.total_calls(), "total_tokens": self.total_tokens(),
                "by_agent": self.by_agent(), "daily_estimates_millions": self.DAILY_ESTIMATES,
                "daily_total_estimated_millions": sum(self.DAILY_ESTIMATES.values())}

    def export_json(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.summary(), indent=2))
        return p

    def reset(self) -> None:
        self._records.clear()
        self._session_start = time.time()

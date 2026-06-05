"""Configuration for APIForge.

APIForge speaks the OpenAI-compatible ``/chat/completions`` protocol, so it
works with any provider exposing that API: OpenAI, OpenRouter, Ollama, local
llama.cpp servers, Xiaomi MiMo Token Plan, and more. Select a provider via
``provider=`` (or the ``APIFORGE_PROVIDER`` env var) or point ``mimo_base_url``
at any compatible endpoint.

The historical ``mimo_*`` fields remain the canonical config attributes for
backward compatibility; they simply hold whichever provider's key/url/model is
active.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

# Provider presets: base_url, auth header style, default model, and the env
# vars used to populate the key / base_url when they aren't set explicitly.
# auth_style is "bearer" (Authorization: Bearer) or "api-key" (api-key header).
PROVIDER_PRESETS: dict[str, dict[str, str]] = {
    "mimo": {
        "base_url": "https://token-plan-sgp.xiaomimimo.com/v1",
        "auth_style": "api-key",
        "model": "mimo-v2.5-pro",
        "env_key": "MIMO_API_KEY",
        "env_base": "MIMO_BASE_URL",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "auth_style": "bearer",
        "model": "gpt-4o-mini",
        "env_key": "OPENAI_API_KEY",
        "env_base": "OPENAI_BASE_URL",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "auth_style": "bearer",
        "model": "openai/gpt-4o-mini",
        "env_key": "OPENROUTER_API_KEY",
        "env_base": "OPENROUTER_BASE_URL",
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "auth_style": "bearer",
        "model": "llama3.1",
        "env_key": "OLLAMA_API_KEY",
        "env_base": "OLLAMA_BASE_URL",
    },
}

DEFAULT_PROVIDER = "mimo"


@dataclass
class APIForgeConfig:
    provider: str = field(default_factory=lambda: os.getenv("APIFORGE_PROVIDER", DEFAULT_PROVIDER))
    mimo_api_key: str = field(default_factory=lambda: os.getenv("MIMO_API_KEY", ""))
    mimo_base_url: str = field(default_factory=lambda: os.getenv("MIMO_BASE_URL", ""))
    mimo_model: str = field(default_factory=lambda: os.getenv("MIMO_MODEL", ""))
    auth_style: str = ""  # "bearer" | "api-key" — resolved from provider if blank
    output_dir: str = field(default_factory=lambda: os.getenv("APIFORGE_OUTPUT_DIR", "./output"))
    framework: str = field(default_factory=lambda: os.getenv("APIFORGE_FRAMEWORK", "fastapi"))

    def __post_init__(self) -> None:
        preset = PROVIDER_PRESETS.get(self.provider, PROVIDER_PRESETS[DEFAULT_PROVIDER])
        # Only fall back to a provider env key if the canonical key is empty.
        if not self.mimo_api_key:
            self.mimo_api_key = os.getenv(preset["env_key"], "")
        if not self.mimo_base_url:
            self.mimo_base_url = os.getenv(preset["env_base"], preset["base_url"])
        if not self.mimo_model:
            self.mimo_model = preset["model"]
        if not self.auth_style:
            self.auth_style = preset["auth_style"]

    # Generic, provider-neutral aliases for new code.
    @property
    def api_key(self) -> str:
        return self.mimo_api_key

    @property
    def base_url(self) -> str:
        return self.mimo_base_url

    @property
    def model(self) -> str:
        return self.mimo_model

    @property
    def headers(self) -> dict[str, str]:
        """Auth + content headers, matching the provider's expected auth style."""
        headers = {"Content-Type": "application/json"}
        if self.auth_style == "bearer":
            headers["Authorization"] = f"Bearer {self.mimo_api_key}"
        else:
            headers["api-key"] = self.mimo_api_key
        return headers

    def validate(self) -> list[str]:
        errors = []
        if not self.mimo_api_key:
            errors.append("MIMO_API_KEY is not set")
        if self.framework not in ("fastapi", "flask", "express"):
            errors.append(f"Unsupported framework: {self.framework}")
        return errors

    @classmethod
    def from_env(cls) -> "APIForgeConfig":
        return cls()

"""Configuration for APIForge.

APIForge speaks the OpenAI-compatible ``/chat/completions`` protocol, so it
works with any provider exposing that API: OpenAI, OpenRouter, Ollama, local
llama.cpp / vLLM servers, Xiaomi MiMo, and more. Select a provider via
``provider=`` (or the ``APIFORGE_PROVIDER`` env var, default ``openai``).

Resolution order for the key, base URL and model:

1. explicit constructor arguments;
2. the generic ``APIFORGE_API_KEY`` / ``APIFORGE_BASE_URL`` / ``APIFORGE_MODEL``
   env vars (work with every provider, e.g. a self-hosted endpoint);
3. the provider's own env vars (``OPENAI_API_KEY``, ``OPENROUTER_API_KEY``, ...);
4. the provider preset's defaults.

The ``mimo_*`` attribute names are kept for backward compatibility; they hold
whichever provider's key/url/model is active. Prefer the ``api_key`` /
``base_url`` / ``model`` aliases in new code.
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
        "env_model": "MIMO_MODEL",
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
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "auth_style": "bearer",
        "model": "llama-3.3-70b-versatile",
        "env_key": "GROQ_API_KEY",
        "env_base": "GROQ_BASE_URL",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "auth_style": "bearer",
        "model": "deepseek-chat",
        "env_key": "DEEPSEEK_API_KEY",
        "env_base": "DEEPSEEK_BASE_URL",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "auth_style": "bearer",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "env_key": "TOGETHER_API_KEY",
        "env_base": "TOGETHER_BASE_URL",
    },
    "mistral": {
        "base_url": "https://api.mistral.ai/v1",
        "auth_style": "bearer",
        "model": "mistral-small-latest",
        "env_key": "MISTRAL_API_KEY",
        "env_base": "MISTRAL_BASE_URL",
    },
}

DEFAULT_PROVIDER = "openai"


@dataclass
class APIForgeConfig:
    provider: str = field(
        default_factory=lambda: os.getenv("APIFORGE_PROVIDER", DEFAULT_PROVIDER)
    )
    mimo_api_key: str = field(default_factory=lambda: os.getenv("APIFORGE_API_KEY", ""))
    mimo_base_url: str = field(
        default_factory=lambda: os.getenv("APIFORGE_BASE_URL", "")
    )
    mimo_model: str = field(default_factory=lambda: os.getenv("APIFORGE_MODEL", ""))
    auth_style: str = ""  # "bearer" | "api-key" — resolved from provider if blank
    output_dir: str = field(
        default_factory=lambda: os.getenv("APIFORGE_OUTPUT_DIR", "./output")
    )
    framework: str = field(
        default_factory=lambda: os.getenv("APIFORGE_FRAMEWORK", "fastapi")
    )

    def __post_init__(self) -> None:
        preset = self.preset
        # Fall back to the provider's own env vars, then to the preset defaults.
        if not self.mimo_api_key:
            self.mimo_api_key = os.getenv(preset["env_key"], "")
        if not self.mimo_base_url:
            self.mimo_base_url = os.getenv(preset["env_base"], preset["base_url"])
        if not self.mimo_model:
            env_model = preset.get("env_model")
            self.mimo_model = (os.getenv(env_model, "") if env_model else "") or preset[
                "model"
            ]
        if not self.auth_style:
            self.auth_style = preset["auth_style"]

    @property
    def preset(self) -> dict[str, str]:
        """The active provider preset (unknown providers fall back to the default)."""
        return PROVIDER_PRESETS.get(self.provider, PROVIDER_PRESETS[DEFAULT_PROVIDER])

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
            errors.append(
                f"API key is not set (set {self.preset['env_key']} or APIFORGE_API_KEY)"
            )
        if self.framework not in ("fastapi", "flask", "express"):
            errors.append(f"Unsupported framework: {self.framework}")
        return errors

    @classmethod
    def from_env(cls) -> "APIForgeConfig":
        return cls()

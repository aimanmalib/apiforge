"""Configuration for APIForge."""
from __future__ import annotations
import os
from dataclasses import dataclass, field


@dataclass
class APIForgeConfig:
    mimo_api_key: str = field(default_factory=lambda: os.getenv("MIMO_API_KEY", ""))
    mimo_base_url: str = field(default_factory=lambda: os.getenv("MIMO_BASE_URL", "https://token-plan-sgp.xiaomimimo.com/v1"))
    mimo_model: str = field(default_factory=lambda: os.getenv("MIMO_MODEL", "mimo-v2.5-pro"))
    output_dir: str = field(default_factory=lambda: os.getenv("APIFORGE_OUTPUT_DIR", "./output"))
    framework: str = field(default_factory=lambda: os.getenv("APIFORGE_FRAMEWORK", "fastapi"))

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

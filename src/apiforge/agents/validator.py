"""ValidateAgent -- Validate OpenAPI specs."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .base import BaseAgent


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    score: int  # 0-100


class ValidateAgent(BaseAgent):
    name = "validator"

    def _build_system_prompt(self) -> str:
        return "You validate OpenAPI specs for correctness and best practices."

    async def validate(self, spec: dict[str, Any]) -> ValidationResult:
        errors, warnings = [], []
        if "openapi" not in spec: errors.append("Missing openapi version")
        if "info" not in spec: errors.append("Missing info object")
        if "paths" not in spec: errors.append("Missing paths object")
        info = spec.get("info", {})
        if not info.get("title"): errors.append("Missing API title")
        if not info.get("version"): errors.append("Missing API version")
        for path, methods in spec.get("paths", {}).items():
            for method, op in methods.items():
                if method in ("get", "post", "put", "delete", "patch"):
                    if "responses" not in op: errors.append(f"Missing responses for {method.upper()} {path}")
                    if "summary" not in op and "operationId" not in op: warnings.append(f"Missing summary for {method.upper()} {path}")
        score = max(0, 100 - len(errors) * 10 - len(warnings) * 2)
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings, score=score)

    async def run(self, **kwargs: Any) -> ValidationResult:
        return await self.validate(kwargs["spec"])

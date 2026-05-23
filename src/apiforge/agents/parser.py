"""ParserAgent -- Parse natural language API descriptions."""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import Any
from .base import BaseAgent


@dataclass
class ParsedEndpoint:
    path: str
    method: str
    description: str
    parameters: list[dict[str, Any]] = field(default_factory=list)
    request_body: dict[str, Any] | None = None
    response_schema: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    auth_required: bool = True


@dataclass
class APIDescription:
    title: str
    description: str
    version: str = "1.0.0"
    base_path: str = "/api/v1"
    endpoints: list[ParsedEndpoint] = field(default_factory=list)
    auth_type: str = "bearer"
    models: list[dict[str, Any]] = field(default_factory=list)


class ParserAgent(BaseAgent):
    name = "parser"

    def _build_system_prompt(self) -> str:
        return "You are APIForge parser. Extract structured API data as JSON."

    async def parse(self, description: str) -> APIDescription:
        prompt = "Parse this API description into JSON: " + description
        response = await self._call_mimo(prompt)
        try:
            text = response.content
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            data = json.loads(text.strip())
            endpoints = [
                ParsedEndpoint(
                    path=ep.get("path", "/"), method=ep.get("method", "GET").upper(),
                    description=ep.get("description", ""), parameters=ep.get("parameters", []),
                    request_body=ep.get("request_body"), response_schema=ep.get("response_schema", {}),
                    tags=ep.get("tags", []), auth_required=ep.get("auth_required", True),
                ) for ep in data.get("endpoints", [])
            ]
            return APIDescription(
                title=data.get("title", "API"), description=data.get("description", ""),
                version=data.get("version", "1.0.0"), base_path=data.get("base_path", "/api/v1"),
                endpoints=endpoints, auth_type=data.get("auth_type", "bearer"),
                models=data.get("models", []))
        except (json.JSONDecodeError, IndexError):
            return APIDescription(title="Parsed API", description=description)

    async def run(self, **kwargs: Any) -> APIDescription:
        return await self.parse(kwargs["description"])

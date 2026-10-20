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


_SCHEMA_HINT = """Reply with ONE JSON object and nothing else (no prose, no markdown).
Use exactly this shape:
{
  "title": "string",
  "description": "string",
  "version": "1.0.0",
  "base_path": "/api/v1",
  "auth_type": "bearer" | "api_key" | "none",
  "endpoints": [
    {
      "path": "/resource/{id}",
      "method": "GET" | "POST" | "PUT" | "PATCH" | "DELETE",
      "description": "string",
      "parameters": [
        {"name": "id", "in": "path" | "query", "type": "string" | "integer" | "boolean", "required": true}
      ],
      "request_body": {"field": "type"} | null,
      "response_schema": {"field": "type"},
      "tags": ["string"],
      "auth_required": true
    }
  ],
  "models": [
    {"name": "Resource", "fields": [{"name": "id", "type": "string", "required": true}]}
  ]
}
Paths are relative to base_path. Include every endpoint the user describes."""


def _extract_json(text: str) -> Any:
    """Parse a JSON object from an LLM reply, tolerating code fences and prose."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    if "```" in text:
        fenced = text.split("```")[1]
        if fenced.startswith("json"):
            fenced = fenced[4:]
        try:
            return json.loads(fenced.strip())
        except json.JSONDecodeError:
            pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start : end + 1])
    raise json.JSONDecodeError("no JSON object found", text, 0)


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
        return (
            "You are the APIForge parser. Turn a natural-language API description "
            "into a structured JSON spec.\n" + _SCHEMA_HINT
        )

    async def parse(self, description: str) -> APIDescription:
        prompt = "Parse this API description into the JSON shape above:\n" + description
        response = await self._call_mimo(prompt)
        try:
            data = _extract_json(response.content or "")
            if not isinstance(data, dict):
                raise ValueError("parser reply is not a JSON object")
            endpoints = [
                ParsedEndpoint(
                    path=ep.get("path", "/"),
                    method=ep.get("method", "GET").upper(),
                    description=ep.get("description", ""),
                    parameters=ep.get("parameters", []),
                    request_body=ep.get("request_body"),
                    response_schema=ep.get("response_schema", {}),
                    tags=ep.get("tags", []),
                    auth_required=ep.get("auth_required", True),
                )
                for ep in data.get("endpoints", [])
            ]
            return APIDescription(
                title=data.get("title", "API"),
                description=data.get("description", ""),
                version=data.get("version", "1.0.0"),
                base_path=data.get("base_path", "/api/v1"),
                endpoints=endpoints,
                auth_type=data.get("auth_type", "bearer"),
                models=data.get("models", []),
            )
        except (
            json.JSONDecodeError,
            IndexError,
            ValueError,
            AttributeError,
            TypeError,
        ):
            return APIDescription(title="Parsed API", description=description)

    async def run(self, **kwargs: Any) -> APIDescription:
        return await self.parse(kwargs["description"])

"""SchemaAgent -- Generate OpenAPI 3.1 specs."""

from __future__ import annotations
from typing import Any
from .base import BaseAgent
from .parser import APIDescription


class SchemaAgent(BaseAgent):
    name = "schema"

    def _build_system_prompt(self) -> str:
        return "You generate OpenAPI 3.1 specs from API descriptions."

    def _build_paths(self, desc: APIDescription) -> dict[str, Any]:
        paths: dict[str, Any] = {}
        for ep in desc.endpoints:
            if ep.path not in paths:
                paths[ep.path] = {}
            op: dict[str, Any] = {
                "summary": ep.description,
                "operationId": f"{ep.method.lower()}_{ep.path.replace('/', '_').strip('_')}",
                "tags": ep.tags or ["default"],
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": ep.response_schema or {"type": "object"}
                            }
                        },
                    }
                },
            }
            if ep.parameters:
                op["parameters"] = [
                    {
                        "name": p.get("name"),
                        "in": p.get("in", "query"),
                        "required": p.get("required", False),
                        "schema": {"type": p.get("type", "string")},
                    }
                    for p in ep.parameters
                ]
            if ep.request_body and ep.method in ("POST", "PUT", "PATCH"):
                op["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": ep.request_body}},
                }
            if ep.auth_required:
                op["security"] = [{"bearerAuth": []}]
            paths[ep.path][ep.method.lower()] = op
        return paths

    def _build_schemas(self, desc: APIDescription) -> dict[str, Any]:
        schemas: dict[str, Any] = {}
        for m in desc.models:
            props, req = {}, []
            for f in m.get("fields", []):
                props[f["name"]] = {"type": f.get("type", "string")}
                if f.get("required"):
                    req.append(f["name"])
            schemas[m["name"]] = {
                "type": "object",
                "properties": props,
                "required": req,
            }
        return schemas

    async def generate_spec(self, desc: APIDescription) -> dict[str, Any]:
        return {
            "openapi": "3.1.0",
            "info": {
                "title": desc.title,
                "description": desc.description,
                "version": desc.version,
            },
            "servers": [{"url": desc.base_path}],
            "paths": self._build_paths(desc),
            "components": {
                "schemas": self._build_schemas(desc),
                "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
            },
            "security": [{"bearerAuth": []}],
        }

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        return await self.generate_spec(kwargs["description"])

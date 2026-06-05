"""RouterAgent -- Generate FastAPI route code."""

from __future__ import annotations
from typing import Any
from .base import BaseAgent
from .parser import APIDescription


class RouterAgent(BaseAgent):
    name = "router"

    def _build_system_prompt(self) -> str:
        return "You generate production-ready FastAPI route code."

    def _generate_code(self, desc: APIDescription) -> str:
        lines = [
            '"""Auto-generated FastAPI routes by APIForge."""',
            "from fastapi import APIRouter, HTTPException, Query",
            'router = APIRouter(prefix="' + desc.base_path + '")',
            "",
        ]
        for ep in desc.endpoints:
            fname = (
                ep.path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                or "root"
            )
            method = ep.method.lower()
            fname = f"{method}_{fname}"
            params = []
            for p in ep.parameters:
                ptype = {"integer": "int", "string": "str", "boolean": "bool"}.get(
                    p.get("type", "string"), "str"
                )
                if p.get("in") == "path":
                    params.append(f"{p['name']}: {ptype}")
                else:
                    params.append(f"{p['name']}: {ptype} = Query(None)")
            if ep.request_body and method in ("post", "put", "patch"):
                params.append("body: dict")
            ps = ", ".join(params)
            lines.append(f'@router.{method}("{ep.path}")')
            lines.append(f"async def {fname}({ps}):")
            lines.append(f'    """{ep.description}"""')
            lines.append("    return {}")
            lines.append("")
        return "\n".join(lines)

    async def generate_routes(self, desc: APIDescription) -> str:
        code = self._generate_code(desc)
        resp = await self._call_mimo(
            f"Review and improve this FastAPI code:\n```python\n{code}\n```"
        )
        if "```" in resp.content:
            extracted = resp.content.split("```")[1]
            if extracted.startswith("python"):
                extracted = extracted[6:]
            return extracted.strip()
        return code

    async def run(self, **kwargs: Any) -> str:
        return await self.generate_routes(kwargs["description"])

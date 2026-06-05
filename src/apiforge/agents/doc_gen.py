"""DocAgent -- Generate API documentation."""

from __future__ import annotations
from typing import Any
from .base import BaseAgent
from .parser import APIDescription


class DocAgent(BaseAgent):
    name = "doc_gen"

    def _build_system_prompt(self) -> str:
        return "You generate clear API documentation in markdown."

    async def generate_docs(self, desc: APIDescription) -> str:
        lines = [
            f"# {desc.title}",
            "",
            desc.description,
            "",
            "## Base URL",
            f"`{desc.base_path}`",
            "",
            "## Authentication",
            f"Type: {desc.auth_type}",
            "",
            "## Endpoints",
            "",
        ]
        for ep in desc.endpoints:
            lines.append(f"### `{ep.method} {ep.path}`")
            lines.append(ep.description)
            if ep.parameters:
                lines.append("| Name | In | Type | Required |")
                lines.append("|------|-----|------|----------|")
                for p in ep.parameters:
                    lines.append(
                        f"| {p.get('name')} | {p.get('in', 'query')} | {p.get('type', 'string')} | {p.get('required', False)} |"
                    )
            lines.append("")
        resp = await self._call_mimo(
            "Improve this API documentation:\n" + "\n".join(lines[:50])
        )
        return resp.content if resp.content else "\n".join(lines)

    async def run(self, **kwargs: Any) -> str:
        return await self.generate_docs(kwargs["description"])

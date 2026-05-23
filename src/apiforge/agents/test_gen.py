"""TestAgent -- Generate pytest test suites."""
from __future__ import annotations
from typing import Any
from .base import BaseAgent
from .parser import APIDescription


class TestAgent(BaseAgent):
    name = "test_gen"

    def _build_system_prompt(self) -> str:
        return "You generate comprehensive pytest test suites for FastAPI APIs."

    async def generate_tests(self, desc: APIDescription) -> str:
        lines = ['"""Auto-generated tests by APIForge."""', "import pytest",
                 "from fastapi.testclient import TestClient", ""]
        for ep in desc.endpoints:
            fname = ep.path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
            method = ep.method.lower()
            test_name = f"test_{method}_{fname}"
            lines.append(f"def {test_name}(client):")
            lines.append(f'    """Test {ep.method} {ep.path}."""')
            if ep.method == "GET":
                lines.append(f'    resp = client.get("{ep.path}")')
            else:
                lines.append(f'    resp = client.{method}("{ep.path}", json={{}})')
            lines.append("    assert resp.status_code in (200, 201, 401, 422)")
            lines.append("")
        return "\n".join(lines)

    async def run(self, **kwargs: Any) -> str:
        return await self.generate_tests(kwargs["description"])

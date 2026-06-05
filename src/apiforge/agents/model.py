"""ModelAgent -- Generate Pydantic models."""

from __future__ import annotations
from typing import Any
from .base import BaseAgent
from .parser import APIDescription


class ModelAgent(BaseAgent):
    name = "model"
    TYPE_MAP = {"string": "str", "integer": "int", "boolean": "bool", "number": "float"}

    def _build_system_prompt(self) -> str:
        return "You generate Pydantic v2 models from API descriptions."

    def _generate_models(self, desc: APIDescription) -> str:
        lines = [
            '"""Auto-generated models."""',
            "from pydantic import BaseModel, Field",
            "from typing import Optional",
            "",
        ]
        for m in desc.models:
            lines.append(f"class {m['name']}(BaseModel):")
            for fld in m.get("fields", []):
                ftype = self.TYPE_MAP.get(fld.get("type", "string"), "str")
                if not fld.get("required", True):
                    lines.append(f"    {fld['name']}: Optional[{ftype}] = None")
                else:
                    lines.append(f"    {fld['name']}: {ftype}")
            lines.append("")
        return "\n".join(lines)

    async def generate_models(self, desc: APIDescription) -> str:
        code = self._generate_models(desc)
        resp = await self._call_mimo(
            f"Review these Pydantic models:\n```python\n{code}\n```"
        )
        if "```" in resp.content:
            extracted = resp.content.split("```")[1]
            if extracted.startswith("python"):
                extracted = extracted[6:]
            return extracted.strip()
        return code

    async def run(self, **kwargs: Any) -> str:
        return await self.generate_models(kwargs["description"])

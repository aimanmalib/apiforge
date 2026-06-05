"""AuthAgent -- Generate auth middleware."""

from __future__ import annotations
from typing import Any
from .base import BaseAgent


class AuthAgent(BaseAgent):
    name = "auth"

    def _build_system_prompt(self) -> str:
        return "You generate secure auth middleware for FastAPI."

    async def generate_auth(self, auth_type: str = "bearer") -> str:
        if auth_type == "api_key":
            code = '"""API Key Auth."""\nfrom fastapi import Security, HTTPException\nfrom fastapi.security import APIKeyHeader\nimport os\n\nheader = APIKeyHeader(name="X-API-Key")\nKEYS = set(os.getenv("API_KEYS", "").split(","))\n\nasync def verify(key: str = Security(header)):\n    if key not in KEYS:\n        raise HTTPException(403, "Invalid API key")\n    return key'
        else:
            code = '"""JWT Auth."""\nfrom fastapi import Depends, HTTPException\nfrom fastapi.security import HTTPBearer\nimport jwt, os\n\nsec = HTTPBearer()\nSECRET = os.getenv("JWT_SECRET", "change-me")\n\nasync def get_user(creds = Depends(sec)):\n    try:\n        return jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])\n    except jwt.InvalidTokenError:\n        raise HTTPException(401, "Invalid token")'
        resp = await self._call_mimo(f"Review this auth code:\n```python\n{code}\n```")
        if "```" in resp.content:
            extracted = resp.content.split("```")[1]
            if extracted.startswith("python"):
                extracted = extracted[6:]
            return extracted.strip()
        return code

    async def run(self, **kwargs: Any) -> str:
        return await self.generate_auth(kwargs.get("auth_type", "bearer"))

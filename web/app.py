"""APIForge web dashboard -- full FastAPI application."""
from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from apiforge.config import PROVIDER_PRESETS, APIForgeConfig
from apiforge.pipeline import APIForgePipeline
from apiforge.token_tracker import TokenTracker

app = FastAPI(title="APIForge Dashboard", version="1.0.0")

_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
_jobs: dict[str, dict[str, Any]] = {}
_tracker = TokenTracker()


class GenerateRequest(BaseModel):
    description: str
    framework: str = "fastapi"
    auth_type: str = "bearer"


class ValidateRequest(BaseModel):
    spec: dict[str, Any]


class JobStatus(BaseModel):
    job_id: str
    status: str
    created_at: str
    completed_at: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None


class TokenSummary(BaseModel):
    total_calls: int
    total_tokens: int
    by_agent: dict[str, Any]
    daily_estimates_millions: dict[str, float]
    daily_total_estimated_millions: float


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_id() -> str:
    import uuid
    return str(uuid.uuid4())[:8]


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "templates" / "index.html"
    if html_path.exists():
        return html_path.read_text()
    return "<h1>APIForge</h1><p>Dashboard template not found.</p>"


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "apiforge",
        "version": "1.0.0",
        "timestamp": _now(),
    }


@app.post("/api/generate")
async def generate_api(req: GenerateRequest):
    """Submit an API generation job."""
    job_id = _generate_id()
    _jobs[job_id] = {
        "job_id": job_id,
        "status": "running",
        "created_at": _now(),
        "completed_at": None,
        "result": None,
        "error": None,
    }
    try:
        config = APIForgeConfig.from_env()
        pipeline = APIForgePipeline(config)
        result = await pipeline.generate(req.description)
        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["completed_at"] = _now()
        _jobs[job_id]["result"] = {
            "title": result.description.title,
            "endpoints_count": len(result.description.endpoints),
            "validation_score": result.validation.score,
            "validation_valid": result.validation.valid,
            "validation_errors": result.validation.errors,
            "validation_warnings": result.validation.warnings,
            "token_summary": result.token_summary,
            "openapi_spec": result.openapi_spec,
            "router_code": result.router_code,
            "model_code": result.model_code,
            "auth_code": result.auth_code,
            "test_code": result.test_code,
            "docs": result.docs,
        }
    except Exception as exc:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["error"] = str(exc)
        _jobs[job_id]["completed_at"] = _now()
    return {"job_id": job_id, "status": _jobs[job_id]["status"]}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and result."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs."""
    return {"jobs": list(_jobs.values()), "count": len(_jobs)}


@app.post("/api/validate")
async def validate_spec(req: ValidateRequest):
    """Validate an OpenAPI spec."""
    config = APIForgeConfig.from_env()
    pipeline = APIForgePipeline(config)
    result = await pipeline.validator.validate(spec=req.spec)
    await pipeline.client.close()
    return {
        "valid": result.valid,
        "score": result.score,
        "errors": result.errors,
        "warnings": result.warnings,
    }


@app.get("/api/tokens")
async def get_token_stats():
    """Get token usage statistics."""
    return _tracker.summary()


@app.get("/api/tokens/daily")
async def get_daily_estimates():
    """Get daily token consumption estimates."""
    return {
        "estimates": TokenTracker.DAILY_ESTIMATES,
        "total_daily": sum(TokenTracker.DAILY_ESTIMATES.values()),
    }


@app.get("/api/models")
async def list_supported_models():
    """List the built-in provider presets and the currently configured model."""
    config = APIForgeConfig.from_env()
    return {
        "provider": config.provider,
        "models": [
            {"provider": name, "id": preset["model"]}
            for name, preset in PROVIDER_PRESETS.items()
        ],
        "default": config.model,
    }


@app.get("/api/frameworks")
async def list_frameworks():
    """List supported target frameworks."""
    return {
        "frameworks": [
            {"id": "fastapi", "name": "FastAPI", "language": "Python"},
            {"id": "flask", "name": "Flask", "language": "Python"},
            {"id": "express", "name": "Express", "language": "TypeScript"},
        ],
        "default": "fastapi",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__},
    )

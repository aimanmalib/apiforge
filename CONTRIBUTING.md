# Contributing to APIForge

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/apiforge
cd apiforge

# Install in development mode
pip install -e ".[dev]"

# Run tests
PYTHONPATH=src python -m pytest tests/ -v

# Run the web dashboard
uvicorn web.app:app --reload --port 8080
```

## Architecture

APIForge uses a multi-agent pipeline architecture:

1. **ParserAgent** — Converts natural language to structured API description
2. **SchemaAgent** — Generates OpenAPI 3.1 specifications
3. **RouterAgent** — Generates FastAPI route code
4. **ModelAgent** — Generates Pydantic v2 models
5. **AuthAgent** — Generates JWT/API key authentication
6. **TestAgent** — Generates pytest test suites
7. **DocAgent** — Generates API documentation (markdown)
8. **ValidateAgent** — Validates OpenAPI specs with scoring

## Adding a New Agent

1. Create `src/apiforge/agents/my_agent.py`
2. Extend `BaseAgent` and implement `run()`
3. Add to `APIForgePipeline` in `pipeline.py`
4. Add tests in `tests/test_my_agent.py`

## Code Style

- Python 3.10+ with type hints everywhere
- `from __future__ import annotations` in every module
- Pydantic v2 for data validation
- async/await for all I/O operations
- pytest for testing, 90%+ coverage target

## MiMo API Integration

**CRITICAL**: The MiMo API uses `api-key` header, NOT `Authorization: Bearer`.

```python
headers = {"api-key": "your-key-here"}
```

Endpoint: `https://token-plan-sgp.xiaomimimo.com/v1/chat/completions`

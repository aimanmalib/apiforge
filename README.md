# 🔧 APIForge

**API Scaffolding Engine powered by Xiaomi MiMo V2.5 Pro**

> Describe your API in natural language — get a complete FastAPI backend with OpenAPI spec, routes, models, auth, tests, and docs.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    APIForge Pipeline                      │
│                                                          │
│  ┌──────────┐                                            │
│  │  Parser  │  "Blog API with auth and pagination"       │
│  │  Agent   │──▶ APIDescription (structured)             │
│  └──────────┘                                            │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Schema   │  │ Router   │  │  Model   │               │
│  │ Agent    │  │ Agent    │  │  Agent   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│       │              │              │                     │
│       ▼              ▼              ▼                     │
│  OpenAPI 3.1   FastAPI Routes  Pydantic Models           │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Auth    │  │ Test Gen │  │ Doc Gen  │               │
│  │  Agent   │  │  Agent   │  │  Agent   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│       │              │              │                     │
│       ▼              ▼              ▼                     │
│  JWT/API Key    pytest Suite    API.md Docs              │
│       │                                                  │
│       ▼                                                  │
│  ┌──────────┐                                            │
│  │Validator │  Score: 0-100                              │
│  │  Agent   │  Errors + Warnings                        │
│  └──────────┘                                            │
│                                                          │
│  ═══════════════════════════════════════════              │
│  Xiaomi MiMo V2.5 Pro                                    │
│  token-plan-sgp.xiaomimimo.com/v1                        │
└─────────────────────────────────────────────────────────┘
```

## Agents

| Agent | Role | Est. Tokens/Day |
|-------|------|-----------------|
| **Parser** | Parse NL API descriptions | 0.30M |
| **Schema** | Generate OpenAPI 3.1 specs | 0.50M |
| **Router** | Generate FastAPI route code | 0.45M |
| **Model** | Generate Pydantic models | 0.35M |
| **Auth** | Generate JWT/API key middleware | 0.20M |
| **Test Gen** | Generate pytest test suites | 0.40M |
| **Doc Gen** | Generate API docs (markdown) | 0.25M |
| **Validator** | Validate OpenAPI specs | 0.15M |

**Daily Total: ~2.6M tokens**

## Token Consumption Report

| Metric | Value |
|--------|-------|
| Daily token consumption | ~2.6M tokens |
| Per-generation (avg) | ~15K tokens |
| Primary model | mimo-v2.5-pro |
| API endpoint | `token-plan-sgp.xiaomimimo.com/v1` |
| Auth method | `api-key` header |

## Why MiMo?

1. **Code generation quality** — MiMo produces clean, syntactically correct Python with proper type hints
2. **Structured output** — Consistently generates valid JSON for OpenAPI specs and Pydantic models
3. **Cost efficiency** — 8-agent pipeline consumes significant tokens; MiMo's pricing enables full pipeline runs
4. **Reasoning depth** — Chain-of-thought helps the Validator agent identify subtle spec issues
5. **API compatibility** — OpenAI-compatible endpoint simplifies integration

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Set API key
export MIMO_API_KEY="your-key-here"

# Generate an API
apiforge generate "Blog API with users, posts, comments, JWT auth, and pagination"

# Validate a spec
apiforge validate output/openapi.json

# View token stats
apiforge stats
```

## Example

```bash
$ apiforge generate "E-commerce API with products, cart, orders, Stripe payments"
# Generates:
#   output/openapi.json  - OpenAPI 3.1 specification
#   output/routes.py     - FastAPI routes
#   output/models.py     - Pydantic models
#   output/auth.py       - JWT authentication
#   output/test_api.py   - pytest test suite
#   output/API.md        - API documentation
```

## Tech Stack

- Python 3.10+
- Click + Rich (CLI)
- FastAPI (web dashboard)
- httpx (async HTTP)
- Jinja2 (code templates)
- Pydantic v2 (models)
- pytest (testing)

## API Details

- **Endpoint**: `https://token-plan-sgp.xiaomimimo.com/v1/chat/completions`
- **Model**: `mimo-v2.5-pro`
- **Auth**: `api-key` header (NOT `Authorization: Bearer`)
- **Streaming**: SSE with `reasoning_content` field

## License

MIT

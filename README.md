# 🔧 APIForge

**8-Agent API Scaffolding Engine for any OpenAI-compatible LLM**

> Describe your API in natural language — get a complete FastAPI backend with OpenAPI spec, routes, models, auth, tests, and docs.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![CI](https://github.com/aimanmalib/apiforge/actions/workflows/ci.yml/badge.svg)](https://github.com/aimanmalib/apiforge/actions/workflows/ci.yml)
[![Tests: 144](https://img.shields.io/badge/tests-144-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Works with **OpenAI, OpenRouter, Ollama, llama.cpp, Xiaomi MiMo**, or any endpoint that speaks the OpenAI `/chat/completions` protocol. Pick a provider with one config line — no code changes.

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
│  Any OpenAI-compatible /chat/completions endpoint        │
│  (OpenAI · OpenRouter · Ollama · MiMo · ...)             │
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

## Supported Providers

APIForge talks to any OpenAI-compatible `/chat/completions` endpoint. Built-in presets:

| Provider | `provider=` | Default model | Auth | Env vars |
|----------|-------------|---------------|------|----------|
| OpenAI | `openai` | `gpt-4o-mini` | Bearer | `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| OpenRouter | `openrouter` | `openai/gpt-4o-mini` | Bearer | `OPENROUTER_API_KEY` |
| Ollama (local) | `ollama` | `llama3.1` | Bearer | `OLLAMA_BASE_URL` |
| Xiaomi MiMo | `mimo` | `mimo-v2.5-pro` | api-key | `MIMO_API_KEY` |

Select a provider with the `APIFORGE_PROVIDER` env var (or `APIForgeConfig(provider=...)`), or point `MIMO_BASE_URL` at any other compatible endpoint (llama.cpp, vLLM, LM Studio, a local proxy). The right auth header (bearer vs api-key) is chosen automatically per provider.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Pick any provider — set its API key (OpenAI shown here)
export APIFORGE_PROVIDER=openai
export OPENAI_API_KEY="sk-your-key-here"

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

## LLM Backend

- **Protocol**: OpenAI-compatible `/chat/completions`
- **Providers**: OpenAI, OpenRouter, Ollama, llama.cpp, Xiaomi MiMo, or any compatible endpoint
- **Auth**: bearer token or `api-key` header, selected automatically per provider
- **Config**: set `APIFORGE_PROVIDER` + the provider's API key env var

## License

MIT

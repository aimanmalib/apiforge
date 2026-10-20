> [!IMPORTANT]
> **apiforge has moved into [crewforge](https://github.com/aimanmalib/crewforge).** It now lives on as `crewforge scaffold` and `crewforge validate`, on a shared core
> that fails loudly instead of reporting success on empty output. This repository is archived and kept for history;
> new issues and changes go to crewforge.

# 🔧 APIForge

**Multi-agent API scaffolding for any OpenAI-compatible LLM**

> Describe your API in plain English — get an OpenAPI 3.1 spec, FastAPI routes, Pydantic models, auth middleware, a pytest skeleton and Markdown docs.

[![CI](https://github.com/aimanmalib/apiforge/actions/workflows/ci.yml/badge.svg)](https://github.com/aimanmalib/apiforge/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Works with **OpenAI, OpenRouter, Ollama, Groq, DeepSeek, Together, Mistral, Xiaomi MiMo**, or any self-hosted endpoint that speaks the OpenAI `/chat/completions` protocol (llama.cpp, vLLM, LM Studio, ...). Pick a provider with environment variables — no code changes.

> APIForge produces a **starting point**, not finished software. Review the generated code before you run it anywhere that matters.

---

## How it works

```
"Todo API with GET /todos"
          │
          ▼
   ┌──────────────┐
   │ Parser   LLM │  natural language ──▶ structured APIDescription (JSON)
   └──────────────┘
          │
          ├──▶ Schema           OpenAPI 3.1 spec              (deterministic)
          ├──▶ Router      LLM  FastAPI routes                (template + LLM review)
          ├──▶ Model       LLM  Pydantic models               (template + LLM review)
          ├──▶ Auth        LLM  JWT / API-key middleware      (template + LLM review)
          ├──▶ Test Gen         pytest skeleton               (deterministic)
          ├──▶ Doc Gen     LLM  API.md                        (template + LLM rewrite)
          └──▶ Validator        spec checks, score 0–100      (deterministic)
```

The pipeline has eight stages. Five of them call the LLM; the schema builder, test generator and validator are plain Python, so one `generate` run makes **5 LLM calls**.

## Supported providers

Built-in presets (from [`src/apiforge/config.py`](src/apiforge/config.py)):

| Provider | `APIFORGE_PROVIDER=` | Default model | Auth header | Key env var |
|----------|----------------------|---------------|-------------|-------------|
| OpenAI *(default)* | `openai` | `gpt-4o-mini` | `Authorization: Bearer` | `OPENAI_API_KEY` |
| OpenRouter | `openrouter` | `openai/gpt-4o-mini` | `Authorization: Bearer` | `OPENROUTER_API_KEY` |
| Ollama (local) | `ollama` | `llama3.1` | `Authorization: Bearer` | `OLLAMA_API_KEY` (optional) |
| Groq | `groq` | `llama-3.3-70b-versatile` | `Authorization: Bearer` | `GROQ_API_KEY` |
| DeepSeek | `deepseek` | `deepseek-chat` | `Authorization: Bearer` | `DEEPSEEK_API_KEY` |
| Together | `together` | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | `Authorization: Bearer` | `TOGETHER_API_KEY` |
| Mistral | `mistral` | `mistral-small-latest` | `Authorization: Bearer` | `MISTRAL_API_KEY` |
| Xiaomi MiMo | `mimo` | `mimo-v2.5-pro` | `api-key` | `MIMO_API_KEY` |

Each preset also reads `<PROVIDER>_BASE_URL` (e.g. `OPENAI_BASE_URL`, `OLLAMA_BASE_URL`) to override its endpoint.

These generic variables work with **every** provider and take priority over the provider-specific ones:

| Variable | Purpose |
|----------|---------|
| `APIFORGE_API_KEY` | API key |
| `APIFORGE_BASE_URL` | Base URL of any OpenAI-compatible endpoint (e.g. `http://localhost:8000/v1`) |
| `APIFORGE_MODEL` | Model name |

## Quick start

```bash
git clone https://github.com/aimanmalib/apiforge.git
cd apiforge
pip install -e .            # add ".[dev]" for tests and ruff

# OpenAI is the default provider
export OPENAI_API_KEY="sk-..."

# Or OpenRouter
# export APIFORGE_PROVIDER=openrouter
# export OPENROUTER_API_KEY="sk-or-..."

# Or any self-hosted OpenAI-compatible server
# export APIFORGE_BASE_URL=http://localhost:8000/v1
# export APIFORGE_MODEL=my-model
# export APIFORGE_API_KEY=anything

apiforge --help
apiforge generate "Todo API with GET /todos returning a list of todos" -o output
apiforge validate output/openapi.json
```

`generate` writes these files to the output directory (default `./output`):

| File | Contents |
|------|----------|
| `openapi.json` | OpenAPI 3.1 specification |
| `routes.py` | FastAPI routes |
| `models.py` | Pydantic models |
| `auth.py` | JWT or API-key auth dependency |
| `test_api.py` | pytest skeleton (expects you to provide a `client` fixture) |
| `API.md` | API documentation |

It finishes by printing the validation score and the number of tokens the run actually used.

`apiforge stats` prints an *illustrative* per-agent token budget. Those numbers are planning estimates, not measurements.

## Web dashboard

A small FastAPI dashboard lives in [`web/`](web/). It is not part of the installed package; run it from the repository root:

```bash
pip install -e .            # uvicorn is already a dependency
uvicorn web.app:app --reload
# open http://127.0.0.1:8000
```

It uses the same environment variables as the CLI.

## Example

[`examples/ecommerce/`](examples/ecommerce/) is a curated, runnable sample of the kind of FastAPI code APIForge targets (products, cart, orders; in-memory storage).

## Development

```bash
pip install -e ".[dev]"
ruff check src/ tests/
ruff format --check src/ tests/
pytest
```

CI runs the same checks on Python 3.10–3.13. See [CONTRIBUTING.md](CONTRIBUTING.md) to add a provider preset, and [SECURITY.md](SECURITY.md) to report a vulnerability.

## Tech stack

Python 3.10+, Click + Rich (CLI), httpx (async HTTP), Pydantic v2, Jinja2, FastAPI (dashboard), pytest.

## License

[MIT](LICENSE)

---

Built by [Sasa Teguh](https://sasateguh.com) · Malaysia

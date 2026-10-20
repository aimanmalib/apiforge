"""Shared fixtures for APIForge tests."""

import pytest
from unittest.mock import AsyncMock
from apiforge.client import MiMoClient, CompletionResponse
from apiforge.config import APIForgeConfig
from apiforge.token_tracker import TokenTracker


_ENV_VARS = (
    "APIFORGE_PROVIDER",
    "APIFORGE_API_KEY",
    "APIFORGE_BASE_URL",
    "APIFORGE_MODEL",
    "OPENAI_API_KEY",
    "OPENAI_BASE_URL",
    "OPENROUTER_API_KEY",
    "MIMO_API_KEY",
    "MIMO_BASE_URL",
    "MIMO_MODEL",
)


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    """Keep the developer's real provider env vars out of the tests."""
    for name in _ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def config():
    return APIForgeConfig(
        mimo_api_key="test-key", mimo_base_url="https://test.api.com/v1"
    )


@pytest.fixture
def tracker():
    return TokenTracker()


@pytest.fixture
def mock_response():
    def _make(content="Test", prompt_tokens=100, completion_tokens=50):
        return CompletionResponse(
            content=content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    return _make


@pytest.fixture
def mock_client(mock_response):
    client = AsyncMock(spec=MiMoClient)
    client.chat_completion = AsyncMock(return_value=mock_response())
    client.stats = {"request_count": 0, "total_tokens": 0}
    return client

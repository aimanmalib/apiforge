"""Tests for the OpenAI-compatible LLM client."""

from apiforge.client import LLMClient, MiMoClient, CompletionResponse
from apiforge.config import APIForgeConfig


class TestLLMClient:
    def test_mimo_alias(self):
        assert MiMoClient is LLMClient

    def test_init(self, config):
        c = MiMoClient(config)
        assert c.config.mimo_api_key == "test-key"

    def test_headers_default_to_bearer(self, config):
        h = LLMClient(config).headers
        assert h["Authorization"] == "Bearer test-key"
        assert "api-key" not in h

    def test_headers_use_api_key_for_mimo(self):
        c = LLMClient(APIForgeConfig(provider="mimo", mimo_api_key="test-key"))
        h = c.headers
        assert h["api-key"] == "test-key"
        assert "Authorization" not in h

    def test_base_url_strips_slash(self, config):
        config.mimo_base_url = "https://x.com/v1/"
        c = MiMoClient(config)
        assert c.base_url == "https://x.com/v1"

    def test_initial_stats(self, config):
        c = MiMoClient(config)
        assert c.stats["request_count"] == 0

    def test_completion_response_defaults(self):
        r = CompletionResponse()
        assert r.content == ""
        assert r.total_tokens == 0

"""Tests for MiMo client."""

from apiforge.client import MiMoClient, CompletionResponse


class TestMiMoClient:
    def test_init(self, config):
        c = MiMoClient(config)
        assert c.config.mimo_api_key == "test-key"

    def test_headers_use_api_key(self, config):
        c = MiMoClient(config)
        h = c.headers
        assert "api-key" in h
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

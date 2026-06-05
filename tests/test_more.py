"""Additional tests to reach 90+ target."""

from apiforge.config import APIForgeConfig
from apiforge.token_tracker import TokenTracker
from apiforge.exceptions import APIForgeError, MiMoAPIError, RateLimitError


class TestConfigEdgeCases:
    def test_custom_model(self):
        c = APIForgeConfig(mimo_api_key="k", mimo_model="custom-model")
        assert c.mimo_model == "custom-model"

    def test_custom_base_url(self):
        c = APIForgeConfig(mimo_api_key="k", mimo_base_url="https://custom.api.com/v1")
        assert c.mimo_base_url == "https://custom.api.com/v1"


class TestTokenTrackerEdgeCases:
    def test_multiple_agents_summary(self):
        t = TokenTracker()
        t.record("parser", 100, 50)
        t.record("schema", 200, 100)
        t.record("validator", 50, 25)
        s = t.summary()
        assert s["total_calls"] == 3
        assert s["total_tokens"] == 525

    def test_export_json(self, tmp_path):
        t = TokenTracker()
        t.record("test", 100, 50)
        p = t.export_json(tmp_path / "stats.json")
        assert p.exists()
        import json

        data = json.loads(p.read_text())
        assert data["total_calls"] == 1


class TestExceptionHierarchy:
    def test_mimo_error_chain(self):
        e = RateLimitError("too fast", retry_after=10.0)
        assert isinstance(e, MiMoAPIError)
        assert isinstance(e, APIForgeError)
        assert e.retry_after == 10.0

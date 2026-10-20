"""Tests for config."""

from apiforge.config import APIForgeConfig


class TestConfig:
    def test_default(self):
        c = APIForgeConfig(mimo_api_key="k")
        assert c.provider == "openai"
        assert c.model == "gpt-4o-mini"

    def test_validate_no_key(self):
        c = APIForgeConfig(mimo_api_key="")
        errors = c.validate()
        assert any("OPENAI_API_KEY" in e for e in errors)
        assert any("APIFORGE_API_KEY" in e for e in errors)

    def test_validate_no_key_names_provider_env(self):
        c = APIForgeConfig(provider="openrouter", mimo_api_key="")
        assert any("OPENROUTER_API_KEY" in e for e in c.validate())

    def test_validate_bad_framework(self):
        c = APIForgeConfig(mimo_api_key="k", framework="cobol")
        assert any("framework" in e.lower() for e in c.validate())

    def test_validate_good(self):
        c = APIForgeConfig(mimo_api_key="k")
        assert len(c.validate()) == 0

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "env-k")
        c = APIForgeConfig.from_env()
        assert c.mimo_api_key == "env-k"

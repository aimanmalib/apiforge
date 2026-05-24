"""Tests for config."""
import pytest
from apiforge.config import APIForgeConfig

class TestConfig:
    def test_default(self):
        c = APIForgeConfig(mimo_api_key="k")
        assert c.mimo_model == "mimo-v2.5-pro"

    def test_validate_no_key(self):
        c = APIForgeConfig(mimo_api_key="")
        assert any("MIMO_API_KEY" in e for e in c.validate())

    def test_validate_bad_framework(self):
        c = APIForgeConfig(mimo_api_key="k", framework="cobol")
        assert any("framework" in e.lower() for e in c.validate())

    def test_validate_good(self):
        c = APIForgeConfig(mimo_api_key="k")
        assert len(c.validate()) == 0

    def test_from_env(self, monkeypatch):
        monkeypatch.setenv("MIMO_API_KEY", "env-k")
        c = APIForgeConfig.from_env()
        assert c.mimo_api_key == "env-k"

"""Tests for CLI."""

from click.testing import CliRunner
from apiforge.cli import main


class TestCLI:
    def test_help(self):
        r = CliRunner().invoke(main, ["--help"])
        assert r.exit_code == 0
        assert "APIForge" in r.output

    def test_stats(self):
        r = CliRunner().invoke(main, ["stats"])
        assert r.exit_code == 0

    def test_generate_help(self):
        r = CliRunner().invoke(main, ["generate", "--help"])
        assert r.exit_code == 0

    def test_generate_without_key_fails_cleanly(self, monkeypatch):
        r = CliRunner().invoke(main, ["generate", "Todo API"])
        assert r.exit_code == 1
        assert "OPENAI_API_KEY" in r.output

    def test_generate_writes_valid_json_spec(self, tmp_path, monkeypatch):
        """openapi.json must be real JSON so `apiforge validate` can read it back."""
        import json
        from unittest.mock import AsyncMock

        from apiforge import cli
        from apiforge.agents.parser import APIDescription
        from apiforge.agents.validator import ValidationResult
        from apiforge.pipeline import PipelineResult

        spec = {"openapi": "3.1.0", "info": {"title": "T", "version": "1"}, "paths": {}}
        fake = PipelineResult(
            description=APIDescription(title="T", description="d"),
            openapi_spec=spec,
            router_code="r",
            model_code="m",
            auth_code="a",
            test_code="t",
            docs="d",
            validation=ValidationResult(valid=True, errors=[], warnings=[], score=100),
            token_summary={"total_tokens": 42, "total_calls": 8},
        )
        monkeypatch.setenv("APIFORGE_API_KEY", "k")
        monkeypatch.setattr(
            cli.APIForgePipeline, "generate", AsyncMock(return_value=fake)
        )
        out = tmp_path / "out"
        r = CliRunner().invoke(main, ["generate", "Todo API", "-o", str(out)])
        assert r.exit_code == 0, r.output
        assert json.loads((out / "openapi.json").read_text()) == spec
        assert "Tokens used: 42" in r.output

        r = CliRunner().invoke(main, ["validate", str(out / "openapi.json")])
        assert r.exit_code == 0
        assert "Invalid JSON" not in r.output

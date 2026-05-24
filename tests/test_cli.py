"""Tests for CLI."""
import pytest
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

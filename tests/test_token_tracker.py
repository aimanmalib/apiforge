"""Tests for token tracker."""

from apiforge.token_tracker import TokenTracker


class TestTokenTracker:
    def test_initial(self):
        t = TokenTracker()
        assert t.total_tokens() == 0
        assert t.total_calls() == 0

    def test_record(self):
        t = TokenTracker()
        t.record("parser", 100, 50, 200.0)
        assert t.total_calls() == 1
        assert t.total_tokens() == 150

    def test_by_agent(self):
        t = TokenTracker()
        t.record("parser", 100, 50)
        t.record("parser", 200, 100)
        t.record("schema", 150, 75)
        by = t.by_agent()
        assert by["parser"]["calls"] == 2
        assert by["schema"]["calls"] == 1

    def test_summary(self):
        t = TokenTracker()
        t.record("test", 100, 50)
        s = t.summary()
        assert s["total_calls"] == 1
        assert "daily_estimates_millions" in s

    def test_reset(self):
        t = TokenTracker()
        t.record("test", 100, 50)
        t.reset()
        assert t.total_calls() == 0

    def test_daily_estimates(self):
        t = TokenTracker()
        assert "parser" in t.DAILY_ESTIMATES
        assert sum(t.DAILY_ESTIMATES.values()) > 0

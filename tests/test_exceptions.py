"""Tests for exceptions."""

from apiforge.exceptions import (
    APIForgeError,
    ParseError,
    GenerationError,
    ValidationError,
    MiMoAPIError,
    QuotaExceededError,
    RateLimitError,
)


class TestExceptions:
    def test_base_error(self):
        e = APIForgeError("test error")
        assert str(e) == "test error"
        assert e.details == {}

    def test_base_error_with_details(self):
        e = APIForgeError("err", details={"key": "val"})
        assert e.details["key"] == "val"

    def test_parse_error(self):
        e = ParseError("parse failed")
        assert isinstance(e, APIForgeError)

    def test_generation_error(self):
        e = GenerationError("gen failed")
        assert isinstance(e, APIForgeError)

    def test_validation_error(self):
        e = ValidationError("val failed")
        assert isinstance(e, APIForgeError)

    def test_mimo_api_error(self):
        e = MiMoAPIError("api err", status_code=500)
        assert e.status_code == 500
        assert isinstance(e, APIForgeError)

    def test_quota_exceeded(self):
        e = QuotaExceededError("quota")
        assert isinstance(e, MiMoAPIError)

    def test_rate_limit(self):
        e = RateLimitError("rate limited", retry_after=30.0)
        assert e.retry_after == 30.0
        assert isinstance(e, MiMoAPIError)

    def test_inheritance_chain(self):
        assert issubclass(RateLimitError, MiMoAPIError)
        assert issubclass(MiMoAPIError, APIForgeError)
        assert issubclass(APIForgeError, Exception)

"""Custom exceptions for APIForge."""

from __future__ import annotations


class APIForgeError(Exception):
    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


class ParseError(APIForgeError):
    pass


class GenerationError(APIForgeError):
    pass


class ValidationError(APIForgeError):
    pass


class MiMoAPIError(APIForgeError):
    def __init__(self, message: str, status_code: int = 0, **kwargs) -> None:
        super().__init__(message, **kwargs)
        self.status_code = status_code


class QuotaExceededError(MiMoAPIError):
    pass


class RateLimitError(MiMoAPIError):
    def __init__(self, message: str, retry_after: float = 60.0, **kwargs) -> None:
        super().__init__(message, **kwargs)
        self.retry_after = retry_after

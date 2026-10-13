"""Errors raised by external providers. Callers branch on `kind`, never on message text."""

from __future__ import annotations


class ProviderError(Exception):
    """A provider call did not produce a usable result."""

    kind: str = "failed"


class ProviderUnavailable(ProviderError):
    """Nothing usable came back: missing token, timeout, network error, 5xx or rate limit. Retryable."""

    kind = "unavailable"


class ProviderFailed(ProviderError):
    """The provider answered, but the answer cannot be used: bad token, unknown model, malformed payload."""

    kind = "failed"

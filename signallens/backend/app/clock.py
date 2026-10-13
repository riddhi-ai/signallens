"""The single source of time for the backend. Inject a fixed clock in tests."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    """Serialise an aware datetime as UTC ISO-8601 with microseconds, so text sorts by time."""
    if value.tzinfo is None:
        raise ValueError("Naive datetimes are not allowed; use timezone-aware UTC values.")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)

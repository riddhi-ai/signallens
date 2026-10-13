"""Pure functions that turn raw provider JSON into typed results.

No network code lives here, so these can be unit-tested without HTTP clients or API keys.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class MalformedProviderResponse(ValueError):
    """A provider payload does not match the shape this app expects."""


@dataclass(frozen=True)
class ZeroShotResult:
    label: str  # candidate label exactly as the provider echoed it back
    score: float  # provider score in [0, 1]; a model score, not a probability of an incident


@dataclass(frozen=True)
class CurrentWeather:
    observed_at: str  # provider timestamp for the "current" block (UTC, as requested)
    temperature_c: float | None
    precipitation_mm: float | None
    weather_code: int | None  # WMO weather interpretation code
    wind_speed_kmh: float | None


def parse_zero_shot(payload: Any, expected_labels: set[str]) -> ZeroShotResult:
    """Parse a zero-shot classification response: {"labels": [...], "scores": [...]}.

    Every label must be one we asked for. Unknown labels are rejected rather than guessed at.
    """
    if not isinstance(payload, dict):
        raise MalformedProviderResponse("expected a JSON object")
    labels = payload.get("labels")
    scores = payload.get("scores")
    if not isinstance(labels, list) or not isinstance(scores, list):
        raise MalformedProviderResponse("missing 'labels' or 'scores' list")
    if not labels or len(labels) != len(scores):
        raise MalformedProviderResponse("'labels' and 'scores' must be non-empty and the same length")

    pairs: list[tuple[str, float]] = []
    for label, score in zip(labels, scores, strict=True):
        if not isinstance(label, str) or label not in expected_labels:
            raise MalformedProviderResponse(f"unexpected label {label!r}")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise MalformedProviderResponse("score is not numeric")
        if not 0.0 <= float(score) <= 1.0:
            raise MalformedProviderResponse("score is outside [0, 1]")
        pairs.append((label, float(score)))

    best_label, best_score = max(pairs, key=lambda pair: pair[1])
    return ZeroShotResult(label=best_label, score=best_score)


def _number(value: Any, field: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MalformedProviderResponse(f"'{field}' is not numeric")
    return float(value)


def _integer(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or float(value) != int(value):
        raise MalformedProviderResponse(f"'{field}' is not an integer")
    return int(value)


def parse_open_meteo_current(payload: Any) -> CurrentWeather:
    """Parse an Open-Meteo forecast response that was requested with a `current` block."""
    if not isinstance(payload, dict):
        raise MalformedProviderResponse("expected a JSON object")
    current = payload.get("current")
    if not isinstance(current, dict):
        raise MalformedProviderResponse("missing 'current' block")
    observed_at = current.get("time")
    if not isinstance(observed_at, str):
        raise MalformedProviderResponse("missing 'current.time'")
    return CurrentWeather(
        observed_at=observed_at,
        temperature_c=_number(current.get("temperature_2m"), "temperature_2m"),
        precipitation_mm=_number(current.get("precipitation"), "precipitation"),
        weather_code=_integer(current.get("weather_code"), "weather_code"),
        wind_speed_kmh=_number(current.get("wind_speed_10m"), "wind_speed_10m"),
    )

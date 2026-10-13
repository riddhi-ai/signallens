"""Test doubles for the provider interfaces. No network access is needed to run the suite."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.providers.errors import ProviderError
from app.providers.parsers import CurrentWeather, ZeroShotResult

T0 = datetime(2026, 10, 13, 7, 0, tzinfo=timezone.utc)


class MutableClock:
    def __init__(self, start: datetime = T0) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs: float) -> None:
        self.now = self.now + timedelta(**kwargs)


class FakeTextClassifier:
    model_id = "fake/zero-shot"

    def __init__(self, label: str | None = None, score: float = 0.9, error: ProviderError | None = None) -> None:
        self._label = label
        self._score = score
        self._error = error
        self.calls = 0

    def classify(self, text: str, candidate_labels: list[str]) -> ZeroShotResult:
        self.calls += 1
        if self._error is not None:
            raise self._error
        assert self._label is not None
        return ZeroShotResult(label=self._label, score=self._score)


class FakeWeatherProvider:
    name = "fake-weather"

    def __init__(self, current: CurrentWeather | None = None, error: ProviderError | None = None) -> None:
        self._current = current
        self._error = error

    def current(self, latitude: float, longitude: float) -> CurrentWeather:
        if self._error is not None:
            raise self._error
        assert self._current is not None
        return self._current


def dry_weather() -> CurrentWeather:
    return CurrentWeather(
        observed_at="2026-10-13T07:00",
        temperature_c=24.5,
        precipitation_mm=0.0,
        weather_code=3,
        wind_speed_kmh=11.0,
    )


def rainy_weather() -> CurrentWeather:
    return CurrentWeather(
        observed_at="2026-10-13T07:00",
        temperature_c=21.0,
        precipitation_mm=2.4,
        weather_code=63,
        wind_speed_kmh=18.0,
    )

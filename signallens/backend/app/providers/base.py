"""Provider interfaces. Services depend on these, so any model or weather source can be swapped."""

from __future__ import annotations

from typing import Protocol

from app.providers.parsers import CurrentWeather, ZeroShotResult


class TextClassifier(Protocol):
    model_id: str

    def classify(self, text: str, candidate_labels: list[str]) -> ZeroShotResult:
        """Return the best-matching candidate label. Raises ProviderError on failure."""
        ...


class WeatherProvider(Protocol):
    name: str

    def current(self, latitude: float, longitude: float) -> CurrentWeather:
        """Return current conditions for a coordinate. Raises ProviderError on failure."""
        ...

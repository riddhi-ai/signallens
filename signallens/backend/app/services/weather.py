"""Weather context lookup. Weather is contextual evidence, never proof of an incident."""

from __future__ import annotations

from datetime import datetime

from app.providers.base import WeatherProvider
from app.providers.errors import ProviderError
from app.schemas.weather import WeatherOut, WeatherSummary


def fetch_weather_context(
    provider: WeatherProvider,
    latitude: float,
    longitude: float,
    *,
    retrieved_at: datetime,
) -> WeatherOut:
    try:
        current = provider.current(latitude, longitude)
    except ProviderError as exc:
        return WeatherOut(
            status="unavailable",
            provider=provider.name,
            latitude=latitude,
            longitude=longitude,
            retrieved_at=retrieved_at,
            message=str(exc),
        )
    return WeatherOut(
        status="success",
        provider=provider.name,
        latitude=latitude,
        longitude=longitude,
        observed_at=current.observed_at,
        retrieved_at=retrieved_at,
        summary=WeatherSummary(
            temperature_c=current.temperature_c,
            precipitation_mm=current.precipitation_mm,
            weather_code=current.weather_code,
            wind_speed_kmh=current.wind_speed_kmh,
        ),
    )

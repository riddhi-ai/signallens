from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

WEATHER_NOTE = (
    "Current conditions from Open-Meteo. This is context only. "
    "Weather does not confirm that an incident happened."
)


class WeatherSummary(BaseModel):
    temperature_c: float | None = None
    precipitation_mm: float | None = None
    weather_code: int | None = None
    wind_speed_kmh: float | None = None


class WeatherOut(BaseModel):
    status: Literal["success", "unavailable"]
    provider: str = "open-meteo"
    latitude: float
    longitude: float
    observed_at: str | None = None  # provider timestamp for the "current" block, UTC
    retrieved_at: datetime | None = None  # when SignalLens made the call, UTC
    summary: WeatherSummary | None = None
    message: str | None = None
    note: str = Field(default=WEATHER_NOTE)

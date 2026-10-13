from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from app.clock import utc_now
from app.schemas.weather import WeatherOut
from app.services.weather import fetch_weather_context

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherOut)
def get_weather(
    request: Request,
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> WeatherOut:
    """Live current conditions for a coordinate. Not stored. Returns 503 when the provider fails."""
    provider = request.app.state.weather_provider
    result = fetch_weather_context(provider, latitude, longitude, retrieved_at=utc_now())
    if result.status == "unavailable":
        raise HTTPException(status_code=503, detail=result.message or "Weather is unavailable.")
    return result

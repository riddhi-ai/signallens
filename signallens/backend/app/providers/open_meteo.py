"""Open-Meteo adapter for current conditions. No API key is needed for non-commercial use."""

from __future__ import annotations

import httpx

from app.providers.errors import ProviderFailed, ProviderUnavailable
from app.providers.parsers import CurrentWeather, MalformedProviderResponse, parse_open_meteo_current

CURRENT_FIELDS = "temperature_2m,precipitation,weather_code,wind_speed_10m"


class OpenMeteoProvider:
    name = "open-meteo"

    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url
        self._timeout = timeout_seconds

    def current(self, latitude: float, longitude: float) -> CurrentWeather:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": CURRENT_FIELDS,
            "timezone": "UTC",
        }
        try:
            response = httpx.get(self._base_url, params=params, timeout=self._timeout)
        except httpx.TimeoutException as exc:
            raise ProviderUnavailable("The Open-Meteo request timed out.") from exc
        except httpx.TransportError as exc:
            raise ProviderUnavailable("Could not reach Open-Meteo.") from exc

        if response.status_code == 429 or response.status_code >= 500:
            raise ProviderUnavailable(f"Open-Meteo returned HTTP {response.status_code}.")
        if response.status_code >= 400:
            raise ProviderFailed(f"Open-Meteo rejected the request (HTTP {response.status_code}).")
        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderFailed("Open-Meteo returned a response that is not JSON.") from exc
        try:
            return parse_open_meteo_current(payload)
        except MalformedProviderResponse as exc:
            raise ProviderFailed(f"Unexpected Open-Meteo response: {exc}.") from exc

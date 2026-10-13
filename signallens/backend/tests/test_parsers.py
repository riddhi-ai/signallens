from __future__ import annotations

import pytest

from app.providers.parsers import (
    MalformedProviderResponse,
    parse_open_meteo_current,
    parse_zero_shot,
)

LABELS = {"flooding or waterlogging on a road", "traffic disruption or congestion"}


def test_zero_shot_returns_highest_scoring_label() -> None:
    payload = {
        "labels": ["traffic disruption or congestion", "flooding or waterlogging on a road"],
        "scores": [0.12, 0.81],
    }
    result = parse_zero_shot(payload, LABELS)
    assert result.label == "flooding or waterlogging on a road"
    assert result.score == pytest.approx(0.81)


def test_zero_shot_rejects_unknown_label() -> None:
    payload = {"labels": ["something else"], "scores": [0.9]}
    with pytest.raises(MalformedProviderResponse):
        parse_zero_shot(payload, LABELS)


def test_zero_shot_rejects_mismatched_lengths_and_bad_scores() -> None:
    with pytest.raises(MalformedProviderResponse):
        parse_zero_shot({"labels": ["traffic disruption or congestion"], "scores": []}, LABELS)
    with pytest.raises(MalformedProviderResponse):
        parse_zero_shot({"labels": ["traffic disruption or congestion"], "scores": [1.7]}, LABELS)
    with pytest.raises(MalformedProviderResponse):
        parse_zero_shot({"labels": ["traffic disruption or congestion"], "scores": [True]}, LABELS)


def test_zero_shot_rejects_non_object_payload() -> None:
    with pytest.raises(MalformedProviderResponse):
        parse_zero_shot(["not", "an", "object"], LABELS)


def test_open_meteo_current_block_is_parsed() -> None:
    payload = {
        "latitude": 12.96,
        "current": {
            "time": "2026-10-13T07:00",
            "temperature_2m": 24.5,
            "precipitation": 0.0,
            "weather_code": 3,
            "wind_speed_10m": 11.2,
        },
    }
    current = parse_open_meteo_current(payload)
    assert current.observed_at == "2026-10-13T07:00"
    assert current.temperature_c == 24.5
    assert current.weather_code == 3
    assert current.precipitation_mm == 0.0


def test_open_meteo_missing_current_block_is_malformed() -> None:
    with pytest.raises(MalformedProviderResponse):
        parse_open_meteo_current({"latitude": 1.0})


def test_open_meteo_non_integer_weather_code_is_malformed() -> None:
    payload = {"current": {"time": "2026-10-13T07:00", "weather_code": 3.5}}
    with pytest.raises(MalformedProviderResponse):
        parse_open_meteo_current(payload)

from __future__ import annotations

from datetime import timedelta

from app.schemas.prediction import PredictionOut
from app.schemas.weather import WeatherOut, WeatherSummary
from app.services.evidence import build_evidence
from tests.fakes import T0


def _prediction(label: str | None, status: str = "success") -> PredictionOut:
    return PredictionOut(
        id="p1",
        task="text_classification",
        model_id="fake/zero-shot",
        label=label,
        score=0.9 if status == "success" else None,
        status=status,  # type: ignore[arg-type]
        message=None,
        created_at=T0,
    )


def _weather(precipitation: float, code: int) -> WeatherOut:
    return WeatherOut(
        status="success",
        latitude=12.9,
        longitude=77.6,
        observed_at="2026-10-13T07:00",
        retrieved_at=T0,
        summary=WeatherSummary(temperature_c=20.0, precipitation_mm=precipitation, weather_code=code, wind_speed_kmh=5.0),
    )


def _check(evidence, name: str):
    return next(check for check in evidence.checks if check.name == name)


def test_reports_older_than_threshold_are_stale() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[],
        weather=None,
        now=T0 + timedelta(hours=7),
        stale_after_hours=6,
    )
    assert evidence.freshness == "stale"
    assert "stale" in evidence.indicators
    assert evidence.age_minutes == 420


def test_fresh_community_report_is_flagged_unverified_source() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[],
        weather=None,
        now=T0 + timedelta(minutes=10),
        stale_after_hours=6,
    )
    assert evidence.freshness == "recent"
    assert "source_unverified" in evidence.indicators
    assert "no_model_result" in evidence.indicators


def test_rain_context_is_consistent_but_explicitly_not_proof() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[_prediction("flooding")],
        weather=_weather(precipitation=2.4, code=63),
        now=T0,
        stale_after_hours=6,
    )
    check = _check(evidence, "weather_context")
    assert check.result == "consistent"
    assert "does not confirm or rule out an incident" in check.detail
    assert "weather_context_consistent" in evidence.indicators


def test_dry_weather_does_not_support_a_flooding_prediction() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[_prediction("flooding")],
        weather=_weather(precipitation=0.0, code=3),
        now=T0,
        stale_after_hours=6,
    )
    assert _check(evidence, "weather_context").result == "not_consistent"


def test_weather_is_not_used_for_unrelated_categories() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[_prediction("traffic")],
        weather=_weather(precipitation=2.4, code=63),
        now=T0,
        stale_after_hours=6,
    )
    assert _check(evidence, "weather_context").result == "not_assessed"


def test_disagreeing_model_labels_are_flagged() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[_prediction("flooding"), _prediction("traffic")],
        weather=None,
        now=T0,
        stale_after_hours=6,
    )
    assert "model_disagreement" in evidence.indicators
    assert _check(evidence, "model_agreement").result == "disagreement"


def test_cross_modal_check_is_honestly_not_assessed() -> None:
    evidence = build_evidence(
        created_at=T0,
        source_type="community",
        predictions=[],
        weather=None,
        now=T0,
        stale_after_hours=6,
    )
    assert _check(evidence, "cross_modal").result == "not_assessed"

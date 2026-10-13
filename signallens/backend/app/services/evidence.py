"""Transparent evidence checks.

Deliberately NOT a combined risk or probability score. Each check is reported on its own, so a
reviewer can see what was compared and what was not. Weather is context only: it can be
consistent with a category, but it never proves that an incident happened.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from app.schemas.evidence import EvidenceCheck, EvidenceOut
from app.schemas.prediction import PredictionOut
from app.schemas.weather import WeatherOut

# WMO weather codes that indicate rain, drizzle, showers or thunderstorms.
RAIN_WEATHER_CODES = frozenset({51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99})
RAIN_RELATED_CATEGORIES = frozenset({"flooding", "severe_weather"})


def build_evidence(
    *,
    created_at: datetime,
    source_type: str,
    predictions: Sequence[PredictionOut],
    weather: WeatherOut | None,
    now: datetime,
    stale_after_hours: float,
) -> EvidenceOut:
    age_minutes = max(0, int((now - created_at).total_seconds() // 60))
    freshness = "stale" if age_minutes > stale_after_hours * 60 else "recent"

    indicators: list[str] = [freshness]
    checks: list[EvidenceCheck] = [
        EvidenceCheck(
            name="freshness",
            result=freshness,
            detail=f"Submitted {age_minutes} min ago (stale after {stale_after_hours:g} h).",
        ),
        EvidenceCheck(name="source", result=source_type, detail=_source_detail(source_type)),
    ]
    if source_type != "official":
        indicators.append("source_unverified")

    text_successes = [
        prediction
        for prediction in predictions
        if prediction.task == "text_classification" and prediction.status == "success" and prediction.label
    ]
    labels = {prediction.label for prediction in text_successes}
    if not text_successes:
        indicators.append("no_model_result")
        checks.append(
            EvidenceCheck(name="model_agreement", result="not_assessed", detail="No successful model prediction is available.")
        )
    elif len(labels) > 1:
        indicators.append("model_disagreement")
        checks.append(
            EvidenceCheck(
                name="model_agreement",
                result="disagreement",
                detail=f"Models returned different labels ({', '.join(sorted(str(label) for label in labels))}). Flagged for review.",
            )
        )
    else:
        checks.append(
            EvidenceCheck(name="model_agreement", result="single_model", detail="Only one text model is configured, so there is nothing to compare.")
        )

    category = text_successes[-1].label if text_successes else None
    checks.append(_weather_check(category, weather, indicators))
    checks.append(EvidenceCheck(name="cross_modal", result="not_assessed", detail="Image classification is not enabled in this MVP."))

    return EvidenceOut(age_minutes=age_minutes, freshness=freshness, indicators=indicators, checks=checks)


def _source_detail(source_type: str) -> str:
    if source_type == "official":
        return "Official source reference recorded."
    if source_type == "demo":
        return "Sample data for demonstration. Not a real event."
    return "Submitted by a community contributor. Not independently verified."


def _weather_check(category: str | None, weather: WeatherOut | None, indicators: list[str]) -> EvidenceCheck:
    if weather is None:
        return EvidenceCheck(name="weather_context", result="not_retrieved", detail="Weather has not been retrieved for this report.")
    if weather.status != "success" or weather.summary is None:
        return EvidenceCheck(
            name="weather_context",
            result="unavailable",
            detail="Weather context is unavailable, so it was not compared with the prediction.",
        )
    if category not in RAIN_RELATED_CATEGORIES:
        return EvidenceCheck(name="weather_context", result="not_assessed", detail="Weather is not used to judge this category.")

    precipitation = weather.summary.precipitation_mm or 0.0
    code = weather.summary.weather_code
    rain_present = precipitation > 0 or (code is not None and code in RAIN_WEATHER_CODES)
    detail = (
        f"At retrieval: precipitation {precipitation:.1f} mm, weather code {code if code is not None else 'n/a'}. "
        "Context only: this does not confirm or rule out an incident."
    )
    if rain_present:
        indicators.append("weather_context_consistent")
        return EvidenceCheck(name="weather_context", result="consistent", detail=detail)
    return EvidenceCheck(name="weather_context", result="not_consistent", detail=detail)

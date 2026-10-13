"""Service-level tests for the report workflow, using fake providers and a SQLite file in a temp dir."""

from __future__ import annotations

import tempfile
from datetime import timedelta
from pathlib import Path

import pytest

from app.providers.errors import ProviderFailed, ProviderUnavailable
from app.repositories.reports import SqliteReportRepository
from app.schemas.report import ReportCreate, ReviewStatus, StatusUpdate
from app.services.categories import CATEGORY_CANDIDATES
from app.services.reports import ReportNotFound, ReportService
from app.services.status import InvalidTransition
from tests.fakes import FakeTextClassifier, FakeWeatherProvider, MutableClock, dry_weather, rainy_weather

FLOOD = CATEGORY_CANDIDATES["flooding"]
SUBMIT = ReportCreate(
    description="Water is collecting near the underpass on the main road.",
    latitude=12.9716,
    longitude=77.5946,
    location_label="Bengaluru, India",
)


def _service(tmp: Path, classifier, weather, clock: MutableClock | None = None) -> tuple[ReportService, MutableClock]:
    clock = clock or MutableClock()
    repo = SqliteReportRepository(tmp / "test.db")
    service = ReportService(
        repository=repo,
        text_classifier=classifier,
        weather_provider=weather,
        stale_after_hours=6,
        clock=clock,
    )
    return service, clock


def test_new_report_is_unverified_even_with_a_very_high_model_score() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, _ = _service(Path(tmp), FakeTextClassifier(label=FLOOD, score=0.99), FakeWeatherProvider(dry_weather()))
        detail = service.create_report(SUBMIT)
        assert detail.status == ReviewStatus.unverified
        assert detail.category == "flooding"
        assert detail.predictions[0].is_verified is False
        assert detail.predictions[0].model_id == "fake/zero-shot"


def test_classifier_outage_is_shown_explicitly_and_no_label_is_invented() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        classifier = FakeTextClassifier(error=ProviderUnavailable("HF_TOKEN is not set on the server"))
        service, _ = _service(Path(tmp), classifier, FakeWeatherProvider(dry_weather()))
        detail = service.create_report(SUBMIT)
        prediction = detail.predictions[0]
        assert prediction.status == "unavailable"
        assert prediction.label is None and prediction.score is None
        assert detail.category is None
        assert "no_model_result" in detail.evidence.indicators


def test_provider_rejection_is_recorded_as_error_not_unavailable() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        classifier = FakeTextClassifier(error=ProviderFailed("Hugging Face rejected the token."))
        service, _ = _service(Path(tmp), classifier, FakeWeatherProvider(dry_weather()))
        assert service.create_report(SUBMIT).predictions[0].status == "error"


def test_weather_failure_does_not_block_the_report() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        weather = FakeWeatherProvider(error=ProviderUnavailable("Could not reach Open-Meteo."))
        service, _ = _service(Path(tmp), FakeTextClassifier(label=FLOOD), weather)
        detail = service.create_report(SUBMIT)
        assert detail.weather is not None and detail.weather.status == "unavailable"
        assert detail.predictions[0].status == "success"
        assert _check(detail, "weather_context").result == "unavailable"


def test_rain_supports_flooding_context_but_status_stays_unverified() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, _ = _service(Path(tmp), FakeTextClassifier(label=FLOOD), FakeWeatherProvider(rainy_weather()))
        detail = service.create_report(SUBMIT)
        assert _check(detail, "weather_context").result == "consistent"
        assert detail.status == ReviewStatus.unverified


def test_retry_classification_stores_a_new_prediction_row() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        classifier = FakeTextClassifier(error=ProviderUnavailable("timeout"))
        service, _ = _service(Path(tmp), classifier, FakeWeatherProvider(dry_weather()))
        first = service.create_report(SUBMIT)
        classifier._error = None
        classifier._label = FLOOD
        retried = service.classify(first.id)
        assert [p.status for p in retried.predictions] == ["unavailable", "success"]
        assert retried.category == "flooding"


def test_status_change_is_recorded_with_note_and_time() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, clock = _service(Path(tmp), FakeTextClassifier(label=FLOOD), FakeWeatherProvider(dry_weather()))
        created = service.create_report(SUBMIT)
        clock.advance(minutes=5)
        updated = service.update_status(created.id, StatusUpdate(status=ReviewStatus.under_review, note="Checking with the council"))
        assert updated.status == ReviewStatus.under_review
        assert updated.review_note == "Checking with the council"
        assert updated.updated_at > updated.created_at


def test_invalid_transition_is_rejected_and_status_is_unchanged() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, _ = _service(Path(tmp), FakeTextClassifier(label=FLOOD), FakeWeatherProvider(dry_weather()))
        created = service.create_report(SUBMIT)
        with pytest.raises(InvalidTransition):
            service.update_status(created.id, StatusUpdate(status=ReviewStatus.resolved))
        assert service.get_report(created.id).status == ReviewStatus.unverified


def test_reports_turn_stale_as_the_clock_advances() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, clock = _service(Path(tmp), FakeTextClassifier(label=FLOOD), FakeWeatherProvider(dry_weather()))
        created = service.create_report(SUBMIT)
        assert created.freshness == "recent"
        clock.advance(hours=7)
        assert service.get_report(created.id).freshness == "stale"


def test_unknown_report_raises_not_found() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, _ = _service(Path(tmp), FakeTextClassifier(label=FLOOD), FakeWeatherProvider(dry_weather()))
        with pytest.raises(ReportNotFound):
            service.get_report("does-not-exist")


def test_list_returns_newest_first() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        service, clock = _service(Path(tmp), FakeTextClassifier(label=FLOOD), FakeWeatherProvider(dry_weather()))
        first = service.create_report(SUBMIT)
        clock.advance(minutes=1)
        second = service.create_report(SUBMIT.model_copy(update={"location_label": "Mumbai, India"}))
        assert [item.id for item in service.list_reports()] == [second.id, first.id]


def test_weather_snapshot_can_be_refreshed_after_a_failure() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        weather = FakeWeatherProvider(error=ProviderUnavailable("timeout"))
        service, clock = _service(Path(tmp), FakeTextClassifier(label=FLOOD), weather)
        created = service.create_report(SUBMIT)
        assert created.weather is not None and created.weather.status == "unavailable"
        weather._error = None
        weather._current = rainy_weather()
        clock.advance(minutes=2)
        refreshed = service.refresh_weather(created.id)
        assert refreshed.weather is not None and refreshed.weather.status == "success"
        assert refreshed.weather.summary is not None and refreshed.weather.summary.precipitation_mm == 2.4


def _check(detail, name: str):
    return next(check for check in detail.evidence.checks if check.name == name)

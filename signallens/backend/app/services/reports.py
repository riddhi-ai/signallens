"""Report workflow: submit → classify → weather → evidence, plus review and retry actions.

Every step is independent. A failed model call or weather call is stored and shown as such,
and the report itself is still returned.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.clock import iso, parse_iso, utc_now
from app.providers.base import TextClassifier, WeatherProvider
from app.repositories.reports import SqliteReportRepository
from app.schemas.evidence import EvidenceOut
from app.schemas.prediction import PredictionOut
from app.schemas.report import ReportCreate, ReportDetail, ReportOut, ReviewStatus, StatusUpdate
from app.schemas.weather import WeatherOut, WeatherSummary
from app.services.classification import run_text_classification
from app.services.evidence import build_evidence
from app.services.status import validate_transition
from app.services.weather import fetch_weather_context


class ReportNotFound(LookupError):
    def __init__(self, report_id: str) -> None:
        super().__init__(f"Report '{report_id}' was not found.")


def weather_from_row(row: dict[str, Any]) -> WeatherOut:
    summary_json = row.get("summary_json")
    return WeatherOut(
        status=row["status"],
        provider=row["provider"],
        latitude=row["latitude"],
        longitude=row["longitude"],
        observed_at=row["observed_at"],
        retrieved_at=parse_iso(row["retrieved_at"]),
        summary=WeatherSummary(**json.loads(summary_json)) if summary_json else None,
        message=row["message"],
    )


class ReportService:
    def __init__(
        self,
        *,
        repository: SqliteReportRepository,
        text_classifier: TextClassifier,
        weather_provider: WeatherProvider,
        stale_after_hours: float,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repo = repository
        self._text_classifier = text_classifier
        self._weather_provider = weather_provider
        self._stale_after_hours = stale_after_hours
        self._clock = clock

    # --- commands ------------------------------------------------------------

    def create_report(self, data: ReportCreate) -> ReportDetail:
        now = self._clock()
        report_id = str(uuid4())
        self._repo.insert_report(
            {
                "id": report_id,
                "description": data.description,
                "location_label": data.location_label,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "source_type": "community",
                "source_reference": None,
                "status": ReviewStatus.unverified.value,
                "review_note": None,
                "created_at": iso(now),
                "updated_at": iso(now),
            }
        )
        self._store_prediction(report_id, data.description)
        self._store_weather(report_id, data.latitude, data.longitude)
        return self.get_report(report_id)

    def classify(self, report_id: str) -> ReportDetail:
        row = self._require(report_id)
        self._store_prediction(report_id, row["description"])
        return self.get_report(report_id)

    def refresh_weather(self, report_id: str) -> ReportDetail:
        row = self._require(report_id)
        self._store_weather(report_id, row["latitude"], row["longitude"])
        return self.get_report(report_id)

    def update_status(self, report_id: str, update: StatusUpdate) -> ReportDetail:
        row = self._require(report_id)
        validate_transition(ReviewStatus(row["status"]), update.status)
        self._repo.update_status(report_id, update.status.value, update.note, iso(self._clock()))
        return self.get_report(report_id)

    # --- queries -------------------------------------------------------------

    def list_reports(self) -> list[ReportOut]:
        results: list[ReportOut] = []
        for row in self._repo.list_reports():
            predictions, _, evidence = self._load(row)
            results.append(ReportOut(**self._summary_fields(row, predictions, evidence)))
        return results

    def get_report(self, report_id: str) -> ReportDetail:
        row = self._require(report_id)
        predictions, weather, evidence = self._load(row)
        return ReportDetail(
            **self._summary_fields(row, predictions, evidence),
            predictions=predictions,
            weather=weather,
            evidence=evidence,
        )

    # --- internals -----------------------------------------------------------

    def _require(self, report_id: str) -> dict[str, Any]:
        row = self._repo.get_report(report_id)
        if row is None:
            raise ReportNotFound(report_id)
        return row

    def _store_prediction(self, report_id: str, description: str) -> None:
        now = self._clock()
        outcome = run_text_classification(self._text_classifier, description)
        self._repo.insert_prediction(
            {"id": str(uuid4()), "report_id": report_id, **outcome, "created_at": iso(now)}
        )

    def _store_weather(self, report_id: str, latitude: float, longitude: float) -> None:
        retrieved_at = self._clock()
        result = fetch_weather_context(self._weather_provider, latitude, longitude, retrieved_at=retrieved_at)
        self._repo.insert_weather_snapshot(
            {
                "id": str(uuid4()),
                "report_id": report_id,
                "provider": result.provider,
                "latitude": result.latitude,
                "longitude": result.longitude,
                "status": result.status,
                "observed_at": result.observed_at,
                "retrieved_at": iso(retrieved_at),
                "summary_json": result.summary.model_dump_json() if result.summary else None,
                "message": result.message,
            }
        )

    def _load(self, row: dict[str, Any]) -> tuple[list[PredictionOut], WeatherOut | None, EvidenceOut]:
        predictions = [PredictionOut.model_validate(item) for item in self._repo.list_predictions(row["id"])]
        snapshot = self._repo.latest_weather_snapshot(row["id"])
        weather = weather_from_row(snapshot) if snapshot else None
        evidence = build_evidence(
            created_at=parse_iso(row["created_at"]),
            source_type=row["source_type"],
            predictions=predictions,
            weather=weather,
            now=self._clock(),
            stale_after_hours=self._stale_after_hours,
        )
        return predictions, weather, evidence

    @staticmethod
    def _summary_fields(
        row: dict[str, Any], predictions: list[PredictionOut], evidence: EvidenceOut
    ) -> dict[str, Any]:
        latest = next(
            (p for p in reversed(predictions) if p.task == "text_classification" and p.status == "success"),
            None,
        )
        return {
            "id": row["id"],
            "description": row["description"],
            "location_label": row["location_label"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "source_type": row["source_type"],
            "source_reference": row["source_reference"],
            "status": ReviewStatus(row["status"]),
            "review_note": row["review_note"],
            "created_at": parse_iso(row["created_at"]),
            "updated_at": parse_iso(row["updated_at"]),
            "freshness": evidence.freshness,
            "category": latest.label if latest else None,
            "category_score": latest.score if latest else None,
        }

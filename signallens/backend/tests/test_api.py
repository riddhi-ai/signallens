"""HTTP-level tests. Skipped automatically when FastAPI or httpx is not installed."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from app.providers.huggingface import HuggingFaceZeroShotProvider  # noqa: E402
from app.services.categories import CATEGORY_CANDIDATES  # noqa: E402
from tests.fakes import FakeTextClassifier, FakeWeatherProvider, MutableClock, dry_weather  # noqa: E402

VALID = {
    "description": "Water is collecting near the underpass on the main road.",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "location_label": "Bengaluru, India",
}


def _client(tmp: str, classifier=None) -> TestClient:
    settings = Settings(database_path=Path(tmp) / "api.db", seed_demo_data=True, cors_origins=["http://localhost:5173"])
    app = create_app(
        settings,
        text_classifier=classifier or FakeTextClassifier(label=CATEGORY_CANDIDATES["flooding"]),
        weather_provider=FakeWeatherProvider(dry_weather()),
        clock=MutableClock(),
    )
    return TestClient(app)


def test_health_is_ok() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        assert _client(tmp).get("/health").json()["status"] == "ok"


def test_seeded_reports_are_listed_and_labelled_as_demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        items = _client(tmp).get("/api/reports").json()
        assert len(items) >= 1
        assert all(item["source_type"] == "demo" for item in items)
        assert all(item["status"] == "unverified" for item in items)


def test_submit_returns_201_unverified_with_prediction_and_weather() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        response = _client(tmp).post("/api/reports", json=VALID)
        assert response.status_code == 201
        body = response.json()
        assert body["status"] == "unverified"
        assert body["predictions"][0]["is_verified"] is False
        assert body["weather"]["status"] == "success"


def test_invalid_coordinates_and_empty_description_are_rejected() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        client = _client(tmp)
        assert client.post("/api/reports", json={**VALID, "latitude": 123}).status_code == 422
        assert client.post("/api/reports", json={**VALID, "description": "          "}).status_code == 422


def test_unknown_report_returns_404() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        assert _client(tmp).get("/api/reports/missing-id").status_code == 404


def test_invalid_status_transition_returns_409() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        client = _client(tmp)
        report_id = client.post("/api/reports", json=VALID).json()["id"]
        response = client.patch(f"/api/reports/{report_id}/status", json={"status": "resolved"})
        assert response.status_code == 409


def test_without_hf_token_the_api_says_so_and_returns_no_fabricated_label() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        classifier = HuggingFaceZeroShotProvider(token=None, model_id="facebook/bart-large-mnli", base_url="https://example.invalid", timeout_seconds=1)
        body = _client(tmp, classifier=classifier).post("/api/reports", json=VALID).json()
        assert body["predictions"][0]["status"] == "unavailable"
        assert body["predictions"][0]["label"] is None
        assert "HF_TOKEN" in body["predictions"][0]["message"]

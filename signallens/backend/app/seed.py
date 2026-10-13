"""Clearly labelled sample reports so the dashboard is never empty on first run.

Seeded reports carry NO model predictions. Predictions are only created by a real
classification call, so the UI never shows a fabricated AI result.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from app.clock import iso
from app.repositories.reports import SqliteReportRepository

DEMO_REPORTS: list[dict[str, object]] = [
    {
        "description": "Water is collecting near the underpass on the main road. Cars are slowing down.",
        "location_label": "Bengaluru, India",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "minutes_ago": 25,
    },
    {
        "description": "Large branch down across the footpath near the north gate. Pedestrians are walking around it.",
        "location_label": "Mumbai, India",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "minutes_ago": 140,
    },
    {
        "description": "Heavy rain since the afternoon, and the drains on the ring road look full.",
        "location_label": "London, United Kingdom",
        "latitude": 51.5072,
        "longitude": -0.1276,
        "minutes_ago": 260,
    },
]


def seed_demo_reports(repository: SqliteReportRepository, now: datetime) -> int:
    for item in DEMO_REPORTS:
        created = now - timedelta(minutes=int(item["minutes_ago"]))  # type: ignore[arg-type]
        repository.insert_report(
            {
                "id": str(uuid4()),
                "description": item["description"],
                "location_label": item["location_label"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "source_type": "demo",
                "source_reference": "sample-data",
                "status": "unverified",
                "review_note": "Sample report for demonstration. Not a real event.",
                "created_at": iso(created),
                "updated_at": iso(created),
            }
        )
    return len(DEMO_REPORTS)

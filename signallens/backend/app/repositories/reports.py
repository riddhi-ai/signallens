"""SQLite persistence for reports, model predictions and weather snapshots.

Uses the standard-library sqlite3 module (no ORM) to keep the MVP dependency-light.
The repository returns plain dicts. Services map them to API schemas.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (
    id               TEXT PRIMARY KEY,
    description      TEXT NOT NULL,
    location_label   TEXT NOT NULL,
    latitude         REAL NOT NULL,
    longitude        REAL NOT NULL,
    source_type      TEXT NOT NULL,
    source_reference TEXT,
    status           TEXT NOT NULL,
    review_note      TEXT,
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
    id         TEXT PRIMARY KEY,
    report_id  TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    task       TEXT NOT NULL,
    model_id   TEXT NOT NULL,
    label      TEXT,
    score      REAL,
    status     TEXT NOT NULL,
    message    TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_snapshots (
    id           TEXT PRIMARY KEY,
    report_id    TEXT NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    provider     TEXT NOT NULL,
    latitude     REAL NOT NULL,
    longitude    REAL NOT NULL,
    status       TEXT NOT NULL,
    observed_at  TEXT,
    retrieved_at TEXT NOT NULL,
    summary_json TEXT,
    message      TEXT
);

CREATE INDEX IF NOT EXISTS idx_reports_created ON reports(created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_report ON predictions(report_id, created_at);
CREATE INDEX IF NOT EXISTS idx_weather_report ON weather_snapshots(report_id, retrieved_at);
"""


class SqliteReportRepository:
    def __init__(self, database_path: Path) -> None:
        self._path = Path(database_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self._path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # --- reports -------------------------------------------------------------

    def count_reports(self) -> int:
        with self._connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0])

    def insert_report(self, row: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO reports (id, description, location_label, latitude, longitude,
                    source_type, source_reference, status, review_note, created_at, updated_at)
                VALUES (:id, :description, :location_label, :latitude, :longitude,
                    :source_type, :source_reference, :status, :review_note, :created_at, :updated_at)
                """,
                row,
            )

    def get_report(self, report_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
            return dict(row) if row else None

    def list_reports(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM reports ORDER BY created_at DESC, rowid DESC").fetchall()
            return [dict(row) for row in rows]

    def update_status(self, report_id: str, status: str, note: str | None, updated_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE reports SET status = ?, review_note = ?, updated_at = ? WHERE id = ?",
                (status, note, updated_at, report_id),
            )

    # --- predictions ---------------------------------------------------------

    def insert_prediction(self, row: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO predictions (id, report_id, task, model_id, label, score, status, message, created_at)
                VALUES (:id, :report_id, :task, :model_id, :label, :score, :status, :message, :created_at)
                """,
                row,
            )

    def list_predictions(self, report_id: str) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM predictions WHERE report_id = ? ORDER BY created_at ASC, rowid ASC",
                (report_id,),
            ).fetchall()
            return [dict(row) for row in rows]

    # --- weather -------------------------------------------------------------

    def insert_weather_snapshot(self, row: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO weather_snapshots (id, report_id, provider, latitude, longitude, status,
                    observed_at, retrieved_at, summary_json, message)
                VALUES (:id, :report_id, :provider, :latitude, :longitude, :status,
                    :observed_at, :retrieved_at, :summary_json, :message)
                """,
                row,
            )

    def latest_weather_snapshot(self, report_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM weather_snapshots WHERE report_id = ? ORDER BY retrieved_at DESC, rowid DESC LIMIT 1",
                (report_id,),
            ).fetchone()
            return dict(row) if row else None

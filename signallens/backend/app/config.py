"""Runtime configuration, read from environment variables (and backend/.env if present).

Secrets such as HF_TOKEN are read only on the server. They are never returned by an
API response and never shipped to the frontend bundle.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")  # no-op when the file does not exist

DEFAULT_HF_BASE_URL = "https://router.huggingface.co/hf-inference/models"
DEFAULT_OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _flag(value: str | None, default: bool) -> bool:
    if value is None or not value.strip():
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _csv(value: str | None, default: list[str]) -> list[str]:
    if value is None or not value.strip():
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _sqlite_path(database_url: str) -> Path:
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("DATABASE_URL must use the sqlite:/// scheme in the MVP.")
    path = Path(database_url[len(prefix):])
    return path if path.is_absolute() else BACKEND_DIR / path


@dataclass(frozen=True)
class Settings:
    app_env: str = "development"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173"])
    database_path: Path = BACKEND_DIR / "signallens.db"
    hf_token: str | None = None
    hf_text_model: str = "facebook/bart-large-mnli"
    hf_inference_base_url: str = DEFAULT_HF_BASE_URL
    open_meteo_base_url: str = DEFAULT_OPEN_METEO_URL
    http_timeout_seconds: float = 10.0
    stale_after_hours: float = 6.0
    seed_demo_data: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "development"),
            cors_origins=_csv(os.getenv("CORS_ORIGINS"), ["http://localhost:5173"]),
            database_path=_sqlite_path(os.getenv("DATABASE_URL", "sqlite:///./signallens.db")),
            hf_token=os.getenv("HF_TOKEN", "").strip() or None,
            hf_text_model=os.getenv("HF_TEXT_MODEL", "facebook/bart-large-mnli").strip(),
            hf_inference_base_url=os.getenv("HF_INFERENCE_BASE_URL", DEFAULT_HF_BASE_URL).strip(),
            open_meteo_base_url=os.getenv("OPEN_METEO_BASE_URL", DEFAULT_OPEN_METEO_URL).strip(),
            http_timeout_seconds=float(os.getenv("HTTP_TIMEOUT_SECONDS", "10")),
            stale_after_hours=float(os.getenv("STALE_AFTER_HOURS", "6")),
            seed_demo_data=_flag(os.getenv("SEED_DEMO_DATA"), True),
        )

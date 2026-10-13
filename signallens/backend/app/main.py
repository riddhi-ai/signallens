"""SignalLens API entry point.

Run locally with:   uvicorn app.main:app --reload
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health, reports, weather
from app.clock import utc_now
from app.config import Settings
from app.providers.base import TextClassifier, WeatherProvider
from app.providers.huggingface import HuggingFaceZeroShotProvider
from app.providers.open_meteo import OpenMeteoProvider
from app.repositories.reports import SqliteReportRepository
from app.seed import seed_demo_reports
from app.services.reports import ReportNotFound, ReportService
from app.services.status import InvalidTransition

DISCLAIMER = "Prototype, not an official alert system. Model outputs are predictions, not verified facts."


def create_app(
    settings: Settings | None = None,
    *,
    text_classifier: TextClassifier | None = None,
    weather_provider: WeatherProvider | None = None,
    clock: Callable[[], datetime] = utc_now,
) -> FastAPI:
    """Build the app. Tests inject fake providers and a fixed clock through the keyword arguments."""
    settings = settings or Settings.from_env()
    repository = SqliteReportRepository(settings.database_path)
    classifier = text_classifier or HuggingFaceZeroShotProvider(
        token=settings.hf_token,
        model_id=settings.hf_text_model,
        base_url=settings.hf_inference_base_url,
        timeout_seconds=settings.http_timeout_seconds,
    )
    weather_client = weather_provider or OpenMeteoProvider(
        base_url=settings.open_meteo_base_url,
        timeout_seconds=settings.http_timeout_seconds,
    )
    if settings.seed_demo_data and repository.count_reports() == 0:
        seed_demo_reports(repository, clock())

    service = ReportService(
        repository=repository,
        text_classifier=classifier,
        weather_provider=weather_client,
        stale_after_hours=settings.stale_after_hours,
        clock=clock,
    )

    app = FastAPI(title="SignalLens API", version="0.1.0", description=DISCLAIMER)
    app.state.settings = settings
    app.state.report_service = service
    app.state.weather_provider = weather_client

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
    )

    app.include_router(health.router)
    app.include_router(reports.router, prefix="/api")
    app.include_router(weather.router, prefix="/api")

    @app.exception_handler(ReportNotFound)
    async def _not_found(_: Request, exc: ReportNotFound) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidTransition)
    async def _invalid_transition(_: Request, exc: InvalidTransition) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    return app


app = create_app()
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.evidence import EvidenceOut
from app.schemas.prediction import PredictionOut
from app.schemas.weather import WeatherOut


class ReviewStatus(str, Enum):
    unverified = "unverified"
    under_review = "under_review"
    confirmed = "confirmed"
    disputed = "disputed"
    resolved = "resolved"


class ReportCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=10, max_length=500)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_label: str = Field(min_length=2, max_length=80)

    @field_validator("description", "location_label")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be blank")
        return cleaned


class StatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: ReviewStatus
    note: str | None = Field(default=None, max_length=200)


class ReportOut(BaseModel):
    """Report summary used in the feed. The predicted category is a prediction, not ground truth."""

    id: str
    description: str
    location_label: str
    latitude: float
    longitude: float
    source_type: Literal["community", "official", "demo"]
    source_reference: str | None
    status: ReviewStatus
    review_note: str | None
    created_at: datetime
    updated_at: datetime
    freshness: Literal["recent", "stale"]
    category: str | None
    category_score: float | None


class ReportDetail(ReportOut):
    predictions: list[PredictionOut]
    weather: WeatherOut | None
    evidence: EvidenceOut

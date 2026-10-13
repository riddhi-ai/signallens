from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class PredictionOut(BaseModel):
    """A model output. It is always a prediction and is never marked as verified."""

    id: str
    task: Literal["text_classification", "image_classification"]
    model_id: str
    label: str | None
    score: float | None
    status: Literal["success", "unavailable", "error"]
    message: str | None
    created_at: datetime
    is_verified: Literal[False] = False

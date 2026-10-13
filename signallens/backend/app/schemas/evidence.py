from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class EvidenceCheck(BaseModel):
    """One transparent check. Checks are listed separately; they are never merged into a score."""

    name: str
    result: str
    detail: str


class EvidenceOut(BaseModel):
    age_minutes: int
    freshness: Literal["recent", "stale"]
    indicators: list[str]
    checks: list[EvidenceCheck]

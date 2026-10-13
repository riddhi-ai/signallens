"""The disruption taxonomy.

Keys are stable internal identifiers stored in the database. Values are the natural-language
candidate labels passed to the zero-shot model. Change them carefully and version the change.
"""

from __future__ import annotations

from typing import Final

CATEGORY_CANDIDATES: Final[dict[str, str]] = {
    "flooding": "flooding or waterlogging on a road",
    "road_closure": "road closure or blocked road",
    "severe_weather": "severe weather such as storms or heavy rain",
    "infrastructure": "infrastructure damage such as a fallen tree or broken utility",
    "traffic": "traffic disruption or congestion",
    "unclear": "unrelated or unclear report",
}

_PHRASE_TO_KEY: Final[dict[str, str]] = {phrase: key for key, phrase in CATEGORY_CANDIDATES.items()}


def category_for_phrase(phrase: str) -> str | None:
    """Map a provider-echoed candidate label back to its stable key, or None if unknown."""
    return _PHRASE_TO_KEY.get(phrase)

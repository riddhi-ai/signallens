"""Text classification orchestration: provider result → stored prediction row.

On failure this returns an explicit `unavailable` or `error` row with no label. It never
substitutes a hard-coded prediction.
"""

from __future__ import annotations

from typing import Any

from app.providers.base import TextClassifier
from app.providers.errors import ProviderError
from app.services.categories import CATEGORY_CANDIDATES, category_for_phrase


def run_text_classification(classifier: TextClassifier, description: str) -> dict[str, Any]:
    base: dict[str, Any] = {"task": "text_classification", "model_id": classifier.model_id}
    try:
        result = classifier.classify(description, list(CATEGORY_CANDIDATES.values()))
    except ProviderError as exc:
        status = "unavailable" if exc.kind == "unavailable" else "error"
        return {**base, "label": None, "score": None, "status": status, "message": str(exc)}

    label = category_for_phrase(result.label)
    if label is None:
        return {
            **base,
            "label": None,
            "score": None,
            "status": "error",
            "message": "The model returned a label outside the SignalLens taxonomy.",
        }
    return {**base, "label": label, "score": round(result.score, 4), "status": "success", "message": None}

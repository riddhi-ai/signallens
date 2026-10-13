"""Hugging Face Inference Providers adapter for zero-shot text classification.

Runs server-side only, authenticated with HF_TOKEN. The request and response shapes follow
the zero-shot task on the hf-inference route. Provider support for a specific checkpoint can
change, so check it against the current Hugging Face docs before you rely on it.
"""

from __future__ import annotations

import time
from typing import Any

import httpx

from app.providers.errors import ProviderFailed, ProviderUnavailable
from app.providers.parsers import MalformedProviderResponse, ZeroShotResult, parse_zero_shot

MAX_ATTEMPTS = 2
RETRY_DELAY_SECONDS = 1.0


class HuggingFaceZeroShotProvider:
    name = "huggingface"

    def __init__(self, *, token: str | None, model_id: str, base_url: str, timeout_seconds: float) -> None:
        self._token = token
        self.model_id = model_id
        self._endpoint = f"{base_url.rstrip('/')}/{model_id}"
        self._timeout = timeout_seconds

    def classify(self, text: str, candidate_labels: list[str]) -> ZeroShotResult:
        if not self._token:
            raise ProviderUnavailable("HF_TOKEN is not set on the server, so no model prediction was made.")
        body = {
            "inputs": text,
            "parameters": {"candidate_labels": candidate_labels, "multi_label": False},
        }
        response = self._post_with_retry(body)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ProviderFailed("Hugging Face returned a response that is not JSON.") from exc
        try:
            return parse_zero_shot(payload, set(candidate_labels))
        except MalformedProviderResponse as exc:
            raise ProviderFailed(f"Unexpected Hugging Face response: {exc}.") from exc

    def _post_with_retry(self, body: dict[str, Any]) -> httpx.Response:
        headers = {"Authorization": f"Bearer {self._token}"}
        last_problem = "Hugging Face is unavailable."
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = httpx.post(self._endpoint, json=body, headers=headers, timeout=self._timeout)
            except httpx.TimeoutException:
                last_problem = "The Hugging Face request timed out."
            except httpx.TransportError:
                last_problem = "Could not reach Hugging Face."
            else:
                if response.status_code < 400:
                    return response
                if response.status_code in (401, 403):
                    raise ProviderFailed("Hugging Face rejected the token. Check HF_TOKEN and its permissions.")
                if response.status_code == 404:
                    raise ProviderFailed(f"Model '{self.model_id}' is not served by the configured provider.")
                last_problem = f"Hugging Face returned HTTP {response.status_code}."
                if response.status_code != 429 and response.status_code < 500:
                    raise ProviderFailed(last_problem)  # other 4xx: retrying will not help
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)
        raise ProviderUnavailable(last_problem)

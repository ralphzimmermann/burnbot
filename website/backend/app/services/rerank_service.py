from __future__ import annotations

import json
import time
from typing import List, Optional, Sequence

import httpx


class RerankService:
    """Minimal Chat-based reranking using OpenAI Chat Completions API.

    Sends the query and a compact list of candidate items and expects a JSON
    array of event IDs ordered from best to worst.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-3.5-turbo",
        max_retries: int = 4,
        initial_backoff_s: float = 1.0,
        request_timeout_s: float = 60.0,
    ) -> None:
        self._api_key = openai_api_key
        self._client: Optional[httpx.Client] = None
        self.model = model
        self.max_retries = max_retries
        self.initial_backoff_s = initial_backoff_s
        self.request_timeout_s = request_timeout_s

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            timeout = httpx.Timeout(self.request_timeout_s)
            self._client = httpx.Client(timeout=timeout)
        return self._client

    def rerank(
        self,
        query: str,
        candidates: Sequence[dict],
    ) -> List[str]:
        """Return a list of candidate IDs in the preferred order.

        Each candidate must be a dict with keys: id, title, type, camp, description.
        """
        system_msg = (
            "You are a helpful assistant that re-ranks event candidates. "
            "Given a user query and a list of events, produce a JSON array "
            "containing only the event ids sorted from best to worst match. "
            "Do not include explanations. Respond with JSON only."
        )

        # Keep prompt compact by truncating description
        compact = [
            {
                "id": c.get("id", ""),
                "title": c.get("title", ""),
                "type": c.get("type", ""),
                "camp": c.get("camp", ""),
                "description": (c.get("description", "") or "")[:240],
            }
            for c in candidates
        ]

        messages = [
            {"role": "system", "content": system_msg},
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "query": query,
                        "candidates": compact,
                    }
                ),
            },
        ]

        backoff = self.initial_backoff_s
        last_error: Optional[Exception] = None

        for _ in range(self.max_retries):
            try:
                resp = self._get_client().post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.0,
                    },
                )
                resp.raise_for_status()
                payload = resp.json()
                content = (
                    payload["choices"][0]["message"]["content"].strip()  # type: ignore[index]
                )
                # Expect a JSON array of ids
                order = json.loads(content)
                if isinstance(order, list) and all(isinstance(x, str) for x in order):
                    return order  # type: ignore[return-value]
                # If not a list of strings, fall through to retry once
                last_error = ValueError("Invalid re-rank response structure")
            except Exception as exc:
                last_error = exc
                time.sleep(backoff)
                backoff = min(backoff * 2, 30.0)

        if last_error is not None:
            raise last_error
        return []



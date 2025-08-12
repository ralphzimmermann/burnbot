from __future__ import annotations

import json
import time
from typing import List, Optional, Sequence, Tuple, Any

import httpx


class RerankService:
    """Minimal Chat-based reranking using OpenAI Chat Completions API.

    Sends the query and a compact list of candidate items and expects a JSON
    array of event IDs ordered from best to worst.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4.1-2025-04-14",
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
    ) -> Tuple[List[str], Optional[str]]:
        """Return a tuple: (ordered candidate IDs, optional 2-sentence rationale).

        Each candidate must be a dict with keys: id, title, type, camp, description.
        """
        system_msg = (
            "You are a helpful assistant that re-ranks event candidates. "
            "Given a user query and a list of events, respond with a compact JSON object with two fields: "
            '"order": an array of event ids sorted from best to worst match, and '
            '"rationale": a fun, playful, upbeat explanation (max 2 sentences) describing why the selected events match the query. '
            "Keep it concise and friendly; you may include at most one fitting emoji. "
            "Respond with JSON only, no extra commentary."
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
        print(f"Messages: {messages}")

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
                # Expect either an object { order: [...], rationale: "..." } or legacy array
                parsed: Any = json.loads(content)
                if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
                    return parsed, None
                if (
                    isinstance(parsed, dict)
                    and isinstance(parsed.get("order"), list)
                    and all(isinstance(x, str) for x in parsed["order"])  # type: ignore[index]
                ):
                    rationale_val = parsed.get("rationale")
                    rationale_str: Optional[str] = (
                        str(rationale_val).strip() if isinstance(rationale_val, str) else None
                    )
                    return parsed["order"], rationale_str  # type: ignore[return-value]
                # If not valid, fall through to retry once
                last_error = ValueError("Invalid re-rank response structure")
            except Exception as exc:
                last_error = exc
                time.sleep(backoff)
                backoff = min(backoff * 2, 30.0)

        if last_error is not None:
            raise last_error
        return [], None



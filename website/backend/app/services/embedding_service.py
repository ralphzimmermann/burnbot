from __future__ import annotations

import time
from typing import Iterable, List, Optional

import numpy as np
import httpx

from app.models.event import Event, EventTime


class EmbeddingService:
    """Generates embeddings for events using OpenAI embeddings API.

    This service is intentionally minimal for Phase 2. It provides
    synchronous methods suitable for a one-time generation script.
    """

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "text-embedding-3-large",
        max_retries: int = 5,
        initial_backoff_s: float = 1.0,
    ) -> None:
        self._api_key = openai_api_key
        self._client: Optional[httpx.Client] = None
        self.model = model
        self.max_retries = max_retries
        self.initial_backoff_s = initial_backoff_s

    def _get_client(self) -> httpx.Client:
        if self._client is None:
            timeout = httpx.Timeout(60.0)
            self._client = httpx.Client(timeout=timeout)
        return self._client

    def _build_event_text(self, event: Event) -> str:
        """Compose a concise text representation of an event for embedding."""
        # Only essential fields per YAGNI
        time_buckets = self._summarize_time_of_day(event.times)
        parts: List[str] = [
            (f"Title: {event.title}" if event.title else ""),
            f"Type: {event.type}",
            f"Camp: {event.camp}",
            event.description or "",
        ]
        if time_buckets:
            parts.append(f"Times: {', '.join(time_buckets)}")
        return ". ".join(p for p in parts if p).strip()

    @staticmethod
    def _summarize_time_of_day(times: List[EventTime]) -> List[str]:
        """Summarize event times into coarse buckets for embedding text.

        Buckets:
            - morning:   05:00–11:59
            - afternoon: 12:00–16:59
            - evening:   17:00–20:59
            - night:     21:00–04:59 (wraps midnight)
        """
        def to_minutes(hhmm: str) -> Optional[int]:
            try:
                parts = hhmm.split(":")
                if len(parts) != 2:
                    return None
                hour = int(parts[0])
                minute = int(parts[1])
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    return None
                return hour * 60 + minute
            except Exception:
                return None

        # Bucket ranges (start inclusive, end exclusive) in minutes
        MORNING = (5 * 60, 12 * 60)       # 300–720
        AFTERNOON = (12 * 60, 17 * 60)    # 720–1020
        EVENING = (17 * 60, 21 * 60)      # 1020–1260
        NIGHT_1 = (21 * 60, 24 * 60)      # 1260–1440
        NIGHT_2 = (0, 5 * 60)             # 0–300

        def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
            return a_start < b_end and a_end > b_start

        found = set()
        for t in times:
            start = to_minutes(t.start_time)
            end = to_minutes(t.end_time)
            if start is None or end is None:
                continue

            # Normalize intervals; handle wrap over midnight
            segments: List[tuple[int, int]]
            if end >= start:
                segments = [(start, end)]
            else:
                segments = [(start, 24 * 60), (0, end)]

            for seg_start, seg_end in segments:
                if overlaps(seg_start, seg_end, *MORNING):
                    found.add("morning")
                if overlaps(seg_start, seg_end, *AFTERNOON):
                    found.add("afternoon")
                if overlaps(seg_start, seg_end, *EVENING):
                    found.add("evening")
                if overlaps(seg_start, seg_end, *NIGHT_1) or overlaps(seg_start, seg_end, *NIGHT_2):
                    found.add("night")

        bucket_order = ["morning", "afternoon", "evening", "night"]
        return [b for b in bucket_order if b in found]

    def generate_event_embedding(self, event: Event) -> List[float]:
        """Generate an embedding vector for a single event.

        Retries on transient errors with exponential backoff.
        """
        text = self._build_event_text(event)
        return self.generate_text_embedding(text)

    def generate_text_embedding(self, text: str) -> List[float]:
        """Generate an embedding for arbitrary text using OpenAI API with retries."""
        backoff = self.initial_backoff_s
        last_error: Optional[Exception] = None

        for _ in range(self.max_retries):
            try:
                resp = self._get_client().post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": text,
                    },
                )
                resp.raise_for_status()
                payload = resp.json()
                return payload["data"][0]["embedding"]  # type: ignore[no-any-return]
            except Exception as exc:  # Broad by design to keep deps minimal
                last_error = exc
                time.sleep(backoff)
                backoff = min(backoff * 2, 30.0)

        # If all retries failed, re-raise last error
        assert last_error is not None
        raise last_error

    def generate_all_embeddings(
        self,
        events: Iterable[Event],
        progress_interval: int = 100,
        dtype: np.dtype = np.float32,
    ) -> np.ndarray:
        """Generate embeddings for all events.

        Args:
            events: Iterable of Event models
            progress_interval: Print progress every N events
            dtype: dtype for the resulting numpy array

        Returns:
            np.ndarray of shape (num_events, embedding_dim)
        """
        embeddings: List[List[float]] = []
        for index, event in enumerate(events, start=1):
            vector = self.generate_event_embedding(event)
            embeddings.append(vector)
            if progress_interval and index % progress_interval == 0:
                print(f"Processed {index} events...")

        # Infer dimension from first embedding
        if not embeddings:
            return np.empty((0, 0), dtype=dtype)

        arr = np.asarray(embeddings, dtype=dtype)
        return arr



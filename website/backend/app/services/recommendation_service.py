from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Tuple, Set
from datetime import datetime
import re

import faiss
import numpy as np
from dotenv import load_dotenv

from app.models.event import Event
from app.services.embedding_service import EmbeddingService
from app.services.rerank_service import RerankService


class RecommendationService:
    """Loads events and embeddings, builds a FAISS index, and serves queries."""

    def __init__(self, data_dir: Path | None = None, openai_api_key: str | None = None) -> None:
        base = Path(__file__).resolve().parents[2]  # website/backend/
        self.data_dir = data_dir or (base / "data")
        self.events: List[Event] = []
        self.embeddings: np.ndarray | None = None
        self.index: faiss.Index | None = None
        # Load env if not already loaded and pick up API key
        load_dotenv()
        api_key = openai_api_key if openai_api_key is not None else os.environ.get("OPENAI_API_KEY")
        self.embedding_service = EmbeddingService(openai_api_key=api_key)
        self.rerank_service = RerankService(openai_api_key=api_key)
        self.rerank_enabled = os.environ.get("ENABLE_RERANK", "false").lower() in {"1", "true", "yes"}
        self.rerank_top_n = int(os.environ.get("RERANK_TOP_N", "50"))
        self._load_data()

    def _load_data(self) -> None:
        events_path = self.data_dir / "events.json"
        embeddings_path = self.data_dir / "embeddings.npy"

        with events_path.open("r", encoding="utf-8") as f:
            items = json.load(f)
            self.events = [Event.model_validate(item) for item in items]

        self.embeddings = np.load(str(embeddings_path))

        # Normalize embeddings for cosine similarity (L2 normalized vectors)
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = self.embeddings / norms

        dim = normalized.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(normalized.astype(np.float32))

    def find_similar_events(self, query_embedding: np.ndarray, k: int = 20) -> List[Tuple[int, float]]:
        """Return list of (event_index, score) sorted by similarity."""
        assert self.index is not None and self.embeddings is not None

        q = query_embedding.astype(np.float32)
        # Normalize query for cosine similarity
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            q = q
        else:
            q = q / q_norm
        q = q.reshape(1, -1)

        scores, indices = self.index.search(q, k)
        result: List[Tuple[int, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            result.append((int(idx), float(score)))
        return result

    def get_recommendations(self, query: str, max_results: int = 5) -> Tuple[List[Event], Optional[str]]:
        if not query or not query.strip():
            return [], None

        vector = self.embedding_service.generate_text_embedding(query)
        query_vec = np.asarray(vector, dtype=np.float32)
        # Fetch more candidates for potential reranking
        initial_k = max(self.rerank_top_n if self.rerank_enabled else max_results, max_results)
        matches = self.find_similar_events(query_vec, k=initial_k)
        print(f"Matches: {len(matches)}")
        # Map matches to events, dedup by id preserving order
        seen: set[str] = set()
        candidates: List[Event] = []
        for idx, _score in matches:
            ev = self.events[idx]
            if ev.id not in seen:
                candidates.append(ev)
                seen.add(ev.id)
                print(f"Added: {ev}")
            if len(candidates) >= initial_k:
                break

        # Parse temporal filters (weekday, time-of-day) from query and filter candidates
        weekday_indexes, time_buckets = self._parse_temporal_filters(query)

        filtered: List[Event] = candidates
        if weekday_indexes or time_buckets:
            filtered = [e for e in candidates if self._event_matches_filters(e, weekday_indexes, time_buckets)]
            # Progressive fallback if over-constrained
            if not filtered and weekday_indexes and time_buckets:
                only_weekday = [e for e in candidates if self._event_matches_filters(e, weekday_indexes, None)]
                filtered = only_weekday or [e for e in candidates if self._event_matches_filters(e, None, time_buckets)]

        working_set = filtered or candidates

        if self.rerank_enabled and working_set:
            try:
                order, rationale_text = self.rerank_service.rerank(
                    query,
                    [
                        {
                            "id": e.id,
                            "title": e.title,
                            "type": e.type,
                            "camp": e.camp,
                            "description": e.description,
                        }
                        for e in working_set
                    ],
                )
                id_to_event = {e.id: e for e in working_set}
                reranked = [id_to_event[i] for i in order if i in id_to_event]
                return reranked[: max_results], rationale_text
            except Exception:
                # On failure, fall back to vector order
                return working_set[: max_results], None

        return working_set[: max_results], None

    # --- Internal helpers for temporal parsing and filtering ---
    @staticmethod
    def _parse_temporal_filters(query: str) -> Tuple[Optional[Set[int]], Optional[Set[str]]]:
        """Extract weekday indexes and time-of-day buckets from a free-text query.

        Returns:
            (weekday_indexes, time_buckets) where weekday_indexes are Monday=0..Sunday=6
            and time_buckets are in {"morning","afternoon","evening","night"}.
        """
        q = query.lower()
        # Weekday detection with aliases
        weekday_aliases = {
            "monday": 0, "mon": 0,
            "tuesday": 1, "tue": 1, "tues": 1,
            "wednesday": 2, "wed": 2,
            "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
            "friday": 4, "fri": 4,
            "saturday": 5, "sat": 5,
            "sunday": 6, "sun": 6,
        }
        weekday_indexes: Set[int] = set()
        for token, idx in weekday_aliases.items():
            if re.search(r"\b" + re.escape(token) + r"\b", q):
                weekday_indexes.add(idx)

        # Time-of-day buckets with synonyms
        bucket_aliases = {
            "morning": "morning",
            "afternoon": "afternoon",
            "evening": "evening",
            "night": "night",
            "late night": "night",
            "latenight": "night",
            "tonight": "night",  # heuristic
        }
        time_buckets: Set[str] = set()
        # Longer phrases first to avoid partial matches
        for phrase in sorted(bucket_aliases.keys(), key=len, reverse=True):
            if re.search(r"\b" + re.escape(phrase) + r"\b", q):
                time_buckets.add(bucket_aliases[phrase])

        return (weekday_indexes or None), (time_buckets or None)

    @staticmethod
    def _event_matches_filters(event: Event, weekday_indexes: Optional[Set[int]], time_buckets: Optional[Set[str]]) -> bool:
        """Return True if the event matches all provided filters.

        - If weekday_indexes provided, at least one occurrence must be on one of those weekdays.
        - If time_buckets provided, at least one occurrence must overlap one of those buckets.
        If both provided, a single occurrence must satisfy both (same occurrence).
        """
        def to_minutes(hhmm: str) -> Optional[int]:
            try:
                hh, mm = hhmm.split(":")
                h = int(hh); m = int(mm)
                if 0 <= h <= 23 and 0 <= m <= 59:
                    return h * 60 + m
                return None
            except Exception:
                return None

        # Bucket ranges (start inclusive, end exclusive)
        MORNING = (5 * 60, 12 * 60)
        AFTERNOON = (12 * 60, 17 * 60)
        EVENING = (17 * 60, 21 * 60)
        NIGHT_1 = (21 * 60, 24 * 60)
        NIGHT_2 = (0, 5 * 60)

        def overlaps(a_start: int, a_end: int, b_start: int, b_end: int) -> bool:
            return a_start < b_end and a_end > b_start

        def matches_bucket(seg_start: int, seg_end: int, bucket: str) -> bool:
            if bucket == "morning":
                return overlaps(seg_start, seg_end, *MORNING)
            if bucket == "afternoon":
                return overlaps(seg_start, seg_end, *AFTERNOON)
            if bucket == "evening":
                return overlaps(seg_start, seg_end, *EVENING)
            if bucket == "night":
                return overlaps(seg_start, seg_end, *NIGHT_1) or overlaps(seg_start, seg_end, *NIGHT_2)
            return False

        for t in event.times:
            # Parse weekday
            weekday_ok = True
            if weekday_indexes is not None:
                try:
                    dt = datetime.strptime(t.date, "%m/%d/%Y")
                    weekday_ok = (dt.weekday() in weekday_indexes)
                except Exception:
                    weekday_ok = False

            if not weekday_ok:
                continue

            # Parse time and evaluate buckets
            bucket_ok = True
            if time_buckets is not None:
                start = to_minutes(t.start_time)
                end = to_minutes(t.end_time)
                if start is None or end is None:
                    bucket_ok = False
                else:
                    segments: List[tuple[int, int]]
                    if end >= start:
                        segments = [(start, end)]
                    else:
                        segments = [(start, 24 * 60), (0, end)]
                    bucket_ok = any(
                        matches_bucket(seg_start, seg_end, bucket)
                        for bucket in time_buckets
                        for seg_start, seg_end in segments
                    )

            if weekday_ok and bucket_ok:
                return True

        return False



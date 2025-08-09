from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple

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

    def get_recommendations(self, query: str, max_results: int = 5) -> List[Event]:
        if not query or not query.strip():
            return []

        vector = self.embedding_service.generate_text_embedding(query)
        query_vec = np.asarray(vector, dtype=np.float32)
        # Fetch more candidates for potential reranking
        initial_k = max(self.rerank_top_n if self.rerank_enabled else max_results, max_results)
        matches = self.find_similar_events(query_vec, k=initial_k)

        # Map matches to events, dedup by id preserving order
        seen: set[str] = set()
        candidates: List[Event] = []
        for idx, _score in matches:
            ev = self.events[idx]
            if ev.id not in seen:
                candidates.append(ev)
                seen.add(ev.id)
            if len(candidates) >= initial_k:
                break

        if self.rerank_enabled and candidates:
            try:
                order = self.rerank_service.rerank(
                    query,
                    [
                        {
                            "id": e.id,
                            "title": e.title,
                            "type": e.type,
                            "camp": e.camp,
                            "description": e.description,
                        }
                        for e in candidates
                    ],
                )
                id_to_event = {e.id: e for e in candidates}
                reranked = [id_to_event[i] for i in order if i in id_to_event]
                return reranked[: max_results]
            except Exception:
                # On failure, fall back to vector order
                pass

        return candidates[: max_results]



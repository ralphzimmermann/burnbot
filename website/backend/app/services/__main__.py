"""One-time embedding generation script.

Usage:
    python -m app.services --output data/embeddings.npy [--limit 100]

Requires OPENAI_API_KEY to be set in the environment.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import List

import numpy as np
from dotenv import load_dotenv

from app.models.event import Event
from app.services.embedding_service import EmbeddingService


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate embeddings for events.json")
    parser.add_argument(
        "--events",
        default="data/events.json",
        help="Path to events JSON (default: data/events.json)",
    )
    parser.add_argument(
        "--output",
        default="data/embeddings.npy",
        help="Path to output .npy file (default: data/embeddings.npy)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional limit for number of events (for testing)",
    )

    args = parser.parse_args()

    # Load environment from .env if present (keeps setup simple)
    load_dotenv()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is not set")

    events_path = Path(args.events)
    if not events_path.exists():
        raise SystemExit(f"Events file not found: {events_path}")

    with events_path.open("r", encoding="utf-8") as f:
        data: List[dict] = json.load(f)

    if args.limit is not None:
        data = data[: args.limit]

    events = [Event.model_validate(item) for item in data]

    # Validate that all events have titles before generating embeddings
    missing_title_ids = [e.id for e in events if not (e.title and e.title.strip())]
    if missing_title_ids:
        sample = ", ".join(missing_title_ids[:10])
        raise SystemExit(
            f"Found {len(missing_title_ids)} event(s) with missing/empty title. "
            f"Example IDs: {sample}. Please fix data/events.json before generating embeddings."
        )

    service = EmbeddingService(openai_api_key=api_key)
    vectors = service.generate_all_embeddings(events)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(output_path), vectors)
    print(f"Saved embeddings: {output_path} shape={vectors.shape} dtype={vectors.dtype}")


if __name__ == "__main__":
    main()



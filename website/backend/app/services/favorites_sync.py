from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from sqlalchemy.orm import Session

from app.models.favorites import Favorite


def _load_events_map(data_dir: Path) -> Dict[str, Dict[str, Any]]:
    events_path = data_dir / "events.json"
    with events_path.open("r", encoding="utf-8") as f:
        items: List[Dict[str, Any]] = json.load(f)
    return {str(it.get("id")): it for it in items}


def sync_favorites_with_events(db: Session, data_dir: Path) -> int:
    """Update all favorites' stored event_json to match current events.json.

    - For each favorite, if the event id exists, replace all fields from events.json
      (including new fields like latitude/longitude).
    - If the event id no longer exists, set its description to "DELETED" while
      preserving the other known fields if present.

    Returns number of favorites updated.
    """
    events_map = _load_events_map(data_dir)

    favorites = db.query(Favorite).all()
    updated = 0
    for fav in favorites:
        event_id = str(fav.event_id)
        if event_id in events_map:
            # Overwrite completely with latest event object
            latest = events_map[event_id]
            fav.event_json = json.dumps(latest, ensure_ascii=False)
            updated += 1
        else:
            # Mark as deleted: update description field only, keep other fields if possible
            try:
                current = json.loads(fav.event_json)
            except Exception:
                current = {"id": event_id}
            current["description"] = "DELETED"
            fav.event_json = json.dumps(current, ensure_ascii=False)
            updated += 1

    if updated:
        db.commit()
    return updated




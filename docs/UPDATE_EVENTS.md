## Update Events and Embeddings

Use the helper script to collect the latest Events, Camps, and Art directory data and regenerate embeddings used by the recommendation engine.

### Prerequisites
- Python 3
- Internet access (for event collection)
- `OPENAI_API_KEY` present either in your environment or in `website/backend/.env`
- The script will create/activate virtual environments in:
  - `data-collector/venv` (or `data-collector/.venv`)
  - `website/backend/.venv`

### Usage
```bash
/Users/ralph/dev/bm-eventguide/update_events.sh
```

- Events JSON → `website/backend/data/events.json`
- Camps JSON → `website/backend/data/camps.json`
- Art JSON → `website/backend/data/arts.json`
- Embeddings → `website/backend/data/embeddings.npy`

### Options
- Pass-through args to the collector (e.g., limit events during testing):
```bash
/Users/ralph/dev/bm-eventguide/update_events.sh --max-events 100
```
- Quick embeddings test via env var:
```bash
export EMBEDDINGS_LIMIT=50
/Users/ralph/dev/bm-eventguide/update_events.sh
```

### What the script does
- Activates data-collector venv and runs (in this order):
  - `python collect_camps.py --output website/backend/data/camps.json`
  - `python collect_arts.py --output website/backend/data/arts.json`
  - `python collect_events.py --output website/backend/data/events.json --camps website/backend/data/camps.json [your args]`
- Activates backend venv and runs:
  - `python -m app.services --output website/backend/data/embeddings.npy [--limit $EMBEDDINGS_LIMIT]`

Notes:
- If venvs do not exist, they will be created and dependencies installed from the respective `requirements.txt` files.
- Events are enriched with camp `location` (normalized, e.g., "C & 6:45") and `latitude`/`longitude` when available. Unresolved locations are set to `"n/a"` for manual review.
- The embeddings generator reads `website/backend/data/events.json`. Ensure collection completed successfully before generation.
 - If `OPENAI_API_KEY` is not exported, the script will try to read it from `website/backend/.env`.



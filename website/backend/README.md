# BM EventGuide Backend

Minimal FastAPI backend foundation for the AI Recommendation Engine.

## Quickstart

### Local (recommended for dev)

```bash
cd website/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Optional but recommended if you want data-backed endpoints
mkdir -p data && ln -sf ../../data/events.json data/events.json

uvicorn app.main:app --reload --port 8000
# Health check
curl http://localhost:8000/health
```

### Docker (serves API and built frontend)

```bash
cd <repo-root>
docker compose up -d
open http://localhost:8000
```

See `docs/DOCKER.md` for details (env vars, how it bundles frontend, etc.).

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template and configure as needed:
   ```bash
   cp .env.example .env
   ```
4. Create the data symlink (one-time):
   ```bash
   mkdir -p data
   ln -sf ../../data/events.json data/events.json
   ```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"message":"Hello World"}
```

## Notes

- Follow YAGNI: only minimal endpoints in Phase 1.
- Embedding and recommendation services will be added in later phases.

### CORS

Configure allowed origins (comma-separated):

```bash
export CORS_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
```

## Embeddings (Phase 2)

Generate embeddings (requires `OPENAI_API_KEY`):

```bash
export OPENAI_API_KEY=... # or set it in your .env and export before running
python -m app.services --output data/embeddings.npy --limit 50   # test run
python -m app.services --output data/embeddings.npy              # full run
```

The script reads `data/events.json` and saves a NumPy array to `data/embeddings.npy`.

Validation: the generation script fails fast if any event has a missing or empty `title`. Fix the data (e.g., via `data-collector`) before re-running.

# How to start

### 1. Collect All Events
```bash
cd data-collector
python collect_events.py
```

### 2. Generate embeddings
```bash
cd website/backend
python -m app.services --output data/embeddings.npy   
```




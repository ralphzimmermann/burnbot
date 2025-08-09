# BM EventGuide Backend

Minimal FastAPI backend foundation for the AI Recommendation Engine.

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




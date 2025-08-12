# EventGuide Docker Setup

This project runs frontend and backend in a single container for simplicity.

## Build and Run

```bash
# From repo root
docker compose build
docker compose up -d

# Open in browser
open http://localhost:8000
```

## Environment Variables

- `OPENAI_API_KEY`: required for generating query embeddings and optional reranking
- `ENABLE_RERANK`: `true|false` (default `false`)
- `RERANK_TOP_N`: number of candidates to rerank (default `50`)
- `CORS_ORIGINS`: allowed origins for CORS (not needed for same-origin)

Compose loads variables from `.env` in the repo root and `website/backend/.env` automatically. You can also set them inline. Example `.env`:

```env
OPENAI_API_KEY=sk-...
ENABLE_RERANK=false
```

## How it Works

- The Dockerfile builds the Vite frontend (`website/frontend`) and copies the `dist/` output into the image.
- FastAPI (`website/backend`) serves API routes and statically serves the built frontend with an SPA fallback.
- The single container exposes port `8000`.

## Development

For local dev without Docker:

```bash
# Backend
cd website/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd website/frontend
npm ci
npm run dev
```

Point the frontend to the backend with `VITE_API_BASE_URL` if not same-origin:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```



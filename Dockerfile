# syntax=docker/dockerfile:1

# --- Build frontend (Vite) ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/website/frontend

# Install dependencies first (better caching)
COPY website/frontend/package*.json ./
RUN npm ci

# Copy source and build
COPY website/frontend .
RUN npm run build


# --- Runtime (Python + FastAPI) ---
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# System deps (faiss runtime needs libgomp)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/website/backend

# Install Python deps
COPY website/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and data
COPY website/backend /app/website/backend

# Copy built frontend assets from builder
COPY --from=frontend-builder /app/website/frontend/dist /app/website/frontend/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]



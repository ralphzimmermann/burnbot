# syntax=docker/dockerfile:1

# --- Build frontend (Vite) ---
# Use Debian-based image so lightningcss has a compatible prebuilt binary (alpine/musl lacks it)
FROM node:20-bookworm-slim AS frontend-builder
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
    && apt-get install -y --no-install-recommends libgomp1 nginx certbot python3-certbot-dns-route53 openssl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/website/backend

# Install Python deps
COPY website/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code and data
COPY website/backend /app/website/backend

# Copy built frontend assets from builder
COPY --from=frontend-builder /app/website/frontend/dist /app/website/frontend/dist

# --- Nginx config ---
COPY website/nginx/app.conf /etc/nginx/conf.d/app.conf
COPY website/nginx/sites-available /website/nginx/sites-available
RUN rm -f /etc/nginx/sites-enabled/default /etc/nginx/conf.d/default.conf 2>/dev/null || true

EXPOSE 80 443

# Entrypoint script to run backend and nginx together
COPY website/nginx/start.sh /start.sh
RUN chmod +x /start.sh
COPY certbot-dns-issue.sh /certbot-dns-issue.sh
RUN chmod +x /certbot-dns-issue.sh
COPY certbot-dns-manual.sh /certbot-dns-manual.sh
RUN chmod +x /certbot-dns-manual.sh
COPY certbot-dns-route53.sh /certbot-dns-route53.sh
RUN chmod +x /certbot-dns-route53.sh

CMD ["/start.sh"]



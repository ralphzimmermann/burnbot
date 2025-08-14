#!/bin/sh
set -euo pipefail

DOMAIN=${1:-}
EMAIL=${EMAIL:-"admin@thehealthwarriors.net"}

if [ -z "$DOMAIN" ]; then
  echo "Usage: $0 <domain>"
  exit 1
fi

if [ ! -f "/etc/letsencrypt/cloudflare.ini" ]; then
  echo "Missing /etc/letsencrypt/cloudflare.ini with Cloudflare API token."
  echo "Create it and ensure permissions: chmod 600 /etc/letsencrypt/cloudflare.ini"
  exit 1
fi

certbot certonly \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  -d "$DOMAIN"

echo "Certificate issuance attempted for $DOMAIN. If successful, certs are in /etc/letsencrypt/live/$DOMAIN/."



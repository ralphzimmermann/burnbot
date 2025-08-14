#!/bin/sh
set -euo pipefail

# Manual DNS-01 issuance for domains without a DNS API plugin.
# Usage: certbot-dns-manual.sh burnbot.thehealthwarriors.net [email]

DOMAIN=${1:-}
EMAIL=${2:-"admin@thehealthwarriors.net"}

if [ -z "$DOMAIN" ]; then
  echo "Usage: $0 <domain> [email]"
  exit 1
fi

echo "This will run Certbot in manual DNS mode for $DOMAIN."
echo "You will be prompted to create a DNS TXT record. Keep this terminal open while you add the record."

certbot certonly \
  --manual \
  --preferred-challenges dns \
  --agree-tos \
  --manual-public-ip-logging-ok \
  --non-interactive 2>/dev/null || true

# Fallback to interactive if non-interactive failed (expected for manual)
certbot certonly \
  --manual \
  --preferred-challenges dns \
  --agree-tos \
  --manual-public-ip-logging-ok \
  --email "$EMAIL" \
  -d "$DOMAIN"

echo "If successful, certs are in /etc/letsencrypt/live/$DOMAIN/. Reload nginx: nginx -s reload"



#!/bin/sh
set -euo pipefail

# Issue/renew Let's Encrypt cert using Certbot's Route 53 plugin.
# Usage: certbot-dns-route53.sh burnbot.thehealthwarriors.net [email]
# Requires AWS creds in env (or IAM role if running on EC2):
#   AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

DOMAIN=${1:-}
EMAIL=${2:-"admin@thehealthwarriors.net"}

if [ -z "$DOMAIN" ]; then
  echo "Usage: $0 <domain> [email]"
  exit 1
fi

if [ -z "${AWS_ACCESS_KEY_ID:-}" ] || [ -z "${AWS_SECRET_ACCESS_KEY:-}" ]; then
  echo "Missing AWS credentials in environment. Set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_DEFAULT_REGION."
  exit 1
fi

# Use a fixed cert name to avoid creating -0001 lineages repeatedly
certbot certonly \
  --non-interactive \
  --agree-tos \
  --email "$EMAIL" \
  --dns-route53 \
  --cert-name "$DOMAIN" \
  -d "$DOMAIN"

echo "Certificate issuance attempted for $DOMAIN. If successful, certs are in /etc/letsencrypt/live/$DOMAIN/."



#!/bin/sh
set -euo pipefail

DOMAIN="burnbot.thehealthwarriors.net"
LE_LIVE_BASE="/etc/letsencrypt/live"
CANON_PATH="$LE_LIVE_BASE/$DOMAIN"

mkdir -p /var/www/certbot

# Resolve the actual live directory for the domain, coping with -0001/-0002 suffixes
resolve_live_dir() {
  if [ -f "$CANON_PATH/fullchain.pem" ] && [ -f "$CANON_PATH/privkey.pem" ]; then
    echo "$CANON_PATH"
    return 0
  fi

  # Find highest numeric suffix with both files present
  best=""
  best_num=-1
  for d in "$LE_LIVE_BASE"/${DOMAIN}-*; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    suffix=${name#$DOMAIN-}
    case "$suffix" in
      ''|*[!0-9]*) continue;;
    esac
    if [ -f "$d/fullchain.pem" ] && [ -f "$d/privkey.pem" ]; then
      num=$suffix
      if [ "$num" -gt "$best_num" ]; then
        best_num=$num
        best="$d"
      fi
    fi
  done
  if [ -n "$best" ]; then
    echo "$best"
    return 0
  fi
  return 1
}

LIVE_DIR=""
if LIVE_DIR=$(resolve_live_dir); then
  # Ensure canonical path points to the selected live dir
  if [ "$LIVE_DIR" != "$CANON_PATH" ]; then
    echo "Linking $CANON_PATH -> $LIVE_DIR"
    ln -sfn "$LIVE_DIR" "$CANON_PATH"
  fi
fi

# Manage Nginx site enablement based on presence of certs (in canonical path)
HTTPS_CONF_SRC="/website/nginx/sites-available/https_proxy.conf"
HTTP_CONF_SRC="/website/nginx/sites-available/http_proxy.conf"
ACTIVE_CONF_DIR="/etc/nginx/conf.d"

rm -f "$ACTIVE_CONF_DIR"/*.conf 2>/dev/null || true

if [ -f "$CANON_PATH/fullchain.pem" ] && [ -f "$CANON_PATH/privkey.pem" ]; then
  echo "Found Let's Encrypt certs in $CANON_PATH. Enabling HTTPS site."
  ln -sf "$HTTPS_CONF_SRC" "$ACTIVE_CONF_DIR/app.conf"
else
  echo "No real certs found. Enabling HTTP-only site."
  ln -sf "$HTTP_CONF_SRC" "$ACTIVE_CONF_DIR/app.conf"
fi

# Start the FastAPI app in the background
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start nginx in the foreground
nginx -g 'daemon off;'



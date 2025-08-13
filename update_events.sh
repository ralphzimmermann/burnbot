#!/usr/bin/env bash

# Update events and generate embeddings for BM EventGuide.
#
# Steps:
# 1) Activate data-collector venv and run collect_events.py
#    → writes JSON to website/backend/data/events.json
# 2) Activate backend venv and run `python -m app.services`
#    → reads events.json and writes embeddings to data/embeddings.npy
#
# Requirements:
# - data-collector requirements installed (handled by this script if venv needs init)
# - backend requirements installed (handled by this script if venv needs init)
# - OPENAI_API_KEY set in the environment for embeddings
#
# Optional environment variables:
# - EMBEDDINGS_LIMIT: pass a limit to the embeddings generator (e.g., 50 for a quick test)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

COLLECTOR_DIR="$REPO_ROOT/data-collector"
BACKEND_DIR="$REPO_ROOT/website/backend"
BACKEND_DATA_DIR="$BACKEND_DIR/data"
EVENTS_JSON="$BACKEND_DATA_DIR/events.json"
EMBEDDINGS_NPY="$BACKEND_DATA_DIR/embeddings.npy"

ensure_dir() {
  mkdir -p "$1"
}

load_openai_key_from_env_file() {
  # If OPENAI_API_KEY isn't exported, try to read it from backend .env
  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    local env_file="$BACKEND_DIR/.env"
    if [[ -f "$env_file" ]]; then
      echo "› Loading OPENAI_API_KEY from $env_file"
      # Read the last occurrence to allow overrides later in the file
      local key_line
      key_line="$(grep -E '^[[:space:]]*OPENAI_API_KEY[[:space:]]*=' "$env_file" | tail -n1 || true)"
      if [[ -n "$key_line" ]]; then
        local value
        value="${key_line#*=}"
        # Trim surrounding quotes and whitespace
        value="${value##[[:space:]]}"
        value="${value%%[[:space:]]}"
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        export OPENAI_API_KEY="$value"
      fi
    fi
  fi
}

activate_collector_venv() {
  # Prefer existing venv at data-collector/venv, otherwise create .venv
  local venv_path="$COLLECTOR_DIR/venv"
  if [[ -d "$venv_path" ]]; then
    echo "› Activating data-collector venv: $venv_path"
    # shellcheck disable=SC1091
    source "$venv_path/bin/activate"
  else
    venv_path="$COLLECTOR_DIR/.venv"
    if [[ ! -d "$venv_path" ]]; then
      echo "› Creating data-collector venv: $venv_path"
      python3 -m venv "$venv_path"
    fi
    echo "› Activating data-collector venv: $venv_path"
    # shellcheck disable=SC1091
    source "$venv_path/bin/activate"
    echo "› Installing data-collector requirements"
    pip install -r "$COLLECTOR_DIR/requirements.txt"
  fi
}

activate_backend_venv() {
  local venv_path="$BACKEND_DIR/.venv"
  if [[ ! -d "$venv_path" ]]; then
    echo "› Creating backend venv: $venv_path"
    python3 -m venv "$venv_path"
  fi
  echo "› Activating backend venv: $venv_path"
  # shellcheck disable=SC1091
  source "$venv_path/bin/activate"
  echo "› Installing backend requirements"
  pip install -r "$BACKEND_DIR/requirements.txt"
}

run_collector() {
  ensure_dir "$BACKEND_DATA_DIR"
  echo "→ Collecting events → $EVENTS_JSON"
  # Forward any arguments provided to this script to the collector (e.g., --max-events 100)
  python3 "$COLLECTOR_DIR/collect_events.py" --output "$EVENTS_JSON" "$@"
}

run_embeddings() {
  load_openai_key_from_env_file
  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    echo "ERROR: OPENAI_API_KEY is not set. Export it or add it to $BACKEND_DIR/.env before running." >&2
    exit 1
  fi

  pushd "$BACKEND_DIR" >/dev/null
  echo "→ Generating embeddings → $EMBEDDINGS_NPY"

  # Allow quick test runs via EMBEDDINGS_LIMIT. Full run if not set.
  if [[ -n "${EMBEDDINGS_LIMIT:-}" ]]; then
    echo "› Using EMBEDDINGS_LIMIT=$EMBEDDINGS_LIMIT"
    python -m app.services --output "$EMBEDDINGS_NPY" --limit "$EMBEDDINGS_LIMIT"
  else
    python -m app.services --output "$EMBEDDINGS_NPY"
  fi
  popd >/dev/null
}

main() {
  echo "=== Updating events and embeddings ==="

  # 1) Collect events
  activate_collector_venv
  run_collector "$@"
  deactivate || true

  # 2) Generate embeddings
  activate_backend_venv
  run_embeddings
  deactivate || true

  echo "✓ Done. Updated:"
  echo "  - Events:     $EVENTS_JSON"
  echo "  - Embeddings: $EMBEDDINGS_NPY"
}

main "$@"



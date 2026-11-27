#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${NEXUS_DATABASE_URL:-}" || -n "${TELEGRAM_BOT_TOKEN:-}" || -n "${GEMINI_API_KEY:-}" ]]; then
  echo "Refusing build with runtime credentials" >&2
  exit 1
fi
test -s requirements-preview.lock
python -m venv .preview-venv
.preview-venv/bin/python -m pip install --require-hashes -r requirements-preview.lock
.preview-venv/bin/python -m pip check
.preview-venv/bin/python -m unittest -v

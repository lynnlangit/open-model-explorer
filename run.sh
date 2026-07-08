#!/usr/bin/env bash
# Open Model Explorer — local launcher for macOS (Apple Silicon).
# Checks Ollama, sets up a Python venv, pre-pulls demo models, starts the app.
set -e

cd "$(dirname "$0")"
echo "=== Open Model Explorer ==="

# 1) Ollama present?
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed."
  echo "Install it with:  brew install ollama"
  echo "or download from: https://ollama.com/download"
  exit 1
fi

# 2) Ollama server running? Start it in the background if not.
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "Starting Ollama server..."
  ollama serve >/tmp/ollama.log 2>&1 &
  for i in $(seq 1 30); do
    sleep 1
    curl -s http://localhost:11434/api/tags >/dev/null 2>&1 && break
  done
fi

# 3) Python venv + dependencies
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 4) Pre-pull the demo models listed in models.json (small + one medical).
echo "Pre-pulling demo models (first run only; this can take a few minutes)..."
python3 - <<'PY'
import json, subprocess, sys
cfg = json.load(open("models.json"))
for m in cfg.get("preload", []):
    print(f"  -> ollama pull {m}")
    subprocess.run(["ollama", "pull", m], check=False)
PY

# 5) Launch the app and open the browser.
echo ""
echo "Launching at http://localhost:8000"
echo "(auto-reload on: edits to the app restart the server automatically — just refresh the browser)"
( sleep 2 && open http://localhost:8000 ) &
python3 -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload --reload-include "*.json" --reload-include "*.html"

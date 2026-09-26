#!/bin/bash
# The Morning Brief — local daily run (launchd fires this at 10:00).
# If the Mac was asleep at 10:00, launchd runs it at the next wake.
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$HOME/Documents/Code Projects/morning-brief"
cd "$REPO" || exit 1
LOG="$REPO/.tmp/run_$(date +%Y-%m-%d).log"
mkdir -p .tmp

{
  echo "=== $(date '+%Y-%m-%d %H:%M %Z') ==="

  # --- deterministic half -------------------------------------------------
  python3 execution/collect.py || echo "WARN: collect had failures (non-fatal)"
  python3 execution/archive.py || { echo "FATAL: archive failed"; exit 1; }

  # --- editorial half ----------------------------------------------------
  # Runs on the Claude Pro subscription, no API key, no per-run cost.
  claude -p "$(cat directives/RUN_PROMPT.md)" \
    --permission-mode bypassPermissions \
    --model opus \
    2>&1

  echo "=== done $(date '+%H:%M') ==="
} >> "$LOG" 2>&1

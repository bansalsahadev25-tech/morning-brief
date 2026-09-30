#!/bin/bash
# The Morning Brief — local daily run. launchd fires this at 10:00.
# If the Mac was asleep, launchd runs it at the next wake.
#
# NOTE: this repo must live OUTSIDE ~/Documents, ~/Desktop and ~/Downloads.
# macOS TCC blocks launchd agents from executing there (exit 126,
# "Operation not permitted") BEFORE any code runs, so there is no app log.
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$HOME/morning-brief"
cd "$REPO" || exit 1
mkdir -p .tmp
LOG="$REPO/.tmp/run_$(date +%Y-%m-%d).log"
TODAY="$(date +%Y-%m-%d)"

{
  echo "=== $(date '+%Y-%m-%d %H:%M %Z') ==="

  # --- 1. deterministic collection ---------------------------------------
  python3 execution/collect.py || {
      echo "FATAL: collection starved (exit $?). Publishing nothing."
      exit 2
  }
  python3 execution/archive.py || { echo "FATAL: archive failed"; exit 1; }

  # --- 2. editorial pass (Claude Pro subscription, no API key) ------------
  claude -p "$(cat directives/RUN_PROMPT.md)" \
    --permission-mode bypassPermissions --model opus 2>&1

  # --- 3. deterministic publish ------------------------------------------
  # Kept in the shell, not the prompt: these must happen even if the
  # editorial pass ends early or skips a step.
  if [ ! -f "issues/$TODAY.html" ]; then
      echo "ERROR: issues/$TODAY.html missing — editorial pass did not finish."
      echo "Not updating latest.html; yesterday's issue stays up."
      exit 3
  fi
  python3 execution/build_index.py

  git add archive/ issues/ index.html latest.html
  git commit -q -m "Brief: $TODAY

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" || echo "(nothing to commit)"
  git push -q origin main || echo "WARN: push failed (brief still built locally)"

  # --- 4. put it in front of him -----------------------------------------
  # Local file: instant, works offline, no waiting on a Pages deploy.
  # -a activates Brave and brings it to the front.
  open -a "Brave Browser" "file://$REPO/latest.html" \
    || open "file://$REPO/latest.html" \
    || echo "WARN: could not open a browser"

  osascript -e 'display notification "Issue is up — opened in Brave." with title "The Morning Brief" sound name "Glass"' 2>/dev/null || true

  echo "=== done $(date '+%H:%M') ==="
} >> "$LOG" 2>&1

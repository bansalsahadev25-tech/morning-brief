#!/bin/bash
# The Morning Brief — local daily run. launchd fires this at 10:00.
#
# Two hard-won constraints:
#  1. This repo must live OUTSIDE ~/Documents, ~/Desktop and ~/Downloads.
#     macOS TCC blocks launchd agents from executing there (exit 126,
#     "Operation not permitted") BEFORE any code runs — no app log at all.
#  2. The Mac wakes at 9:55 but Wi-Fi can take minutes to reassociate.
#     On 2026-10-02 the job started at 10:12 into dead DNS and burned
#     2.5 hours retrying. Hence wait_for_network and the retry loop.
set -u
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
REPO="$HOME/morning-brief"
cd "$REPO" || exit 1
mkdir -p .tmp
LOG="$REPO/.tmp/run_$(date +%Y-%m-%d).log"
TODAY="$(date +%Y-%m-%d)"

notify() {  # $1 title, $2 message, $3 sound
  osascript -e "display notification \"$2\" with title \"$1\" sound name \"${3:-Glass}\"" 2>/dev/null || true
}

wait_for_network() {  # up to 12 minutes, checking every 15s
  local tries=0
  until ping -c1 -t2 1.1.1.1 >/dev/null 2>&1 && \
        ( host -W 2 hn.algolia.com >/dev/null 2>&1 || \
          curl -s -m 5 -o /dev/null https://news.ycombinator.com ); do
    tries=$((tries + 1))
    if [ "$tries" -ge 48 ]; then
      echo "network never came up after 12 minutes"
      return 1
    fi
    sleep 15
  done
  echo "network up after $((tries * 15))s"
  return 0
}

{
  echo "=== $(date '+%Y-%m-%d %H:%M %Z') ==="

  # --- 0. don't start until the machine can actually reach the internet ---
  if ! wait_for_network; then
      notify "The Morning Brief" "No network. No issue today." "Basso"
      exit 4
  fi

  # --- 1. collection, with retries for a flaky post-wake network ---------
  attempt=1
  until python3 execution/collect.py; do
      code=$?
      if [ "$code" -eq 3 ] && [ "$attempt" -lt 3 ]; then
          echo "collection failed on network (exit 3), attempt $attempt — retrying in 10 min"
          attempt=$((attempt + 1))
          sleep 600
          continue
      fi
      echo "FATAL: collection starved (exit $code) after $attempt attempt(s)."
      notify "The Morning Brief" "Collection failed — no issue today. Check the log." "Basso"
      exit "$code"
  done
  python3 execution/archive.py || { echo "FATAL: archive failed"; exit 1; }

  # --- 2. editorial pass (Claude Pro subscription, no API key) -----------
  claude -p "$(cat directives/RUN_PROMPT.md)" \
    --permission-mode bypassPermissions --model opus 2>&1

  # --- 3. deterministic publish; must survive an early-exiting LLM pass --
  if [ ! -f "issues/$TODAY.html" ]; then
      echo "ERROR: issues/$TODAY.html missing — editorial pass did not finish."
      notify "The Morning Brief" "Editorial pass failed — yesterday's issue stays up." "Basso"
      exit 5
  fi
  python3 execution/build_index.py

  git add archive/ issues/ index.html latest.html config/problems.yaml
  git commit -q -m "Brief: $TODAY

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" || echo "(nothing to commit)"
  git push -q origin main || echo "WARN: push failed (brief still built locally)"

  # --- 4. put it in front of him -----------------------------------------
  open -a "Brave Browser" "file://$REPO/latest.html" \
    || open "file://$REPO/latest.html" \
    || echo "WARN: could not open a browser"
  notify "The Morning Brief" "$(grep -oE 'Issue [0-9]+' "issues/$TODAY.html" | head -1) is up — opened in Brave."

  echo "=== done $(date '+%H:%M') ==="
} >> "$LOG" 2>&1

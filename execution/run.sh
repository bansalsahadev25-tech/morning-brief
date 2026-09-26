#!/bin/bash
# The Morning Brief — daily run. Wire it to launchd for 06:00.
set -u
cd "$(dirname "$0")/.."
echo "=== $(date '+%Y-%m-%d %H:%M') ==="
python3 execution/collect.py || echo "collect had failures (non-fatal)"
python3 execution/archive.py
echo "Raw + archive ready. Editorial pass (triage, research, render) runs in Claude Code:"
echo "  claude -p 'Run directives/daily_brief.md against the latest .tmp/raw_*.json'"

#!/bin/bash
# focus — friction, not willpower.
#
# The premise: an urge lasts 10-20 minutes. You do not need permanent
# self-control, you need the path to be longer than the urge. Nothing here
# is a prison; all of it is reversible. The point is that reversing it is
# slow and deliberate, so the impulse expires before the block does.
#
#   focus on         block distractions (needs sudo)
#   focus off        unblock after a 20-minute wait  <- the important one
#   focus off now    unblock immediately (deliberate, and it tells you)
#   focus dns        route adult content to a dead end, system-wide
#   focus dns-off    undo that
#   focus status     what is currently on
set -u
HOSTS=/etc/hosts
MARK_A="# --- focus:start ---"
MARK_B="# --- focus:end ---"
STATE="$HOME/.focus_state"

SITES=(
  www.youtube.com youtube.com m.youtube.com
  www.reddit.com reddit.com
  www.instagram.com instagram.com
  x.com www.x.com twitter.com www.twitter.com
  www.tiktok.com tiktok.com
)

need_sudo() {
  if [ "$(id -u)" -ne 0 ]; then
    echo "needs sudo:  sudo $0 $*" >&2
    exit 1
  fi
}

flush() { dscacheutil -flushcache 2>/dev/null; killall -HUP mDNSResponder 2>/dev/null; true; }

case "${1:-status}" in
  on)
    need_sudo "$@"
    sed -i '' "/$MARK_A/,/$MARK_B/d" "$HOSTS"
    {
      echo "$MARK_A"
      for s in "${SITES[@]}"; do echo "127.0.0.1 $s"; done
      echo "$MARK_B"
    } >> "$HOSTS"
    flush
    date +%s > "$STATE"
    echo "focus on. $(( ${#SITES[@]} )) hosts blocked."
    echo "to lift it: focus off   (takes 20 minutes on purpose)"
    ;;

  off)
    if [ "${2:-}" = "now" ]; then
      need_sudo "$@"
      sed -i '' "/$MARK_A/,/$MARK_B/d" "$HOSTS"; flush; rm -f "$STATE"
      echo "unblocked immediately."
      echo "You chose to skip the wait. Worth noticing which part of you did that."
      exit 0
    fi
    PEND="$HOME/.focus_pending"
    if [ -f "$PEND" ]; then
      left=$(( 1200 - ( $(date +%s) - $(cat "$PEND") ) ))
      if [ "$left" -gt 0 ]; then
        echo "already waiting. $(( left / 60 ))m $(( left % 60 ))s left."
        echo "If the urge has passed, run: focus cancel"
        exit 0
      fi
      need_sudo "$@"
      sed -i '' "/$MARK_A/,/$MARK_B/d" "$HOSTS"; flush; rm -f "$PEND" "$STATE"
      echo "wait served. unblocked."
      exit 0
    fi
    date +%s > "$PEND"
    echo "20-minute wait started."
    echo "Most urges do not survive it. Do something else and come back:"
    echo "  focus off      (again, once the time is up)"
    echo "  focus cancel   (if you no longer want to)"
    ;;

  cancel)
    rm -f "$HOME/.focus_pending"
    echo "wait cancelled. still blocked. good."
    ;;

  dns)
    need_sudo "$@"
    # Cloudflare for Families — 1.1.1.3 filters adult content at the
    # resolver, before any browser or profile is involved.
    for svc in "Wi-Fi" "Ethernet"; do
      networksetup -setdnsservers "$svc" 1.1.1.3 1.0.0.3 2>/dev/null \
        && echo "DNS filtering on for $svc"
    done
    flush
    ;;

  dns-off)
    need_sudo "$@"
    for svc in "Wi-Fi" "Ethernet"; do
      networksetup -setdnsservers "$svc" empty 2>/dev/null \
        && echo "DNS filtering off for $svc"
    done
    flush
    ;;

  status)
    grep -q "$MARK_A" "$HOSTS" 2>/dev/null \
      && echo "sites:  BLOCKED" || echo "sites:  open"
    cur=$(networksetup -getdnsservers "Wi-Fi" 2>/dev/null | head -1)
    [ "$cur" = "1.1.1.3" ] \
      && echo "dns:    filtered (Cloudflare for Families)" \
      || echo "dns:    $cur"
    [ -f "$HOME/.focus_pending" ] && {
      left=$(( 1200 - ( $(date +%s) - $(cat "$HOME/.focus_pending") ) ))
      [ "$left" -gt 0 ] && echo "unlock: $(( left / 60 ))m $(( left % 60 ))s remaining"
    }
    [ -f "$STATE" ] && echo "since:  $(date -r "$(cat "$STATE")" '+%a %H:%M')"
    exit 0
    ;;

  *) sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//' ;;
esac

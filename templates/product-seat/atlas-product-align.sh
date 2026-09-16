#!/bin/sh
# atlas-product-align — Stop hook: alignment gate. If origin moved past this checkout,
# block the turn once and say to pull + re-orient. Simple copy of the arch gate's core
# (throttled; respects stop_hook_active; bounded stdin).
set -e
CONF="$(dirname -- "$0")/.atlas-product.conf"
[ -f "$CONF" ] && . "$CONF"
[ -n "${ATLAS_VAULT:-}" ] || exit 0
if [ ! -t 0 ]; then
  if command -v timeout >/dev/null 2>&1; then PAY=$(timeout 2 cat 2>/dev/null || true)
  else PAY=""; read -t 2 -r PAY 2>/dev/null || true; fi
  case "$PAY" in *'"stop_hook_active": true'*|*'"stop_hook_active":true'*) exit 0 ;; esac
fi
REMOTE=$(git -C "$ATLAS_VAULT" remote get-url origin 2>/dev/null || true)
[ -n "$REMOTE" ] || exit 0
BR=$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
T="${TMPDIR:-/tmp}/atlas-product-fresh.$(printf '%s %s' "$REMOTE" "$BR" | cksum | cut -d' ' -f1)"
NOW=$(date +%s); LAST=$(cat "$T" 2>/dev/null || echo 0)
case "$LAST" in *[!0-9]*|"") LAST=0 ;; esac
[ $((NOW - LAST)) -ge 30 ] || exit 0
printf '%s' "$NOW" > "$T" 2>/dev/null || true
CUR=$(git ls-remote "$REMOTE" "refs/heads/$BR" 2>/dev/null | cut -f1 || true)
[ -n "$CUR" ] || exit 0
HEAD=$(git -C "$ATLAS_VAULT" rev-parse HEAD 2>/dev/null || true)
[ "$CUR" = "$HEAD" ] && exit 0
if git -C "$ATLAS_VAULT" cat-file -e "$CUR" 2>/dev/null &&
   git -C "$ATLAS_VAULT" merge-base --is-ancestor "$CUR" "$HEAD" 2>/dev/null; then
  exit 0
fi
echo "Atlas: VAULT UPDATED under you — origin/$BR moved (arch decision, contract, or a need to you). Pull, re-run sh atlas-product-context.sh, reconcile, then finish." >&2
exit 2

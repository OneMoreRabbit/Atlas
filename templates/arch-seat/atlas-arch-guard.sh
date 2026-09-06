#!/bin/sh
# atlas-arch-guard — Stop hook: the arch seat's alignment gate (method 1.25).
# The vault moves under a RUNNING arch seat too: component outbox PRs auto-merge, CI
# regen commits derived views, cross-vault deliveries land. At every turn end, one
# ls-remote of the vault's current branch; if the remote holds commits this checkout
# does not, refuse to end the turn: pull, re-run atlas-arch-context.sh, reconcile.
# Quiet when local is equal OR AHEAD (your own unpushed work is not staleness).
# Fail-open everywhere; stop_hook_active prevents same-turn loops; 30s throttle.
set -e
: "${ATLAS_VAULT:=.}"
PAYLOAD=""
[ -t 0 ] || PAYLOAD=$(cat 2>/dev/null || true)
case "$PAYLOAD" in *'"stop_hook_active":true'*|*'"stop_hook_active": true'*) exit 0 ;; esac
[ -d "$ATLAS_VAULT/.git" ] || exit 0
BR=$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
[ -n "$BR" ] && [ "$BR" != "HEAD" ] || exit 0
REMOTE=$(git -C "$ATLAS_VAULT" remote get-url origin 2>/dev/null || true)
[ -n "$REMOTE" ] || exit 0
THROTTLE="${TMPDIR:-/tmp}/atlas-fresh.$(printf '%s %s' "$REMOTE" "$BR" | cksum | cut -d' ' -f1)"
NOW=$(date +%s); LAST=$(cat "$THROTTLE" 2>/dev/null || echo 0)
case "$LAST" in *[!0-9]*|"") LAST=0 ;; esac
[ $((NOW - LAST)) -ge 30 ] || exit 0
printf '%s' "$NOW" > "$THROTTLE" 2>/dev/null || true
CUR=$(git ls-remote "$REMOTE" "refs/heads/$BR" 2>/dev/null | cut -f1 || true)
[ -n "$CUR" ] || exit 0
HEADSHA=$(git -C "$ATLAS_VAULT" rev-parse HEAD 2>/dev/null || true)
[ "$CUR" = "$HEADSHA" ] && exit 0
# remote sha known locally and an ancestor of HEAD -> we are ahead (unpushed work): quiet
if git -C "$ATLAS_VAULT" cat-file -e "$CUR" 2>/dev/null &&
   git -C "$ATLAS_VAULT" merge-base --is-ancestor "$CUR" "$HEADSHA" 2>/dev/null; then
  exit 0
fi
echo "Atlas: VAULT UPDATED under you — origin/$BR moved (a component publish, CI regen, or delivery). Before finishing: git -C '$ATLAS_VAULT' pull, re-run your reorientation (sh atlas-arch-context.sh), reconcile your in-flight review against what arrived, then finish." >&2
exit 2

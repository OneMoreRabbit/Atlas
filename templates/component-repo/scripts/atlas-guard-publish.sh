#!/bin/sh
# atlas-guard-publish — Stop guard. Refuses to end a session with unpublished vault
# work. Nags at most once per session (atlas-context re-arms it); CI is the backstop,
# so a session that genuinely cannot publish is never trapped in a loop.
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"

# ---- Alignment gate (1.24): the vault moved since this seat's briefing ----------------
# One ls-remote per turn end. If the work branch is ahead of the commit the briefing was
# compiled from, refuse to end the turn and instruct a re-brief — an arch update then
# cascades to every RUNNING seat at the end of its current turn, with git as the only
# transport. Fail open on anything missing (offline work is never blocked); the
# stop_hook_active flag prevents a same-turn loop; a 30s throttle keeps rapid turns cheap.
PAYLOAD=""
[ -t 0 ] || PAYLOAD=$(cat 2>/dev/null || true)
case "$PAYLOAD" in *'"stop_hook_active":true'*|*'"stop_hook_active": true'*) exit 0 ;; esac
REC=$(cat "$ATLAS_REPO_ROOT/.git/info/atlas-compiled-sha" 2>/dev/null | tr -d '[:space:]' || true)
BWORK=$(atlas_work_branch 2>/dev/null || true)
if [ -n "$REC" ] && [ -n "$BWORK" ] && [ -n "$ATLAS_VAULT_REMOTE" ]; then
  THROTTLE="${TMPDIR:-/tmp}/atlas-fresh.$(printf '%s' "$ATLAS_REPO_ROOT" | cksum | cut -d' ' -f1)"
  NOW=$(date +%s); LAST=$(cat "$THROTTLE" 2>/dev/null || echo 0)
  case "$LAST" in *[!0-9]*|"") LAST=0 ;; esac
  if [ $((NOW - LAST)) -ge 30 ]; then
    printf '%s' "$NOW" > "$THROTTLE" 2>/dev/null || true
    CUR=$(git ls-remote "$ATLAS_VAULT_REMOTE" "refs/heads/$BWORK" 2>/dev/null | cut -f1 || true)
    if [ -n "$CUR" ] && [ "$CUR" != "$REC" ]; then
      echo "Atlas: VAULT UPDATED — the work branch moved to ${CUR%????????????????????????????????} since your briefing was compiled from ${REC%????????????????????????????????}. Before finishing: run \`sh scripts/atlas-context.sh\`, read the fresh briefing (pins, ADRs, contracts or needs may have changed your task), reconcile your in-flight work against it, then finish." >&2
      exit 2
    fi
  fi
fi

[ -d "$ATLAS_VAULT/.git" ] || exit 0
[ -f "$ATLAS_SENTINEL" ] && exit 0
[ -n "$(git -C "$ATLAS_VAULT" status --porcelain)" ] || exit 0

: > "$ATLAS_SENTINEL"
echo "Atlas: $ATLAS_VAULT has uncommitted changes — the outbox half of the session protocol has not run. Run /atlas-publish: contracts to components/$SLUG/docs/provides/, asks to docs/needs/, an ADR for shared changes, stamp updated:, recompile as a check only, then commit authored files only on branch atlas/$SLUG/<topic> and open the PR." >&2
exit 2

#!/bin/sh
# atlas-guard-publish — Stop guard. Refuses to end a session with unpublished vault
# work. Nags at most once per session (atlas-context re-arms it); CI is the backstop,
# so a session that genuinely cannot publish is never trapped in a loop.
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"

[ -d "$ATLAS_VAULT/.git" ] || exit 0
[ -f "$ATLAS_SENTINEL" ] && exit 0
[ -n "$(git -C "$ATLAS_VAULT" status --porcelain)" ] || exit 0

: > "$ATLAS_SENTINEL"
echo "Atlas: $ATLAS_VAULT has uncommitted changes — the outbox half of the session protocol has not run. Run /atlas-publish: contracts to components/$SLUG/docs/provides/, asks to docs/needs/, an ADR for shared changes, stamp updated:, recompile as a check only, then commit authored files only on branch atlas/$SLUG/<topic> and open the PR." >&2
exit 2

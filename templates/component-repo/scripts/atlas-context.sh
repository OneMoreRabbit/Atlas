#!/bin/sh
# atlas-context — emit this component's ATLAS-CONTEXT.md to stdout.
# A SessionStart hook injects stdout into the session context automatically.
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"
cd "$ATLAS_REPO_ROOT"

rm -f "$ATLAS_SENTINEL"   # new session: re-arm the publish guard

sh scripts/atlas-sync.sh >&2

PY=$(command -v python3 || command -v python)
"$PY" -c "import yaml" 2>/dev/null ||
  "$PY" -m pip install -q -r "$ATLAS_METHOD/tools/requirements.txt"

# The briefing is compiled from the WORK branch, not from whatever the vault clone has
# checked out. 1.11 rightly leaves an in-progress atlas/<slug>/<topic> publish branch
# alone — but a briefing compiled from it is silently historical: stale pins, an accepted
# ADR still rendered `status: proposed`. It presents as authority, not as an error, so a
# warning alone was not enough (agent-skeleton finding, 2026-08-26; method 1.12 warned,
# 1.14 compiles correctly). A throwaway worktree of origin/<work> is the whole fix.
BWORK=$(atlas_work_branch)
VBR=$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
SRC="$ATLAS_VAULT"
WT=""
if [ -n "$BWORK" ] && [ "$VBR" != "$BWORK" ]; then
  WT="${TMPDIR:-/tmp}/atlas-context-$$"
  if git -C "$ATLAS_VAULT" worktree add --detach -q "$WT" "origin/$BWORK" 2>/dev/null; then
    SRC="$WT"
    echo "atlas-context: clone is on '$VBR'; compiled from origin/$BWORK instead" >&2
  else
    WT=""
    echo "atlas-context: WARNING — could not check out origin/$BWORK; briefing compiled from '$VBR' and may be historical" >&2
  fi
fi
cleanup() { [ -n "$WT" ] && git -C "$ATLAS_VAULT" worktree remove --force "$WT" >/dev/null 2>&1; }
trap cleanup EXIT

OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$SRC" --emit-context "$SLUG")

case "$OUT" in
  "# ATLAS-CONTEXT"*) ;;
  *)
    echo "atlas-context: ERROR — method $(git -C "$ATLAS_METHOD" describe --tags --always) did not produce a context artefact." >&2
    exit 2 ;;
esac

# Provenance: every briefing states the branch and commit it was built from, so a
# stale one can never look like a fresh one.
SHA=$(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo '?')
SRCBR=$([ -n "$WT" ] && echo "origin/$BWORK" || echo "$VBR")
NOTE="> **Compiled from** vault \`$SRCBR\` @ \`$SHA\`."
if [ -z "$WT" ] && [ -n "$BWORK" ] && [ "$VBR" != "$BWORK" ]; then
  NOTE="> ⚠⚠ **STALE SOURCE** — compiled from vault branch \`$VBR\` @ \`$SHA\`, not the work branch \`$BWORK\`. Pins, ADRs and contracts may be historical. Switch the vault clone to \`$BWORK\` and re-run \`sh scripts/atlas-context.sh\` before relying on this."
fi
OUT=$(printf '%s\n\n%s' "$NOTE" "$OUT")

# Report the size of what we inject. Growth here is a defect in the io-graph,
# not a fact of life — the retrieval invariant is only worth anything if measured.
printf '%s' "$OUT" | wc -c |
  awk '{printf "atlas-context: %s — %d bytes (~%d tokens) injected\n", "'"$SLUG"'", $1, $1/4}' >&2

printf '%s\n' "$OUT"

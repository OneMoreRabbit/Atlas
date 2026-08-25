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

OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$ATLAS_VAULT" --emit-context "$SLUG")

# A method older than 1.1 has no --emit-context: it ignores the flag, runs validate
# mode (mutating $ATLAS_VAULT!), and exits 0 with a drift report on stdout. Never
# inject that as context — fail loudly instead.
case "$OUT" in
  "# ATLAS-CONTEXT"*) ;;
  *)
    echo "atlas-context: ERROR — method $(git -C "$ATLAS_METHOD" describe --tags --always) did not produce a context artefact." >&2
    echo "atlas-context: the vault's method pin likely predates 1.1 (--emit-context). Re-pin the vault, then discard any generated churn: git -C $ATLAS_VAULT checkout -- ." >&2
    exit 2 ;;
esac

# The briefing must come from the WORK branch. 1.11 rightly leaves an in-progress
# atlas/<slug>/<topic> publish branch alone at sync — but a briefing compiled from it
# is silently historical (stale pins, an accepted ADR still shown as proposed).
# Warn loudly, in the briefing itself, so the session cannot miss it.
BWORK=$(awk '/^branching:/{b=1;next} b&&/^[^ ]/{b=0} b&&/work:/{gsub(/[^A-Za-z0-9._\/-]/,"",$2); print $2; exit}' \
        "$ATLAS_VAULT/registry/io-graph.yml" 2>/dev/null || true)
VBR=$(git -C "$ATLAS_VAULT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)
if [ -n "$BWORK" ] && [ "$VBR" != "$BWORK" ] && [ "$VBR" != "HEAD" ]; then
  echo "atlas-context: WARNING — briefing compiled from vault branch '$VBR', not work branch '$BWORK' (may be historical)" >&2
  OUT=$(printf '%s\n\n%s' \
    "> ⚠⚠ **STALE SOURCE** — this briefing was compiled from vault branch \`$VBR\`, not the work branch \`$BWORK\`. Pins, ADRs and contracts may be historical. Finish or park the publish, switch the vault clone to \`$BWORK\`, and re-run \`sh scripts/atlas-context.sh\` before relying on this." \
    "$OUT")
fi

# Report the size of what we inject. Growth here is a defect in the io-graph,
# not a fact of life — the retrieval invariant is only worth anything if measured.
printf '%s' "$OUT" | wc -c |
  awk '{printf "atlas-context: %s — %d bytes (~%d tokens) injected\n", "'"$SLUG"'", $1, $1/4}' >&2

printf '%s\n' "$OUT"

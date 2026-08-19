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

# Report the size of what we inject. Growth here is a defect in the io-graph,
# not a fact of life — the retrieval invariant is only worth anything if measured.
printf '%s' "$OUT" | wc -c |
  awk '{printf "atlas-context: %s — %d bytes (~%d tokens) injected\n", "'"$SLUG"'", $1, $1/4}' >&2

printf '%s\n' "$OUT"

#!/bin/sh
# atlas-arch-context — emit the arch seat's reorientation briefing to stdout.
# A SessionStart hook (no matcher) injects this on startup, resume, clear AND compact —
# so an arch seat re-orients itself after a compaction instead of losing its bearings
# (method 1.23). Install in the arch seat's working dir (the vault checkout, or its
# launch dir); point $ATLAS_METHOD at the pinned method checkout.
set -e
: "${ATLAS_VAULT:=.}"                 # arch seat works the vault directly
: "${ATLAS_METHOD:=.atlas-method}"

# SessionStart payload arrives on stdin as JSON with "source"; read only off a pipe so a
# manual run never blocks on cat.
SRC=""
[ -t 0 ] || SRC=$(cat 2>/dev/null | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -1)

PY=$(command -v python3 || command -v python)
"$PY" -c "import yaml" 2>/dev/null || "$PY" -m pip install -q -r "$ATLAS_METHOD/tools/requirements.txt" 2>/dev/null || true
OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$ATLAS_VAULT" --emit-arch-context)

case "$OUT" in
  "# ATLAS-CONTEXT"*) ;;
  *) echo "atlas-arch-context: ERROR — no arch briefing produced (method too old for --emit-arch-context?)" >&2; exit 2 ;;
esac

case "$SRC" in
  compact|resume|clear)
    OUT=$(printf '%s\n\n%s' "> ⟳ **REORIENT — session was ${SRC}ed.** Read this arch-seat briefing in full before your next action; confirm your project and in-flight review queue, and resume. Do not ask the operator to re-orient you." "$OUT") ;;
esac

printf '%s' "$OUT" | wc -c | awk '{printf "atlas-arch-context: %d bytes (~%d tokens) injected\n", $1, $1/4}' >&2
printf '%s\n' "$OUT"

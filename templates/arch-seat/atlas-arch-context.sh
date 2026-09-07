#!/bin/sh
# atlas-arch-context — emit the arch seat's reorientation briefing to stdout.
# A SessionStart hook (no matcher) injects this on startup, resume, clear AND compact —
# so an arch seat re-orients itself after a compaction instead of losing its bearings
# (method 1.23). Install in the arch seat's working dir (the vault checkout, or its
# launch dir); point $ATLAS_METHOD at the pinned method checkout.
set -e
# Which sibling is the vault? Resolved, not assumed (1.24.3): the operator's arch seat
# launches in a dir holding BOTH Atlas-<P> and Nav-<P>. The fingerprint of a project
# vault is registry/io-graph.yml — a Nav vault never has one. Order: explicit env >
# .atlas-arch.conf (written at install) > the unique fingerprinted sibling > cwd.
LD=$(cd "$(dirname -- "$0")" && pwd)
if [ -z "${ATLAS_VAULT:-}" ] && [ -f "$LD/.atlas-arch.conf" ]; then
  # shellcheck disable=SC1091
  . "$LD/.atlas-arch.conf"
fi
if [ -z "${ATLAS_VAULT:-}" ]; then
  if [ -f "$LD/registry/io-graph.yml" ]; then ATLAS_VAULT="$LD"; else
    FOUND=""
    for _d in "$LD"/*/; do
      [ -f "${_d}registry/io-graph.yml" ] || continue
      if [ -n "$FOUND" ]; then FOUND="MULTI"; break; fi
      FOUND="${_d%/}"
    done
    if [ "$FOUND" = "MULTI" ]; then
      echo "atlas-arch: several vaults beside $LD — set ATLAS_VAULT (or .atlas-arch.conf) to pick one" >&2
    elif [ -n "$FOUND" ]; then ATLAS_VAULT="$FOUND"; fi
  fi
fi
: "${ATLAS_VAULT:=.}"
: "${ATLAS_METHOD:=.atlas-method}"

# SessionStart payload arrives on stdin as JSON with "source"; read only off a pipe so a
# manual run never blocks on cat.
# Bounded stdin read (1.25.1, blocks finding): non-terminal stdin is not proof of data —
# an open-empty pipe made cat hang forever. Never a bare cat.
hook_payload() {
  [ -t 0 ] && return 0
  if command -v timeout >/dev/null 2>&1; then timeout 2 cat 2>/dev/null || true
  else _l=""; if read -t 2 -r _l 2>/dev/null; then printf '%s' "$_l"; fi; fi
}
SRC=$(hook_payload | sed -n 's/.*"source"[[:space:]]*:[[:space:]]*"\([a-z]*\)".*/\1/p' | head -1)

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

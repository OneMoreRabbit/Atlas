#!/bin/sh
# atlas-arch-context — print the head of the arch seat's briefing; write the rest to files.
# A SessionStart hook (no matcher) injects this on startup, resume, clear AND compact —
# so an arch seat re-orients itself after a compaction instead of losing its bearings
# (method 1.23). Install in the arch seat's working dir (the vault checkout, or its
# launch dir); point $ATLAS_METHOD at the pinned method checkout.
#
# The runtime carries at most 10,000 characters from one hook; over that it keeps the
# first 2,000 and does not ask the agent to read the rest. So stdout is a short head: the
# list of files to read, then what must always be in context. The content is in
# ATLAS-CONTEXT.d/ beside this script, rewritten at every start (1.35.9).
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
# ATLAS_METHOD must resolve to a real method checkout — never build a garbage path
# from an empty base (1.26.1: '//.atlas-method' died on every arch seat when the
# installer dropped the key). Conf > env > <vault>/.atlas-method > launch-dir sibling.
[ -n "${ATLAS_METHOD:-}" ] || ATLAS_METHOD="$ATLAS_VAULT/.atlas-method"
[ -f "$ATLAS_METHOD/tools/atlas_validate.py" ] || ATLAS_METHOD="$LD/Atlas"
if [ ! -f "$ATLAS_METHOD/tools/atlas_validate.py" ]; then
  echo "atlas-arch-context: ERROR — no method checkout found. Set ATLAS_METHOD=\"<path to Atlas clone>\" in $LD/.atlas-arch.conf" >&2
  exit 2
fi

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

# The briefing files. Local-only: excluded if the launch dir is itself a git repo.
ART="$LD/ATLAS-CONTEXT.d"
rm -rf "$ART"
if [ -d "$LD/.git" ] && ! grep -qs '^ATLAS-CONTEXT.d/$' "$LD/.git/info/exclude" 2>/dev/null; then
  mkdir -p "$LD/.git/info" && echo 'ATLAS-CONTEXT.d/' >> "$LD/.git/info/exclude"
fi
# Only pass the flag if the method checkout's validator knows it (as atlas-context.sh).
HELP=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" --help 2>/dev/null || true)
set -- "$ATLAS_VAULT" --emit-arch-context
PARTS=""
case "$HELP" in *"--parts-dir"*) PARTS=1; set -- "$@" --parts-dir "$ART" ;; esac
OUT=$("$PY" "$ATLAS_METHOD/tools/atlas_validate.py" "$@")

case "$OUT" in
  "# ATLAS-CONTEXT"*) ;;
  *) echo "atlas-arch-context: ERROR — no arch briefing produced (method too old for --emit-arch-context?)" >&2; exit 2 ;;
esac

# TOP is this script's own lines: it leads the head.
TOP=""
case "$SRC" in compact|resume|clear)
  if [ -f "${ATLAS_METHOD:-}/templates/reorient.md" ]; then
    TOP=$(cat "$ATLAS_METHOD/templates/reorient.md")
  else
    TOP="> REORIENT — session was $SRC. Re-orient from durable state before your next action: your briefing, repos, bridge, needs, contracts. Read, don't recall."
  fi ;;
esac

# Cross-vault needs (1.27.2): needs addressed to this arch seat but filed in OTHER vaults
# — the estate's --refresh keeps ~/.atlas/needs-open.md current. With briefing files it is
# listed among them and read in place; without, it is carried in the briefing.
NEEDS_FILE="${HOME:-~}/.atlas/needs-open.md"
if [ -z "$PARTS" ] && [ -s "$NEEDS_FILE" ]; then
  OUT=$(printf '%s\n\n---\n\n# Needs addressed to me from other vaults (read in place)\n\n%s' "$OUT" "$(cat "$NEEDS_FILE")")
fi

# ---- what the hook prints (1.35.9) -------------------------------------------------
WHOLE="$OUT"
[ -z "$TOP" ] || WHOLE=$(printf '%s\n\n%s' "$TOP" "$OUT")
HEAD=""
if [ -n "$PARTS" ]; then
  HEAD=$(printf '%s\n' "$WHOLE" | "$PY" "$ATLAS_METHOD/tools/atlas_validate.py" --compose-head \
    --parts-dir "$ART" \
    --also-read "$NEEDS_FILE=Needs addressed to you, filed in other vaults") || HEAD=""
fi
# The floor: this hook never prints more than the runtime carries. Reached when the
# method checkout predates 1.35.9 (the whole briefing is in $WHOLE) or the step above
# failed. A short briefing is printed as it is; a long one goes to one file and the
# hook prints where it is.
if [ -z "$HEAD" ]; then
  [ -z "$PARTS" ] || WHOLE=$(printf '%s\n\n%s' "# ATLAS-CONTEXT: read these files before you act

> **This text is only the head of your briefing.** The rest is in the \`.md\` files at the top of \`$ART\`, written fresh at this session start. **Read every one now, in full, in name order, before your next action.**" "$WHOLE")
  if [ "$(printf '%s' "$WHOLE" | wc -c)" -le 9000 ]; then
    HEAD="$WHOLE"
  else
    mkdir -p "$ART"
    printf '%s\n' "$WHOLE" > "$ART/0-briefing.md"
    HEAD="# ATLAS-CONTEXT: read this file before you act

> **This text is only the head of your briefing.** A session-start hook carries at most 10,000 characters. The whole briefing is in one file, written fresh at this session start. **Read it now, in full, before your next action:**
>
> \`$ART/0-briefing.md\`"
    [ -z "$TOP" ] || HEAD=$(printf '%s\n\n%s' "$HEAD" "$TOP")
    echo "atlas-arch-context: briefing written whole to $ART/0-briefing.md (the method checkout predates 1.35.9, or the head could not be composed)" >&2
  fi
  printf '%s' "$HEAD" | wc -c | awk '{printf "atlas-arch-context: head %d bytes in the hook\n", $1}' >&2
fi
printf '%s\n' "$HEAD"

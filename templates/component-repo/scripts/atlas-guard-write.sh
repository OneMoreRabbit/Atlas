#!/bin/sh
# atlas-guard-write — PreToolUse guard. Denies writes into the vault outside this
# component's outbox: golden rule 2 made mechanical locally, mirroring the CI path
# guard in templates/vault-ci/atlas-guard.yml.
#
# NOTE: the hook payload arrives on stdin, so the python below must be passed with
# -c, never a heredoc — a heredoc would consume stdin and the guard would silently
# allow everything.
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"

PY=$(command -v python3 || command -v python)

P=$("$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("__ATLAS_PARSE_ERROR__")
    raise SystemExit
ti = d.get("tool_input") or {}
print(ti.get("file_path") or ti.get("notebook_path") or "")
')

# A guard that cannot parse its input denies, never allows (AAC-method §9).
if [ "$P" = "__ATLAS_PARSE_ERROR__" ]; then
  "$PY" -c '
import json
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Atlas write guard could not parse the hook payload - failing closed. Retry the write; if it persists, the guard or harness is broken and needs fixing before vault writes resume.",
}}))
'
  exit 0
fi
[ -n "$P" ] || exit 0   # parsed fine, no path field — not a file write

# Normalise Windows paths: Claude Code passes backslash paths on Windows, and an
# unnormalised path would silently match nothing — allowing every vault write.
P=$(printf '%s' "$P" | tr '\\' '/')
V=$(printf '%s' "$ATLAS_VAULT" | tr '\\' '/')
R=$(printf '%s' "$ATLAS_REPO_ROOT" | tr '\\' '/')

# Which checkouts are "the vault"? Not only $ATLAS_VAULT (the .atlas clone inside the
# code repo): a both-hats or arch seat edits the SIBLING checkout in its launch dir
# (Atlas-<P> beside Nav-<P>, 1.24.3), and a guard that governed one while the seat wrote
# the other was inert on exactly the writes it exists for — while --verify said PASS
# (DiscoCat finding, 2026-09-08). Resolve every candidate the arch scripts already know:
# $ATLAS_VAULT, .atlas-arch.conf, and any launch-dir sibling carrying registry/io-graph.yml.
VAULTS="$V"
SLUGS="$SLUG"          # this seat's slugs — own, plus any wired sibling at the launch dir
LD=$(printf '%s' "${ATLAS_LAUNCH_DIR:-}" | sed "s|^\$HOME|$HOME|" | tr '\\' '/')
if [ -n "$LD" ] && [ -d "$LD" ]; then
  if [ -f "$LD/.atlas-arch.conf" ]; then
    _av=$(sed -n 's/^ATLAS_VAULT="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "$LD/.atlas-arch.conf" | tr -d '\r' | head -1)
    [ -n "$_av" ] && VAULTS="$VAULTS
$_av"
  fi
  for _d in "$LD"/*/; do
    [ -f "${_d}registry/io-graph.yml" ] && VAULTS="$VAULTS
${_d%/}"
    # sibling code repos wired to the SAME vault are members of ONE seat (1.28.3,
    # arc-platform): the write guard allows the UNION of their slugs, as the briefing
    # already covers all their components. Two per-repo guards each scoped to one slug
    # denied each other's outbox, leaving a two-component seat unable to write either.
    [ -f "${_d}.atlas.conf" ] || continue
    _sv=$(sed -n 's/^ATLAS_VAULT_REMOTE="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "${_d}.atlas.conf" | tr -d '
' | head -1)
    [ "$_sv" = "$ATLAS_VAULT_REMOTE" ] || continue
    _ss=$(sed -n 's/^SLUG="\{0,1\}\([^"]*\)"\{0,1\}$/\1/p' "${_d}.atlas.conf" | tr -d '
' | head -1)
    [ -n "$_ss" ] && SLUGS="$SLUGS
$_ss"
  done
fi

# Find the vault this write lands in (if any). Writes outside every vault — the seat's
# own code, other repos — are not the guard's business.
REL=""
for _vr in $(printf '%s\n' "$VAULTS" | sort -u); do
  [ -n "$_vr" ] || continue
  case "$P" in
    *"/$_vr/"*) REL=${P#*"/$_vr/"}; break ;;
    "$_vr"/*)   REL=${P#"$_vr"/};   break ;;
  esac
done
[ -n "$REL" ] || exit 0                          # not a vault write

# Both-hats mode (1.24.5, orchestrator brief): a single-seat project's one agent is its
# vault's architecture AND its component's author. DECLARED, never inferred —
# ATLAS_ROLE="both" in .atlas.conf, reviewable in git. Scope is the union and nothing
# more; an ordinary component seat (ATLAS_ROLE unset or "component") is exactly as
# constrained as before. Transitional by design: the moment the vault gains a second
# component, the seat goes back to one hat (see AAC-method §9, the migration).
# the component this write targets, if any
_comp=""
case "$REL" in components/*/*) _comp=${REL#components/}; _comp=${_comp%%/*} ;; esac
for _s in $(printf '%s\n' "$SLUGS" | sort -u); do
  [ -n "$_s" ] && [ "$_comp" = "$_s" ] && exit 0     # a component of THIS seat: allowed
done
case "$REL" in
  architecture/proposals/*) exit 0 ;;
  registry/io-graph.yml)    exit 0 ;;
esac
if [ "${ATLAS_ROLE:-component}" = "both" ]; then
  case "$REL" in
    architecture/*) exit 0 ;;
  esac
fi

"$PY" -c '
import json, sys
slugs, rel = sys.argv[1], sys.argv[2]
first = slugs.split(", ")[0]
comp = "|".join(slugs.split(", ")) if ", " in slugs else slugs
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": (
        f"Atlas golden rule 2 - this seat ({slugs}) writes only to components/{{{comp}}}/**, an additive "
        f"architecture/proposals/NNNN-*.md, or its own edges in registry/io-graph.yml. "
        f"Refused: {rel}. If you need something that lives here, do not widen the write: "
        f"raise it in components/{first}/docs/needs/ with a `to:` naming the owner, or open "
        f"an ADR if it is shared architecture."),
}}))
' "$(printf '%s\n' "$SLUGS" | sort -u | grep -v '^$' | tr '\n' ',' | sed 's/,$//;s/,/, /g')" "$REL"
exit 0

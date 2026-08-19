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
    print("")
    raise SystemExit
ti = d.get("tool_input") or {}
print(ti.get("file_path") or ti.get("notebook_path") or "")
')
[ -n "$P" ] || exit 0

# Normalise Windows paths: Claude Code passes backslash paths on Windows, and an
# unnormalised path would silently match nothing — allowing every vault write.
P=$(printf '%s' "$P" | tr '\\' '/')
V=$(printf '%s' "$ATLAS_VAULT" | tr '\\' '/')

case "$P" in
  *"/$V/"*) REL=${P#*"/$V/"} ;;
  "$V"/*)   REL=${P#"$V"/}   ;;
  *) exit 0 ;;                                    # not a vault write
esac

case "$REL" in
  components/"$SLUG"/*)     exit 0 ;;
  architecture/proposals/*) exit 0 ;;
  registry/io-graph.yml)    exit 0 ;;
esac

"$PY" -c '
import json, sys
slug, rel = sys.argv[1], sys.argv[2]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": (
        f"Atlas golden rule 2 - {slug} writes only to components/{slug}/**, an additive "
        f"architecture/proposals/NNNN-*.md, or its own edges in registry/io-graph.yml. "
        f"Refused: {rel}. If you need something that lives here, do not widen the write: "
        f"raise it in components/{slug}/docs/needs/ with a `to:` naming the owner, or open "
        f"an ADR if it is shared architecture."),
}}))
' "$SLUG" "$REL"
exit 0

#!/bin/sh
# atlas-test-guard — PreToolUse write guard for a TEST seat (method 1.30.10, §10).
# Scope: tests/ at the vault root, components/<name>/tests/, and its own outbox
# components/test/docs/**. Never architecture/, never component code. Fail-closed
# on unparseable input, like every write guard.
set -e
CONF="$(dirname -- "$0")/.atlas-test.conf"
[ -f "$CONF" ] && . "$CONF"
: "${ATLAS_VAULT:?atlas-test-guard: ATLAS_VAULT unset}"
PY=$(command -v python3 || command -v python)
P=$("$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("__ATLAS_PARSE_ERROR__"); raise SystemExit
ti = d.get("tool_input") or {}
print(ti.get("file_path") or ti.get("notebook_path") or "")
')
if [ "$P" = "__ATLAS_PARSE_ERROR__" ]; then
  "$PY" -c 'import json; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Atlas test guard could not parse the hook payload - failing closed. Retry the write."}}))'
  exit 0
fi
[ -n "$P" ] || exit 0
P=$(printf '%s' "$P" | tr '\\' '/'); V=$(printf '%s' "$ATLAS_VAULT" | tr '\\' '/')
case "$P" in
  "$V"/*|*"/$V/"*) REL=${P#*"$V"/} ;;
  *) exit 0 ;;                                   # outside the vault: not our business
esac
case "$REL" in
  tests/*) exit 0 ;;
  components/*/tests/*) exit 0 ;;
  components/test/docs/*) exit 0 ;;
esac
"$PY" -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny",
  "permissionDecisionReason": (
    "Atlas test seat writes tests/ at the vault root, components/<name>/tests/, and "
    "its own outbox (components/test/docs/) - nothing else (method 1.30.10). Refused: "
    + sys.argv[1] + ". A defect you found is a need addressed to the owning component; "
    "an architecture concern goes to your arch seat.")}}))
' "$REL"
exit 0

#!/bin/sh
# atlas-arch-write — PreToolUse write guard for the ARCH seat (method 1.28.14).
# Until the product seat existed the arch seat was unfenced in its vault — one owner,
# nothing to fence. Now the vault can have two owners, and the boundary must hold BOTH
# ways (orchestrator finding, Labs bring-up): the arch seat never writes product/**,
# and in the Nav vault it writes _bridge/** only — never _bridge/tasks.md, which is
# the operator's file (one writer per file, 1.28.11). Fail-closed on unparseable input.
set -e
LD=$(cd "$(dirname -- "$0")" && pwd)
# shellcheck disable=SC1091
[ -z "${ATLAS_VAULT:-}" ] && [ -f "$LD/.atlas-arch.conf" ] && . "$LD/.atlas-arch.conf"
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
  "$PY" -c 'import json; print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "Atlas arch write guard could not parse the hook payload - failing closed. Retry the write."}}))'
  exit 0
fi
[ -n "$P" ] || exit 0
P=$(printf '%s' "$P" | tr '\\' '/')

deny() {
  "$PY" -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny", "permissionDecisionReason": sys.argv[1]}}))
' "$1"
  exit 0
}

# The project vault: everything is the arch seat's EXCEPT product/** (1.28.14).
V=$(printf '%s' "${ATLAS_VAULT:-}" | tr '\\' '/')
if [ -n "$V" ]; then
  case "$P" in
    "$V"/product/*|*"/$V/product/"*)
      deny "Atlas: product/** belongs to the product seat (method 1.28.14) - the boundary holds both ways. To reshape a requirement, raise a need addressed to your project's product seat (<project>-product); arch's word on COST is final, but the text is theirs." ;;
    "$V"/*|*"/$V/"*) exit 0 ;;
  esac
fi

# The Nav vault (a launch-dir sibling with _bridge/ and no io-graph): _bridge/** only,
# and never the operator's tasks.md.
for _d in "$LD"/*/; do
  [ -d "${_d}_bridge" ] || continue
  [ -f "${_d}registry/io-graph.yml" ] && continue
  N=${_d%/}
  case "$P" in
    "$N"/_bridge/*|*"/$N/_bridge/"*) exit 0 ;;
    "$N"/*|*"/$N/"*)
      deny "Atlas: in the Nav vault the arch seat writes _bridge/** only (method 1.28.11). Refused: ${P#*"$N"/}." ;;
  esac
done
exit 0

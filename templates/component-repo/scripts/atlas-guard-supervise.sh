#!/bin/sh
# atlas-guard-supervise — PreToolUse (Bash) guard for SUPERVISED mode (method 1.26.10).
# A supervised seat develops and tests freely, but the act of PUBLISHING or RELEASING
# pauses for the operator: this routes publish/release-shaped Bash commands to the
# harness's interactive approve/deny prompt (permissionDecision "ask"). Autonomous mode
# does nothing here — oversight is the write model, CI and the hub. Never gates
# development; only the git/gh operations that reach other seats.
set -e
# shellcheck source=atlas-common.sh disable=SC1091
. "$(dirname -- "$0")/atlas-common.sh"

[ "${ATLAS_MODE:-supervised}" = "supervised" ] || exit 0   # autonomous: no gate

PY=$(command -v python3 || command -v python)
CMD=$("$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("__PARSE__"); raise SystemExit
print((d.get("tool_input") or {}).get("command", ""))
')
# Parse failure: do not gate. The operator is present in supervised mode, and CI +
# review still apply — over-blocking Bash on a bad payload would be maddening.
[ "$CMD" = "__PARSE__" ] && exit 0
[ -n "$CMD" ] || exit 0

if printf '%s' "$CMD" | grep -Eq 'git[[:space:]]+push|gh[[:space:]]+pr[[:space:]]+(create|merge)|gh[[:space:]]+release[[:space:]]+create|git[[:space:]]+tag[[:space:]]+(-a|-s|-m|v[0-9])'; then
  "$PY" - "$SLUG" <<'PYEOF'
import json, sys
slug = sys.argv[1]
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": (
        f"Atlas supervised mode ({slug}): this publishes or releases. Confirm with the "
        "operator before it lands \u2014 is the issue agreed, and was this tested against "
        "the REAL environment (not a fixture)? Declare ATLAS_MODE=autonomous in "
        ".atlas.conf to lift supervision."),
}}))
PYEOF
fi
exit 0

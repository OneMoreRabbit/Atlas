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

_PL=$("$PY" -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    print("__ATLAS_PARSE_ERROR__")
    raise SystemExit
ti = d.get("tool_input") or {}
print(ti.get("file_path") or ti.get("notebook_path") or "")
body = (ti.get("content") or ti.get("new_string") or "").replace("\r", "")
import re
m = re.search(r"^(?:to|addressed-to):\s*(.+)$", body, re.M)
print(m.group(1).strip() if m else "")
')
P=$(printf '%s\n' "$_PL" | sed -n 1p)
TO=$(printf '%s\n' "$_PL" | sed -n 2p)

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
addr_check() {
  # to:-lookup at authoring (1.30.6, operator): a needs doc whose addressee the LOCAL
  # io-graph cannot resolve is refused, with the valid list in the message. Local
  # files only — never the network; the estate audit covers cross-vault drift.
  # Advisory-hard: OUR parse failure allows (the path-scope guard above stays the
  # fail-closed one); a confident no-match denies.
  case "$REL" in components/*/docs/needs/*.md) ;; *) return 0 ;; esac
  [ -n "$TO" ] || return 0                    # Edit without frontmatter in the diff: CI backstops
  _rc=0
  "$PY" - "$V" "$TO" <<'PYEOF2' || _rc=$?
import re, sys
vault, to = sys.argv[1], sys.argv[2]
try:
    g = open(vault + "/registry/io-graph.yml", encoding="utf-8").read()
except OSError:
    sys.exit(0)                                # no graph readable: allow, CI decides
pn = (re.search(r"^project:\s*([\w.-]+)", g, re.M) or [None, ""])[1].lower()
comps, roles = [], []
for m in re.finditer(r"^\s*-\s+(?:component|slug):\s*([\w.-]+)(.*?)(?=^\s*-\s|\Z)", g, re.M | re.S):
    name = m.group(1).lower()
    r = re.search(r"^\s*role:\s*([\w-]+)", m.group(2), re.M)
    (roles if (r and r.group(1).lower() != "component") else comps).append(
        (name, r.group(1).lower() if r else "component"))
ok = {"atlas", "method", "arch", "nav"}
ok |= {n for n, _ in comps} | {n for n, _ in roles}
if pn:
    ok |= {f"{pn}.component.{n}" for n, _ in comps}
    ok |= {f"{pn}.{r}" for _, r in roles} | {f"{pn}.arch", f"{pn}-arch", pn}
ext_pj = set()
for m in re.finditer(r"provider:\s*([\w.-]+)", g):
    ok.add(m.group(1).lower())
for m in re.finditer(r"(?:Atlas|Nav)-([\w.-]+?)(?:\.git)?\s*$", g, re.M):
    pj = m.group(1).lower(); ext_pj.add(pj)
    ok |= {pj, f"{pj}-arch", f"{pj}.arch"}
toks = [x.strip().lower().strip('[]').strip(chr(39)).strip(chr(34)) for x in re.split(r'[,;]', to) if x.strip().strip('[]')]
bad = [x for x in toks
       if x not in ok and not any(x.startswith(p + ".") for p in ext_pj)]
if not toks or not bad:
    sys.exit(0)
valid = ", ".join(sorted(ok - {"arch", "nav"}))
import json
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
  "permissionDecision": "deny",
  "permissionDecisionReason": (
    "Atlas addressing (1.30.6): '" + ", ".join(bad) + "' resolves to nothing in this "
    "vault's io-graph. Addressable from here: " + valid + ". A new external must be "
    "declared by your arch seat before you can address it (AAC-method 5).")}}))
sys.exit(3)
PYEOF2
  [ "$_rc" = 3 ] && exit 0 || return 0
}
for _s in $(printf '%s\n' "$SLUGS" | sort -u); do
  if [ -n "$_s" ] && [ "$_comp" = "$_s" ]; then
    addr_check
    exit 0                                     # a component of THIS seat: allowed
  fi
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

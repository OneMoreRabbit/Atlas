#!/bin/sh
# atlas-common — resolve the repo root, load .atlas.conf, set defaults.
# Sourced by every atlas-* script; not run directly.
ATLAS_REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -f "$ATLAS_REPO_ROOT/.atlas.conf" ]; then
  echo "atlas: no .atlas.conf at $ATLAS_REPO_ROOT (copy .atlas.conf.example and set SLUG)" >&2
  exit 2
fi
# shellcheck disable=SC1091
. "$ATLAS_REPO_ROOT/.atlas.conf"
# A CRLF .atlas.conf must fail closed, not skew the guards: a trailing \r in
# ATLAS_VAULT makes the write guard's path match miss and allow everything.
SLUG=$(printf '%s' "${SLUG:-}" | tr -d '\r')
ATLAS_VAULT=$(printf '%s' "${ATLAS_VAULT:-}" | tr -d '\r')
ATLAS_METHOD=$(printf '%s' "${ATLAS_METHOD:-}" | tr -d '\r')
ATLAS_VAULT_REMOTE=$(printf '%s' "${ATLAS_VAULT_REMOTE:-}" | tr -d '\r')
ATLAS_METHOD_REMOTE=$(printf '%s' "${ATLAS_METHOD_REMOTE:-}" | tr -d '\r')
if [ -z "${SLUG:-}" ] || [ "${SLUG:-}" = "<slug>" ]; then
  echo "atlas: SLUG is unset in .atlas.conf" >&2
  exit 2
fi
: "${ATLAS_VAULT:=.atlas}"
: "${ATLAS_METHOD:=.atlas-method}"
: "${ATLAS_METHOD_REMOTE:=https://github.com/OneMoreRabbit/Atlas.git}"
# --- shared vault-graph resolution -------------------------------------------------
# The io-graph must be read from the WORK branch, never from whatever the clone has
# checked out: a publish branch's `method:` pin and policy are by definition equal or
# stale (agent-skeleton finding, 2026-08-26). Defined here so atlas-sync and
# atlas-context agree — a child process cannot export back to its parent.
atlas_graph_text() {
  if [ -n "${1:-}" ] &&
     git -C "$ATLAS_VAULT" cat-file -e "origin/$1:registry/io-graph.yml" 2>/dev/null; then
    git -C "$ATLAS_VAULT" show "origin/$1:registry/io-graph.yml"
  else
    cat "$ATLAS_VAULT/registry/io-graph.yml" 2>/dev/null || true
  fi
}

atlas_branching_work() {
  printf '%s\n' "$1" |
    awk '/^branching:/{b=1;next} b&&/^[^ ]/{b=0} b&&/work:/{gsub(/[^A-Za-z0-9._\/-]/,"",$2); print $2; exit}'
}

# -> the policy work branch, resolved from the work branch itself where possible
atlas_work_branch() {
  _bw=$(atlas_branching_work "$(atlas_graph_text)")
  atlas_branching_work "$(atlas_graph_text "$_bw")"
}

ATLAS_SENTINEL="${TMPDIR:-/tmp}/atlas-nag.$(printf '%s' "$ATLAS_REPO_ROOT" | cksum | cut -d' ' -f1)"
export ATLAS_REPO_ROOT ATLAS_VAULT ATLAS_METHOD ATLAS_METHOD_REMOTE ATLAS_SENTINEL SLUG

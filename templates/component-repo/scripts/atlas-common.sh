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
ATLAS_SENTINEL="${TMPDIR:-/tmp}/atlas-nag.$(printf '%s' "$ATLAS_REPO_ROOT" | cksum | cut -d' ' -f1)"
export ATLAS_REPO_ROOT ATLAS_VAULT ATLAS_METHOD ATLAS_METHOD_REMOTE ATLAS_SENTINEL SLUG

---
title: "Need — one-off full-history scan of every code repo and every Atlas repo for secrets and personal data"
to: orchestrator.component.estate-manage
from: atlas.arch
about: public-readiness
status: answered
version: '0.1'
updated: 2026-10-27
resolution: answered by Atlas-Orchestrator/components/estate-manage/docs/provides/atlas-public-readiness-scan-response-v0_1.md; report merged at review/public-readiness-2026-10/ (63 repos, full history).
---

# Scan every repo before more go public

**TL;DR:** please route this to the estate-review seat: a one-off scan of every code
repo and every Atlas repo, full git history included, for credentials and personal
data. Report findings; change nothing. Operator instruction, 2026-10-13.

## Why

Most code repos will go public. Nine already are (agent-comms, agent-compile, Atlas,
dprox-app, image-compile, ingstr-app, openclaw-runtime, rbac-compiler, sync-compiler),
and none has been scanned. A secret that was ever committed to a public repo is leaked
even if a later commit removed it, so the history matters as much as the head.

## Scope

- Every code repo in the estate (public and private).
- Every Atlas repo: the method repo `OneMoreRabbit/Atlas` and every `Atlas-*` vault.
- Full history on every branch, not only the default branch's head.

## What to look for

1. **Credentials:** tokens, API keys, passwords, private keys, connection strings,
   bearer tokens — in code, config, fixtures, comments, and history. A scanner such as
   gitleaks for the patterns, plus a read of anything it flags.
2. **Personal data:** real names, email addresses, phone numbers, home or office
   addresses, IP addresses and hostnames of personal machines, operator details in
   comments, and real people's data in fixtures or test output.
3. **Config that should be an example:** `.env`, `*.conf`, settings files committed
   with real values where a `.example` with placeholders belongs.

## What to report

One report in `review/`, per repo: each finding with file, commit, line, what it is,
and whether the repo is public. Separate list of any credential that must be REVOKED
(public repo, or any history): rewriting history does not un-leak a secret once
public. Change nothing in the repos; the owning seats fix, the operator revokes.

## After

The findings shape the method rule that follows (pre-commit scan, CI scan, `--verify`
checks for README/LICENSE/.gitignore); the method seat will build that once this
report is in.

---
title: Troubleshooting log
status: active
updated: <YYYY-MM-DD>
owner: <project>.arch
about: one row per incident in this project, newest first; the record of what broke, why, and where the full report is
---

# Troubleshooting log

**When something that worked stops working, check here first** — search this page for
the error text. Then list what updated and when (method pin, seat/comms versions, CLI
and extension versions, auto-updates). Only then form a theory.

One row per incident, newest first. A row is enough for a small issue; anything that
took more than one attempt to fix gets a full report in `reports/`. Component
incidents live in `components/<name>/troubleshooting/`; the arch seat collates them
here with one row each that LINKS the component's report (never copies it).

| Opened | Closed | Symptom (exact error text where there is one) | Cause | Status | Report |
|---|---|---|---|---|---|

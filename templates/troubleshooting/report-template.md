---
title: "<what broke, in one line — the symptom, not the theory>"
status: open                # open | fixed | tolerated | recurred
opened: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
owner: <the address of whoever investigates — <project>.arch or <project>.component.<name>>
about: "<one sentence: symptom -> cause -> fix>"
versions: "<every relevant version at the time: method pin, seat, comms, CLI, extensions>"
---

# <title> — <opened> to <closed>

## In one paragraph
<What happened, what caused it, what fixed it. A reader who stops here should know
whether this is their problem.>

## Symptom
<Exact error text, verbatim, so a search finds it. What the user or seat saw.>

## Root cause
<The real cause, with the evidence that proves it — not the first plausible theory.>

## Fix
<The exact commands or edits, runnable as written. Which file, which repo, which seat.>

## Wrong turns
<Every explanation tried and abandoned, and why it was wrong. This section saves the
next person the most time.>

## How to tell if it is back
<The check that detects recurrence: a command, a grep, an observable symptom.>

## If tolerated
<Only for status: tolerated — why we live with it, and the condition that reverses
that decision.>

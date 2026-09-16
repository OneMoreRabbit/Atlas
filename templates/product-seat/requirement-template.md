---
id: R-0001                      # stable for life — citations use this, never the filename
title: "<one line: what the product must do, in domain language>"
status: draft                   # draft | proposed | accepted | superseded
version: '0.1'                  # moves with the PRODUCT release line (§4) — quoted
updated: <YYYY-MM-DD>
grounded_in:                    # REQUIRED — a requirement citing no direction and no
  - "<bridge item, user evidence, data, or observation of the running product>"
criteria:                       # acceptance criteria — testable, in the domain's language
  - id: AC1
    given: "<the situation>"
    when: "<the action>"
    then: "<the observable outcome>"
  - id: AC2
    given: ""
    when: ""
    then: ""
---

# R-0001 — <title>

## What and why
<The need, in the problem space. What the product must do and how you would know —
never how it is built. Domain terms only; the arch seat maps them to design.>

## Evidence
<Why this is real: the direction or observation behind `grounded_in`, expanded.>

## Out of scope
<What this requirement deliberately does not ask for.>

<!--
File as product/requirements/R-NNNN-<slug>.md. The id never changes; the filename
never carries a version. A contract that satisfies a criterion cites it:
satisfies: ["R-0001.AC1@0.1"]. When arch rules the cost too high, it raises a need
to <project>-product and this doc is reshaped — arch has the final word on cost.
-->

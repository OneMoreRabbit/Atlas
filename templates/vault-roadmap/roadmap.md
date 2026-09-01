---
title: <Project> product roadmap
interface: <project>-roadmap
version: '0.2'
status: draft
updated: 2026-09-01
owner: nav (direction) / arch (record)

# Timeline config — everything about HOW and WHEN it renders lives here.
timeline:
  title: <Project> product roadmap
  axis_format: '%b %Y'        # try '%b %y' if labels crowd
  tick_interval: 2month       # 1month | 2month | 1quarter ...

# Dates in ONE place. Give a release `start` + `end`, or `start` + `duration`,
# or just a `duration` to chain it after the previous one — so moving a single
# date shifts everything downstream without editing another line.
releases:
  - {name: MVP,    status: shipped,     start: 2026-05-01, end: 2026-08-31}
  - {name: Beta 1, status: in progress, start: 2026-09-01, duration: 6w}
  # - {name: v0.1, status: next,        duration: 7w}   # chains after Beta 1
---

# <Project> product roadmap

What <Project> ships, by release. **The bullet lists below are the source**; the
timeline is generated from them plus the `releases:` config in the frontmatter,
by `meta/roadmap_timeline.py` — never hand-edit the diagram.

> **Direction is @nav's.** This file is the durable *record* of direction agreed
> on the bridge, not the place it is decided. Everything below `MVP` is a draft
> scaffold built from what the vault evidences; correct it and I will keep it.

**Status of this draft:** shipped items are drawn from accepted ADRs, published
contracts and component maturity in `registry/io-graph.yml`. Unshipped items are
drawn from open proposals in `architecture/proposals/`. Release names, dates and
anything not evidenced by the vault are **proposals awaiting @nav**.

<!-- roadmap:timeline:begin -->
<!-- roadmap:timeline:end -->


## MVP

- [ ] <the smallest thing that is genuinely usable>
- [x] <tick items as they ship — the diagram counts these>

## Beta 1

- [ ] <...>

---

## How to maintain this

1. Edit the bullets. `- [x]` = done, `- [ ]` = outstanding.
2. Dates, order and status live in the frontmatter `releases:` list — one place.
   A release takes `start` + `end`, `start` + `duration`, or just `duration` to
   chain after the one before it. Statuses that colour the bar: `shipped` (done),
   `in progress` (active), `at risk` (crit); anything else renders plain.
   Rendering is tuned in `timeline:` (`axis_format`, `tick_interval`).
3. Regenerate the timeline from the vault root:

   ```bash
   python3 meta/roadmap_timeline.py           # rewrite the diagram
   python3 meta/roadmap_timeline.py --check   # exit 1 if stale
   ```

Feature counts in the diagram are derived from the checkboxes, so progress shows
without anyone maintaining a percentage.

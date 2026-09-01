#!/usr/bin/env python3
"""Regenerate the roadmap's Mermaid timeline from its frontmatter + bullets.

Split of concerns:
  * frontmatter `timeline:` and `releases:`  — WHEN and how it renders (config)
  * `## <Release>` sections + `- [ ]` bullets — WHAT ships (content)
  * the block between the roadmap:timeline markers — DERIVED, never hand-edited

Dates are configured in one place. A release may give explicit `start`/`end`,
or a `duration` that chains after the previous release, so shifting one date
moves everything downstream without touching another line.

Usage   python3 meta/roadmap_timeline.py            (from the vault root)
        python3 meta/roadmap_timeline.py --check    (exit 1 if stale — for CI)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

DOC = Path("roadmap.md")
BEGIN, END = "<!-- roadmap:timeline:begin -->", "<!-- roadmap:timeline:end -->"
# Mermaid tags by status; anything unlisted renders as a plain future bar.
TAGS = {"shipped": "done", "in progress": "active", "at risk": "crit"}
DEFAULTS = {"title": "Product roadmap", "date_format": "YYYY-MM-DD",
            "axis_format": "%b %Y", "tick_interval": "2month"}


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split on a line that is exactly '---'. Splitting on the bare string would
    also match a '---' that merely ends a comment line inside the frontmatter."""
    m = re.match(r"^---\n(?P<fm>.*?)\n---\n(?P<body>.*)\Z", text, re.S)
    if not m:
        raise SystemExit("roadmap_timeline: no YAML frontmatter")
    return yaml.safe_load(m.group("fm")) or {}, m.group("body")


def counts(body: str) -> dict[str, tuple[int, int]]:
    """Feature tallies per '## <Name>' section, from its checkbox bullets."""
    out, cur = {}, None
    for line in body.splitlines():
        if line.startswith("## "):
            cur = line[3:].strip()
            out.setdefault(cur, [0, 0])
        elif cur and line.startswith("- ["):
            out[cur][1] += 1
            if line.startswith("- [x]"):
                out[cur][0] += 1
    return {k: tuple(v) for k, v in out.items()}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower()) or "r"


def gantt(fm: dict, tally: dict) -> str:
    cfg = {**DEFAULTS, **(fm.get("timeline") or {})}
    releases = fm.get("releases") or []
    lines = ["```mermaid", "gantt",
             f"    title {cfg['title']}",
             f"    dateFormat {cfg['date_format']}",
             f"    axisFormat {cfg['axis_format']}"]
    if cfg.get("tick_interval"):
        lines.append(f"    tickInterval {cfg['tick_interval']}")
    lines.append("")

    prev = None
    for r in releases:
        name = str(r["name"])
        done, total = tally.get(name, (0, 0))
        tag = TAGS.get(str(r.get("status", "")).lower(), "")
        rid = slug(name)
        if r.get("start"):
            when = f"{r['start']}, {r['end']}" if r.get("end") else f"{r['start']}, {r['duration']}"
        elif prev:
            when = f"after {prev}, {r['duration']}"
        else:
            raise SystemExit(f"roadmap_timeline: '{name}' needs a start (it is first)")
        label = f"{name} ({done}/{total})" if total else name   # ':' would split the row
        fields = ", ".join(x for x in (tag, rid, when) if x)
        lines += [f"    section {name}", f"    {label} :{fields}", ""]
        prev = rid
    lines.append("```")
    return "\n".join(lines)


def main() -> int:
    if not DOC.exists():
        print(f"roadmap_timeline: {DOC} not found — run from the vault root", file=sys.stderr)
        return 2
    text = DOC.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print("roadmap_timeline: timeline markers missing", file=sys.stderr)
        return 2
    fm, body = split_frontmatter(text)
    if not fm.get("releases"):
        print("roadmap_timeline: no `releases:` in frontmatter", file=sys.stderr)
        return 2
    tally = counts(body)
    for r in fm["releases"]:
        if r["name"] not in tally:
            print(f"roadmap_timeline: WARN release '{r['name']}' has no '## {r['name']}' "
                  "section — it will render with no feature count", file=sys.stderr)

    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{BEGIN}\n{gantt(fm, tally)}\n{END}{tail}"

    if "--check" in sys.argv:
        stale = new != text
        print("roadmap timeline is stale — run meta/roadmap_timeline.py" if stale
              else "roadmap timeline is current")
        return 1 if stale else 0

    DOC.write_text(new, encoding="utf-8")
    done = sum(d for d, _ in tally.values())
    total = sum(t for _, t in tally.values())
    print(f"regenerated timeline — {len(fm['releases'])} releases, {done}/{total} features complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

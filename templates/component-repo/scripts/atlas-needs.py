#!/usr/bin/env python3
"""atlas-needs — tell THIS seat what the estate has addressed to it (method 1.27.2).

A seat's briefing renders needs addressed to it from inside its own vault. A need filed
in ANOTHER vault is correctly placed (one home, the author's outbox) and is EXTERNAL
to the seat that owes it: the in-vault briefing cannot render it — a location fact, not a
read receipt (the method has no notion of "seen"). Measured 2026-09-13: 58 of 78 open needs
estate-wide
(ansible-platform finding; tool designed and first deployed by the orchestrator, adopted
here). This reads the estate's needs register, filters to this seat, and keeps a local
file the briefing and the Stop guard read.

  --refresh   fetch the register, write ~/.atlas/needs-open.md   (the ESTATE schedules this)
  --show      exit 2 with a short message IF the file changed     (Stop guard, every turn)
  (no flag)   print the file                                       (by hand)

Split on purpose: --refresh touches the network; --show never does (two stats). A seat
persists for days, so SessionStart is too rare to rely on — the briefing carries the
file at start/compaction, and --show surfaces CHANGES at turn end.

NEVER WAKES A SEAT. --refresh writes a file. --show speaks only inside a turn the seat is
already taking, as a Stop block (exit 2) — the only way a Stop hook reaches the model;
an exit-0 print never reaches it. Told once per change, not every turn.

INERT WITHOUT A REGISTER. ATLAS_NEEDS_REGISTER unset (a single-vault project) → does
nothing. Cross-vault needs only exist at estate scale, where the orchestrator publishes
the register (method §10, registries) and every seat holds the vault-read token.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

HOME = Path(os.environ.get("HOME", "~")).expanduser()
STATE = HOME / ".atlas"
OUT = STATE / "needs-open.md"
STAMP = STATE / "needs-shown"
EXTRA_SLUGS = STATE / "needs-slugs"           # operator override, one per line
REPO = Path(__file__).resolve().parent.parent  # scripts/.. = the wired repo


def conf(path: Path) -> dict:
    d = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r'^([A-Z_]+)="?([^"\r\n]*)"?\s*$', line)
            if m:
                d[m.group(1)] = m.group(2)
    except OSError:
        pass
    return d


def my_slugs(explicit: str | None) -> list[str]:
    if explicit:
        return [s.strip() for s in explicit.split(",") if s.strip()]
    c = conf(REPO / ".atlas.conf")
    slugs = [c["SLUG"]] if c.get("SLUG") else []
    # a seat holding N wired repos answers to all of them (launch-dir siblings, 1.21)
    launch = c.get("ATLAS_LAUNCH_DIR", "").replace("$HOME", str(HOME))
    if launch and Path(launch).is_dir():
        for d in Path(launch).iterdir():
            s = conf(d / ".atlas.conf").get("SLUG")
            if s and s not in slugs:
                slugs.append(s)
    # a both-hats seat is ALSO its vault's arch: answer to `arch` and `<project>-arch`
    # (1.27.5; ATLAS_PROJECT in .atlas.conf, else nothing project-specific is assumed)
    if c.get("ATLAS_ROLE", "").strip().lower() == "both":
        slugs.append("arch")
        pj = c.get("ATLAS_PROJECT", "").strip().lower()
        if pj:
            slugs.append(f"{pj}-arch")
    if EXTRA_SLUGS.exists():
        slugs += [l.strip() for l in EXTRA_SLUGS.read_text().splitlines() if l.strip()]
    return slugs


def register_url() -> str:
    return conf(REPO / ".atlas.conf").get("ATLAS_NEEDS_REGISTER", "") \
        or os.environ.get("ATLAS_NEEDS_REGISTER", "")


def token_for(url: str) -> str | None:
    """The seat's own credential routing (git credential fill) — never a hardcoded file."""
    m = re.match(r"https?://([^/]+)", url)
    if not m:
        return None
    try:
        out = subprocess.run(["git", "credential", "fill"], input=f"protocol=https\nhost={m.group(1)}\n\n",
                             capture_output=True, text=True, timeout=10).stdout
        for line in out.splitlines():
            if line.startswith("password="):
                return line[len("password="):]
    except (OSError, subprocess.SubprocessError):
        pass
    return os.environ.get("GITHUB_TOKEN")


def addressed_to_me(value, slugs: list[str]) -> bool:
    """Token-aware: `a; b`, `a, b`, a YAML list, trailing punctuation all resolve."""
    vals = value if isinstance(value, list) else [value]
    toks = []
    for v in vals:
        head = re.split(r"[(\[]", str(v), 1)[0]
        toks += [t.strip().lower() for t in re.split(r"[;,/]|\band\b", head) if t.strip()]
    return any(s.lower() in toks for s in slugs)


def fetch(url: str) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.raw+json",
                                               "User-Agent": "atlas-needs"})
    tok = token_for(url)
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def refresh(explicit_slugs: str | None) -> int:
    url = register_url()
    if not url:
        return 0                                   # single-vault project: inert
    slugs = my_slugs(explicit_slugs)
    if not slugs:
        print("atlas-needs: no slug found (.atlas.conf or --slugs)", file=sys.stderr)
        return 0
    try:
        reg = fetch(url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        print(f"atlas-needs: refresh failed ({e}); keeping the existing file", file=sys.stderr)
        return 0
    reg_date = str(reg.get("updated", ""))[:10]
    mine = [n for n in reg.get("needs", [])
            if not str(n.get("status", "open")).lower().startswith(RETIRED)
            and addressed_to_me(n.get("addressee", ""), slugs)]
    ext = sum(1 for n in mine if n.get("vault"))
    L = [f"# Needs addressed to this seat ({', '.join(slugs)})", "",
         f"_Estate register dated {reg_date}. **{len(mine)} open**, all EXTERNAL — filed in "
         "other vaults, so this vault's briefing cannot render them (a location fact, not a "
         "read state). Read each where it lives (you hold the vault-read token); answer in "
         "your own provides/ with `responds_to:`._", ""]
    try:
        age = (date.today() - datetime.strptime(reg_date, "%Y-%m-%d").date()).days
        if age > 3:
            L += [f"> **The register is {age} days old** — it has stopped being rebuilt; "
                  "treat this list as possibly incomplete.", ""]
    except ValueError:
        pass
    if mine:
        L += ["| need | from | vault | updated |", "|---|---|---|---|"]
        L += [f"| {n.get('title', n.get('path', '?'))} <br>`{n.get('path', '?')}` | "
              f"{n.get('author', '?')} | {n.get('vault', '?')} | {n.get('updated', '?')} |"
              for n in mine]
    else:
        L.append("_none open._")
    STATE.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"atlas-needs: {len(mine)} open need(s) addressed to {', '.join(slugs)} -> {OUT}",
          file=sys.stderr)
    refresh_consumers(slugs)
    return 0


RETIRED = ("resolved", "closed", "done", "superseded")   # a need is live unless retired (method RETIRED_STATUSES); 1.27.8
CONS = STATE / "consumers.md"


def edges_register_url() -> str:
    return conf(REPO / ".atlas.conf").get("ATLAS_EDGES_REGISTER", "") \
        or os.environ.get("ATLAS_EDGES_REGISTER", "")


def refresh_consumers(slugs: list[str]) -> None:
    """Cross-vault CONSUMERS (method 1.27.4, agent-compile finding): a provider cannot see,
    from its own vault, which other vaults pin its contracts — an absent edge and no
    consumer look identical. If the estate publishes an edges register (every vault's
    external: entries: {vault, consumer, provider, interface, pinned}), list the entries
    whose provider is one of this seat's slugs. Inert without the register."""
    url = edges_register_url()
    if not url:
        return
    try:
        reg = fetch(url)
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
        print(f"atlas-needs: consumers refresh failed ({e}); keeping the existing file",
              file=sys.stderr)
        return
    mine = [e for e in reg.get("edges", [])
            if str(e.get("provider", "")).lower() in [s.lower() for s in slugs]]
    L = [f"# Contracts of this seat ({', '.join(slugs)}) pinned in other vaults", "",
         f"_Estate edges register dated {str(reg.get('updated',''))[:10]}. "
         f"**{len(mine)} cross-vault consumer edge(s).** Who breaks if you change an "
         "interface: these, plus this vault's own edges._", ""]
    if mine:
        L += ["| interface | consumer | vault | pinned |", "|---|---|---|---|"]
        L += [f"| `{e.get('interface','?')}` | {e.get('consumer','?')} | {e.get('vault','?')} | "
              f"{e.get('pinned','unpinned')} |" for e in mine]
    else:
        L.append("_none — no other vault pins a contract of yours (as far as the register knows)._")
    STATE.mkdir(parents=True, exist_ok=True)
    CONS.write_text("\n".join(L) + "\n", encoding="utf-8")


def show() -> int:
    """Stop guard: exit 2 (block + message) ONLY when the file changed since last shown."""
    if not OUT.exists():
        return 0
    payload = "" if sys.stdin.isatty() else sys.stdin.read(4096)
    if '"stop_hook_active": true' in payload or '"stop_hook_active":true' in payload:
        return 0
    cur = OUT.read_text(encoding="utf-8")
    if STAMP.exists() and STAMP.read_text(encoding="utf-8") == cur:
        return 0
    STAMP.write_text(cur, encoding="utf-8")
    n = cur.count("\n| ") - (1 if "| need |" in cur else 0)
    print(f"Atlas: {max(n, 0)} EXTERNAL need(s) addressed to you — filed in other vaults, so "
          f"your in-vault briefing cannot render them (a location fact, not unread). Read "
          f"{OUT} (also in your briefing), then finish.", file=sys.stderr)
    return 2


if __name__ == "__main__":
    args = sys.argv[1:]
    slugs = None
    if "--slugs" in args:
        slugs = args[args.index("--slugs") + 1]
    if "--refresh" in args:
        sys.exit(refresh(slugs))
    if "--show" in args:
        sys.exit(show())
    sys.stdout.write(OUT.read_text(encoding="utf-8") if OUT.exists() else "atlas-needs: no file yet — run --refresh\n")

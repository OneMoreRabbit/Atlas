#!/usr/bin/env python3
"""atlas_init — install the Atlas code-repo half into a component repo.

Usage:  python atlas_init.py --component <name> --vault-remote <url>
                             [--project <name>] [--repo <path>] [--force]

Installs templates/component-repo/ from this method repo into the target code repo
(component-init.md §4 as one command): the atlas-* scripts, a filled-in .atlas.conf,
a substituted AGENTS.md, the .gitignore entries, the /atlas-publish command, and one
hook file per agent runtime, rendered from templates/seat-hooks.json (merged into an
existing file rather than overwriting it).

Existing files are left alone unless --force; the scripts are meant to be re-copied
this way when atlas-sync reports self-drift. Stdlib only — no dependencies.

Bootstrap note: the method repo must be present to run this once —
    git clone --depth 1 <method-remote> .atlas-method
    python .atlas-method/tools/atlas_init.py --component <name> --vault-remote <url>
after which scripts/atlas-sync.sh manages both clones per session.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "component-repo"
ARCH_TEMPLATES = TEMPLATES.parent / "arch-seat"
PRODUCT_TEMPLATES = TEMPLATES.parent / "product-seat"
TEST_TEMPLATES = TEMPLATES.parent / "test-seat"
ROLE_TEMPLATES = {"arch": ARCH_TEMPLATES, "product": PRODUCT_TEMPLATES, "test": TEST_TEMPLATES}
SEAT_HOOKS = TEMPLATES.parent / "seat-hooks.json"
SEAT_INSTRUCTIONS = TEMPLATES.parent / "seat-instructions.md"
PAYLOAD_HELPER = "atlas-payload.py"   # every write guard calls it; it sits beside them
GITIGNORE_MARKER = "# --- Atlas ---"  # append-once marker for both fragments
# the component scripts --verify requires present, committed and equal to the templates
COMPONENT_SCRIPTS = ("atlas-common.sh", "atlas-sync.sh", "atlas-context.sh",
                     "atlas-guard-write.sh", "atlas-guard-publish.sh", "atlas-needs.py",
                     "atlas-discard-views.sh", PAYLOAD_HELPER)


def derive_project(remote: str) -> str:
    name = remote.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name[len("Atlas-"):] if name.startswith("Atlas-") else name


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def install(dst: Path, text: str, force: bool, written: list) -> bool:
    if dst.exists() and not force:
        print(f"  skip   {dst} (exists — --force overwrites)")
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    written.append(dst)
    print(f"  write  {dst}")
    return True


def seat_hooks() -> dict:
    """templates/seat-hooks.json: the hook moments, which script each role runs at each,
    and how each agent runtime wires a moment. The one place a runtime is described."""
    return json.loads(read(SEAT_HOOKS))


def render_hooks(role: str, runtime: str, root: str) -> dict:
    """One runtime's hook file for one role. `root` is where the role's scripts live, as
    the hook command should spell it.

    In the repo that is the runtime's own repo-root expression: the repo's hook file is
    COMMITTED, and a machine path there would break every other clone (AAC-method §9).
    At a launch dir outside the repo it is an absolute path; that file is outside any
    repo, so it is machine-local by construction.
    """
    table = seat_hooks()
    r, rt = table["roles"][role], table["runtimes"][runtime]
    base = root + ("/" + r["dir"] if r["dir"] else "")
    hooks: dict = {}
    for moment, script in r["hooks"]:
        wire = rt["wiring"].get(moment)
        if not wire:
            continue                           # this runtime has no such moment
        cmd = f'sh "{base}/{script}"'
        if moment == "shell" and not rt["ask"]:
            # the runtime cannot put a question to the operator: the supervise guard
            # refuses once instead (atlas-guard-supervise.sh)
            cmd = "ATLAS_NO_ASK=1 " + cmd
        if moment == "prompt":
            cmd += " 2>/dev/null || true"      # a style line must never block a prompt
        entry = {"matcher": wire["matcher"]} if "matcher" in wire else {}
        entry["hooks"] = [{"type": "command", "command": cmd, **wire.get("handler", {})}]
        hooks.setdefault(wire["event"], []).append(entry)
    return {"hooks": hooks}


def repo_root_exprs() -> list:
    return [rt["repo_root"] for rt in seat_hooks()["runtimes"].values()]


def resolve_cmd(cmd: str, root: Path) -> str:
    """A hook command with every runtime's repo-root expression replaced by `root`."""
    for expr in repo_root_exprs():
        cmd = cmd.replace(expr, root.as_posix())
    return cmd


def seat_block(role: str, launch_dir: Path, root: str) -> str | None:
    """The AGENTS.md block for a role: what a runtime with no hooks (or with hooks it has
    not been allowed to run yet) needs to do by hand. None for a role with no briefing."""
    r = seat_hooks()["roles"][role]
    if "briefing" not in r:
        return None
    by = {moment: script for moment, script in r["hooks"]}
    base = root + ("/" + r["dir"] if r["dir"] else "")
    return (read(SEAT_INSTRUCTIONS).strip("\n")
            .replace("<role>", role).replace("<briefing>", r["briefing"])
            .replace("<scope>", r["scope"]).replace("<launch dir>", launch_dir.as_posix())
            .replace("<context>", f"{base}/{by['session-start']}")
            .replace("<gate>", f"{base}/{by['turn-end']}"))


def write_seat_block(role: str, launch_dir: Path, root: str, written: list) -> None:
    """Insert the role's block into AGENTS.md at the launch dir, or replace it between
    its markers. Everything outside the markers is the seat's own and is never touched."""
    block = seat_block(role, launch_dir, root)
    if block is None:
        return
    dst = launch_dir / "AGENTS.md"
    start, end = f"<!-- atlas:{role}-seat", f"<!-- /atlas:{role}-seat -->"
    text = read(dst) if dst.exists() else ""
    if start in text and end in text[text.index(start):]:
        a = text.index(start)
        new = text[:a] + block + text[text.index(end, a) + len(end):]
    else:
        gap = "" if not text else "\n" if text.endswith("\n") else "\n\n"
        new = text + gap + block + "\n"
    if new == text:
        print(f"  ok     {dst} (Atlas {role}-seat block present)")
        return
    with dst.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(new)
    written.append(dst)
    print(f"  write  {dst} (Atlas {role}-seat block; the rest of the file is untouched)")


def print_runtime_notes(launch_dir: Path) -> None:
    for name, rt in seat_hooks()["runtimes"].items():
        if rt.get("after_install"):
            print(f"  note   {name}: " + rt["after_install"].replace("<launch dir>", str(launch_dir)))


def portable_launch_dir(launch_dir: Path) -> str:
    """$HOME-relative when possible: .atlas.conf is COMMITTED, and the seat
    convention (clone parent under $HOME) is shared across machines while the
    absolute path is not (AAC-method §9)."""
    try:
        return "$HOME/" + launch_dir.relative_to(Path.home()).as_posix()
    except ValueError:
        print(f"  WARN   launch dir {launch_dir} is outside $HOME — stored as a "
              "machine path in the committed .atlas.conf")
        return launch_dir.as_posix()


def persist_launch_dir(repo: Path, launch_dir: Path, written: list) -> None:
    """Record where the agent launches, so --verify checks the real launch dir
    instead of self-validating the default (the run-2 false-green)."""
    conf = repo / ".atlas.conf"
    if not conf.exists():
        return
    value = portable_launch_dir(launch_dir)
    text = read(conf)
    line = f'ATLAS_LAUNCH_DIR="{value}"'
    if re.search(r"^ATLAS_LAUNCH_DIR=", text, re.MULTILINE):
        text = re.sub(r"^ATLAS_LAUNCH_DIR=.*$", line, text, count=1, flags=re.MULTILINE)
    else:
        text = (text.rstrip("\n")
                + "\n\n# Where the agent actually starts (persisted by atlas_init"
                + " --launch-dir;\n# read by --verify). $HOME-relative on purpose —"
                + " this file is committed.\n" + line + "\n")
    with conf.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    written.append(conf)
    print(f"  conf   ATLAS_LAUNCH_DIR={value}")


def conf_launch_dir(repo: Path) -> Path | None:
    conf = repo / ".atlas.conf"
    if not conf.exists():
        return None
    m = re.search(r'^ATLAS_LAUNCH_DIR="?([^"\r\n]+)"?', read(conf), re.MULTILINE)
    if not m:
        return None
    raw = m.group(1).replace("$HOME", str(Path.home()))
    return Path(raw).expanduser().resolve()


def prune_dup_hooks(launch_dir: Path, hook_file: str, keep_root: Path, event: str,
                    script: str) -> int:
    """One <script> hook per launch dir for <event>: keep keep_root's entry, drop other
    repos'. Seat scripts (context, write guard) cover their siblings, so one entry serves
    the whole seat; duplicates double-inject the briefing (1.21/1.27.4) or, for the write
    guard, deny each other's outbox (1.28.3, arc-platform). Idempotent."""
    dst = launch_dir / hook_file
    if not dst.exists():
        return 0
    try:
        data = json.loads(read(dst))
    except json.JSONDecodeError:
        return 0
    entries = data.get("hooks", {}).get(event, [])
    kept, removed = [], 0
    pat = re.compile(r'"([^"]+)/scripts/' + re.escape(script) + r'"')
    for entry in entries:
        m = [pat.search(h.get("command", "")) for h in entry.get("hooks", [])]
        if any(x for x in m) and not any(x and Path(x.group(1)) == keep_root for x in m):
            removed += 1
            continue
        kept.append(entry)
    if removed:
        data.setdefault("hooks", {})[event] = kept
        dst.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return removed


def any_context_hook(launch_dir: Path, exclude_root: Path):
    """ANY session-start atlas-context hook installed at this launch dir from another
    repo, in any runtime's hook file. One is enough: since 1.21 the context script emits
    a seat briefing covering every wired sibling it discovers, so a second hook doubles
    the whole injection. That repo owns the launch-dir hooks for the whole seat."""
    for rt in seat_hooks()["runtimes"].values():
        dst = launch_dir / rt["file"]
        if not dst.exists():
            continue
        try:
            entries = json.loads(read(dst)).get("hooks", {}).get(
                rt["wiring"]["session-start"]["event"], [])
        except (json.JSONDecodeError, KeyError):
            continue
        for entry in entries:
            for hook in entry.get("hooks", []):
                m = re.search(r'"([^"]+)/scripts/atlas-context\.sh"', hook.get("command", ""))
                if m and Path(m.group(1)) != exclude_root:
                    return Path(m.group(1))
    return None


def merge_settings(target: Path, hook_file: str, tpl: dict, force: bool, written: list,
                   own: tuple = ()) -> None:
    """Merge the hooks into an existing hook file; never clobber. `own` is the path
    strings that mark an entry as this install's (replaced, never appended)."""
    dst = target / hook_file
    if not dst.exists():
        install(dst, json.dumps(tpl, indent=2) + "\n", force, written)
        return
    current = json.loads(read(dst))
    hooks = current.setdefault("hooks", {})
    added = removed = 0

    def is_this_repos(entry) -> bool:
        cmds = " ".join(h.get("command", "") for h in entry.get("hooks", []))
        return "atlas-" in cmds and any(o in cmds for o in own)

    for event, entries in tpl["hooks"].items():
        bucket = hooks.setdefault(event, [])
        # idempotency per repo: replace, never append, this repo's own entries
        stale = [e for e in bucket if is_this_repos(e) and e not in entries]
        for e in stale:
            bucket.remove(e)
            removed += 1
        for entry in entries:
            if entry not in bucket:
                bucket.append(entry)
                added += 1
    if added or removed:
        with dst.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(current, indent=2) + "\n")
        written.append(dst)
        print(f"  merge  {dst} (+{added}/-{removed} hook entries)")
    else:
        print(f"  ok     {dst} (hooks already wired)")


def conf_value(conf: Path, key: str) -> str | None:
    if not conf.exists():
        return None
    m = re.search(rf'^{key}="?([^"\r\n]+)"?', read(conf), re.MULTILINE)
    return m.group(1).replace("$HOME", str(Path.home())) if m else None


def seat_scripts(role: str) -> list:
    """(name, template) for every script an arch, product or test seat keeps at its
    launch dir: the role's hook scripts plus the payload helper its write guard calls."""
    names = [script for _, script in seat_hooks()["roles"][role]["hooks"]] + [PAYLOAD_HELPER]
    return [(n, ROLE_TEMPLATES[role] / n if (ROLE_TEMPLATES[role] / n).exists()
             else TEMPLATES / "scripts" / n) for n in names]


def copy_seat_scripts(role: str, launch_dir: Path, force: bool, written: list,
                      keep_differing: bool = False) -> None:
    for name, src in seat_scripts(role):
        dst = launch_dir / name
        if keep_differing and dst.exists() and not force and read(dst) != read(src):
            print(f"  skip   {dst} exists and differs — re-run with --force to overwrite")
            continue
        dst.write_text(read(src), encoding="utf-8", newline="\n")
        dst.chmod(0o755)
        written.append(dst)
        print(f"  write  {dst}")


def wire_seat(role: str, launch_dir: Path, force: bool, written: list) -> None:
    """Hooks for an arch, product or test seat: every runtime's hook file at the launch
    dir, with absolute paths (the scripts sit beside them), plus the AGENTS.md block."""
    table = seat_hooks()
    scripts = [script for _, script in table["roles"][role]["hooks"]]
    own = tuple(f"{root}/{s}" for s in scripts for root in {launch_dir.as_posix(), str(launch_dir)})
    for name, rt in table["runtimes"].items():
        merge_settings(launch_dir, rt["file"], render_hooks(role, name, launch_dir.as_posix()),
                       force, written, own)
    write_seat_block(role, launch_dir, launch_dir.as_posix(), written)


def fire_write(cmd: str, sample: dict, path: str, cwd: Path) -> int | None:
    """Run a write-guard hook command the way a runtime would, with that runtime's
    sample payload naming `path`. -> the exit code, None if it could not run."""
    def fill(v):
        if isinstance(v, str):
            return v.replace("<path>", path)
        if isinstance(v, dict):
            return {k: fill(x) for k, x in v.items()}
        return v
    payload = dict(fill(sample), cwd=str(cwd))
    try:
        return subprocess.run(["sh", "-c", cmd], input=json.dumps(payload), cwd=str(cwd),
                              capture_output=True, text=True, timeout=60).returncode
    except (OSError, subprocess.SubprocessError):
        return None


def check_launch_hooks(check, role: str, launch_dir: Path, vault: Path | None,
                       component: str = "", block: bool = True) -> None:
    """The launch-dir rung of --verify, once per runtime: the hook file wires each of
    the role's scripts exactly once, the scripts resolve, and the style line and the
    write guard are FIRED as wired (1.33.1, orchestrator finding: a hook that blocked
    every prompt passed a verify that only counted it). The write guard gets the
    runtime's own payload shape, at a path it must allow and a path it must refuse."""
    table = seat_hooks()
    r = table["roles"][role]
    for rt_name, rt in table["runtimes"].items():
        f = launch_dir / rt["file"]
        check(f.exists(), f"{rt_name}: hook file at the LAUNCH dir",
              "" if f.exists() else f"{f} missing — re-run atlas_init")
        if not f.exists():
            continue
        try:
            hooks = json.loads(read(f)).get("hooks", {})
        except json.JSONDecodeError as exc:
            check(False, f"{rt_name}: {rt['file']} parses", str(exc))
            continue
        for moment, script in r["hooks"]:
            wire = rt["wiring"].get(moment)
            if not wire:
                continue
            # a component's hooks may be a sibling member's (one set serves the seat);
            # a launch-dir role's are its own
            needles = ([f"/{r['dir']}/{script}"] if r["dir"] else
                       [f"{launch_dir.as_posix()}/{script}", f"{launch_dir}/{script}"])
            cmds = [h.get("command", "") for e in hooks.get(wire["event"], [])
                    for h in e.get("hooks", [])
                    if any(n in h.get("command", "") for n in needles)]
            check(len(cmds) == 1, f"{rt_name}: exactly one {script} hook ({wire['event']})",
                  "" if len(cmds) == 1 else "not wired — re-run atlas_init" if not cmds
                  else f"{len(cmds)} found — re-run atlas_init to prune")
            if not cmds:
                continue
            cmd = resolve_cmd(cmds[0], launch_dir)
            m = re.search(r'"([^"]*atlas-[a-z-]+\.sh)"', cmd)
            if m:
                check(Path(m.group(1)).exists(), f"{rt_name}: {script} resolves",
                      "" if Path(m.group(1)).exists() else
                      f"{m.group(1)} — launched elsewhere? re-run with --launch-dir")
            if moment == "prompt":
                try:
                    pr = subprocess.run(["sh", "-c", cmd], capture_output=True, text=True,
                                        stdin=subprocess.DEVNULL, timeout=10)
                    fired = pr.returncode == 0 and "HOUSE STYLE" in pr.stdout
                except (OSError, subprocess.SubprocessError):
                    fired = False
                check(fired, f"{rt_name}: style hook FIRES and emits the style line",
                      "" if fired else f"command failed as wired: {cmd[:100]}")
            if moment == "write" and vault is not None:
                for want, key, word in ((0, "allowed", "ALLOWS"), (2, "refused", "REFUSES")):
                    rel = r[key].replace("<component>", component)
                    rc = fire_write(cmd, rt["sample_write"], (vault / rel).as_posix(), launch_dir)
                    check(rc == want, f"{rt_name}: write guard {word} {rel}",
                          "" if rc == want else f"exit {rc}, expected {want} — the guard as "
                          "wired is not this method version's; re-run atlas_init with --force")
    if block and "briefing" in r:
        ag = launch_dir / "AGENTS.md"
        has = ag.exists() and f"<!-- atlas:{role}-seat" in read(ag)
        check(has, f"AGENTS.md at the launch dir carries the Atlas {role}-seat block",
              "" if has else "the fallback for a runtime that runs no hooks — re-run atlas_init")


def verify_seat(role: str, launch_dir: Path) -> int:
    """--verify for an arch, product or test seat at its launch dir. Reads and fires;
    writes nothing (1.34.8, idea.arch: --arch --verify re-installed the hooks)."""
    ok = True

    def check(good: bool, label: str, detail: str = "") -> None:
        nonlocal ok
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")

    r = seat_hooks()["roles"][role]
    print(f"atlas_init --{role} --verify: launch dir {launch_dir}")
    conf = launch_dir / f".atlas-{role}.conf"
    raw = conf_value(conf, "ATLAS_VAULT")
    vault = Path(raw) if raw else None
    good = vault is not None and (vault / "registry" / "io-graph.yml").exists()
    check(good, f"{conf.name} names the vault checkout",
          "" if good else f"{conf} — install with atlas_init --{role} first")
    missing = [n for n, _ in seat_scripts(role) if not (launch_dir / n).exists()]
    drifted = [n for n, src in seat_scripts(role)
               if (launch_dir / n).exists() and read(launch_dir / n) != read(src)]
    check(not missing, "seat scripts present at the launch dir",
          "MISSING: " + ", ".join(missing) + f" -- re-run atlas_init --{role}" if missing else "")
    check(not drifted, "seat scripts match this method checkout's templates",
          "DRIFTED: " + ", ".join(drifted) + f" -- re-run atlas_init --{role} --force" if drifted else "")
    check_launch_hooks(check, role, launch_dir, vault if good else None)
    if "briefing" in r:
        # The rung above "wired": the briefing script must SUCCEED from the launch dir
        # (1.28.2, arc-platform), run the way the runtime runs it.
        ctx = launch_dir / dict((m, s) for m, s in r["hooks"])["session-start"]
        try:
            run = subprocess.run(["sh", str(ctx)], cwd=str(launch_dir), stdin=subprocess.DEVNULL,
                                 capture_output=True, text=True, timeout=120)
            fired = run.returncode == 0 and r["briefing"] in run.stdout
            tail = (run.stderr.strip().splitlines() or [""])[-1][:140]
            check(fired, f"{ctx.name} runs from the launch dir, exits 0, emits a briefing",
                  "" if fired else f"exit {run.returncode}; {tail}")
        except (OSError, subprocess.SubprocessError) as exc:
            check(False, f"{ctx.name} runs", str(exc)[:140])
    print_runtime_notes(launch_dir)
    print(f"\natlas_init --{role} --verify: " + ("all checks passed" if ok else
          "FAILURES above — the hook layer is not live; fix before trusting the write guard"))
    return 0 if ok else 1


def verify(repo: Path, slug: str, launch_dir: Path | None) -> int:
    """End-to-end check that the hook layer will actually fire (decisions/0002).

    On disk != in force: a repo can carry .atlas.conf and AGENTS.md, report itself
    wired, and still have every hook inert because the agent launches somewhere else.
    """
    ok = True

    def check(good: bool, label: str, detail: str = "") -> None:
        nonlocal ok
        ok = ok and good
        print(f"  {'PASS' if good else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")

    defaulted = False
    if launch_dir is None:
        launch_dir = conf_launch_dir(repo)
        if launch_dir is not None:
            src = "from .atlas.conf ATLAS_LAUNCH_DIR"
        else:
            launch_dir, defaulted = repo, True
            src = "DEFAULTED to the repo"
    else:
        src = "from --launch-dir"
    print(f"atlas_init --verify: repo {repo}, launch dir {launch_dir} ({src})")
    if defaulted:
        print("  WARN  no --launch-dir given and no ATLAS_LAUNCH_DIR in .atlas.conf — "
              "verifying against the repo itself. If the agent actually launches "
              "elsewhere (a seat in the clone parent), this proves NOTHING: "
              "re-install with --launch-dir, which also persists it for future runs.")
    conf = repo / ".atlas.conf"
    check(conf.exists(), ".atlas.conf present", "" if conf.exists() else str(conf))
    if conf.exists():
        text = conf.read_text(encoding="utf-8")
        m = re.search(r'^COMPONENT="?([^"\r\n]*)"?', text, re.MULTILINE)
        legacy = re.search(r'^SLUG="?([^"\r\n]*)"?', text, re.MULTILINE)
        found = (m or legacy).group(1) if (m or legacy) else None
        check(found == slug, f".atlas.conf COMPONENT == {slug}", f"found {found!r}")
        if legacy and not m:
            print("  ◻ migration: .atlas.conf still uses SLUG= — re-run the installer "
                  "to write COMPONENT= (the fallback dies with the estate migration)")
        check("\r" not in text, ".atlas.conf has no CRLF", "add gitattributes.fragment")
    def tracked(name: str) -> bool:
        return subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", name],
                              capture_output=True).returncode == 0
    # committed means TRACKED (1.33.10, estate-monitor): an untracked file passed the
    # old existence check while git status said '??' — a false PASS on the exact word
    # the check printed.
    def clean(paths) -> bool:
        return subprocess.run(["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--"] + paths,
                              capture_output=True).returncode == 0
    # COMMITTED means tracked AND no uncommitted changes (1.34.1, agent-eco/ingstr: a
    # tracked file with every line modified and unstaged passed "committed"; on a seat
    # that never commits, the check could not fail - the checks-that-pass shape again).
    for _f in ("AGENTS.md", ".atlas.conf"):
        _ok = tracked(_f) and clean([_f])
        check(_ok, f"{_f} committed (tracked, no uncommitted changes)",
              "" if _ok else ("NOT tracked" if not tracked(_f) else "has UNCOMMITTED changes")
              + " — git add + commit it")
    _sc = [f"scripts/{n}" for n in COMPONENT_SCRIPTS if (repo / "scripts" / n).exists()]
    _sok = all(tracked(s) for s in _sc) and clean(_sc)
    check(_sok, "scripts/ committed (tracked, no uncommitted changes)",
          "" if _sok else "one or more atlas scripts are untracked or modified — git add + commit")
    # The hook files and the command the installer writes into the REPO (1.35.1,
    # agent-eco's sync-compile: --force rewrote them, the steps staged only
    # AGENTS.md/.atlas.conf/scripts/, verify looked only there - dirty tree, ALL PASS).
    # A launch-dir hook file is outside the repo and is not git's business.
    _hf = [rt["file"] for rt in seat_hooks()["runtimes"].values()]
    _cl = [c for c in _hf + [".claude/commands/atlas-publish.md"] if (repo / c).exists()]
    if _cl:
        _cok = all(tracked(c) for c in _cl) and clean(_cl)
        check(_cok, "hook files and commands committed (" + ", ".join(_cl) + ")",
              "" if _cok else "untracked or modified — git add "
              + " ".join(sorted({c.split("/")[0] + "/" for c in _cl}))
              + " + commit (the installer writes them)")
    # pushed: local-only check against the upstream tracking ref (no network); a WARN,
    # not a FAIL, because verify may legitimately run between commit and push
    _ab = subprocess.run(["git", "-C", str(repo), "rev-list", "--count", "@{u}..HEAD"],
                         capture_output=True, text=True)
    if _ab.returncode == 0 and _ab.stdout.strip() not in ("", "0"):
        print(f"  WARN  {_ab.stdout.strip()} commit(s) not pushed to the upstream branch — push them")
    # content, not presence (1.33.11, agent-eco: --force regressed a FILLED AGENTS.md
    # back to literal placeholders in the write-scope lines, four seats shipped it, and
    # presence/tracked checks cannot go red on it; after one unexamined commit the diff
    # is silent forever — this grep is the only detector)
    ag = repo / "AGENTS.md"
    if ag.exists():
        bad = [w for w in ("<component name>", "<component>", "<slug>") if w in read(ag)]
        check(not bad, "AGENTS.md carries no unresolved placeholders",
              "found " + ", ".join(bad) + " — re-run atlas_init --force (it fills them in "
              "place), then commit" if bad else "")
    drifted = []
    for name in COMPONENT_SCRIPTS:
        dst = repo / "scripts" / name
        check(dst.exists(), f"scripts/{name}")
        src = TEMPLATES / "scripts" / name
        if dst.exists() and src.exists() and read(dst) != read(src):
            drifted.append(name)
    # An upgrade without --force skips every drifted script and this verify still said
    # PASS while the seat ran 1.28.0 code under a 1.28.5 pin (1.28.6, arc-platform).
    # Compare bytes against the method checkout this verify runs from — the pinned one.
    check(not drifted, "scripts match this method checkout's templates",
          "DRIFTED: " + ", ".join(drifted) + " -- re-run atlas_init with --force" if drifted else "")
    # the publish steps are a copy too (1.35.5, sync-compile): an old one keeps old commands
    _pub = Path(".claude") / "commands" / "atlas-publish.md"
    if (repo / _pub).exists():
        _pok = read(repo / _pub) == read(TEMPLATES / _pub)
        check(_pok, f"{_pub.as_posix()} matches this method checkout's template",
              "" if _pok else "DRIFTED -- re-run atlas_init with --force")

    _v = Path(conf_value(conf, "ATLAS_VAULT") or ".atlas")
    # a launch dir outside the repo carries the AGENTS.md block; in the repo itself the
    # committed AGENTS.md already says it
    check_launch_hooks(check, "component", launch_dir, _v if _v.is_absolute() else repo / _v,
                       slug, block=launch_dir != repo)
    # The rung above "firing": the SessionStart script must SUCCEED. A registered hook
    # whose script exits non-zero on the healthy path passed every check here while
    # reporting failure at every session start (arc-platform platform seat, 2026-09-03).
    ctx = repo / "scripts" / "atlas-context.sh"
    if ctx.exists():
        try:
            r = subprocess.run(["sh", str(ctx)], cwd=repo, capture_output=True, text=True,
                               stdin=subprocess.DEVNULL,
                               timeout=300)
            good = r.returncode == 0 and "# ATLAS-CONTEXT" in r.stdout
            tail = (r.stderr.strip().splitlines() or [""])[-1][:140]
            check(good, "scripts/atlas-context.sh runs, exits 0, emits a briefing",
                  f"exit {r.returncode}; {tail}" if not good else
                  f"{len(r.stdout.encode()):,} bytes")
        except (OSError, subprocess.TimeoutExpired) as exc:
            check(False, "scripts/atlas-context.sh runs", str(exc)[:140])

    print_runtime_notes(launch_dir)
    print("\natlas_init --verify: " + ("all checks passed" if ok else
          "FAILURES above — the hook layer is not live; fix before trusting the write guard"))
    return 0 if ok else 1


def install_test(vault: Path, launch_dir: Path, force: bool) -> int:
    """Test-seat mode (1.30.10, §10): the tests/-scoped write guard at the launch dir,
    plus .atlas-test.conf and the role identity file. Deliberately minimal — a test
    seat re-orients from the vault it reads; no briefing machinery of its own."""
    if not (vault / "registry" / "io-graph.yml").exists():
        print(f"atlas_init --test: {vault} has no registry/io-graph.yml — point --repo "
              "at the project VAULT checkout", file=sys.stderr)
        return 2
    graph_text = read(vault / "registry" / "io-graph.yml")
    if not re.search(r"^\s*role:\s*test\s*$", graph_text, re.MULTILINE):
        print("  warn   the io-graph declares no `role: test` entry — ask the arch seat "
              "to add one (the seat is not yet declared, §10)")
    written: list = []
    copy_seat_scripts("test", launch_dir, force, written)
    tdir = vault / "components" / "test"
    (tdir / "docs").mkdir(parents=True, exist_ok=True)
    cmd = tdir / "component.md"
    if not cmd.exists():
        cmd.write_text(read(TEST_TEMPLATES / "test-component.md"), encoding="utf-8", newline="\n")
        print(f"  write  {cmd}")
    conf = launch_dir / ".atlas-test.conf"
    conf.write_text(f'ATLAS_VAULT="{vault}"\n', encoding="utf-8", newline="\n")
    print(f"  write  {conf}")
    wire_seat("test", launch_dir, force, written)
    print("atlas_init --test: installed — tests/-scoped write guard. Checking it:")
    return verify_seat("test", launch_dir)


def install_product(vault: Path, launch_dir: Path, force: bool, nav: str | None = None) -> int:
    """Product-seat mode (1.28.9, §10): installs the reorientation hook, the product/**
    write guard and the alignment gate into the launch dir, plus .atlas-product.conf.
    Deliberately simple — mirrors --arch without the arch briefing machinery."""
    if not (vault / "registry" / "io-graph.yml").exists():
        print(f"atlas_init --product: {vault} has no registry/io-graph.yml — point "
              "--repo at the project VAULT checkout", file=sys.stderr)
        return 2
    graph_text = read(vault / "registry" / "io-graph.yml")
    if not re.search(r"^product:", graph_text, re.MULTILINE):
        print("  warn   the io-graph declares no `product:` block — the seat is not yet "
              "declared (§10). Ask the arch seat to add `product: {enabled: true}`.")
    written: list = []
    copy_seat_scripts("product", launch_dir, force, written)
    (vault / "product" / "requirements").mkdir(parents=True, exist_ok=True)
    tpl = vault / "product" / "requirements" / "requirement-template.md"
    if not tpl.exists():
        tpl.write_text(read(PRODUCT_TEMPLATES / "requirement-template.md"),
                       encoding="utf-8", newline="\n")
        print(f"  write  {tpl} (copy per requirement as R-NNNN-<slug>.md)")
    conf = launch_dir / ".atlas-product.conf"
    kept = {}
    if conf.exists():
        for line in read(conf).splitlines():
            m = re.match(r'^([A-Z_]+)="?([^"]*)"?$', line)
            if m:
                kept[m.group(1)] = m.group(2)
    kept["ATLAS_VAULT"] = str(vault)
    if nav:
        kept["ATLAS_NAV"] = str(Path(nav).resolve())
    kept.setdefault("ATLAS_METHOD", str(Path(__file__).resolve().parent.parent))
    conf.write_text("".join(f'{k}="{v}"\n' for k, v in kept.items()),
                    encoding="utf-8", newline="\n")
    print(f"  write  {conf} (vault={kept['ATLAS_VAULT']})")
    # hooks live at the launch dir with absolute paths (the arch launch-dir lesson, 1.28.2)
    wire_seat("product", launch_dir, force, written)
    print("atlas_init --product: installed — reorientation, product/** write guard and "
          "alignment gate. Checking them:")
    # prove the hooks FIRE from the launch dir (the 1.28.2 rung), not just that files exist
    return verify_seat("product", launch_dir)


def install_arch(vault: Path, launch_dir: Path, force: bool) -> int:
    """Arch-seat mode (1.24.2): symmetric to the component install, keyed on role — an
    arch seat works the VAULT checkout and has no slug. Installs the reorientation hook
    (SessionStart -> atlas-arch-context.sh) and the alignment gate (Stop ->
    atlas-arch-guard.sh) into the launch dir, with scripts beside the settings."""
    if not (vault / "registry" / "io-graph.yml").exists():
        print(f"atlas_init --arch: {vault} has no registry/io-graph.yml — point --repo "
              "at the project VAULT checkout (the arch seat's working copy)",
              file=sys.stderr)
        return 2
    written: list = []
    copy_seat_scripts("arch", launch_dir, force, written, keep_differing=True)
    wire_seat("arch", launch_dir, force, written)
    # MERGE the conf, never clobber it (1.26.1, canary catch: the rewrite dropped an
    # existing ATLAS_METHOD and every arch seat's reorientation died on a garbage path).
    # The installer also knows the method checkout it is running from — record it.
    conf = launch_dir / ".atlas-arch.conf"
    kept = {}
    if conf.exists():
        for line in read(conf).splitlines():
            m = re.match(r'^([A-Z_]+)="?([^"\r\n]*)"?\s*$', line)
            if m:
                kept[m.group(1)] = m.group(2)
    kept["ATLAS_VAULT"] = str(vault)
    # ATLAS_METHOD must be the PINNED method the seat resolves, not a sibling clone on a
    # branch (1.28.2, arc-platform): prefer a .atlas-method worktree beside the vault or in
    # the launch dir; else the checkout the installer ran from — and warn if that looks like
    # a full clone (Atlas) rather than a pinned worktree (.atlas-method).
    invoked = Path(__file__).resolve().parent.parent
    method = None
    for cand in (vault / ".atlas-method", launch_dir / ".atlas-method"):
        if (cand / "tools" / "atlas_init.py").exists():
            method = cand.resolve(); break
    if method is None:
        method = invoked
        if invoked.name != ".atlas-method":
            print(f"  warn   ATLAS_METHOD={invoked} is not a `.atlas-method` pinned worktree; "
                  "the arch briefing will compile with whatever this checkout is on. Run "
                  "atlas_init from the pinned .atlas-method, or set ATLAS_METHOD by hand.")
    kept.setdefault("ATLAS_METHOD", str(method))
    conf.write_text("".join(f'{k}="{v}"\n' for k, v in kept.items()),
                    encoding="utf-8", newline="\n")
    print(f"  write  {conf} (vault={kept['ATLAS_VAULT']}, method={kept['ATLAS_METHOD']})")
    print("atlas_init --arch: installed — reorientation, alignment gate and write guard; "
          "the first two fire on compact as well as startup. Checking them:")
    # Prove they FIRE, not just that files exist (1.28.2, arc-platform ask #2): the arch
    # analogue of the component --verify rung (1.12).
    return verify_seat("arch", launch_dir)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--component", dest="slug", metavar="NAME",
                    help="this seat's component name (matches the io-graph entry)")
    ap.add_argument("--slug", dest="slug",
                    help=argparse.SUPPRESS)   # retired spelling (1.30.9); same dest
    ap.add_argument("--needs-register", metavar="URL", default=None,
                    help="the estate's needs register (raw JSON URL) written to .atlas.conf "
                         "as ATLAS_NEEDS_REGISTER so atlas-needs.py can show this seat the "
                         "needs filed for it in OTHER vaults (1.27.2). Unset = inert")
    ap.add_argument("--mode", choices=["supervised", "autonomous"], default=None,
                    help="development posture written to .atlas.conf (1.26.10): "
                         "'supervised' (the default when unset) pauses for operator "
                         "confirmation at the publish/release boundary; 'autonomous' "
                         "runs free, oversight via the write model and the hub")
    ap.add_argument("--role", choices=["component", "both"], default="component",
                    help="'both' declares a both-hats seat (a single-seat project whose "
                         "one agent is the vault's architecture AND its component's "
                         "author): the write guard grants the union scope and the "
                         "publish nag names the direct-to-work flow. Declared here, "
                         "reviewable in the committed .atlas.conf; never inferred "
                         "(1.24.5). Transitional: split back when a second component "
                         "arrives (AAC-method §9)")
    ap.add_argument("--nav", metavar="PATH", default=None,
                    help="product seat: path to the project's Nav vault checkout — "
                         "written to .atlas-product.conf as ATLAS_NAV so the guard "
                         "scopes writes there to _gps/ (1.28.10)")
    ap.add_argument("--test", action="store_true", dest="test_role",
                    help="install a TEST seat (1.30.10, §10): tests/-scoped write guard "
                         "at the launch dir; point --repo at the vault checkout")
    ap.add_argument("--product", action="store_true",
                    help="install a PRODUCT seat (1.28.9, §10): reorientation hook, "
                         "product/** write guard and alignment gate at the launch dir; "
                         "point --repo at the vault checkout")
    ap.add_argument("--arch", action="store_true",
                    help="install the ARCH SEAT hooks instead (no slug): reorientation "
                         "(SessionStart -> --emit-arch-context) and the alignment gate "
                         "(Stop). Run from, or --repo, the vault checkout; --launch-dir "
                         "if the agent starts elsewhere (1.24.2, orchestrator ask)")
    ap.add_argument("--vault-remote",
                    help="git URL of the project's Atlas-<Project> vault repo "
                         "(required for install; unused by --verify)")
    ap.add_argument("--project", help="project display name for AGENTS.md "
                    "(default: derived from the vault remote name)")
    ap.add_argument("--repo", default=".", help="target code-repo root (default: cwd)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing files (hook files are always merged)")
    ap.add_argument("--launch-dir", metavar="PATH",
                    help="where the agent actually starts, if not the repo root (a seat "
                         "launching in the clone parent, e.g. $HOME/work). Hooks are also "
                         "installed there with absolute paths, since the repo's own "
                         "hook files are not loaded when it is not the project dir")
    ap.add_argument("--verify", action="store_true",
                    help="check an existing install end to end and exit (no writes)")
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if not TEMPLATES.is_dir():
        print(f"atlas_init: no templates at {TEMPLATES} — run from a method checkout",
              file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f"atlas_init: no such directory {repo}", file=sys.stderr)
        return 2
    role = "test" if args.test_role else "product" if args.product else "arch" if args.arch else None
    if role:
        ld = Path(args.launch_dir).resolve() if args.launch_dir else Path.cwd().resolve()
        if args.verify:
            return verify_seat(role, ld)
        if ld == repo:
            print(f"atlas_init --{role}: refusing to install hooks into the vault working "
                  "tree — hooks load from where the AGENT LAUNCHES (typically the vault's "
                  f"parent), not the checkout. Re-run with `--launch-dir {repo.parent}` "
                  "(commonly \"$HOME/work\").", file=sys.stderr)
            return 2
        if role == "test":
            rc = install_test(repo, ld, args.force)
        elif role == "product":
            rc = install_product(repo, ld, args.force, args.nav)
        else:
            rc = install_arch(repo, ld, args.force)
        return rc
    if not args.slug:
        ap.error("--component is required (component mode; use --arch/--product/--test "
                 "for those seats)")
    if args.verify:
        return verify(repo, args.slug,
                      Path(args.launch_dir).resolve() if args.launch_dir else None)
    if not args.vault_remote:
        ap.error("--vault-remote is required (except with --verify)")
    launch_dir = Path(args.launch_dir).resolve() if args.launch_dir else repo
    project = args.project or derive_project(args.vault_remote)
    written: list = []
    print(f"atlas_init: installing '{args.slug}' (project {project}) into {repo}")

    # scripts/ — byte-identical copies, checksum-verified by atlas-sync. Glob covers .py
    # too: atlas-needs.py shipped in 1.28.0 but a *.sh-only glob never copied it, so seats
    # got no cross-vault needs signal while every surface reported success (1.28.1).
    for src in sorted(list((TEMPLATES / "scripts").glob("*.sh"))
                      + list((TEMPLATES / "scripts").glob("*.py"))):
        dst = repo / "scripts" / src.name
        install(dst, read(src), args.force, written)
        if dst.exists():
            dst.chmod(0o755)

    # .atlas.conf — the only per-repo values. PRESERVING (1.28.6, arc-platform): a
    # rewrite that rebuilt the file from template + this run's flags silently dropped
    # every previously-set value whose flag was omitted — ATLAS_MODE twice (an autonomous
    # seat reverted to supervised, paging the operator per action), ATLAS_NEEDS_REGISTER
    # once (a seat gone blind to needs) — and reported success either way. Now an
    # existing conf is kept verbatim and only the keys THIS run explicitly sets are
    # updated; the template seeds the file only when it does not exist yet.
    def set_key(text: str, key: str, value: str, comment: str = "") -> str:
        line = f'{key}="{value}"'
        if re.search(rf"^{key}=", text, re.MULTILINE):
            return re.sub(rf"^{key}=.*$", line, text, count=1, flags=re.MULTILINE)
        block = (f"\n{comment}" if comment else "\n") + line + "\n"
        return text.rstrip("\n") + "\n" + block
    existing = repo / ".atlas.conf"
    if existing.exists():
        conf = read(existing)
        conf = set_key(conf, "COMPONENT", args.slug)
        # retire the old key in the same write (managed transition, not preservation)
        conf = re.sub(r"^SLUG=.*\n?", "", conf, flags=re.MULTILINE)
        conf = set_key(conf, "ATLAS_VAULT_REMOTE", args.vault_remote)
    else:
        conf = (read(TEMPLATES / ".atlas.conf.example")
                .replace('COMPONENT="<component>"', f'COMPONENT="{args.slug}"')
                .replace('ATLAS_VAULT_REMOTE="https://github.com/<org>/Atlas-<Project>.git"',
                         f'ATLAS_VAULT_REMOTE="{args.vault_remote}"'))
    if args.role == "both":
        conf = set_key(conf, "ATLAS_ROLE", "both",
                       "# Both hats (AAC-method §9): this seat is the vault's architecture AND this\n"
                       "# component's author — a single-seat project. Transitional by design.\n")
    if args.needs_register:
        conf = set_key(conf, "ATLAS_NEEDS_REGISTER", args.needs_register,
                       "# Cross-vault needs (1.27.2): the estate needs register, read in place.\n")
    if not args.mode and not existing.exists():
        # the value governs behaviour, so it exists where a reader can find it
        # (1.33.11, ingstr): fresh installs RECORD the default instead of implying it
        conf = set_key(conf, "ATLAS_MODE", "supervised",
                       "# Development mode (AAC-method §6): supervised pauses to confirm before\n"
                       "# publishing/releasing; autonomous runs free.\n")
    if args.mode:
        conf = set_key(conf, "ATLAS_MODE", args.mode,
                       "# Development mode (AAC-method §6): supervised pauses to confirm before\n"
                       "# publishing/releasing; autonomous runs free. Default when unset: supervised.\n")
    if existing.exists() and read(existing) != conf:
        existing.write_text(conf, encoding="utf-8", newline="\n")
        written.append(existing)
        print(f"  update {existing} (managed keys only; everything else preserved)")
    elif not existing.exists():
        install(repo / ".atlas.conf", conf, args.force, written)
    # Echo the posture, always — including when it is the default. The installer
    # echoed ATLAS_LAUNCH_DIR and was silent about ATLAS_MODE, so the one field
    # under discussion was the one it never mentioned: an arch seat told eight
    # component seats "the conf records it", nothing contradicted them at install
    # time, and four seats had to reason the gap out of atlas-common.sh afterwards
    # (agent-eco, 2026-09-11, sync-compile). A default that is never printed is
    # indistinguishable from a value that was written.
    if args.mode:
        print(f"  conf   ATLAS_MODE={args.mode}")
    else:
        print("  conf   ATLAS_MODE=supervised (DEFAULT — not written to .atlas.conf; "
              "pass --mode supervised to record it)")

    # AGENTS.md — committed entry hook
    agents = (read(TEMPLATES / "AGENTS.md.template")
              .replace("<component>", args.slug)
              .replace("<slug>", args.slug).replace("<Project>", project))
    agents_dst = repo / "AGENTS.md"
    if agents_dst.exists():
        # fill leftover placeholders in place (1.34.3, arc-platform: six repos COMMITTED
        # the unsubstituted template, so "restore from git" restored the broken copy).
        # Only the literal tokens are replaced, so local edits can never be lost.
        _cur = read(agents_dst)
        _fixed = (_cur.replace("<component name>", args.slug)
                      .replace("<component>", args.slug).replace("<slug>", args.slug))
        if _fixed != _cur:
            agents_dst.write_text(_fixed, encoding="utf-8", newline="\n")
            written.append(agents_dst)
            print("  fix    AGENTS.md — filled leftover <component name> placeholders "
                  "(nothing else touched); commit it")
    if not agents_dst.exists():
        install(agents_dst, agents, args.force, written)
    elif read(agents_dst) != agents:
        print("  keep   AGENTS.md — exists and differs; seat instructions are never "
              "overwritten by --force (1.33.7). Diff against the template by hand if "
              "you want the update.")

    # .gitignore / .gitattributes — append each fragment once (marker-guarded)
    for fragment_name, dst_name in (("gitignore.fragment", ".gitignore"),
                                    ("gitattributes.fragment", ".gitattributes")):
        dst = repo / dst_name
        existing = read(dst) if dst.exists() else ""
        if GITIGNORE_MARKER in existing:
            print(f"  ok     {dst} (Atlas block present)")
            continue
        fragment = read(TEMPLATES / fragment_name)
        joined = existing + ("" if not existing or existing.endswith("\n") else "\n") + fragment
        with dst.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(joined)
        written.append(dst)
        print(f"  append {dst}")

    # /atlas-publish + hooks
    install(repo / ".claude" / "commands" / "atlas-publish.md",
            read(TEMPLATES / ".claude" / "commands" / "atlas-publish.md"),
            args.force, written)
    table = seat_hooks()
    comp_hooks = table["roles"]["component"]["hooks"]
    own = tuple(f"{root}/scripts/" for root in [repo.as_posix()] + repo_root_exprs())
    for name, rt in table["runtimes"].items():
        merge_settings(repo, rt["file"], render_hooks("component", name, rt["repo_root"]),
                       args.force, written, own)
    if launch_dir and launch_dir != repo:
        # ONE hook of each kind per launch dir (1.21 for the briefing; 1.28.3 for the
        # guards; 1.34.3 for the style line). The SEAT scripts discover every wired
        # sibling — the context script briefs the whole seat, the write guard allows the
        # union of its components. A second repo's hooks would only double-inject the
        # briefing or, for the write guard, deny this repo's outbox. So the first member
        # installed owns the launch-dir hooks; the others add none and prune strays.
        other = any_context_hook(launch_dir, exclude_root=repo)
        keep = other or repo
        for name, rt in table["runtimes"].items():
            for moment, script in comp_hooks:
                if moment not in rt["wiring"]:
                    continue
                _pr = prune_dup_hooks(launch_dir, rt["file"], keep,
                                      rt["wiring"][moment]["event"], script)
                if _pr:
                    print(f"  prune  {_pr} duplicate {script} hook(s) in {launch_dir / rt['file']}"
                          " -- one per seat")
            if not other:
                merge_settings(launch_dir, rt["file"],
                               render_hooks("component", name, repo.as_posix()),
                               args.force, written, own)
            elif f"{other.as_posix()}/scripts/atlas-context.sh" not in (
                    read(launch_dir / rt["file"]) if (launch_dir / rt["file"]).exists() else ""):
                # temporary, while a seat's members upgrade one by one: dies when the
                # owning member has re-run the installer
                print(f"  WARN   {launch_dir / rt['file']} is not wired yet — re-run "
                      f"atlas_init in {other} (it owns this seat's launch-dir hooks)")
        if other:
            print(f"  skip   launch-dir hooks at {launch_dir} — the seat's are already "
                  f"installed from {other} and discover '{args.slug}' automatically")
        else:
            write_seat_block("component", launch_dir, repo.as_posix(), written)
            print(f"  hooks  also installed at {launch_dir} (absolute paths — the agent "
                  "launches there, not in the repo)")
        persist_launch_dir(repo, launch_dir, written)
    print_runtime_notes(launch_dir)

    print(f"\natlas_init: {len(written)} file(s) written. Next:")
    _in_repo = sorted({str(w.resolve().relative_to(repo.resolve())).split("/")[0] + ("/" if w.resolve().relative_to(repo.resolve()).parts[1:] else "")
                       for w in written if w.resolve().is_relative_to(repo.resolve())})
    _hook_dirs = sorted({rt["file"].split("/")[0] + "/" for rt in table["runtimes"].values()})
    print("  1. git add " + " ".join(_in_repo or ["AGENTS.md", ".atlas.conf", "scripts/"] + _hook_dirs)
          + " && git commit   # --verify requires them COMMITTED")
    print("  2. sh scripts/atlas-context.sh   # sync + first ATLAS-CONTEXT.md")
    print("  3. register the component in the vault (component-init.md §1–3)")
    print(f"  4. python {Path(__file__).name} --component {args.slug} --verify"
          "   # confirm the hooks actually fire")
    return 0


if __name__ == "__main__":
    sys.exit(main())

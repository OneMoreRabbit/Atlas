#!/usr/bin/env python3
"""atlas_init — install the Atlas code-repo half into a component repo.

Usage:  python atlas_init.py --slug <slug> --vault-remote <url>
                             [--project <name>] [--repo <path>] [--force]

Installs templates/component-repo/ from this method repo into the target code repo
(component-init.md §4 as one command): the atlas-* scripts, a filled-in .atlas.conf,
a substituted AGENTS.md, the .gitignore entries, the /atlas-publish command, and the
.claude hooks (merged into an existing settings.json rather than overwriting it).

Existing files are left alone unless --force; the scripts are meant to be re-copied
this way when atlas-sync reports self-drift. Stdlib only — no dependencies.

Bootstrap note: the method repo must be present to run this once —
    git clone --depth 1 <method-remote> .atlas-method
    python .atlas-method/tools/atlas_init.py --slug <slug> --vault-remote <url>
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
GITIGNORE_MARKER = "# --- Atlas ---"  # append-once marker for both fragments


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


def hook_settings(repo: Path, absolute: bool) -> dict:
    """The hooks template, with script paths resolved for where the agent launches.

    Default: ${CLAUDE_PROJECT_DIR} — correct when the agent's project dir IS the repo,
    and portable, which matters because the repo's .claude/settings.json is COMMITTED
    (a machine path there would break every other clone — AAC-method §9).
    Absolute: for a launch dir outside the repo (a seat starting in the clone parent).
    That settings file lives outside any repo, so it is machine-local by construction.
    """
    tpl = json.loads(read(TEMPLATES / ".claude" / "settings.json"))
    if not absolute:
        return tpl
    root = repo.as_posix()
    for entries in tpl["hooks"].values():
        for entry in entries:
            for hook in entry["hooks"]:
                hook["command"] = hook["command"].replace("${CLAUDE_PROJECT_DIR}", root)
    return tpl


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


def prune_dup_hooks(launch_dir: Path, keep_root: Path, event: str, script: str) -> int:
    """One <script> hook per launch dir for <event>: keep keep_root's entry, drop other
    repos'. Seat scripts (context, write guard) cover their siblings, so one entry serves
    the whole seat; duplicates double-inject the briefing (1.21/1.27.4) or, for the write
    guard, deny each other's outbox (1.28.3, arc-platform). Idempotent."""
    dst = launch_dir / ".claude" / "settings.json"
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


def prune_context_hooks(launch_dir: Path, keep_root: Path) -> int:
    return prune_dup_hooks(launch_dir, keep_root, "SessionStart", "atlas-context.sh")


def any_context_hook(launch_dir: Path, exclude_root: Path):
    """ANY SessionStart atlas-context hook installed at this launch dir from another
    repo. One is enough: since 1.21 the context script emits a seat briefing covering
    every wired sibling it discovers, so a second hook doubles the whole injection."""
    dst = launch_dir / ".claude" / "settings.json"
    if not dst.exists():
        return None
    try:
        entries = json.loads(read(dst)).get("hooks", {}).get("SessionStart", [])
    except json.JSONDecodeError:
        return None
    for entry in entries:
        for hook in entry.get("hooks", []):
            m = re.search(r'"([^"]+)/scripts/atlas-context\.sh"', hook.get("command", ""))
            if m and Path(m.group(1)) != exclude_root:
                return Path(m.group(1))
    return None


def merge_settings(target: Path, tpl: dict, force: bool, written: list,
                   repo_root: Path | None = None) -> None:
    """Merge the hooks into an existing settings.json; never clobber."""
    dst = target / ".claude" / "settings.json"
    if not dst.exists():
        install(dst, json.dumps(tpl, indent=2) + "\n", force, written)
        return
    current = json.loads(read(dst))
    hooks = current.setdefault("hooks", {})
    added = removed = 0

    def is_this_repos(entry) -> bool:
        # an atlas hook already pointing into THIS repo (absolute or project-dir form)
        cmds = " ".join(h.get("command", "") for h in entry.get("hooks", []))
        if "atlas-" not in cmds:
            return False
        return (repo_root is not None and f"{repo_root.as_posix()}/scripts/" in cmds) \
            or "${CLAUDE_PROJECT_DIR}/scripts/" in cmds

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
    check((repo / "AGENTS.md").exists(), "AGENTS.md committed at the repo root")
    drifted = []
    for name in ("atlas-common.sh", "atlas-sync.sh", "atlas-context.sh",
                 "atlas-guard-write.sh", "atlas-guard-publish.sh", "atlas-needs.py"):
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

    settings = launch_dir / ".claude" / "settings.json"
    check(settings.exists(), f"hooks settings at the LAUNCH dir", str(settings))
    if settings.exists():
        try:
            hooks = json.loads(read(settings)).get("hooks", {})
        except json.JSONDecodeError as exc:
            check(False, "settings.json parses", str(exc))
            hooks = {}
        ctx_hooks = sum(1 for e in hooks.get("SessionStart", []) for h in e.get("hooks", [])
                        if "atlas-context.sh" in h.get("command", ""))
        check(ctx_hooks <= 1, "exactly one SessionStart atlas-context hook at the launch dir",
              f"{ctx_hooks} found — each emits the whole seat briefing; re-run atlas_init to prune" if ctx_hooks > 1 else "")
        wg_hooks = sum(1 for e in hooks.get("PreToolUse", []) for h in e.get("hooks", [])
                       if "atlas-guard-write.sh" in h.get("command", ""))
        check(wg_hooks <= 1, "exactly one write-guard hook at the launch dir",
              f"{wg_hooks} found; two per-repo guards deny each other's outbox (1.28.3) -- re-run atlas_init" if wg_hooks > 1 else "")
        for event in ("SessionStart", "PreToolUse", "Stop"):
            cmds = [h["command"] for e in hooks.get(event, []) for h in e.get("hooks", [])
                    if "atlas-" in h.get("command", "")]
            check(bool(cmds), f"{event} hook registered")
            for cmd in cmds:
                m = re.search(r'"([^"]*atlas-[a-z-]+\.sh)"', cmd)
                path = m.group(1) if m else None
                if path and "${CLAUDE_PROJECT_DIR}" in path:
                    resolved = Path(path.replace("${CLAUDE_PROJECT_DIR}", str(launch_dir)))
                    check(resolved.exists(), f"{event} script resolves",
                          f"{resolved} — launched elsewhere? re-run with --launch-dir")
                elif path:
                    check(Path(path).exists(), f"{event} script resolves", path)
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

    print("\natlas_init --verify: " + ("all checks passed" if ok else
          "FAILURES above — the hook layer is not live; fix before trusting the write guard"))
    return 0 if ok else 1


ARCH_TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "arch-seat"
PRODUCT_TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "product-seat"
TEST_TEMPLATES = Path(__file__).resolve().parent.parent / "templates" / "test-seat"


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
    dst = launch_dir / "atlas-test-guard.sh"
    dst.write_text(read(TEST_TEMPLATES / "atlas-test-guard.sh"), encoding="utf-8", newline="\n")
    dst.chmod(0o755)
    print(f"  write  {dst}")
    tdir = vault / "components" / "test"
    (tdir / "docs").mkdir(parents=True, exist_ok=True)
    cmd = tdir / "component.md"
    if not cmd.exists():
        cmd.write_text(read(TEST_TEMPLATES / "test-component.md"), encoding="utf-8", newline="\n")
        print(f"  write  {cmd}")
    conf = launch_dir / ".atlas-test.conf"
    conf.write_text(f'ATLAS_VAULT="{vault}"\n', encoding="utf-8", newline="\n")
    print(f"  write  {conf}")
    tpl = {"hooks": {"PreToolUse": [{"matcher": "Write|Edit|NotebookEdit",
           "hooks": [{"type": "command", "command": f'sh "{launch_dir}/atlas-test-guard.sh"'}]}]}}
    merge_settings(launch_dir, tpl, force, [], repo_root=launch_dir)
    print("atlas_init --test: done — tests/-scoped write guard installed")
    return 0


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
    written = []
    (launch_dir / "atlas-style.sh").write_text(
        read(TEMPLATES / "scripts" / "atlas-style.sh"), encoding="utf-8", newline="\n")
    (launch_dir / "atlas-style.sh").chmod(0o755)
    for name in ("atlas-product-context.sh", "atlas-product-guard.sh",
                 "atlas-product-align.sh"):
        dst = launch_dir / name
        dst.write_text(read(PRODUCT_TEMPLATES / name), encoding="utf-8", newline="\n")
        dst.chmod(0o755)
        written.append(dst)
        print(f"  write  {dst}")
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
    tpl_settings = json.loads(read(PRODUCT_TEMPLATES / "settings.json"))
    # hooks live at the launch dir with absolute paths (the arch launch-dir lesson, 1.28.2)
    for ev in tpl_settings["hooks"].values():
        for entry in ev:
            for h in entry["hooks"]:
                h["command"] = h["command"].replace("$CLAUDE_PROJECT_DIR", str(launch_dir))
    merge_settings(launch_dir, tpl_settings, force, written, repo_root=launch_dir)
    # prove the reorientation hook FIRES from the launch dir (the 1.28.2 rung)
    try:
        r = subprocess.run(["sh", str(launch_dir / "atlas-product-context.sh")],
                           cwd=str(launch_dir), stdin=subprocess.DEVNULL,
                           capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0 and "ATLAS-PRODUCT-CONTEXT" in r.stdout
        print("  verify the product reorientation hook fires from the launch dir: "
              + ("PASS" if ok else f"FAIL (exit {r.returncode}) {(r.stderr or '').strip()[:140]}"))
    except (OSError, subprocess.SubprocessError) as e:
        print(f"  verify the product hook fires: FAIL ({str(e)[:120]})")
    print("atlas_init --product: done — reorientation + product/** write guard + "
          "alignment gate installed")
    return 0


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
    written = []
    style_src = TEMPLATES / "scripts" / "atlas-style.sh"
    (launch_dir / "atlas-style.sh").write_text(read(style_src), encoding="utf-8", newline="\n")
    (launch_dir / "atlas-style.sh").chmod(0o755)
    for name in ("atlas-arch-context.sh", "atlas-arch-guard.sh", "atlas-arch-write.sh"):
        src, dst = ARCH_TEMPLATES / name, launch_dir / name
        if dst.exists() and not force and read(dst) == read(src):
            pass
        elif dst.exists() and not force:
            print(f"  skip   {dst} exists and differs — re-run with --force to overwrite")
            continue
        dst.write_text(read(src), encoding="utf-8", newline="\n")
        os.chmod(dst, 0o755)
        written.append(dst)
        print(f"  write  {dst}")
    tpl = json.loads(read(ARCH_TEMPLATES / ".claude" / "settings.json"))
    for entry_list in tpl["hooks"].values():   # scripts live beside settings: abs paths
        for entry in entry_list:
            for h in entry.get("hooks", []):
                h["command"] = h["command"].replace("${CLAUDE_PROJECT_DIR}",
                                                    str(launch_dir))
    merge_settings(launch_dir, tpl, force, written, repo_root=vault)
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
    # Prove it FIRES, not just that files exist (1.28.2, arc-platform ask #2): run the
    # reorientation hook the way the harness will, from the launch dir, and require a
    # briefing on stdout. This is the arch analogue of the component --verify rung (1.12).
    ctx = launch_dir / "atlas-arch-context.sh"
    try:
        env = dict(os.environ, ATLAS_VAULT=str(vault), ATLAS_METHOD=kept["ATLAS_METHOD"])
        r = subprocess.run(["sh", str(ctx)], cwd=str(launch_dir), env=env,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120)
        ok = r.returncode == 0 and r.stdout.lstrip().startswith("# ATLAS-CONTEXT")
        print(("  verify the arch reorientation hook fires from the launch dir: "
               + ("PASS" if ok else f"FAIL (exit {r.returncode}) — {(r.stderr or '').strip()[:160]}")))
    except (OSError, subprocess.SubprocessError) as e:
        print(f"  verify the arch hook fires: FAIL ({str(e)[:120]})")
    print("atlas_init --arch: done — reorientation (SessionStart) + alignment gate "
          "(Stop) installed; both fire on compact as well as startup")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--component", dest="slug",
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
                    help="overwrite existing files (settings.json is always merged)")
    ap.add_argument("--launch-dir", metavar="PATH",
                    help="where the agent actually starts, if not the repo root (a seat "
                         "launching in the clone parent, e.g. $HOME/work). Hooks are also "
                         "installed there with absolute paths, since the repo's own "
                         ".claude/settings.json is not loaded when it is not the project dir")
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
    if args.test_role:
        ld = Path(args.launch_dir).resolve() if args.launch_dir else Path.cwd().resolve()
        if ld == repo:
            print("atlas_init --test: refusing to install hooks into the vault working "
                  f"tree - re-run with `--launch-dir {repo.parent}`.", file=sys.stderr)
            return 2
        return install_test(repo, ld, args.force)
    if args.product:
        ld = Path(args.launch_dir).resolve() if args.launch_dir else Path.cwd().resolve()
        if ld == repo:
            print("atlas_init --product: refusing to install hooks into the vault working "
                  f"tree — hooks load from the launch dir. Re-run with `--launch-dir {repo.parent}`.",
                  file=sys.stderr)
            return 2
        return install_product(repo, ld, args.force, args.nav)
    if args.arch:
        ld = Path(args.launch_dir).resolve() if args.launch_dir else Path.cwd().resolve()
        if ld == repo:
            print("atlas_init --arch: refusing to install hooks into the vault working "
                  "tree — hooks load from where the AGENT LAUNCHES (typically the vault's "
                  f"parent), not the checkout. Re-run with `--launch-dir {repo.parent}` "
                  "(commonly \"$HOME/work\").", file=sys.stderr)
            return 2
        return install_arch(repo, ld, args.force)
    if not args.slug:
        ap.error("--slug is required (component mode; use --arch for an arch seat)")
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
              .replace("<slug>", args.slug).replace("<Project>", project))
    install(repo / "AGENTS.md", agents, args.force, written)

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
    merge_settings(repo, hook_settings(repo, absolute=False), args.force, written,
                   repo_root=repo)
    if launch_dir and launch_dir != repo:
        tpl = hook_settings(repo, absolute=True)
        other = any_context_hook(launch_dir, exclude_root=repo)
        # 1.27.4 (arc-platform finding): a pre-1.21 seat kept N per-repo SessionStart hooks,
        # and each now emits the whole SEAT briefing — 4 x 75KB, 3.6x worse than the bug
        # 1.21 fixed, silently. Skipping the add was never enough: prune the others.
        keep = other or repo
        for _ev, _sc, _msg in (("SessionStart", "atlas-context.sh", "one seat briefing, emitted once"),
                               ("UserPromptSubmit", "atlas-style.sh", "one style line per turn"),
                               ("PreToolUse", "atlas-guard-write.sh", "one write guard (union of the seat's slugs)"),
                               ("Stop", "atlas-guard-publish.sh", "one publish guard"),
                               ("PreToolUse", "atlas-guard-supervise.sh", "one supervise guard")):
            _pr = prune_dup_hooks(launch_dir, keep, _ev, _sc)
            if _pr:
                print(f"  prune  {_pr} duplicate {_sc} hook(s) at {launch_dir} -- {_msg}")
        if other:
            # ONE hook of each kind per launch dir (1.21 for SessionStart; 1.28.3 for the
            # guards). A sibling seat member already installed the launch-dir hooks, and
            # the SEAT scripts discover every wired sibling — the context script briefs the
            # whole seat, the write guard allows the slug UNION. A second repo's hooks would
            # only double-inject the briefing or, for the write guard, deny this repo's
            # outbox. So add none of them; the existing member's cover this repo too.
            for _ev in ("SessionStart", "PreToolUse", "Stop"):
                tpl["hooks"].pop(_ev, None)
            print(f"  skip   launch-dir hooks at {launch_dir} — the seat's are already "
                  f"installed from {other} and discover '{args.slug}' automatically")
        merge_settings(launch_dir, tpl, args.force, written, repo_root=repo)
        persist_launch_dir(repo, launch_dir, written)
        print(f"  hooks  also installed at {launch_dir}/.claude/settings.json "
              "(absolute paths — the agent launches there, not in the repo)")

    print(f"\natlas_init: {len(written)} file(s) written. Next:")
    print("  1. git add + commit these (AGENTS.md and .atlas.conf must be committed)")
    print("  2. sh scripts/atlas-context.sh   # sync + first ATLAS-CONTEXT.md")
    print("  3. register the component in the vault (component-init.md §1–3)")
    print(f"  4. python {Path(__file__).name} --slug {args.slug} --verify"
          "   # confirm the hooks actually fire")
    return 0


if __name__ == "__main__":
    sys.exit(main())

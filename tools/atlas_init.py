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
import re
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


def context_hook_for_slug(launch_dir: Path, slug: str, exclude_root: Path):
    """A SessionStart atlas-context hook for the same slug, installed from a DIFFERENT
    repo at this launch dir (a multi-repo component). Its briefing is identical, so a
    second one would inject the same context twice."""
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
            if not m:
                continue
            root = Path(m.group(1))
            if root == exclude_root:
                continue
            sm = re.search(r'^SLUG="?([^"\r\n]*)"?',
                           (root / ".atlas.conf").read_text(encoding="utf-8"),
                           re.MULTILINE) if (root / ".atlas.conf").exists() else None
            if sm and sm.group(1) == slug:
                return root
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
        m = re.search(r'^SLUG="?([^"\r\n]*)"?', text, re.MULTILINE)
        found = m.group(1) if m else None
        check(found == slug, f".atlas.conf SLUG == {slug}", f"found {found!r}")
        check("\r" not in text, ".atlas.conf has no CRLF", "add gitattributes.fragment")
    check((repo / "AGENTS.md").exists(), "AGENTS.md committed at the repo root")
    for name in ("atlas-common.sh", "atlas-sync.sh", "atlas-context.sh",
                 "atlas-guard-write.sh", "atlas-guard-publish.sh"):
        check((repo / "scripts" / name).exists(), f"scripts/{name}")

    settings = launch_dir / ".claude" / "settings.json"
    check(settings.exists(), f"hooks settings at the LAUNCH dir", str(settings))
    if settings.exists():
        try:
            hooks = json.loads(read(settings)).get("hooks", {})
        except json.JSONDecodeError as exc:
            check(False, "settings.json parses", str(exc))
            hooks = {}
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
        import subprocess
        try:
            r = subprocess.run(["sh", str(ctx)], cwd=repo, capture_output=True, text=True,
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


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="this component's Atlas slug")
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
    if args.verify:
        return verify(repo, args.slug,
                      Path(args.launch_dir).resolve() if args.launch_dir else None)
    if not args.vault_remote:
        ap.error("--vault-remote is required (except with --verify)")
    launch_dir = Path(args.launch_dir).resolve() if args.launch_dir else repo
    project = args.project or derive_project(args.vault_remote)
    written: list = []
    print(f"atlas_init: installing '{args.slug}' (project {project}) into {repo}")

    # scripts/ — byte-identical copies, checksum-verified by atlas-sync
    for src in sorted((TEMPLATES / "scripts").glob("*.sh")):
        dst = repo / "scripts" / src.name
        install(dst, read(src), args.force, written)
        if dst.exists():
            dst.chmod(0o755)

    # .atlas.conf — the only per-repo values
    conf = (read(TEMPLATES / ".atlas.conf.example")
            .replace('SLUG="<slug>"', f'SLUG="{args.slug}"')
            .replace('ATLAS_VAULT_REMOTE="https://github.com/<org>/Atlas-<Project>.git"',
                     f'ATLAS_VAULT_REMOTE="{args.vault_remote}"'))
    install(repo / ".atlas.conf", conf, args.force, written)

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
        other = context_hook_for_slug(launch_dir, args.slug, exclude_root=repo)
        if other:
            tpl["hooks"].pop("SessionStart", None)
            print(f"  skip   SessionStart at {launch_dir} — slug '{args.slug}' briefing "
                  f"already injected from {other} (multi-repo component: guards are "
                  "per-repo, the briefing is per-slug)")
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

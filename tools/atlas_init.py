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


def merge_settings(repo: Path, force: bool, written: list) -> None:
    """Merge the template hooks into an existing settings.json; never clobber."""
    tpl = json.loads(read(TEMPLATES / ".claude" / "settings.json"))
    dst = repo / ".claude" / "settings.json"
    if not dst.exists():
        install(dst, json.dumps(tpl, indent=2) + "\n", force, written)
        return
    current = json.loads(read(dst))
    hooks = current.setdefault("hooks", {})
    added = 0
    for event, entries in tpl["hooks"].items():
        bucket = hooks.setdefault(event, [])
        for entry in entries:
            if entry not in bucket:
                bucket.append(entry)
                added += 1
    if added:
        with dst.open("w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(current, indent=2) + "\n")
        written.append(dst)
        print(f"  merge  {dst} (+{added} hook entr{'y' if added == 1 else 'ies'})")
    else:
        print(f"  ok     {dst} (hooks already wired)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True, help="this component's Atlas slug")
    ap.add_argument("--vault-remote", required=True,
                    help="git URL of the project's Atlas-<Project> vault repo")
    ap.add_argument("--project", help="project display name for AGENTS.md "
                    "(default: derived from the vault remote name)")
    ap.add_argument("--repo", default=".", help="target code-repo root (default: cwd)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite existing files (settings.json is always merged)")
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
    merge_settings(repo, args.force, written)

    print(f"\natlas_init: {len(written)} file(s) written. Next:")
    print("  1. git add + commit these (AGENTS.md and .atlas.conf must be committed)")
    print("  2. sh scripts/atlas-context.sh   # sync + first ATLAS-CONTEXT.md")
    print("  3. register the component in the vault (component-init.md §1–3)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

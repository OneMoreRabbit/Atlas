#!/usr/bin/env python3
"""Release notes check: a tag with a suffix is not a release and is skipped (1.36.2,
arc-platform.arch, hub #15695). On the work branch, after a release that had a
candidate, the nearest tag is the candidate: the final tag is the merge commit on the
release branch. The check asked for a heading for the candidate. Builds that layout in
a scratch repo and runs the validator's check and the seat script's command; no network.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import atlas_validate as v  # noqa: E402

SCRIPT = ROOT / "templates" / "component-repo" / "scripts" / "atlas-context.sh"
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


def git(repo, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    git(repo, "init", "-q", "-b", "dev")
    (repo / "release-notes.md").write_text("# Release notes\n\n## v0.7.0 — 2026-10-01\n", encoding="utf-8")
    git(repo, "add", "."), git(repo, "commit", "-q", "-m", "0.7.0"), git(repo, "tag", "-a", "v0.7.0", "-m", "x")
    (repo / "release-notes.md").write_text(
        "# Release notes\n\n## v0.8.0 — 2026-11-01\n\n## v0.7.0 — 2026-10-01\n", encoding="utf-8")
    git(repo, "commit", "-q", "-am", "0.8.0 notes"), git(repo, "tag", "v0.8.0rc1")
    git(repo, "checkout", "-q", "-b", "main")
    git(repo, "commit", "-q", "--allow-empty", "-m", "release"), git(repo, "tag", "-a", "v0.8.0", "-m", "x")

    v.ROOT = repo
    # on the work branch the nearest tag is the candidate: no warning for it
    git(repo, "checkout", "-q", "dev")
    expect(git(repo, "describe", "--tags", "--abbrev=0") == "v0.8.0rc1", "the scratch repo does not show the fault")
    expect(v.release_notes_warnings() == [], f"work branch warns: {v.release_notes_warnings()}")
    # the seat script runs the same command
    m = re.search(r'_t=\$\(git -C "\$_r" (describe [^)]*?) 2>/dev/null', SCRIPT.read_text(encoding="utf-8"))
    expect(m is not None, "atlas-context.sh: the tag command was not found")
    if m:
        out = subprocess.run(f'git -C "{repo}" {m.group(1)}', shell=True, capture_output=True, text=True).stdout.strip()
        expect(out == "v0.7.0", f"atlas-context.sh reads '{out}' on the work branch, not v0.7.0")
    # a plain tag with no heading still warns
    git(repo, "checkout", "-q", "main")
    git(repo, "commit", "-q", "--allow-empty", "-m", "next"), git(repo, "tag", "-a", "v0.9.0", "-m", "x")
    w = v.release_notes_warnings()
    expect(len(w) == 1 and "## v0.9.0" in w[0], f"a plain tag with no heading does not warn: {w}")
    # a repo whose only tag has a suffix has no release yet: silent
    only = Path(tmp) / "only"
    only.mkdir()
    git(only, "init", "-q", "-b", "dev"), git(only, "commit", "-q", "--allow-empty", "-m", "a"), git(only, "tag", "v0.1.0rc1")
    v.ROOT = only
    expect(v.release_notes_warnings() == [], f"a repo with only a candidate warns: {v.release_notes_warnings()}")

if fails:
    print("release notes tag: FAIL\n  " + "\n  ".join(fails))
    sys.exit(1)
print("release notes tag: a tag with a suffix is skipped; a plain tag with no heading still warns")

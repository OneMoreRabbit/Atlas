#!/usr/bin/env python3
"""/atlas-publish step 6b never discards a component's own page (1.35.5, agent-eco's
dprox). scripts/atlas-discard-views.sh takes no argument; this runs it in a scratch
component repo and checks that the generated views are restored, that the component's
own component.md keeps its edit, and that a conf with no COMPONENT discards nothing.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS = ROOT / "templates" / "component-repo" / "scripts"
VIEWS = ["registry/graph.md", "dashboard.md", "registry/.compiled/alpha/io-manifest.yml",
         "components/alpha/component.md", "components/beta/component.md"]
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=t", "-c", "user.email=t@t",
                           *args], capture_output=True, text=True)


def modified(vault):
    return sorted(line[3:] for line in git(vault, "status", "--short").stdout.splitlines())


with tempfile.TemporaryDirectory() as tmp:
    repo, vault = Path(tmp) / "repo", Path(tmp) / "repo" / ".atlas"
    (repo / "scripts").mkdir(parents=True)
    for name in ("atlas-common.sh", "atlas-discard-views.sh"):
        shutil.copy(SCRIPTS / name, repo / "scripts" / name)
    for view in VIEWS:
        (vault / view).parent.mkdir(parents=True, exist_ok=True)
        (vault / view).write_text("as committed\n")
    git(vault, "init", "-q")
    git(vault, "add", "-A")
    git(vault, "commit", "-q", "-m", "init")

    def run(conf):
        for view in VIEWS:
            (vault / view).write_text("edited\n")
        (repo / ".atlas.conf").write_text(conf)
        return subprocess.run(["sh", "scripts/atlas-discard-views.sh"], cwd=repo,
                              capture_output=True, text=True).returncode

    rc = run('COMPONENT="alpha"\n')
    expect(rc == 0, f"named component: exit {rc}")
    expect(modified(vault) == ["components/alpha/component.md"],
           f"named component: left modified {modified(vault)}")
    rc = run('ATLAS_VAULT_REMOTE="x"\n')
    expect(rc != 0, "no COMPONENT in .atlas.conf: must not exit 0")
    expect(modified(vault) == sorted(VIEWS), "no COMPONENT in .atlas.conf: something was discarded")

if fails:
    sys.exit("discard views: " + "; ".join(fails))
print("discard views: generated views restored, own component.md kept, no name discards nothing")

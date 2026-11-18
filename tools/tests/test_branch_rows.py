#!/usr/bin/env python3
"""A vault listed as a component is still a vault in the dashboard's branch table
(1.36.0; AAC-method section 9). The project's own Atlas vault has one branch, the work
branch. Its Nav vault has one branch, main. A code repo keeps the work and release
pair. The remote is faked: this checks the rows, not the network."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import atlas_validate as v  # noqa: E402

fails = []


def expect(good, what):
    if not good:
        fails.append(what)


VAULT = "https://github.com/Example/Atlas-Demo.git"
NAV = "https://github.com/Example/Nav-Demo.git"
CODE = "https://github.com/Example/demo-app.git"
graph = {
    "branching": {"work": "dev", "release": "main"},
    "components": [
        {"component": "atlas", "name": "the vault", "source": VAULT},
        {"component": "nav", "name": "the bridge", "source": NAV},
        {"component": "app", "name": "App", "source": CODE},
    ],
}


def rows(remotes):
    v.run_git = lambda args: VAULT + "\n"
    v.component_source = lambda g, c: c["source"]
    v.remote_repo_info = lambda url, *b: remotes[url]
    md, console = v.gen_branch_section(graph)
    return {line.split("|")[1].strip(): line for line in md.splitlines() if line.startswith("| ")}, console


def remote(default, *heads):
    return {"default": default, "heads": {h: "0" * 40 for h in heads}, "tag": None}


# after the migration: every vault has its one branch
table, console = rows({VAULT: remote("dev", "dev"), NAV: remote("main", "main"),
                       CODE: remote("dev", "dev", "main")})
expect("one branch, `dev`" in table["vault"], f"vault row: {table['vault']}")
expect("one branch, `dev`" in table["atlas"], f"the vault as a component: {table['atlas']}")
expect("one branch, `main`" in table["nav"] and "🔴" not in table["nav"], f"nav row: {table['nav']}")
expect("in sync" in table["app"], f"code repo row: {table['app']}")
expect(not [c for c in console if "🔴" in c], f"red on a clean estate: {console}")

# before it: the Atlas vault still has main, the Nav vault has a dev
table, console = rows({VAULT: remote("dev", "dev", "main"), NAV: remote("main", "main", "dev"),
                       CODE: remote("dev", "dev", "main")})
expect("🔴 has a `main` branch" in table["vault"], f"vault with main: {table['vault']}")
expect("🔴 has a `main` branch" in table["atlas"], f"vault as a component, with main: {table['atlas']}")
expect("🔴 has a `dev` branch" in table["nav"], f"nav with dev: {table['nav']}")
expect(len([c for c in console if "branch  vault" in c]) == 1, f"vault named once: {console}")
expect(any("branch  nav" in c for c in console), f"nav not named: {console}")

# a code repo with no work branch is still red
table, console = rows({VAULT: remote("dev", "dev"), NAV: remote("main", "main"),
                       CODE: remote("main", "main")})
expect("🔴 no `dev` branch" in table["app"], f"code repo with no work branch: {table['app']}")

if fails:
    sys.exit("branch rows: " + "; ".join(fails))
print("branch rows: an Atlas vault and a Nav vault listed as components read as one branch each, a code repo keeps the pair")

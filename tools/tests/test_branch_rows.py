#!/usr/bin/env python3
"""A vault listed as a component is still a vault in the dashboard's branch table
(1.36.0; AAC-method section 9). Every vault has one branch, the work branch, and no
release branch: the project's own Atlas vault and its Nav vault alike (1.36.1). A code
repo keeps the work and release pair. The remote is faked: this checks the rows, not
the network."""
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


# every vault on its one branch
table, console = rows({VAULT: remote("dev", "dev"), NAV: remote("dev", "dev"),
                       CODE: remote("dev", "dev", "main")})
expect("one branch, `dev`" in table["vault"], f"vault row: {table['vault']}")
expect("one branch, `dev`" in table["atlas"], f"the vault as a component: {table['atlas']}")
expect("one branch, `dev`" in table["nav"] and "🔴" not in table["nav"], f"nav row: {table['nav']}")
expect("in sync" in table["app"], f"code repo row: {table['app']}")
expect(not [c for c in console if "🔴" in c], f"red on a clean estate: {console}")

# both vaults still have a main
table, console = rows({VAULT: remote("dev", "dev", "main"), NAV: remote("dev", "dev", "main"),
                       CODE: remote("dev", "dev", "main")})
expect("🔴 has a `main` branch" in table["vault"], f"vault with main: {table['vault']}")
expect("🔴 has a `main` branch" in table["atlas"], f"vault as a component, with main: {table['atlas']}")
expect("🔴 has a `main` branch" in table["nav"], f"nav with main: {table['nav']}")
expect(len([c for c in console if "branch  vault" in c]) == 1, f"vault named once: {console}")
expect(any("branch  nav" in c and "delete 'main'" in c for c in console), f"nav not named: {console}")

# a Nav vault that has only main is red: no work branch, wrong default
table, console = rows({VAULT: remote("dev", "dev"), NAV: remote("main", "main"),
                       CODE: remote("dev", "dev", "main")})
expect("🔴 no `dev` branch" in table["nav"] and "policy: `dev`" in table["nav"], f"nav on main only: {table['nav']}")
expect(any("branch  nav" in c for c in console), f"nav on main only not named: {console}")

# a code repo with no work branch is still red
table, console = rows({VAULT: remote("dev", "dev"), NAV: remote("dev", "dev"),
                       CODE: remote("main", "main")})
expect("🔴 no `dev` branch" in table["app"], f"code repo with no work branch: {table['app']}")

if fails:
    sys.exit("branch rows: " + "; ".join(fails))
print("branch rows: every vault reads as one branch, the work branch; a code repo keeps the pair")

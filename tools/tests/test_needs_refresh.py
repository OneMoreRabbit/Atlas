#!/usr/bin/env python3
"""atlas-needs.py: the token is asked for with the repository path, and a register that
cannot be read is visible (1.35.3 and 1.35.7, orchestrator: seats on the credential router
got no token, and a list stayed four days old with nothing a timer could see). Runs the
script against a stand-in `git` and file:// registers; no network.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "templates" / "component-repo" / "scripts" / "atlas-needs.py"
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # 1. The token: a credential helper that answers only when given the repository path
    fake = tmp / "bin"
    fake.mkdir()
    (fake / "git").write_text(
        '#!/bin/sh\nin=$(cat)\nprintf \'%s\\n--\\n\' "$in" >> "$ASKS"\n'
        'case "$in" in *path=acme/vault.git*) echo "password=from-the-path";; esac\n')
    (fake / "git").chmod(0o755)
    os.environ.update(PATH=f"{fake}{os.pathsep}{os.environ['PATH']}", ASKS=str(tmp / "asks"))
    os.environ.pop("GITHUB_TOKEN", None)
    spec = importlib.util.spec_from_file_location("atlas_needs", SCRIPT)
    needs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(needs)
    for url in ("https://api.github.com/repos/acme/vault/contents/registry/needs.json?ref=dev",
                "https://raw.githubusercontent.com/acme/vault/dev/registry/needs.json",
                "https://github.com/acme/vault.git"):
        expect(needs.token_for(url) == "from-the-path", f"no token for {url}")
    expect((tmp / "asks").read_text().startswith("protocol=https\nhost=github.com\npath=acme/vault.git"),
           "the first ask does not carry the repository path")

    # 2. The refresh: a register that cannot be read, then one that can
    home = tmp / "home"
    home.mkdir()
    out = home / ".atlas" / "needs-open.md"
    good = tmp / "needs.json"
    good.write_text(json.dumps({"updated": date.today().isoformat(), "needs": [
        {"addressee": "alpha", "status": "open", "vault": "Atlas-Other", "path": "n.md"}]}))

    def refresh(register):
        env = dict(os.environ, HOME=str(home), ATLAS_NEEDS_REGISTER=register)
        return subprocess.run([sys.executable, str(SCRIPT), "--refresh", "--slugs", "alpha"],
                              env=env, capture_output=True, text=True).returncode

    mark = f"STALE — last refresh FAILED {date.today().isoformat()}"
    missing = (tmp / "nowhere.json").as_uri()
    expect(refresh(missing) == 1, "failed refresh with no list yet does not exit 1")
    expect(out.exists() and mark in out.read_text(), "no dated STALE line when there is no list yet")
    expect(refresh(good.as_uri()) == 0, "good refresh does not exit 0")
    expect("STALE" not in out.read_text() and "n.md" in out.read_text(), "good refresh did not replace the list")
    expect(refresh(missing) == 1 and refresh(missing) == 1, "failed refresh over a list does not exit 1")
    text = out.read_text()
    expect(text.count(mark) == 1 and text.splitlines()[2].startswith("> ") and mark in text.splitlines()[2],
           "the dated STALE line is not once, at the top")
    expect("n.md" in text, "the old list was not kept under the STALE line")

if fails:
    print("needs refresh: FAIL\n  " + "\n  ".join(fails))
    sys.exit(1)
print("needs refresh: token asked with the repository path, failed read dated and exits 1, good read clears it")

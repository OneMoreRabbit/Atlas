#!/usr/bin/env python3
"""The seat hook table renders and the write guards read every runtime's payload
(1.35.4). templates/seat-hooks.json is the one description of the hooks; this checks
that it is complete, that the payload helper lists the right files for each known
payload shape, and that every role's write guard allows and refuses what its row says,
fired with each runtime's own sample payload.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import contextlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import atlas_init  # noqa: E402

table = atlas_init.seat_hooks()
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


# ---- the table is complete ---------------------------------------------------------
for role, r in table["roles"].items():
    for moment, script in r["hooks"]:
        expect(moment in table["moments"], f"{role}: unknown moment {moment}")
        src = (atlas_init.TEMPLATES / "scripts" / script if role == "component"
               else dict(atlas_init.seat_scripts(role))[script])
        expect(src.exists(), f"{role}: no template for {script}")
for name, rt in table["runtimes"].items():
    for key in ("file", "repo_root", "ask", "wiring", "sample_write"):
        expect(key in rt, f"{name}: missing {key}")
    expect(isinstance(rt.get("ask"), bool), f"{name}: ask must be true or false")
    for moment in rt.get("wiring", {}):
        expect(moment in table["moments"], f"{name}: unknown moment {moment}")
    for role in table["roles"]:
        hooks = atlas_init.render_hooks(role, name, "/root")["hooks"]
        expect(hooks, f"{name}/{role}: renders no hooks")

# ---- the two legacy Claude files still equal the rendering -----------------------------
# Temporary: method-ci.yml parses these two paths by name. They go when the orchestrator
# edits the workflow (next-steps.md records it).
for role, path in (("component", "templates/component-repo/.claude/settings.json"),
                   ("arch", "templates/arch-seat/.claude/settings.json")):
    legacy = json.loads((ROOT / path).read_text(encoding="utf-8"))
    expect(legacy == atlas_init.render_hooks(role, "claude", "${CLAUDE_PROJECT_DIR}"),
           f"{path} differs from the claude rendering of the {role} role")

# ---- the payload helper ----------------------------------------------------------------
HELPER = ROOT / "templates" / "component-repo" / "scripts" / atlas_init.PAYLOAD_HELPER


def helper(payload):
    text = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(HELPER)], input=text, capture_output=True,
                          text=True).stdout.rstrip("\n").split("\n")


expect(helper({"tool_input": {"file_path": "/v/a.md", "content": "to: x.arch\n"}})
       == ["/v/a.md\tx.arch"], "path payload")
expect(helper({"cwd": "/w", "tool_input": {"command":
       "*** Begin Patch\n*** Add File: v/a.md\n+to: x.arch\n*** Update File: /v/b.md\n"
       "@@\n-old\n+new\n*** Delete File: v/c.md\n*** End Patch\n"}})
       == ["/w/v/a.md\tx.arch", "/v/b.md\t", "/w/v/c.md\t"], "patch payload, three files")
expect(helper({"tool_input": {"file_path": "/v/components/a/../../product/x.md"}})
       == ["/v/product/x.md\t"], "a path with .. is normalised before it is checked")
for bad in ("not json", {"tool_input": {"command": "ls"}}, {}):
    expect(helper(bad) == ["__ATLAS_PARSE_ERROR__"], f"unreadable payload refused: {bad!r}")
for name, rt in table["runtimes"].items():
    sample = json.loads(json.dumps(rt["sample_write"]).replace("<path>", "/v/x.md"))
    expect(helper(sample) == ["/v/x.md\t"], f"{name}: sample_write names one file")

# ---- every launch-dir role's write guard, with each runtime's payload ----------------------
with tempfile.TemporaryDirectory() as tmp:
    for role in ("arch", "product", "test"):
        ld, vault = Path(tmp) / role, Path(tmp) / role / "vault"
        (vault / "registry").mkdir(parents=True)
        (vault / "registry" / "io-graph.yml").write_text("components: []\n")
        ld.mkdir(exist_ok=True)
        with contextlib.redirect_stdout(io.StringIO()):
            atlas_init.copy_seat_scripts(role, ld, True, [])
        (ld / f".atlas-{role}.conf").write_text(f'ATLAS_VAULT="{vault}"\n')
        guard = dict((m, s) for m, s in table["roles"][role]["hooks"])["write"]
        for name, rt in table["runtimes"].items():
            for want, key in ((0, "allowed"), (2, "refused")):
                path = (vault / table["roles"][role][key]).as_posix()
                rc = atlas_init.fire_write(f'sh "{ld}/{guard}"', rt["sample_write"], path, ld)
                expect(rc == want, f"{role} guard, {name} payload, {key} path: exit {rc}")

if fails:
    sys.exit("seat hooks: " + "; ".join(fails))
print("seat hooks: table complete, payload shapes read, guards allow and refuse for",
      ", ".join(table["runtimes"]))

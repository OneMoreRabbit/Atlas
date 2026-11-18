#!/usr/bin/env python3
"""A seat's own skills are checked, warn-only (1.35.10; skills.md). An agent runtime
loads a skill by the frontmatter of its SKILL.md and skips one it cannot read without
saying so. This builds a scratch vault with one good skill and six broken ones and
checks that the validator names each broken one, says nothing about the good one or an
archived one, and does not change its exit code or report a frontmatter error."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATE = ROOT / "tools" / "atlas_validate.py"
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate(vault):
    return subprocess.run([sys.executable, str(VALIDATE), str(vault)],
                          capture_output=True, text=True, encoding="utf-8")


with tempfile.TemporaryDirectory() as tmp:
    vault = Path(tmp) / "vault"
    write(vault / "registry" / "io-graph.yml", """method:
  pinned: "1.35.10"
branching:
  work: dev
project: demo
components:
  - component: alpha
    name: Alpha
edges: []
""")
    write(vault / "architecture" / "constitution.md", "---\ntitle: Constitution\n---\n\n# Constitution\n")
    write(vault / "components" / "alpha" / "component.md",
          "---\nname: Alpha\ncomponent: alpha\ntype: service\n---\n\n# alpha\n")
    before = validate(vault)
    expect("SKILLS" not in before.stdout, "a vault with no skills got a SKILLS block")

    skills = vault / "components" / "alpha" / "skills"
    write(skills / "good-one" / "SKILL.md",
          "---\nname: good-one\ndescription: Use when the test needs a good skill.\nversion: '0.1'\n---\n\n# Good\n")
    write(skills / "wrong-name" / "SKILL.md",
          "---\nname: another-name\ndescription: Use when the name is wrong.\n---\n\n# Wrong\n")
    write(skills / "no-description" / "SKILL.md", "---\nname: no-description\n---\n\n# None\n")
    write(skills / "no-frontmatter" / "SKILL.md", "# Just a heading\n\nNo frontmatter here.\n")
    write(skills / "bad-yaml" / "SKILL.md", "---\nname: [unclosed\n---\n\n# Bad\n")
    write(skills / "no-file" / "notes.md", "not a skill file\n")
    write(skills / "archive" / "old-one" / "SKILL.md", "# retired, any shape\n")
    write(skills / "Bad_Name" / "SKILL.md",
          "---\nname: Bad_Name\ndescription: Use when the folder name is not a slug.\n---\n\n# Bad name\n")
    write(skills / "codex-thing" / "SKILL.md",
          "---\nname: codex-thing\ndescription: Use when the name is kept for Codex.\n---\n\n# Kept\n")
    after = validate(vault)
    out = after.stdout
    block = out.split("SKILLS", 1)[1] if "SKILLS" in out else ""

    expect("SKILLS — 7 skill folder(s)" in out, f"expected seven warnings, got: {block[:400]!r}")
    expect("good-one" not in block, "the good skill was warned about")
    expect("old-one" not in block and "skills/archive:" not in block, "an archived skill was warned about")
    expect("wrong-name/SKILL.md: name: is 'another-name'" in block, "wrong name not named")
    expect("no-description/SKILL.md: no description:" in block, "missing description not named")
    expect("no-frontmatter/SKILL.md: no frontmatter that parses" in block, "missing frontmatter not named")
    expect("bad-yaml/SKILL.md: no frontmatter that parses" in block, "bad YAML not named")
    expect("skills/no-file: no SKILL.md" in block, "folder without SKILL.md not named")
    expect("skills/Bad_Name: the folder name is not a lowercase slug" in block, "bad folder name not named")
    expect("skills/codex-thing: a name starting codex-" in block, "codex- name not named")
    expect(after.returncode == before.returncode,
           f"skill warnings changed the exit code: {before.returncode} -> {after.returncode}")
    expect("bad-yaml" not in out.split("SKILLS", 1)[0], "a bad skill was reported as a frontmatter error")

if fails:
    sys.exit("skill folders: " + "; ".join(fails))
print("skill folders: each skill a runtime would not load is named, good and archived ones are not, exit code unchanged")

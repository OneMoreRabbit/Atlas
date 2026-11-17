#!/usr/bin/env python3
"""A session-start hook prints a head, not the briefing (1.35.9). The runtime carries at
most 10,000 characters from one hook; over that it keeps the first 2,000 and the seat
never sees the rest. This builds a scratch vault and checks that with --parts-dir the
content goes to files and nothing is lost, that the head names what is open, that
--compose-head lists the files inside the first 2,000 characters and holds the whole to
its limit, and that without --parts-dir the briefing is the one text it always was.
The hook scripts themselves are run by `atlas_init --verify`, which now fails a hook
that prints more than the limit; method-ci.yml runs that on a fixture seat.
STAGED for CI: method-ci.yml runs tools/tests/test_retired_agreement.py by name; the
orchestrator owns the workflow edit that runs every tools/tests/test_*.py."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
VALIDATE = ROOT / "tools" / "atlas_validate.py"
LIMIT, PREVIEW = 10_000, 2_000
fails = []


def expect(good, what):
    if not good:
        fails.append(what)


def units(text):
    return len(text.encode("utf-16-le")) // 2


def validate(vault, *args, stdin=None):
    return subprocess.run([sys.executable, str(VALIDATE), str(vault), *args], input=stdin,
                          capture_output=True, text=True, encoding="utf-8")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def filler(word, n):
    return "".join(f"{word} line {i}: one fact, said once, in the place it belongs.\n"
                   for i in range(n))


def files_in(folder):
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.md"))}


def holders(sentinel, files):
    return [name for name, text in files.items() if sentinel in text]


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    vault = tmp / "vault"
    write(vault / "registry" / "io-graph.yml", """method:
  pinned: "1.35.9"
branching:
  work: main
project: demo
components:
  - component: demo
    name: Demo
  - component: up
    name: Up
edges:
  - from: up
    to: demo
    interface: up-api
    pinned: "1.0"
""")
    for c in ("demo", "up"):
        write(vault / "components" / c / "component.md",
              f"---\nname: {c}\ncomponent: {c}\n---\n\n# {c}\n\n<!-- atlas:edges -->\n"
              "<!-- /atlas:edges -->\n")
    write(vault / "components" / "up" / "docs" / "provides" / "up-api-v1_0.md",
          '---\ninterface: up-api\nversion: "1.0"\nstatus: active\n---\n\n# up-api\n\n'
          "SENTINEL-CONTRACT\n" + filler("Contract", 300))
    write(vault / "components" / "up" / "docs" / "needs" / "up-more-speed-v0_1.md",
          '---\nneed: more-speed\nstatus: open\nversion: "0.1"\nto: demo.component.demo\n'
          "---\n\n# Need more speed\n\nSENTINEL-NEED\n")
    write(vault / "components" / "demo" / "docs" / "needs" / "demo-asks-arch-v0_1.md",
          '---\nneed: a-ruling\ntitle: Demo asks for a ruling\nstatus: open\nversion: "0.1"\n'
          "to: demo.arch\n---\n\n# A ruling\n")
    write(vault / "architecture" / "constitution.md",
          "# Constitution\n\nSENTINEL-CONSTITUTION\n\n" + filler("Principle", 300))
    write(vault / "architecture" / "proposals" / "0001-change-demo.md",
          "---\nstatus: proposed\ntitle: Change demo\naffects: [demo]\n---\n\n# Change demo\n\n"
          "SENTINEL-PROPOSAL\n")
    write(vault / "dashboard.md", "# Dashboard\n")
    write(vault / "next-steps.md", "# Next steps\n\nSENTINEL-NEXT\n")
    r = validate(vault)
    expect((vault / "registry" / ".compiled" / "demo" / "io-manifest.yml").exists(),
           f"fixture did not compile: {r.stdout[-300:]} {r.stderr[-300:]}")

    # ---- without --parts-dir: one text, as before ---------------------------------
    whole = validate(vault, "--emit-context", "demo")
    expect(whole.returncode == 0 and whole.stdout.startswith("# ATLAS-CONTEXT"),
           f"whole briefing: exit {whole.returncode} {whole.stderr[-200:]}")
    expect("\x00" not in whole.stdout, "whole briefing: a part marker leaked into the text")
    for s in ("CONSTITUTION", "CONTRACT", "NEED", "PROPOSAL"):
        expect(f"SENTINEL-{s}" in whole.stdout, f"whole briefing: lost SENTINEL-{s}")
    expect(units(whole.stdout) > LIMIT, "fixture too small to prove anything")

    # ---- with --parts-dir: a head on stdout, the content in files ------------------
    parts = tmp / "parts"
    head = validate(vault, "--emit-context", "demo", "--parts-dir", str(parts))
    files = files_in(parts)
    expect(head.returncode == 0 and head.stdout.startswith("# ATLAS-CONTEXT"),
           f"head: exit {head.returncode} {head.stderr[-200:]}")
    expect(units(head.stdout) < 6_000, f"head is {units(head.stdout)} characters")
    for s, name in (("CONSTITUTION", "1-constitution.md"), ("CONTRACT", "3-contracts.md"),
                    ("NEED", "4-needs.md"), ("PROPOSAL", "5-proposals-and-drift.md")):
        expect(holders(f"SENTINEL-{s}", files) == [name],
               f"SENTINEL-{s} is in {holders(f'SENTINEL-{s}', files)}, expected only {name}")
        expect(f"SENTINEL-{s}" not in head.stdout, f"SENTINEL-{s} is in the head")
    expect("components/up/docs/needs/up-more-speed-v0_1.md" in head.stdout,
           "head does not name the unanswered need")
    expect("architecture/proposals/0001-change-demo.md" in head.stdout,
           "head does not name the proposal in flight")
    expect("SIMPLE IS BETTER THAN COMPLEX" in head.stdout, "head lost the house style")
    expect(all(t.startswith("# ") for t in files.values()), "a file has no title line")
    expect("\x00" not in head.stdout + "".join(files.values()), "a part marker leaked")
    # nothing lost: every line of the whole briefing is in the head or a file, except the
    # guidance lines reworded to point at the files
    there = set((head.stdout + "\n" + "\n".join(files.values())).splitlines())
    lost = [l for l in whole.stdout.splitlines() if l.strip() and l not in there]
    expect(all(l.startswith("> ") for l in lost) and len(lost) <= 8,
           f"lines lost between the whole briefing and the files: {lost[:5]}")

    # ---- --compose-head: the file list first, the whole within the limit -----------
    extra = tmp / "needs-open.md"
    write(extra, "# Needs from other vaults\n\nSENTINEL-EXTERNAL\n")
    top = "> a warning from the hook script\n\n" + head.stdout
    out = validate(vault, "--compose-head", "--parts-dir", str(parts),
                   "--also-read", f"{extra}=Needs filed in other vaults",
                   "--also-read", f"{tmp / 'absent.md'}=Not there", stdin=top)
    expect(out.returncode == 0 and out.stdout.startswith("# ATLAS-CONTEXT"),
           f"compose: exit {out.returncode} {out.stderr[-200:]}")
    expect(units(out.stdout) <= LIMIT, f"composed head is {units(out.stdout)} characters")
    listing = out.stdout[:PREVIEW]
    for name in list(files) + [extra.as_posix(), parts.resolve().as_posix()]:
        expect(name in listing, f"`{name}` is not in the first {PREVIEW} characters")
    expect("absent.md" not in out.stdout, "compose listed a file that does not exist")
    expect(out.stdout.rstrip().endswith(top.rstrip()), "compose changed the head it was given")
    expect("SENTINEL-EXTERNAL" not in out.stdout, "compose inlined a file it should list")

    # over the limit: cut here and say so, never left to the runtime
    long = top + filler("Too long", 400)
    cut = validate(vault, "--compose-head", "--parts-dir", str(parts), stdin=long)
    saved = parts / "0-head-in-full.md"
    expect(cut.returncode == 0 and units(cut.stdout) <= LIMIT,
           f"long head: exit {cut.returncode}, {units(cut.stdout)} characters")
    expect("HEAD CUT HERE" in cut.stdout and "0-head-in-full.md" in cut.stdout[:PREVIEW],
           "long head: the cut is not announced, or the saved file is not listed first")
    expect(saved.exists() and saved.read_text(encoding="utf-8").strip() == long.strip(),
           "long head: the whole head was not saved")
    expect("WARNING" in cut.stderr, "long head: no warning on stderr")
    # the runtime counts UTF-16 units: 6,000 of these are 12,000 units
    wide = validate(vault, "--compose-head", "--parts-dir", str(parts),
                    stdin="\n".join("\U0001F600" * 60 for _ in range(100)))
    expect(units(wide.stdout) <= LIMIT and "HEAD CUT HERE" in wide.stdout,
           f"wide characters: {units(wide.stdout)} units went through uncut")
    validate(vault, "--compose-head", "--parts-dir", str(parts), stdin=top)
    expect(not saved.exists(), "a head that fits left the last run's saved head behind")

    # ---- a seat holding two components ---------------------------------------------
    seat = validate(vault, "--emit-context", "demo,up", "--parts-dir", str(tmp / "seat"))
    expect(seat.returncode == 0 and "`demo`, `up`" in seat.stdout,
           f"seat head: exit {seat.returncode} {seat.stderr[-200:]}")
    expect(holders("SENTINEL-CONTRACT", files_in(tmp / "seat")) == ["3-contracts.md"],
           "seat: the contract is not in 3-contracts.md alone")

    # ---- the arch seat --------------------------------------------------------------
    whole_arch = validate(vault, "--emit-arch-context")
    expect("\x00" not in whole_arch.stdout and "SENTINEL-NEXT" in whole_arch.stdout,
           "whole arch briefing changed")
    arch = validate(vault, "--emit-arch-context", "--parts-dir", str(tmp / "arch"))
    afiles = files_in(tmp / "arch")
    expect(arch.returncode == 0 and arch.stdout.startswith("# ATLAS-CONTEXT"),
           f"arch head: exit {arch.returncode} {arch.stderr[-200:]}")
    expect(holders("SENTINEL-NEXT", afiles) == ["5-next-steps.md"],
           f"next-steps is in {holders('SENTINEL-NEXT', afiles)}")
    expect(holders("SENTINEL-CONSTITUTION", afiles) == ["1-constitution.md"],
           "arch: the constitution is not in 1-constitution.md alone")
    expect("SENTINEL" not in arch.stdout, "arch head carries file content")
    expect("Demo asks for a ruling" in arch.stdout, "arch head does not name its open need")
    expect("0001-change-demo.md" in arch.stdout, "arch head does not name its review queue")
    expect("# The bridge" in arch.stdout, "arch head lost the bridge pointer")
    expect(units(arch.stdout) < 6_000, f"arch head is {units(arch.stdout)} characters")

    half = validate(vault, "--emit-arch-context", "--arch-only", "--parts-dir", str(parts))
    both = files_in(parts)
    expect(half.returncode == 0 and "arch half" in half.stdout, "arch half: no head")
    expect(holders("SENTINEL-NEXT", both) == ["8-arch-next-steps.md"],
           f"arch half: next-steps is in {holders('SENTINEL-NEXT', both)}")
    expect(set(files) < set(both), "arch half overwrote a component file")

if fails:
    sys.exit("briefing head: " + "; ".join(fails))
print("briefing head: content in files with nothing lost, head names what is open, file "
      "list inside the first 2,000 characters, never over the limit")

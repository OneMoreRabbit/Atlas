#!/usr/bin/env python3
"""Assert the two retirement vocabularies agree (1.30.1). atlas-needs.py cannot import
from tools/, so its RETIRED constant is a copy of the validator's RETIRED_STATUSES —
and a copy drifted silently from 1.28.2 to 1.30.0, carrying 25 closed needs as open
work estate-wide. This test fails the build on any future drift.
STAGED for CI: add `python3 tools/tests/test_retired_agreement.py` to method-ci.yml's
parse-gate step (needs the operator's workflow-scope grant to install)."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def const(path, name):
    for node in ast.walk(ast.parse((ROOT / path).read_text(encoding="utf-8"))):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == name for t in node.targets):
            return set(ast.literal_eval(node.value))
    sys.exit(f"{name} not found in {path}")


a = const("tools/atlas_validate.py", "RETIRED_STATUSES")
b = const("templates/component-repo/scripts/atlas-needs.py", "RETIRED")
if a != b:
    sys.exit(f"retirement vocabularies DISAGREE: validator {sorted(a)} vs template {sorted(b)}")
print("retirement vocabularies agree:", sorted(a))

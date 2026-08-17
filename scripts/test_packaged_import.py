#!/usr/bin/env python3
"""US-025 regression: loud intelligence import.

1. Packaged import (via __init__) keeps intelligence layers — no silent drop.
2. Missing intelligence in the package: generate_prompt still returns a dict,
   but the failure is visible on stderr AND in result['warnings'].

Runs everything in subprocesses with cwd OUTSIDE the repo, so absolute
sibling imports cannot accidentally succeed via sys.path.
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # cp1252 consoles choke on ✅/❌

REPO = Path(__file__).resolve().parent.parent
DB = REPO / "references" / "gpt-image2-prompts-full.db"
MODULES = ["db.py", "retrieval.py", "generate.py", "analytics.py", "cli.py",
           "ir.py", "renderers.py", "pqs.py", "intelligence.py",
           "langcheck.py", "feedback.py", "higgsfield_prompt.py"]

CLEAN = """
import hpm_test
r = hpm_test.HiggsfieldPromptMaster().generate_prompt(
    "professional headshot", "Portrait / Selfie")
assert r["intelligence"]["photography"] is True, r["intelligence"]
assert r["warnings"] == [], r["warnings"]
assert r["prompt"], "empty prompt"
print("OK")
"""

DEGRADED = """
import hpm_test
r = hpm_test.HiggsfieldPromptMaster().generate_prompt(
    "professional headshot", "Portrait / Selfie")
assert r["intelligence"]["photography"] is False, r["intelligence"]
assert r["intelligence"]["marketing"] is False, r["intelligence"]
assert r["warnings"] and "intelligence" in r["warnings"][0], r["warnings"]
assert r["prompt"], "empty prompt"
print("OK")
"""


def build_pkg(parent: Path, drop_intelligence: bool = False) -> None:
    pkg = parent / "hpm_test"
    shutil.rmtree(pkg, ignore_errors=True)
    pkg.mkdir(parents=True)
    for m in MODULES:
        if drop_intelligence and m == "intelligence.py":
            continue
        shutil.copy2(REPO / m, pkg / m)
    shutil.copytree(REPO / "data", pkg / "data")
    shutil.copy2(REPO / "pqs_calibration.json", pkg / "pqs_calibration.json")
    (pkg / "__init__.py").write_text(
        "from .higgsfield_prompt import HiggsfieldPromptMaster\n", encoding="utf-8")


def run_pkg(cwd: Path, code: str) -> subprocess.CompletedProcess:
    env = {"HIGGSFIELD_DB": str(DB),
           "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
           "PATH": os.environ.get("PATH", "")}
    return subprocess.run([sys.executable, "-c", code], cwd=cwd,
                          capture_output=True, text=True, env=env)


def main() -> None:
    assert DB.exists(), f"live DB missing: {DB}"

    with tempfile.TemporaryDirectory() as tmp_s:
        tmp = Path(tmp_s)  # cwd for subprocesses; hpm_test lives beside it
        # 1. Packaged import: layers present, no warnings
        build_pkg(tmp)
        p = run_pkg(tmp, CLEAN)
        assert p.returncode == 0 and "OK" in p.stdout, (p.returncode, p.stdout, p.stderr)
        assert "warning" not in p.stderr.lower(), p.stderr
        print("✅ packaged import keeps intelligence layers (photography=True, warnings=[])")

        # 2. intelligence.py deleted: loud degradation, dict still returned
        build_pkg(tmp, drop_intelligence=True)
        p2 = run_pkg(tmp, DEGRADED)
        assert p2.returncode == 0 and "OK" in p2.stdout, (p2.returncode, p2.stdout, p2.stderr)
        assert "WARNING" in p2.stderr and "intelligence" in p2.stderr, p2.stderr
        print("✅ missing intelligence: WARNING on stderr + result['warnings'], dict returned")

    print("✅ US-025 loud intelligence import: all checks passed")


if __name__ == "__main__":
    main()

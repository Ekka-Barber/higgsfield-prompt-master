"""The global installer covers both agent shapes.

Agents come in two flavours and it is easy to ship only one: directory-based
(a folder per skill) and flat-file (a single .md per capability). opencode and
zcode are the flat-file kind and were missed on the first pass -- these tests
stop that recurring.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "install_global", REPO / "scripts" / "install-global.py")
ig = importlib.util.module_from_spec(SPEC)
sys.modules["install_global"] = ig
SPEC.loader.exec_module(ig)


def test_payload_covers_main_skill_and_every_command():
    names = {n for n, _ in ig.payload()}
    assert "rasm-engine" in names, "engine skill must install"
    for cmd in ("rasm", "rasm-arabic", "rasm-help", "rasm-menu", "rasm-model"):
        assert cmd in names, f"{cmd} missing from install payload"
    assert not any(n.startswith("_") for n in names), "_shared must not install"


def test_both_agent_shapes_are_configured():
    assert ig.AGENT_SKILL_DIRS, "no directory-based agents configured"
    assert ig.AGENT_FLAT_FILE_DIRS, "no flat-file agents configured"
    flavours = {f for _, f in ig.AGENT_FLAT_FILE_DIRS}
    assert flavours == {"opencode", "zcode"}, flavours


def test_every_payload_item_has_a_skill_md():
    for name, src in ig.payload():
        assert (src / "SKILL.md").is_file(), f"{name} has no SKILL.md to install"


def test_frontmatter_parses_block_scalars():
    """description: > spans lines; the zcode pointer needs it flattened."""
    fm = ig._frontmatter(REPO / "commands" / "rasm-arabic" / "SKILL.md")
    assert fm.get("name") == "rasm-arabic"
    assert len(fm.get("description", "")) > 80, "block scalar not joined"
    assert "\n" not in fm["description"]


def test_zcode_pointer_references_and_does_not_duplicate(tmp_path):
    """A copy would drift; the pointer must point, not duplicate."""
    stats = ig.install_flat(tmp_path, "zcode")
    assert stats.get("written"), stats
    text = (tmp_path / "rasm-arabic.md").read_text(encoding="utf-8")
    assert "mode: subagent" in text, "zcode needs mode: subagent"
    assert str(REPO / "commands" / "rasm-arabic" / "SKILL.md") in text
    # The real skill body must NOT be inlined.
    assert "proofing checklist" not in text, "pointer inlined skill content"
    # Re-running is a no-op.
    assert ig.install_flat(tmp_path, "zcode").get("ok"), "not idempotent"


def test_dry_run_writes_nothing(tmp_path):
    ig.install_flat(tmp_path, "zcode", dry_run=True)
    assert not list(tmp_path.iterdir()), "dry-run created files"


@pytest.mark.skipif(sys.platform != "win32", reason="hard links tested on Windows")
def test_opencode_hardlink_shares_one_inode(tmp_path):
    """Hard link, not copy -- an edit in the repo must be live immediately."""
    stats = ig.install_flat(tmp_path, "opencode")
    assert stats.get("hardlinked"), stats
    src = REPO / "commands" / "rasm-arabic" / "SKILL.md"
    assert (tmp_path / "rasm-arabic.md").stat().st_ino == src.stat().st_ino
    assert ig.install_flat(tmp_path, "opencode").get("ok"), "not idempotent"

"""The /hf-* command skills are valid and internally consistent.

These files are the user-facing surface of the skill, so a broken frontmatter
block or a dangling reference silently disables a command rather than failing
loudly. Cheap to check, expensive to miss.
"""
import re
from pathlib import Path

import pytest

COMMANDS = Path(__file__).resolve().parent.parent / "commands"
EXPECTED = {
    "hf", "hf-arabic", "hf-brief", "hf-social", "hf-poster", "hf-menu",
    "hf-brand", "hf-product", "hf-edit", "hf-search", "hf-model", "hf-help",
}


def _skills():
    return sorted(p for p in COMMANDS.glob("*/SKILL.md"))


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path.parent.name}: missing YAML frontmatter"
    return m.group(1), text


def test_all_expected_commands_exist():
    found = {p.parent.name for p in _skills()}
    assert found == EXPECTED, f"missing: {EXPECTED - found}, extra: {found - EXPECTED}"


@pytest.mark.parametrize("path", _skills(), ids=lambda p: p.parent.name)
def test_frontmatter_name_matches_directory(path):
    fm, _ = _frontmatter(path)
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    assert name, f"{path.parent.name}: no name: field"
    assert name.group(1) == path.parent.name, (
        f"frontmatter name {name.group(1)!r} != directory {path.parent.name!r} "
        "-- the command would be invoked under the wrong slug")


@pytest.mark.parametrize("path", _skills(), ids=lambda p: p.parent.name)
def test_description_present_and_has_triggers(path):
    fm, _ = _frontmatter(path)
    desc = re.search(r"^description:\s*>?\s*\n?(.+)", fm, re.S | re.M)
    assert desc and len(desc.group(1).strip()) > 40, (
        f"{path.parent.name}: description too short to route on")
    assert "/" + path.parent.name in fm, (
        f"{path.parent.name}: description must name its own /slug as a trigger")


@pytest.mark.parametrize("path", _skills(), ids=lambda p: p.parent.name)
def test_shared_references_resolve(path):
    """A command pointing at a missing shared file loses its rules silently."""
    _, text = _frontmatter(path)
    for ref in re.findall(r"\.\./(_shared/[\w-]+\.md)", text):
        assert (COMMANDS / ref).exists(), f"{path.parent.name}: dangling ref {ref}"


@pytest.mark.parametrize("path", _skills(), ids=lambda p: p.parent.name)
def test_no_refuted_techniques_recommended(path):
    """Guard against the folklore the 2026-08 research refuted creeping back."""
    _, text = _frontmatter(path)
    low = text.lower()
    # REFERENCE_N syntax appears in no vendor doc.
    assert not re.search(r"reference_\d", low) or "never" in low or "no " in low, (
        f"{path.parent.name}: REFERENCE_N used without being warned against")
    # Booster tokens carry no information on either target model.
    for booster in ("trending on artstation", "masterpiece,"):
        if booster in low:
            assert "no booster" in low or "never" in low or "noise" in low, (
                f"{path.parent.name}: booster token {booster!r} not marked as bad")


def test_shared_rules_exist():
    for name in ("arabic-rules.md", "model-routing.md", "grill-protocol.md"):
        assert (COMMANDS / "_shared" / name).exists(), f"missing shared/{name}"


def test_arabic_routes_to_gpt_image_2():
    """Arabic text-in-image routes to gpt-image-2.

    Corrected 2026-08-17. The first version of this rule sent Arabic to Nano
    Banana Pro because Google documents ar-EG support while OpenAI's docs never
    mention Arabic -- an argument from silence. Testing shows gpt-image-2
    composes glyphs as vector shapes through a typographic pathway, giving ~99%
    character accuracy vs ~94%, and roughly a generation lead on RTL.
    """
    rules = (COMMANDS / "_shared" / "arabic-rules.md").read_text(encoding="utf-8")
    routing = (COMMANDS / "_shared" / "model-routing.md").read_text(encoding="utf-8")
    head = rules.split("## 1.")[0]
    assert "gpt-image-2" in head, "Arabic routing rule must name gpt-image-2"
    assert "vector" in head.lower(), "state WHY: the vector typographic pathway"
    assert "gpt-image-2" in routing.split("2. **Reference")[0], (
        "routing rule 1 must send Arabic to gpt-image-2")


def test_nano_banana_still_owns_reference_work():
    """The correction must not erase Nano Banana Pro's genuine strengths."""
    routing = (COMMANDS / "_shared" / "model-routing.md").read_text(encoding="utf-8")
    assert "gemini-3-pro-image" in routing
    for strength in ("character consistency", "localisation"):
        assert strength.lower() in routing.lower(), (
            f"Nano Banana Pro's {strength} strength was lost in the correction")


def test_tashkeel_limit_is_recorded():
    """The one documented Arabic failure on gpt-image-2 must stay visible."""
    rules = (COMMANDS / "_shared" / "arabic-rules.md").read_text(encoding="utf-8")
    assert "1 glyph error in 20" in rules, (
        "the diacritics-at-small-size limit is the reason for the tashkeel rule")


def test_negative_prompts_are_disavowed_in_routing():
    routing = (COMMANDS / "_shared" / "model-routing.md").read_text(encoding="utf-8")
    assert "no negative prompt" in routing.lower()

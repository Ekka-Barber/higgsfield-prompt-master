"""US-021 regression: intelligence data externalized to data/*.json.

Checks:
1. All five claim files load and every claim group carries
   _source/_date/_confidence (the loader enforces this at import —
   importing intelligence IS the first gate).
2. Accessors keep their signatures/behavior: photo sentinel None for
   non-photo categories, goal platform keywords beat category map,
   model accessors return shallow copies.
3. Loader validation can fail (tampered dict raises ValueError).
4. No inline dict literals remain in intelligence.py.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))

import intelligence
from intelligence import (
    PHOTOGRAPHY, MARKETING, ART_DIRECTION, GPT_IMAGE_2, NANO_BANANA_PRO,
    CATEGORY_PHOTO_MAP, CATEGORY_MARKETING_MAP,
    get_photo_intelligence, get_marketing_intelligence,
    get_gpt_image_2_intelligence, get_nano_banana_pro_intelligence,
    _validate,
)

# 1. Provenance on every claim group of every claim file
for name, data in [("photography.json", PHOTOGRAPHY),
                   ("marketing.json", MARKETING),
                   ("art_direction.json", ART_DIRECTION),
                   ("gpt_image_2.json", GPT_IMAGE_2),
                   ("nano_banana_pro.json", NANO_BANANA_PRO)]:
    for group, claims in data.items():
        for key in intelligence._PROVENANCE_KEYS:
            assert key in claims, f"{name}:{group} missing {key}"
print(f"provenance OK: {sum(len(d) for d in (PHOTOGRAPHY, MARKETING, ART_DIRECTION, GPT_IMAGE_2, NANO_BANANA_PRO))} claim groups across 5 files")

# 2. Accessor behavior parity
assert get_photo_intelligence("App / Web Design") is None          # sentinel survives JSON null
assert get_photo_intelligence("Portrait / Selfie")["camera"]       # photo mapping intact
assert get_photo_intelligence("", "food photography")["camera"]    # goal inference intact
m = get_marketing_intelligence("Social Media Post", "linkedin banner")
assert m is MARKETING["linkedin_post"], "goal platform keywords must beat category map"
g2 = get_gpt_image_2_intelligence()
nb = get_nano_banana_pro_intelligence()
assert g2["names"]["latest"] == "gpt-image-2"
assert nb["names"]["model_id"] == "gemini-3-pro-image"
g2["names"] = "mutated"
assert GPT_IMAGE_2["names"]["latest"] == "gpt-image-2"             # top-level shallow copy protects source (nested dicts shared by design, US-005 parity)
# Assert the sections that must exist, not a frozen count -- the layers are
# meant to grow as research lands (arabic_and_rtl and fonts were added
# 2026-08-17), and a hardcoded total turns every addition into a false failure.
for _section in ("names", "structures", "text_rendering", "exclusions",
                 "references", "sizes", "params", "mistakes"):
    assert _section in GPT_IMAGE_2, f"GPT_IMAGE_2 lost section {_section!r}"
for _section in ("names", "prompting", "references", "text", "ratios", "limits"):
    assert _section in NANO_BANANA_PRO, f"NANO_BANANA_PRO lost section {_section!r}"
assert len(GPT_IMAGE_2) >= 11 and len(NANO_BANANA_PRO) >= 12
print("accessor parity OK: sentinel, goal precedence, shallow copies, 11+12 sections")

# 3. Gate can fail: tampered claim group must raise
try:
    _validate({"some_group": {"claim": "x"}}, "tampered.json")
    raise AssertionError("tampered dict passed validation")
except ValueError as err:
    assert "tampered.json:some_group._source" in str(err)
    msg = str(err)
print("validation failure path OK:", msg[:60], "...")

# 4. No inline dict literals left in intelligence.py
#
# The rule is "knowledge lives in data/*.json", so what must not reappear is a
# hardcoded dict LITERAL. A dict comprehension that derives a map from data
# already loaded off disk (US-032's category registry) honours that rule -- but
# a substring test for "= {" cannot tell the two apart and failed on it. Use the
# parser: a literal is ast.Dict, a comprehension is ast.DictComp.
import ast

src = (Path(__file__).parent.parent / "intelligence.py").read_text(encoding="utf-8")
literals = [
    target.id
    for node in ast.parse(src).body
    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
    and node.value.keys                      # {} is an empty accumulator, fine
    for target in node.targets
    if isinstance(target, ast.Name)
]
assert not literals, f"inline dict literal(s) in intelligence.py: {literals}"
print("no inline dicts OK (dict comprehensions over loaded data allowed)")

print("✅ test_intelligence_data: all checks passed")

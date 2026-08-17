#!/usr/bin/env python3
"""US-011 self-check: IR schema + slot extraction over synthetic fixtures
and the full live corpus (every searchable exemplar, all 3 structures)."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir import IR_FIELDS, PromptIR, extract_ir
from higgsfield_prompt import HiggsfieldPromptMaster

# ── 1. IR fields defined exactly ──
assert IR_FIELDS == (
    "subject", "action", "environment", "style", "lighting", "color", "mood",
    "composition", "text_elements", "negative_concepts", "aspect_ratio",
    "references", "output_intent", "quality_tier")
assert list(PromptIR().to_dict()) == list(IR_FIELDS)
assert PromptIR().output_intent == "general_image"
assert PromptIR().quality_tier == "standard"

# ── 2. Synthetic fixtures (deterministic) ──
tpl = ('Goal: Create a poster titled {argument name="headline text" default="SALE"}\n'
       '\nCanvas: 4:5 aspect ratio, dark navy palette, moody atmosphere.\n'
       '\nLayout: Arrange content into exactly 8 numbered badges in three '
       'columns without watermarks.')
ir = extract_ir(tpl)
assert any("headline" in f.lower() for f in ir.text_elements), ir.text_elements
assert ir.aspect_ratio == "4:5", ir.aspect_ratio
assert any("8 numbered badges" in f for f in ir.composition), ir.composition
assert any("three columns" in f.lower() for f in ir.composition), ir.composition
assert ir.negative_concepts and any("watermarks" in f for f in ir.negative_concepts)
assert ir.output_intent == "poster", ir.output_intent
assert any("canvas" in f.lower() for f in ir.composition), ir.composition  # zone name

ir = extract_ir('A hyper-realistic portrait of a chef in a dim kitchen, golden '
                'hour lighting, warm amber palette, inspired by Wes Anderson, '
                'without text or watermarks. 4:5')
assert ir.subject and "chef" in ir.subject[0].lower(), ir.subject
assert any("golden hour" in f.lower() for f in ir.lighting), ir.lighting
assert ir.quality_tier == "high", ir.quality_tier
assert any("wes anderson" in f.lower() for f in ir.references), ir.references
assert ir.aspect_ratio == "4:5", ir.aspect_ratio

ir = extract_ir('{"style":"isometric illustration","composition":"1:1 format, '
                'three tiers","lighting":"soft studio lighting",'
                '"palette":["navy","cyan"],"negative":["watermark"]}')
assert any("isometric" in f for f in ir.style), ir.style
assert ir.lighting and ir.negative_concepts, (ir.lighting, ir.negative_concepts)
assert ir.aspect_ratio == "1:1", ir.aspect_ratio

# ── 3. Full corpus sweep — no exemplar may raise ──
m = HiggsfieldPromptMaster()
rows = m.conn.execute(
    f"SELECT id, prompt_text, structure_type FROM prompts WHERE {m._searchable}"
).fetchall()
tallies, filled = {}, 0
for r in rows:
    ir = extract_ir(r["prompt_text"])
    tallies[r["structure_type"]] = tallies.get(r["structure_type"], 0) + 1
    if ir.filled():
        filled += 1
print(f"swept {len(rows)} exemplars: {tallies}, {filled} produced non-empty IR")

# ── 4. Per-structure real-exemplar spot checks ──
for structure, must_slot in (("JSON", "composition"), ("Template", "composition"),
                             ("Flat prose", "subject")):
    row = m.conn.execute(
        f"SELECT prompt_text FROM prompts WHERE {m._searchable} AND "
        f"structure_type=? AND length_chars>500 ORDER BY length_chars DESC LIMIT 1",
        (structure,)).fetchone()
    ir = extract_ir(row["prompt_text"])
    assert getattr(ir, must_slot), (structure, ir.to_dict())
    assert ir.output_intent and ir.quality_tier, (structure, ir.output_intent)

# ── 5. Garbage tolerance ──
for garbage in ("", "   ", "!!! ??? ...", "{broken json", 42, None):
    extract_ir(garbage)

print("✅ US-011 IR + slot extraction OK")
sys.exit(0)

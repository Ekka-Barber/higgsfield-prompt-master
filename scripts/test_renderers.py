#!/usr/bin/env python3
"""US-012 self-check: per-model prose renderers — synthetic fixtures with
every AC lever, plus a full live-corpus sweep (extract_ir -> both renderers)
asserting no booster tokens, no REFERENCE_N, no word-limit folklore."""
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

from ir import PromptIR, extract_ir
from renderers import (render_gpt_image_2, render_nano_banana_pro,
                       _BOOSTER_RE, _REFN_RE, _WORD_LIMIT_RE)

BAD = (_BOOSTER_RE, _REFN_RE, _WORD_LIMIT_RE)


def check(text):
    assert text and text.strip(), "empty render"
    for rx in BAD:
        assert not rx.search(text), f"{rx.pattern!r} leaked: {text!r}"
    assert not re.search(r"REFERENCE_\d", text)


# ── 1. Synthetic IR exercising every AC lever ──
ir = PromptIR()
ir.add("subject", "a chef plating a dessert")
ir.add("action", "carefully drizzling caramel")
ir.add("environment", "in a dim specialty kitchen")
ir.add("style", "editorial food photography, 85mm lens, f/1.8")
ir.add("lighting", "warm golden hour side light")
ir.add("color", "deep amber palette")
ir.add("mood", "moody cinematic masterpiece")          # booster planted
ir.add("composition", "close-up framing, shallow depth of field")
ir.add("text_elements", "SALE")                        # CAPS lever
ir.add("text_elements", "grand opening")               # plain -> double quotes
ir.add("negative_concepts", "watermarks")
ir.add("negative_concepts", "traffic")
ir.add("references", "inspired by Wes Anderson")
ir.add("references", "REFERENCE_2 the ceramic plate")  # banned syntax planted
ir.aspect_ratio = "4:5"

gpt = render_gpt_image_2(ir)
check(gpt)
assert gpt.lower().startswith("a chef plating"), gpt  # front-loaded subject
for facet in ("dim specialty kitchen", "golden hour", "deep amber",
              "close-up framing"):
    assert facet in gpt, (facet, gpt)                 # 7-facet coverage
assert "without any watermarks" in gpt and "traffic" in gpt, gpt  # inline channel
assert "SALE" in gpt and '"grand opening"' in gpt, gpt   # quotes/CAPS levers
assert "1024x1536" in gpt, gpt                        # 4:5 -> portrait heuristic
assert "the second image" in gpt, gpt                 # REFERENCE_2 rewritten
assert "Wes Anderson" in gpt, gpt

nb = render_nano_banana_pro(ir)
check(nb)
assert nb.lower().startswith("the scene centers on"), nb  # narrative opener
assert "85mm lens" in nb and "f/1.8" in nb, nb     # camera language welcome
assert "no signs of traffic" in nb, nb                # semantic positive rewrite
assert "no watermarks" not in nb.lower().replace("no signs of", ""), nb
assert "a clean, unmarked finish" in nb, nb           # dict rewrite for watermarks
assert re.search(r"(?i)the second image", nb), nb     # ordinal reference addressing
assert "4:5 frame" in nb, nb                          # Pro ratio kept
assert not re.search(r"^Subject:|: ", nb.split(".")[0]), nb  # no labels up front

# ── 2. Degenerate inputs ──
empty_gpt = render_gpt_image_2(PromptIR())
empty_nb = render_nano_banana_pro(PromptIR())
check(empty_gpt)
check(empty_nb)
check(render_gpt_image_2(extract_ir("")))
check(render_nano_banana_pro(extract_ir("x")))

# ratio hygiene: Pro-forbidden extremes never emitted, out-of-range GPT sizes skipped
ir_bad = PromptIR()
ir_bad.add("subject", "a tall banner")
ir_bad.aspect_ratio = "1:8"
assert "1:8" not in render_nano_banana_pro(ir_bad)
assert "Suggested size" not in render_gpt_image_2(ir_bad)

# ── 3. Full corpus sweep — every searchable exemplar renders cleanly ──
from higgsfield_prompt import HiggsfieldPromptMaster
m = HiggsfieldPromptMaster()
rows = m.conn.execute(
    f"SELECT prompt_text FROM prompts WHERE {m._searchable}").fetchall()
tallied = 0
for r in rows:
    e = extract_ir(r["prompt_text"])
    check(render_gpt_image_2(e))
    check(render_nano_banana_pro(e))
    tallied += 1
assert tallied == m.stats()["total_prompts"], (tallied, m.stats())

print(f"OK - renderers: fixtures + {tallied} corpus exemplars x 2 models, "
      "zero boosters / REFERENCE_N / word-limit folklore")

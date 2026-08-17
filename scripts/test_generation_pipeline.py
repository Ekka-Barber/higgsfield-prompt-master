"""US-013 verification: generate_prompt demonstrably consumes the corpus.

Pipeline: retrieve exemplar -> extract IR -> fill slots from goal + corrected
layers -> render per routed model. Checks:
  1. source_prompt_ids resolve to real corpus rows (exemplars consumed)
  2. Stubbing retrieval to [] changes the output and empties source ids
  3. Goal platform keywords beat the category map (LinkedIn != Instagram)
  4. Template outputs carry 2-4 arguments (corpus average 2.7) and keep
     zone schemas with element counts where the exemplar had them
  5. Rendering follows the routed model (gpt_image_2 | nano_banana_pro)
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

from higgsfield_prompt import HiggsfieldPromptMaster, Prompt
from intelligence import get_marketing_intelligence
from ir import _ARG_RE, _COUNT_RE

hpm = HiggsfieldPromptMaster()
failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
    return cond


# ── 1. Live retrieval: ids resolve to real corpus rows ──
r = hpm.generate_prompt("Premium skincare serum product shot on marble",
                        "Product Marketing", "Template", style="modern, clean")
check(r["source_prompt_ids"], "live retrieval produced no source_prompt_ids")
for pid in r["source_prompt_ids"]:
    row = hpm.conn.execute("SELECT id FROM prompts WHERE id = ?", (pid,)).fetchone()
    check(row is not None, f"source id {pid} not a corpus row")

# ── 2. Stubbing retrieval to [] changes output + empties ids ──
stubbed = {}
# Three retrieval sources feed generation: FTS, category templates, and the
# curated master prompts imported from references/*.md (US-022). All three have
# to be stubbed to assert the empty case -- otherwise curated rows legitimately
# still supply an exemplar and source_prompt_ids is non-empty.
orig = (hpm.fts_search, hpm.get_templates, hpm.search_curated)
hpm.fts_search = lambda *a, **k: []
hpm.get_templates = lambda *a, **k: []
hpm.search_curated = lambda *a, **k: []
try:
    stubbed = hpm.generate_prompt("Premium skincare serum product shot on marble",
                                  "Product Marketing", "Template", style="modern, clean")
finally:
    hpm.fts_search, hpm.get_templates, hpm.search_curated = orig
check(stubbed.get("source_prompt_ids") == [], "stubbed retrieval ids != []")
check(stubbed.get("prompt") != r["prompt"], "stubbed retrieval output identical to live")
check(stubbed.get("prompt"), "stubbed retrieval produced empty prompt")

# ── 3. Goal platform keywords BEFORE category map ──
goal = "LinkedIn carousel graphic for a B2B SaaS analytics report"
m = get_marketing_intelligence("Social Media Post", goal)
check(m and m["framework"] == "Authority", "LinkedIn goal did not route to linkedin_post")
check("Instagram" not in (m or {}).get("safe_zones", ""), "LinkedIn goal emitted Instagram safe-zones")
rl = hpm.generate_prompt(goal, "Social Media Post")
check("instagram" not in rl["prompt"].lower(),
      f"Instagram leaked into LinkedIn output (ar={rl['aspect_ratio']})")

# ── 4. Template exemplar consumption: 2-4 args + element counts preserved ──
row = None
for cand in hpm.conn.execute(
        f"SELECT * FROM prompts WHERE structure_type = 'Template' "
        f"AND {hpm._searchable} LIMIT 800").fetchall():
    text = cand["prompt_text"]
    args = _ARG_RE.findall(text)
    counts = _COUNT_RE.findall(text or "")
    if 2 <= len(args) <= 4 and counts and any(d for _, d in args):
        row = cand
        break
check(row is not None, "no corpus Template exemplar with 2-4 args + element counts found")
if row:
    exemplar = Prompt.from_row(row)
    n_args = len(_ARG_RE.findall(exemplar.prompt_text))
    check(2 <= n_args <= 4, f"selected exemplar carries {n_args} args, expected 2-4")
    orig = (hpm.fts_search, hpm.get_templates)
    hpm.fts_search = lambda *a, **k: [exemplar]
    hpm.get_templates = lambda *a, **k: []
    try:
        fixed = hpm.generate_prompt("organic tea brand poster", "Poster / Flyer", "Template")
    finally:
        hpm.fts_search, hpm.get_templates = orig
    check(fixed["source_prompt_ids"] == [exemplar.id],
          f"source ids {fixed['source_prompt_ids']} != consumed exemplar [{exemplar.id}]")
    low = fixed["prompt"].lower()
    count_phrase = _COUNT_RE.search(exemplar.prompt_text).group(0).lower()
    check(count_phrase in low,
          f"element count phrase {count_phrase!r} from exemplar not preserved in output")
    # An argument DEFAULT is the donor exemplar's own subject ("fitness app",
    # "PulseFit"). It must NOT reach the output: that is how an analytics
    # dashboard goal ended up rendering a fitness brand. Structure transfers
    # (the element-count phrase checked above), subject matter does not.
    defaults = [d for _, d in _ARG_RE.findall(exemplar.prompt_text) if d]
    leaked = [d for d in defaults
              if d.lower() in low and d.lower() not in "organic tea brand poster"]
    check(not leaked,
          f"donor argument default(s) leaked into output: {leaked}")

# Live path: Template generations prefer 2-4-arg exemplars when available
for goal_i, cat in [("mobile app onboarding screens", "App / Web Design"),
                    ("gaming channel cover art", "YouTube Thumbnail")]:
    ri = hpm.generate_prompt(goal_i, cat, "Template")
    if ri["source_prompt_ids"]:
        primary = hpm.conn.execute(
            "SELECT prompt_text FROM prompts WHERE id = ?",
            (ri["source_prompt_ids"][0],)).fetchone()[0]
        n = primary.count("{argument")
        check(n <= 4 or "{argument" not in primary,
              f"primary exemplar for {goal_i!r} has {n} args (>4)")

# ── 5. Rendered per routed model ──
rt = hpm.generate_prompt("bold gaming thumbnail with huge outlined text",
                         "YouTube Thumbnail")
check(rt["model_recommendation"]["id"] == "gpt_image_2",
      f"thumbnail routed to {rt['model_recommendation']['id']}, expected gpt_image_2")
rp = hpm.generate_prompt("consistent character portrait of a founder",
                         "Portrait / Selfie")
check(rp["model_recommendation"]["id"] == "nano_banana_pro",
      f"portrait routed to {rp['model_recommendation']['id']}, expected nano_banana_pro")
check(rp["prompt"].startswith("The scene centers on"),
      "nano_banana_pro render missing narrative opener")
check(not rt["prompt"].startswith("The scene centers on"),
      "gpt_image_2 render used the nano renderer")

if failures:
    for f in failures:
        print(f"❌ {f}")
    sys.exit(1)
print("✅ US-013: retrieval-consumed generation pipeline verified")

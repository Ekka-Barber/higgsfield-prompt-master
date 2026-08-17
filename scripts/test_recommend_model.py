"""Self-check: _recommend_model two-model routing (US-007, SOURCE_TRUTH §6)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from higgsfield_prompt import HiggsfieldPromptMaster

m = HiggsfieldPromptMaster()
r = m._recommend_model

# ids + display names are exactly the two real targets
valid = {"gpt_image_2": ("gpt-image-2", "GPT Image 2"),
         "nano_banana_pro": ("gemini-3-pro-image", "Nano Banana Pro")}

# routing signals: layout/UI/text-dense -> gpt_image_2
for goal in ["App UI dashboard mockup", "text-dense infographic poster", "webpage layout with typography"]:
    rec = r("", goal, "Template")
    assert rec["id"] == "gpt_image_2", goal

# reference compositing / <=5-char consistency / localization / brand -> nano_banana_pro
for goal in ["composite from reference images", "same person in every scene",
             "consistent 5-character brand mascot", "localized packaging", "rebrand our logo identity",
             "product photo portrait"]:
    rec = r("", goal, "Template")
    assert rec["id"] == "nano_banana_pro", goal

# category defaults + every return carries correct ids/names
for cat, goal in [("", "make a poster"), ("Poster / Flyer", ""), ("App / Web Design", ""),
                  ("Portrait / Selfie", ""), ("Unknown", "")]:
    rec = r(cat, goal, "Template")
    mid, name = valid[rec["id"]]
    assert rec["model_id"] == mid and rec["display_name"] == name, rec
    assert set(rec) >= {"id", "model_id", "display_name", "signal"}

# generate_prompt surfaces the dict end-to-end
res = m.generate_prompt(goal="app dashboard UI", category="App / Web Design")
assert res["model_recommendation"]["id"] == "gpt_image_2"

print("✅ router OK —", len(valid), "targets, signals verified")

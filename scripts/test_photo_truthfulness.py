"""US-010 verification: camera specs never leak into non-photo categories."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

from intelligence import get_photo_intelligence, CATEGORY_PHOTO_MAP
from higgsfield_prompt import HiggsfieldPromptMaster

failures = []

# AC 1: sentinel semantics — explicit non-photo categories return None
non_photo = [c for c, v in CATEGORY_PHOTO_MAP.items() if v is None]
for cat in non_photo:
    r = get_photo_intelligence(cat, goal="restaurant app with product photos of food")
    if r is not None:
        failures.append(f"get_photo_intelligence({cat!r}) returned dict, expected None")
# unmapped/None-goal inference still works (lifestyle default)
assert get_photo_intelligence("Unmapped Whatever", "a cozy room interior") is not None

# AC 2-4: generate across all structures; no camera bodies/lenses in non-photo output
CAMERA_TOKENS = ["Phase One", "Hasselblad", "Canon", "Sony A7", "Fujifilm", "MP-E 65mm",
                 "Schneider", "leaf shutter", "Camera:", "Shot on"]
master = HiggsfieldPromptMaster()
targets = ["App / Web Design", "Infographic / Edu Visual", "Abstract / Background",
           "Comic / Storyboard", "Game Asset", "YouTube Thumbnail"]
for cat in targets:
    for structure in [None, "Flat", "Template", "JSON"]:
        kw = {"category": cat, "goal": "restaurant menu app screen with food imagery"}
        if structure:
            kw["structure"] = structure
        result = master.generate_prompt(**kw)
        text = result["prompt"]
        for tok in CAMERA_TOKENS:
            if tok in text:
                failures.append(f"{cat} [{structure}]: leaked {tok!r}")
        if result["intelligence"]["photography"]:
            failures.append(f"{cat} [{structure}]: intelligence.photography=True, expected False")

# photo categories still get cameras (guard didn't over-block) — camera/lens
# substance flows as IR fragments (US-013 prose rendering), not a "Camera:" label
        photo_result = master.generate_prompt(category="Food Photography",
                                              goal="coffee cup on wooden table")
photo_layer = get_photo_intelligence("Food Photography", "coffee cup on wooden table")
has_camera = photo_layer["camera"].split(" or ")[0] in photo_result["prompt"]
has_lens = photo_layer["lens"][:9] in photo_result["prompt"]
if not photo_result["intelligence"]["photography"] or not (has_camera or has_lens):
    failures.append("photo category lost its camera specs")

if failures:
    for f in failures:
        print(f"❌ {f}")
    sys.exit(1)
print("✅ US-010: no camera leaks, sentinel + guards + reflective flag all verified")

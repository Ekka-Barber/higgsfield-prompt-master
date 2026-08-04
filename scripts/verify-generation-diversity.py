#!/usr/bin/env python3
"""
Verify that generate_prompt() produces diverse, goal-specific results.
Catches the 3 critical bugs that were fixed in June 2026:
  1. FTS returning identical source IDs for different goals
  2. Template arguments contaminated from wrong-domain prompts
  3. Photography specs injected into non-photo categories

Usage:
    cd ~/.hermes/skills/higgsfield-prompt-master
    python3 scripts/verify-generation-diversity.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()

# Diverse goals that should produce DIFFERENT source IDs and prompts
test_cases = [
    ("Personal brand hero landing page with portrait", "App / Web Design", "Template"),
    ("Dark mode book reading section with amber light", "App / Web Design", "Template"),
    ("Masonry photo gallery with filter chips", "App / Web Design", "Template"),
    ("Contact form with footer and social links", "App / Web Design", "Template"),
    ("Premium skincare serum product shot on marble", "Product Marketing", "Template"),
    ("Cyberpunk character portrait in neon alleyway", "Portrait / Selfie", "Template"),
]

print("=" * 70)
print("VERIFICATION: Generation Diversity Check")
print("=" * 70)

all_source_ids = []
all_first_args = []
all_prompts = []
errors = []

for goal, cat, struct in test_cases:
    r = hpm.generate_prompt(goal=goal, category=cat, structure=struct, style="modern, clean")
    ids = tuple(r["source_prompt_ids"])
    all_source_ids.append(ids)
    all_prompts.append(r["prompt"])
    
    # Check for contamination: no "Munch" or "vaporwave" or "cyberpunk" in web design prompts
    prompt_lower = r["prompt"].lower()
    if cat == "App / Web Design":
        for bad_term in ["edvard munch", "the scream", "vaporwave", "cyberpunk", "y2k"]:
            if bad_term in prompt_lower:
                errors.append(f"  ❌ CONTAMINATION: '{bad_term}' found in {cat} prompt for goal: {goal[:40]}")
    
    # Check for photography specs in non-photo categories
    if cat in ["App / Web Design", "Infographic / Edu Visual"]:
        for bad_term in ["camera:", "lens:", "f/", "aperture", "bokeh"]:
            if bad_term in prompt_lower and "design system" not in prompt_lower:
                errors.append(f"  ❌ PHOTO SPECS in non-photo category: '{bad_term}' in {cat}")
                break
    
    print(f"\nGoal: {goal[:50]}...")
    print(f"  Source IDs: {list(ids)}")
    print(f"  Score: {r['quality_score']['total']}/100 ({r['quality_score']['grade']})")
    print(f"  Length: {r['length']} chars")

# Check 1: Source IDs should NOT all be identical
unique_id_sets = len(set(all_source_ids))
print(f"\n{'=' * 70}")
print(f"Unique source ID sets: {unique_id_sets}/{len(test_cases)}")
if unique_id_sets < len(test_cases) * 0.5:
    errors.append(f"  ❌ DIVERSITY: Only {unique_id_sets} unique ID sets out of {len(test_cases)} — FTS fallback may be misfiring")
else:
    print(f"  ✅ Good diversity in source retrieval")

# Check 2: No contamination
if errors:
    print(f"\n{'=' * 70}")
    print(f"ERRORS FOUND ({len(errors)}):")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"\n  ✅ No contamination detected")
    print(f"\n{'=' * 70}")
    print("ALL CHECKS PASSED ✅")
    sys.exit(0)

#!/usr/bin/env python3
"""
Verify that generate_prompt() produces diverse, goal-specific results.
Catches the 3 critical bugs that were fixed in June 2026:
  1. FTS returning identical source IDs for different goals
  2. Template arguments contaminated from wrong-domain prompts
  3. Photography specs injected into non-photo categories
Plus duplication-class regression gates (US-015):
  4. Pairwise 5-gram Jaccard across different goals (FAIL >= 0.70)
  5. Goal-swap hard-fail: outputs >= 0.70 similar while goals < 0.20 similar
  6. Batch distinct-3 + source-ID entropy (reported)
  7. Cross-goal discrimination delta (target >= 0.30)

Usage:
    cd ~/.agents/skills/higgsfield-prompt-master
    python3 scripts/verify-generation-diversity.py
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import math
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import HiggsfieldPromptMaster

_STOP = {"a", "an", "the", "with", "and", "for", "of", "in", "on", "to", "at",
         "by", "from", "as", "is", "are", "or", "your"}


def _words(text):
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP]


def _ngrams(text, n):
    ws = re.findall(r"[a-z0-9]+", text.lower())
    return set(tuple(ws[i:i + n]) for i in range(len(ws) - n + 1))


def _jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _goal_recall(prompt_text, goal_words):
    """G(p, g): fraction of goal content words present in the prompt."""
    if not goal_words:
        return 0.0
    pws = set(re.findall(r"[a-z0-9]+", prompt_text.lower()))
    return len(goal_words & pws) / len(goal_words)

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

# Check 2: Source-ID entropy (bits over the flattened donor distribution; ~0 means every goal drew the same donors)
id_counts = Counter(i for ids in all_source_ids for i in ids)
id_total = sum(id_counts.values())
id_entropy = -sum((c / id_total) * math.log2(c / id_total) for c in id_counts.values()) if id_total else 0.0
print(f"Source-ID entropy: {id_entropy:.3f} bits across {len(id_counts)} unique donor IDs")

# Check 3: Pairwise 5-gram Jaccard across different goals (FAIL >= 0.70)
#          + goal-swap hard-fail (outputs >= 0.70 similar while goals < 0.20 similar)
pair_scores = []
for i in range(len(test_cases)):
    for j in range(i + 1, len(test_cases)):
        out_sim = _jaccard(_ngrams(all_prompts[i], 5), _ngrams(all_prompts[j], 5))
        goal_sim = _jaccard(set(_words(test_cases[i][0])), set(_words(test_cases[j][0])))
        pair_scores.append((out_sim, goal_sim, i, j))
worst = max(pair_scores, key=lambda t: t[0])
print(f"Max pairwise output 5-gram Jaccard: {worst[0]:.3f} (that goal pair similarity: {worst[1]:.3f})")
for out_sim, goal_sim, i, j in pair_scores:
    if out_sim >= 0.70:
        errors.append(
            f"  ❌ DUPLICATION: outputs for goals {i+1}/{j+1} have 5-gram Jaccard {out_sim:.3f} >= 0.70 "
            f"({test_cases[i][0][:35]!r} vs {test_cases[j][0][:35]!r})")
        if goal_sim < 0.20:
            errors.append(
                f"  ❌ GOAL-SWAP HARD-FAIL: goals {i+1}/{j+1} only {goal_sim:.3f} similar (<0.20) "
                f"but outputs {out_sim:.3f} similar (>=0.70) — duplication-class bug")

# Check 4: Batch distinct-3 (distinct 3-grams / total 3-grams across the whole batch)
batch_trigrams = []
for p in all_prompts:
    ws = re.findall(r"[a-z0-9]+", p.lower())
    batch_trigrams.extend(tuple(ws[k:k + 3]) for k in range(len(ws) - 2))
distinct3 = len(set(batch_trigrams)) / len(batch_trigrams) if batch_trigrams else 1.0
print(f"Batch distinct-3: {distinct3:.3f} ({len(set(batch_trigrams))}/{len(batch_trigrams)} 3-grams)")

# Check 5: Cross-goal discrimination delta = mean G(pi,gi) - mean G(pi,gj!=i); target >= 0.30
own_scores, cross_scores = [], []
for i in range(len(test_cases)):
    own_scores.append(_goal_recall(all_prompts[i], set(_words(test_cases[i][0]))))
    for j in range(len(test_cases)):
        if j != i:
            cross_scores.append(_goal_recall(all_prompts[i], set(_words(test_cases[j][0]))))
own_mean = sum(own_scores) / len(own_scores)
cross_mean = sum(cross_scores) / len(cross_scores)
delta = own_mean - cross_mean
print(f"Cross-goal discrimination: own-goal G = {own_mean:.3f}, cross-goal G = {cross_mean:.3f}, "
      f"delta = {delta:.3f} (target >= 0.30)")
if delta < 0.30:
    errors.append(f"  ❌ DISCRIMINATION: cross-goal delta {delta:.3f} < 0.30 — outputs do not track their own goals")

# Final verdict
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

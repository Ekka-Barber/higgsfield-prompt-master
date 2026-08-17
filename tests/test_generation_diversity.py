"""Port of scripts/verify-generation-diversity.py to parameterized pytest
(US-024). Runs against the conftest fixture DB via HIGGSFIELD_DB; the
original script remains the live-corpus gate (CI runs it when the 55 MB
DB is present — it is gitignored)."""
import math
import re
from collections import Counter

import pytest

_STOP = {"a", "an", "the", "with", "and", "for", "of", "in", "on", "to", "at",
         "by", "from", "as", "is", "are", "or", "your"}

# (goal, category) pairs from the original script (structure/style fixed).
CASES = [
    ("Personal brand hero landing page with portrait", "App / Web Design"),
    ("Dark mode book reading section with amber light", "App / Web Design"),
    ("Masonry photo gallery with filter chips", "App / Web Design"),
    ("Contact form with footer and social links", "App / Web Design"),
    ("Premium skincare serum product shot on marble", "Product Marketing"),
    ("Cyberpunk character portrait in neon alleyway", "Portrait / Selfie"),
]


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
    if not goal_words:
        return 0.0
    pws = set(re.findall(r"[a-z0-9]+", prompt_text.lower()))
    return len(goal_words & pws) / len(goal_words)


@pytest.fixture(scope="module")
def results(hpm):
    return [hpm.generate_prompt(goal=goal, category=cat, structure="Template",
                                style="modern, clean") for goal, cat in CASES]


@pytest.mark.parametrize("idx", range(len(CASES)), ids=[c[0][:24] for c in CASES])
def test_goal_output_basic_shape(results, idx):
    r = results[idx]
    assert r["prompt"] and r["length"] == len(r["prompt"])
    assert r["source_prompt_ids"], "no exemplars consumed"
    assert 0 <= r["quality_score"]["total"] <= 100


@pytest.mark.parametrize("idx", range(len(CASES)), ids=[c[0][:24] for c in CASES])
def test_no_contamination(results, idx):
    goal, cat = CASES[idx]
    if cat != "App / Web Design":
        pytest.skip("contamination gate targets web-design goals")
    prompt_lower = results[idx]["prompt"].lower()
    for bad_term in ["edvard munch", "the scream", "vaporwave", "cyberpunk", "y2k"]:
        assert bad_term not in prompt_lower, f"CONTAMINATION: {bad_term!r} in {goal[:40]}"


@pytest.mark.parametrize("idx", range(len(CASES)), ids=[c[0][:24] for c in CASES])
def test_no_photo_specs_in_non_photo_categories(results, idx):
    goal, cat = CASES[idx]
    if cat not in ("App / Web Design", "Infographic / Edu Visual"):
        pytest.skip("photo-spec gate targets non-photo categories")
    prompt_lower = results[idx]["prompt"].lower()
    for bad_term in ["camera:", "lens:", "f/", "aperture", "bokeh"]:
        assert bad_term not in prompt_lower or "design system" in prompt_lower, \
            f"PHOTO SPECS in non-photo category: {bad_term!r} in {cat}"


def test_unique_source_id_sets(results):
    id_sets = {tuple(r["source_prompt_ids"]) for r in results}
    assert len(id_sets) >= len(CASES) * 0.5, \
        f"only {len(id_sets)} unique ID sets — FTS fallback may be misfiring"


def test_source_id_entropy(results):
    id_counts = Counter(i for r in results for i in r["source_prompt_ids"])
    total = sum(id_counts.values())
    entropy = -sum((c / total) * math.log2(c / total) for c in id_counts.values())
    assert entropy > 0  # ~0 bits would mean every goal drew the same donors


def test_pairwise_jaccard_below_threshold(results):
    for i in range(len(CASES)):
        for j in range(i + 1, len(CASES)):
            out_sim = _jaccard(_ngrams(results[i]["prompt"], 5),
                               _ngrams(results[j]["prompt"], 5))
            goal_sim = _jaccard(set(_words(CASES[i][0])), set(_words(CASES[j][0])))
            assert out_sim < 0.70, \
                f"DUPLICATION: goals {i+1}/{j+1} 5-gram Jaccard {out_sim:.3f} >= 0.70"
            assert not (out_sim >= 0.70 and goal_sim < 0.20), "goal-swap bug"


def test_cross_goal_discrimination_delta(results):
    own = [_goal_recall(results[i]["prompt"], set(_words(CASES[i][0])))
           for i in range(len(CASES))]
    cross = [_goal_recall(results[i]["prompt"], set(_words(CASES[j][0])))
             for i in range(len(CASES)) for j in range(len(CASES)) if j != i]
    delta = sum(own) / len(own) - sum(cross) / len(cross)
    assert delta >= 0.30, f"discrimination delta {delta:.3f} < 0.30"

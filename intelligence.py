#!/usr/bin/env python3
"""
Intelligence Layers for Prompt Generation
==========================================
Domain expertise that transforms a generic goal into a professional-grade
prompt. All knowledge lives as editable data in data/*.json (US-021);
this module loads, validates provenance, and exposes the accessors.

Files (data/):
  photography.json    — camera bodies, lenses, lighting, color science,
                        bokeh by shoot type (8 groups)
  marketing.json      — AIDA framework, platform specs, safe zones,
                        tone by placement (7 groups)
  art_direction.json  — composition systems, color theory, contrast,
                        style references (4 groups)
  gpt_image_2.json    — OpenAI official-docs guidance (11 claim groups,
                        rebuilt per research/SOURCE_TRUTH.md §3)
  nano_banana_pro.json— Google official-docs guidance for
                        gemini-3-pro-image (12 claim groups, SOURCE_TRUTH §4)
  categories.json     — the category registry: canonical names, aliases, and
                        photo/marketing routing. Single source for this
                        module's maps and db.CATEGORY_NORMALIZE
                        (routing config, not claims — no provenance keys)

Every claim group in the five claim files must carry _source/_date/
_confidence/_review_after evidence fields; the loader raises ValueError
listing any group that doesn't (a claim without evidence is
untrustable by construction). The two model files are GENERATED from
versioned capability profiles (profiles/<model>@<date>.yaml, US-030)
by scripts/sync_profiles.py — edit the profile, not the JSON.
"""

import json
from pathlib import Path

_DATA_DIR = Path(__file__).parent / "data"
_PROVENANCE_KEYS = ("_source", "_date", "_confidence", "_review_after")


def _validate(data: dict, filename: str) -> None:
    """Require _source/_date/_confidence/_review_after on every top-level
    claim group — a claim without evidence fields is rejected outright."""
    missing = [f"{filename}:{group}.{key}"
               for group, claims in data.items()
               for key in _PROVENANCE_KEYS
               if not isinstance(claims, dict) or key not in claims]
    if missing:
        raise ValueError(
            "intelligence data missing evidence fields: " + ", ".join(missing))


def _load(filename: str, provenance: bool = True) -> dict:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        data = json.load(f)
    if provenance:
        _validate(data, filename)
    return data


# ═══════════════════════════════════════════════════════════════════
# LAYERS 1-3: PHOTOGRAPHY / MARKETING / ART DIRECTION
# ═══════════════════════════════════════════════════════════════════
# Curated craft defaults shipped with the original corpus build — no
# external doc backs them (provenance recorded per group in-file as
# "original curated layer"; confidence medium, editable as data).

PHOTOGRAPHY = _load("photography.json")
MARKETING = _load("marketing.json")
ART_DIRECTION = _load("art_direction.json")

# ═══════════════════════════════════════════════════════════════════
# CATEGORY → INTELLIGENCE MAPPING
# ═══════════════════════════════════════════════════════════════════

# Derived from the single category registry (US-032) so a new category is one
# edit in data/categories.json rather than six across db.py and this module.
# A category's "photo": null is meaningful -- it marks an explicit non-photo
# category, which get_photo_intelligence() must distinguish from "unmapped"
# (US-010), so the key is kept with a None value rather than dropped.
_registry = _load("categories.json", provenance=False)["categories"]
CATEGORY_PHOTO_MAP = {c["name"]: c["photo"] for c in _registry
                      if c["photo"] is not None or c["non_photo"]}
CATEGORY_MARKETING_MAP = {c["name"]: c["marketing"] for c in _registry
                          if c["marketing"] is not None}

def get_photo_intelligence(category: str, goal: str = "") -> "dict | None":
    """Get photography settings for a category, with goal-based override.

    Returns None for categories explicitly mapped to None (not photography);
    goal-keyword inference only applies to unmapped categories.
    """
    if category in CATEGORY_PHOTO_MAP:
        photo_key = CATEGORY_PHOTO_MAP[category]
        return PHOTOGRAPHY[photo_key] if photo_key else None
    goal_lower = goal.lower()
    if any(w in goal_lower for w in ["food", "restaurant", "dish", "meal", "recipe"]):
        photo_key = "food"
    elif any(w in goal_lower for w in ["car", "automotive", "vehicle", "truck"]):
        photo_key = "automotive"
    elif any(w in goal_lower for w in ["building", "architecture", "interior", "room"]):
        photo_key = "architectural"
    elif any(w in goal_lower for w in ["fashion", "clothing", "outfit", "runway", "apparel"]):
        photo_key = "fashion"
    elif any(w in goal_lower for w in ["beauty", "cosmetic", "makeup", "skincare"]):
        photo_key = "beauty"
    elif any(w in goal_lower for w in ["product", "bottle", "package", "device"]):
        photo_key = "product"
    else:
        photo_key = "lifestyle"
    return PHOTOGRAPHY.get(photo_key, PHOTOGRAPHY["lifestyle"])

def _goal_platform_key(goal: str):
    """Platform keyword scan of the goal. Checked BEFORE the category map
    (US-013) so e.g. a LinkedIn goal never emits Instagram safe-zones."""
    g = goal.lower()
    if any(w in g for w in ["instagram", "social", "facebook", "twitter"]):
        return "instagram_feed"
    if any(w in g for w in ["story", "reel", "tiktok"]):
        return "instagram_story"
    if any(w in g for w in ["youtube", "video", "thumbnail"]):
        return "youtube_thumbnail"
    if any(w in g for w in ["linkedin", "professional", "b2b"]):
        return "linkedin_post"
    if any(w in g for w in ["poster", "flyer", "event", "concert"]):
        return "poster"
    if any(w in g for w in ["shop", "store", "amazon", "product listing"]):
        return "ecommerce"
    if any(w in g for w in ["billboard", "outdoor", "transit"]):
        return "billboard"
    return None

def get_marketing_intelligence(category: str, goal: str = "") -> dict:
    """Get marketing framework. Goal platform keywords are checked BEFORE
    the category map — a LinkedIn goal under a Social Media Post category
    gets LinkedIn zones, never Instagram safe-zones."""
    mkt_key = _goal_platform_key(goal) or CATEGORY_MARKETING_MAP.get(category)
    return MARKETING.get(mkt_key) if mkt_key else None

def infer_mood(style: str, goal: str) -> str:
    """Infer mood/atmosphere from style and goal keywords."""
    text = f"{style} {goal}".lower()
    if any(w in text for w in ["luxury", "premium", "elegant", "sophisticated"]):
        return "refined, aspirational, exclusive — quiet confidence and understated power"
    elif any(w in text for w in ["vibrant", "energetic", "bold", "dynamic"]):
        return "high-energy, attention-grabbing, confident — bold and unapologetic"
    elif any(w in text for w in ["minimalist", "clean", "simple", "modern"]):
        return "calm, clear, focused — intentional minimalism where every element earns its place"
    elif any(w in text for w in ["cinematic", "dramatic", "moody", "dark"]):
        return "dramatic, atmospheric, cinematic — deep shadows and directional light creating narrative tension"
    elif any(w in text for w in ["playful", "fun", "colorful", "cheerful"]):
        return "joyful, approachable, warm — inviting and human with genuine emotion"
    elif any(w in text for w in ["corporate", "professional", "business"]):
        return "trustworthy, authoritative, competent — professional credibility without coldness"
    elif any(w in text for w in ["natural", "organic", "earthy", "rustic"]):
        return "grounded, authentic, warm — natural materials and honest imperfection"
    elif any(w in text for w in ["futuristic", "tech", "digital", "cyber"]):
        return "innovative, sleek, forward-looking — precision engineering meets aspirational technology"
    else:
        return "polished, professional, purposeful — every detail deliberately crafted for impact"


# ═══════════════════════════════════════════════════════════════════
# LAYER 4: GPT_IMAGE_2 MODEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
# Rebuilt from OpenAI's official docs (cookbook prompting guide + API
# reference + model page + deprecations page — sources per claim group
# in data/gpt_image_2.json). The prior corpus-derived dict contradicted
# official docs on 6 points — JSON-supremacy, negative_prompt closing
# blocks, REFERENCE_N syntax, invented word limits, fixed subject→
# background ordering, lens incantations — all deleted (verdicts:
# research/SOURCE_TRUTH.md §8).

GPT_IMAGE_2 = _load("gpt_image_2.json")


def get_gpt_image_2_intelligence(category: str = "", goal: str = "") -> dict:
    """Get GPT Image 2 official-docs guidance.

    category/goal are accepted for parity with the other accessors;
    guidance is model-level — the old per-category quality_modifiers /
    negative_prompt_library tables were corpus folklore, deleted per
    SOURCE_TRUTH §8. Returns a shallow copy of the full dict; every
    section carries _source/_date/_confidence.
    """
    return dict(GPT_IMAGE_2)


# ═══════════════════════════════════════════════════════════════════
# LAYER 5: NANO_BANANA_PRO MODEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
# Rebuilt from Google's official sources for gemini-3-pro-image ONLY
# (SOURCE_TRUTH §0: engine routes to exactly gpt-image-2 + Nano Banana
# Pro; other family tiers are reference material, never emitted). The
# prior corpus-derived NANO_BANANA dict carried refuted claims, all
# DELETED (verdicts: research/nano-banana-official.md validation table +
# SOURCE_TRUTH §8): flat "14 references" (family-tier conflation; Pro is
# 6 objects + 5 characters + 3 style refs), face-lock "100% accuracy"
# (official phrasing is "completely unchanged"; cap is up to five
# characters), green-screen/chroma workflow (zero official occurrences —
# real workflows are semantic-mask edits and conversational removal),
# 1:4/4:1/1:8/8:1 ratios + 512px (3.1 Flash only, never Pro).

NANO_BANANA_PRO = _load("nano_banana_pro.json")


def get_nano_banana_pro_intelligence(category: str = "", goal: str = "") -> dict:
    """Get Nano Banana Pro (gemini-3-pro-image) official-docs guidance.

    category/goal are accepted for parity with the other accessors;
    guidance is model-level — the old corpus-derived NANO_BANANA dict
    (green-screen workflow, '100% accuracy' face-lock, flat '14 refs',
    mixed-tier ratios) was refuted against Google's docs and deleted per
    SOURCE_TRUTH §4/§8. Returns a shallow copy of the full dict; every
    section carries _source/_date/_confidence.
    """
    return dict(NANO_BANANA_PRO)

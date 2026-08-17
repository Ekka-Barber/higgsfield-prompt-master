#!/usr/bin/env python3
"""Higgsfield Prompt Master — generation layer.

The retrieval pipeline (US-013): exemplar retrieval -> IR extraction ->
slot filling -> per-model rendering, plus model routing and PQS scoring.
"""

import sys

try:
    from db import normalize_category
except ImportError:  # US-025: packaged (package-relative) layout
    from .db import normalize_category

# The only two real model targets (SOURCE_TRUTH §6). Higgsfield is the
# aggregator requests go through — not a model vendor — so routing is
# strictly two-model; Higgsfield's own prompt-light "Soul" flow is out of scope.
MODELS = {
    "gpt_image_2": {
        "id": "gpt_image_2",
        "model_id": "gpt-image-2",
        "snapshot": "gpt-image-2-2026-04-21",
        "display_name": "GPT Image 2",
        "signal": "layout/UI/text-dense — quotes/CAPS text levers, quality=high",
    },
    "nano_banana_pro": {
        "id": "nano_banana_pro",
        "model_id": "gemini-3-pro-image",
        "display_name": "Nano Banana Pro",
        "signal": "reference-heavy compositing, up-to-5-character consistency, localization, brand work",
    },
}

# ─── GENERATION MIXIN ───
class GenerationMixin:
    """Prompt generation, model routing, and quality scoring (composed into
    HiggsfieldPromptMaster by higgsfield_prompt.py)."""

    MODELS = MODELS

    def generate_prompt(self, goal: str, category: str, structure: str = "Template",
                        techniques: list = None, style: str = "", aspect_ratio: str = "") -> dict:
        """
        Generate an optimized prompt via the full retrieval pipeline (US-013):
        retrieve exemplars -> extract IR (ir.extract_ir) -> fill slots from
        goal + corrected intelligence layers -> render per routed model
        (renderers.render_gpt_image_2 / render_nano_banana_pro).

        Both real targets are prose-rendered (SOURCE_TRUTH §1); `structure`
        only biases which corpus exemplars are preferred (Template rows with
        the corpus-average 2-4 {argument} tags), it does not switch output
        format.

        Returns a dict with:
          - 'prompt': the rendered prompt text
          - 'model_recommendation': dict (id, model_id, display_name, signal) — one of the two real targets (gpt_image_2 | nano_banana_pro)
          - 'aspect_ratio': recommended ratio
          - 'quality_score': PQS 0-100 (US-014) — 6-factor geometric mean,
            percentile-graded against the corpus distribution
          - 'intelligence': photo/marketing/art metadata used
          - 'source_prompt_ids': corpus IDs of exemplars actually consumed
          - 'length': len(prompt)
          - 'warnings': non-fatal degradations (US-025) — empty when clean
        """
        try:
            from ir import IR_FIELDS, PromptIR, extract_ir
            from renderers import render_gpt_image_2, render_nano_banana_pro, _CAMERA_RE
            from langcheck import detect_scripts
        except ImportError:  # US-025: packaged layout
            from .ir import IR_FIELDS, PromptIR, extract_ir
            from .renderers import (render_gpt_image_2, render_nano_banana_pro,
                                    _CAMERA_RE)
            from .langcheck import detect_scripts

        # US-025: absolute-then-relative intelligence import; failure is
        # loud (stderr + result dict), never a silent layer drop.
        warnings = []
        try:
            from intelligence import (get_photo_intelligence,
                                      get_marketing_intelligence, infer_mood)
        except ImportError:
            try:
                from .intelligence import (get_photo_intelligence,
                                           get_marketing_intelligence, infer_mood)
            except ImportError as e:
                get_photo_intelligence = get_marketing_intelligence = None
                infer_mood = lambda style, goal: ""
                warnings.append(
                    f"intelligence import failed ({e}); "
                    f"photo/marketing/mood layers dropped")
                print(f"WARNING: {warnings[0]}", file=sys.stderr)

        norm_cat = normalize_category(category)

        if techniques is None:
            guide = self.category_guide(norm_cat)
            techniques = [t["technique"] for t in guide["technique_frequency"][:7]]

        # ── 1. Retrieve exemplars: goal-relevant FTS hits are the corpus
        # evidence (templates would leak off-domain fragments — the June
        # 2026 contamination class); category templates only serve as a
        # last-resort primary when FTS finds nothing. ──
        # US-033: the corpus is English-only, so a non-Latin goal can never match
        # via FTS. Left alone it still returns *something* (the same unrelated
        # exemplar every time) and the user gets a confident, irrelevant prompt.
        # Translate when a hook is available, otherwise say so out loud.
        retrieval_goal, scripts = goal, detect_scripts(goal)
        if scripts:
            translated = self._translate_goal(goal)
            if translated:
                retrieval_goal = translated
                warnings.append(
                    f"Goal contains {'/'.join(scripts)} text; translated to "
                    f"English for retrieval: {translated!r}")
            else:
                warnings.append(
                    f"Goal contains {'/'.join(scripts)} text but the corpus is "
                    "English-only and no translation hook is configured "
                    "(set HiggsfieldPromptMaster.translate_hook). Retrieval was "
                    "skipped; output is built from category guidance only and "
                    "will be generic. Re-run with an English goal for corpus "
                    "grounding.")

        goal_keywords = self._extract_keywords(retrieval_goal)
        if scripts and retrieval_goal is goal:
            similar = []  # untranslated: skip FTS rather than return noise
        else:
            similar = self.fts_search(goal_keywords, limit=5) if goal_keywords else []
            if not similar and retrieval_goal:
                similar = self.fts_search(retrieval_goal[:100], limit=5)

        candidates = similar
        if structure == "Template":
            # Corpus templates average 2.7 {argument} tags — prefer 2-4
            # (stable sort keeps FTS relevance order within each group).
            candidates = sorted(
                similar,
                key=lambda p: not (2 <= p.prompt_text.count("{argument") <= 4))
        if not candidates:
            # US-022: curated master prompts (goal-keyword-gated) before stale
            # corpus category templates — both are last-resort primaries.
            candidates = self.search_curated(query=goal_keywords or goal, limit=1)
        if not candidates:
            candidates = self.get_templates(norm_cat, structure, limit=5)[:1]
        consumed = candidates[:3]

        # ── 2. Extract IR: primary exemplar, then donor fragments merged in ──
        ir = extract_ir(consumed[0].prompt_text) if consumed else PromptIR()
        for donor in consumed[1:]:
            d = extract_ir(donor.prompt_text)
            for f in IR_FIELDS:
                if isinstance(getattr(d, f), list):
                    for frag in getattr(d, f):
                        ir.add(f, frag)
                elif getattr(d, f) and not getattr(ir, f):
                    setattr(ir, f, getattr(d, f))

        # Exemplars lend structure, not subject matter. Scrub the donors' own
        # brands and content enumerations before the goal is layered in, so a
        # dashboard goal never inherits a fitness template's product name.
        ir.scrub_exemplar_identity(goal)

        # ── 3. Fill slots from goal + corrected intelligence layers ──
        # Goal platform keywords beat the category map (US-013); photo is
        # None for non-photo categories (US-010).
        photo = get_photo_intelligence(norm_cat, goal) if get_photo_intelligence else None
        marketing = get_marketing_intelligence(norm_cat, goal) if get_marketing_intelligence else None
        mood = infer_mood(style, goal)

        ir.subject.insert(0, goal)  # the goal leads the rendered subject
        if style:
            ir.add("style", style)
        if mood:
            ir.add("mood", mood)
        if not aspect_ratio and marketing and "ratio" in marketing:
            aspect_ratio = marketing["ratio"].split(" or ")[0]
        if aspect_ratio:
            ir.aspect_ratio = aspect_ratio
        if photo:
            ir.add("composition", f"{photo['camera']}, {photo['lens']}")
            ir.add("lighting", photo["lighting"])
            ir.add("color", photo["color_science"])
        else:
            # Non-photo categories stay camera-free even when corpus
            # exemplars carry camera language (US-010 truthfulness).
            for slot in ("composition", "lighting", "style"):
                setattr(ir, slot, [f for f in getattr(ir, slot)
                                   if not _CAMERA_RE.search(f)])

        # ── 4. Render per routed model ──
        model_rec = self._recommend_model(norm_cat, goal, structure)
        if model_rec["id"] == "nano_banana_pro":
            prompt_text = render_nano_banana_pro(ir)
        else:
            prompt_text = render_gpt_image_2(ir)

        score = self._quality_score(prompt_text, norm_cat, goal)

        return {
            "prompt": prompt_text,
            "model_recommendation": model_rec,
            "aspect_ratio": aspect_ratio or ir.aspect_ratio or "1:1",
            "quality_score": score,
            "intelligence": {
                "photography": photo is not None,
                "marketing": marketing is not None,
                "mood": mood[:80] + "..." if len(mood) > 80 else mood,
            },
            "source_prompt_ids": [p.id for p in consumed],
            "length": len(prompt_text),
            "warnings": warnings,
        }

    #: Optional callable ``(str) -> str`` translating a goal into English.
    #: Left unset by default: this package is pure stdlib and offline, so it
    #: ships no translator rather than pulling in a network dependency. An agent
    #: that already has a model available should set it, e.g.
    #:     HiggsfieldPromptMaster.translate_hook = staticmethod(my_translate)
    #: Returning a falsy value means "could not translate" and the caller warns.
    translate_hook = None

    def _translate_goal(self, goal: str) -> str:
        """Best-effort English rendering of a non-Latin goal, or '' if none."""
        hook = type(self).translate_hook
        if hook is None:
            return ""
        try:
            return (hook(goal) or "").strip()
        except Exception as exc:  # a broken hook must not break generation
            print(f"WARNING: translate_hook failed: {exc}", file=sys.stderr)
            return ""

    def _recommend_model(self, category: str, goal: str, structure: str) -> dict:
        """Route to one of the two real model targets (SOURCE_TRUTH §6)."""
        goal_lower = goal.lower()

        # Reference compositing / <=5-char consistency / localization / brand → nano_banana_pro
        if any(w in goal_lower for w in ["reference", "consistent", "same person",
                                          "same character", "character sheet", "composite",
                                          "localiz", "multilingual", "translated", "brand",
                                          "photo", "portrait", "selfie", "product shot",
                                          "headshot", "profile pic", "real person"]):
            return self.MODELS["nano_banana_pro"]

        # Layout/UI/text-dense → gpt_image_2
        if any(w in goal_lower for w in ["poster", "infographic", "thumbnail", "logo",
                                          "banner", "flyer", "ui", "dashboard",
                                          "diagram", "chart", "layout", "typography",
                                          "mockup", "web design", "menu"]):
            return self.MODELS["gpt_image_2"]

        # Category-based defaults
        cat_map = {
            "Profile / Avatar": "nano_banana_pro",
            "Portrait / Selfie": "nano_banana_pro",
            "E-commerce Main Image": "nano_banana_pro",
            "App / Web Design": "gpt_image_2",
            "Infographic / Edu Visual": "gpt_image_2",
            "YouTube Thumbnail": "gpt_image_2",
            "Poster / Flyer": "gpt_image_2",
        }
        return self.MODELS[cat_map.get(category, "gpt_image_2")]

    def _quality_score(self, prompt_text: str, category: str, goal: str = "") -> dict:
        """PQS quality score (US-014, research/prompt-quality-evaluation.md §8.1):
        6-factor weighted geometric mean — coverage, corpus-IDF/SCS specificity,
        anti-padding atomic density, non-redundancy, goal fidelity @0.30 — minus
        a contradiction/vagueness penalty. Grades are percentiles against the
        corpus distribution held in pqs_calibration.json (no hardcoded cutoffs)."""
        if self._pqs is None:
            try:
                from pqs import PQSScorer
            except ImportError:  # US-025: packaged layout
                from .pqs import PQSScorer
            self._pqs = PQSScorer(conn=self.conn, searchable=self._searchable)
        return self._pqs.score(prompt_text, category, goal)

# SOURCE TRUTH — Reconciled Model Intelligence (v1, 2026-08-17)

> Synthesis of all 7 research streams (OpenAI official, Google official, competing-model
> landscape, academic evidence, production workflows, evaluation research, Claude's audit).
> This is the authoritative basis for rebuilding `GPT_IMAGE_2` and `NANO_BANANA` dicts
> (plan item P1-0) and for the generator redesign (P1-1). Every claim here traces to a
> source in `research/*.md`. Claims WITHOUT evidence are marked [gap] — encode nothing
> from folklore without a row here.

---

## 1. Architecture decision (supersedes "JSON vs prose" entirely)

**The engine keeps a structured INTERNAL representation (IR) and RENDERS per model.**

Evidence: no JSON-vs-prose efficacy study exists anywhere (academic gap); the efficacious
ingredient is *semantic structure* — per-entity attribute slots, zones, counts (LMD ≈2×,
LayoutGPT +20–40%, Make It Count); JSON is *required* only on Ideogram-4-open-weights,
*sanctioned* on FLUX.2, and *optional-irrelevant* on our two actual targets:

- **gpt-image-2**: paragraph default, sections optional, JSON never recommended
- **Gemini image (Nano Banana)**: narrative prose only; "keyword lists won't cut it"

So: retrieve corpus JSON templates for their **structure** (zones/counts/labels), fill
slots from goal + intelligence layers, **render to cohesive prose** (with optional
labeled sections when complexity warrants). JSON rendering becomes a future adapter
(FLUX.2/Ideogram), not the default.

IR fields: `subject, action, environment, style/medium, lighting, color (named+hex),
mood, composition/camera (photoreal only), text_elements[{literal, placement,
typography, color}], negative_concepts[], aspect_ratio, references{type,count,roles},
output_intent (photo|art), quality_tier`.

## 2. Universal principles (all models, evidence-graded)

| Principle | Evidence | Grade |
|---|---|---|
| Front-load primary subject; early tokens weighted | FLUX.2 official; VISOR first-object bias | A |
| Cover 7 facets: Subject, Medium, Environment, Lighting, Color, Mood, Composition | identical lists in MJ + Recraft official docs | A |
| Positive phrasing; NEVER "no X" inline (renders positively) | MJ/FLUX/Recraft official; 2401.06209; 2307.06350 | A |
| Literal text in DOUBLE quotes + typography + placement descriptors | MJ (single quotes fail); FLUX; Qwen; OpenAI | A |
| Concrete counts/collective nouns ("three cats") | MJ + Recraft official | A |
| Common vocabulary; rare/exotic tokens risky | R2F 2410.22376; 2505.09166 | A |
| Exclusion: omit, or model-appropriate channel (see §4) | 2406.02965; vendor docs | A |
| Per-entity attribute grouping (entity→attrs→position slots) | 2212.05032; 2305.13655; 2305.15393 | A |
| Exact counts reliable only for small N; use layout cues | GeckoNum; Make It Count | A |
| Zones/boxes beat spatial prepositions | VISOR; GenEval position 0.04–0.15; LMD | A |
| 30–80 dense tokens for CLIP-backbone; LLM-backbone tolerates more but leaks | 2403.15378; 2505.16915 | B (apply per target) |
| Camera/lens refs raise photoreal quality (photoreal targets ONLY) | FLUX.2 official; [gap academically] | B |
| Quality boosters ("masterpiece, 4k") — NO efficacy evidence | 2204.13988 prevalence-only; 2410.22376 | DROP |
| English prompts most precise (exception: Qwen-Chinese) | BFL official; 2208.09333 | B |
| Translate-then-prompt for non-Latin goals | 2208.09333; LMD | B (Arabic [gap]) |

## 3. GPT_IMAGE_2 dict — corrected spec

- **names**: `gpt-image-2` / snapshot `gpt-image-2-2026-04-21`. gpt-image-1 dies 2026-10-23.
- **structures**: `paragraph` PRIMARY (cohesive descriptive paragraph, element+details
  paired); `labeled_sections` optional for complexity (Subject/Style/Composition/Color/
  Lighting/Mood/Details); `json` — NOT recommended (remove from dict). Break complex
  requests into a series of simpler prompts.
- **text_rendering** (replace word-limits): quotes for literal text; ALL CAPS for
  heading emphasis; letter-by-letter spelling for garbles; verbatim casing; avoid
  hyphens inside words; simple sans-serif fonts; keep text lean for cost/clutter;
  **quality=high for text-heavy**. No numeric word limits exist.
- **exclusions**: NO negative_prompt param. Positive-first + inline exclusion clause
  ("without any clouds").
- **references**: ordinal + role ("the first image… as the background", "the second
  image as reference for the character"); up to 16 inputs on edits; batch ALL changes
  into ONE edit call (edits replace the whole image); blending = merge-first or
  explicit combine instruction; well-known logos need no reference.
- **sizes**: 1024x1024 social · 1024x1536 posters/stories · 1536x1536→1536x1024
  banners/hero · arbitrary W×H (÷16, ratio 1:3–3:1, 262,144–5,529,600 px, edges
  512–3840; >2560×1440 experimental). Prompt cap 32,000 chars.
- **params**: quality low/medium/high/auto (low=iterate, high=final+text); n 1–10;
  output_format png/jpeg/webp; background transparent (png/webp only); moderation
  low/auto; input_fidelity high (edits, fine-grained).
- **ui_mockups**: world knowledge of real products; wireframe-mode; interactive states;
  portrait/custom sizes.
- **localization**: generate English text → edit with reference screenshot ("text layer
  fully editable", natural translations).
- **mistakes to avoid** (official list): overloading; vague descriptors; conflicting
  instructions; unspecified aspect; excessive text; low-res edit inputs.
- **camera**: generic camera/lens/lighting mention endorsed; exact lens incantations
  NOT endorsed ("interpreted loosely" per model page — high-level look only).

## 4. NANO_BANANA dict — corrected spec

- **names** (umbrella): 2 Lite `gemini-3.1-flash-lite-image` · NB2 `gemini-3.1-flash-image`
  · NB Pro `gemini-3-pro-image` (preview id DEAD) · legacy `gemini-2.5-flash-image`.
  Imagen shut down 2026-08-17.
- **prompting**: narrative scene description, hyper-specific, context+intent first;
  formulas: `[Subject]+[Action]+[Location]+[Composition]+[Style]` and
  `[References]+[Relationship]+[New scenario]`. Camera language officially encouraged.
- **references** (per-tier table): Lite 14 objects/no char-style · 3.1 Flash 10 obj +
  4 char · 3 Pro 6 obj + 5 char + 3 style · legacy best ≤3. Replace flat "14".
- **face_lock** (replace "100% accuracy"): "Ensure the person's face and features
  remain completely unchanged." Capped guarantee: up to 5 characters; model card admits
  small-face/spelling struggles.
- **green_screen**: DELETE (not in any official source). Real workflows: semantic-mask
  edits ("change only the blue sofa… keep everything else unchanged"), conversational
  removal, step-by-step construction ("First… Then… Finally…").
- **semantic_negatives**: restate positively ("an empty, deserted street with no signs
  of traffic").
- **text**: per-line font specification works ("'GLOW' in Brush Script; '10% OFF' in
  Impact"); docs advise text-first-then-image for complex text; Arabic = ar-EG listed
  among best languages.
- **ratios**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 (3.1 Flash adds
  1:4, 4:1, 1:8, 8:1); 1K/2K/4K.
- **limits**: won't always honor exact output counts; blending can artifact; verify
  factual content.

## 5. Exclusion/negative adapter matrix

| Target | Channel |
|---|---|
| gpt-image-2 | positive-first + inline "without any clouds" clause |
| Gemini image | semantic positive rewrite ("empty deserted street") |
| Midjourney (future) | `--no item` param |
| SD3.5 / Qwen (future) | dedicated negative field (Qwen: `" "` when empty) |
| FLUX.2 / Ideogram / Recraft (future) | invert to positive phrasing |

## 6. Higgsfield routing corrections

- `_recommend_model()` returning "nano_banana_2"/"gpt_image_2" as "Higgsfield models"
  is wrong framing: Higgsfield is an aggregator (50+ models, own `Soul`). Correct
  design: return model family + the prompt spec above; note Higgsfield is
  identity/camera-first and prompt-LIGHT (Soul IDs, Popcorn storyboards, Cinema Studio
  camera vocabulary) — short cinematography-flavored prompts when routing through it.

## 7. Engine features adopted from production research

Reference-aware generation (complement conditioning, don't re-describe) · locked style
block + slot templates · provenance metadata on every prompt (text+model+params+seed+
refs+style-version) · failure-mode routing (text-critical → strong-text models;
"add text in post" flags) · batch-consistency contract (vary only subject slot) ·
per-channel AR expansion · QA checklist hooks · A/B variants with prompt-level diffs.

## 8. Claim ledger — current dicts vs truth

| Current dict claim | Verdict | Action |
|---|---|---|
| JSON primary, "prose drifts" | refuted | paragraph primary; JSON = internal IR only |
| negative_prompt closing block | refuted | per-target exclusion channel (§5) |
| REFERENCE_0/1 syntax | invented | ordinals + role descriptions |
| ≤6-word headlines / ≤12-word body | invented | quotes/CAPS/letter-spelling/quality=high |
| Subject→…→background fixed order | unsupported | front-load subject; 7-facet coverage |
| Lens-name incantations | overrated | generic camera language; high-level look |
| 14 reference images (flat) | under-specified | per-tier table |
| Face lock "100% accuracy" | refuted | "completely unchanged" phrasing |
| Green-screen workflow | folklore | semantic masking / conversational edit |
| "exactly 4 cards" always honored | overstated | small-N reliable; layout cues for larger |
| Booster tokens | no evidence | drop from any emitted vocabulary |

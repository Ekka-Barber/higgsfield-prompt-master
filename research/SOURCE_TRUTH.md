# SOURCE TRUTH — Reconciled Model Intelligence (v1, 2026-08-17)

> Synthesis of all 7 research streams (OpenAI official, Google official, competing-model
> landscape, academic evidence, production workflows, evaluation research, Claude's audit).
> This is the authoritative basis for rebuilding `GPT_IMAGE_2` and `NANO_BANANA` dicts
> (plan item P1-0) and for the generator redesign (P1-1). Every claim here traces to a
> source in `research/*.md`. Claims WITHOUT evidence are marked [gap] — encode nothing
> from folklore without a row here.

## 0. ENGINE SCOPE (owner directive, 2026-08-17)

**The engine routes to exactly TWO models — nothing else:**
1. **GPT Image 2** — `gpt-image-2` / snapshot `gpt-image-2-2026-04-21` (OpenAI)
2. **Nano Banana Pro** — `gemini-3-pro-image` (Google; NOT the preview id, NOT 2.5/Lite/3.1-Flash)

All other models in `competing-models-landscape.md` are **reference material only** —
they inform universal prompting principles, but no adapters, routers, or emissions
target them. `_recommend_model()` returns exactly: `gpt_image_2` | `nano_banana_pro`.

---

## 1. Architecture decision (supersedes "JSON vs prose" entirely)

**The engine keeps a structured INTERNAL representation (IR) and RENDERS per model.**

Evidence: no JSON-vs-prose efficacy study exists anywhere (academic gap); the efficacious
ingredient is *semantic structure* — per-entity attribute slots, zones, counts (LMD ≈2×,
LayoutGPT +20–40%, Make It Count). JSON is *required* only on Ideogram-4-open-weights,
*sanctioned* on FLUX.2 — **both out of scope**. Our two targets are both prose-renderers:

- **gpt-image-2**: paragraph default, sections optional, JSON never recommended
- **Nano Banana Pro** (`gemini-3-pro-image`): narrative prose only; "keyword lists won't cut it"

So: retrieve corpus JSON templates for their **structure** (zones/counts/labels), fill
slots from goal + intelligence layers, **render to cohesive prose** (with optional
labeled sections when complexity warrants). Two renderers total — one per target model.

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

## 4. NANO_BANANA_PRO dict — corrected spec (`gemini-3-pro-image` ONLY)

> The engine targets **Pro specifically**. Family context (why): "Nano Banana" is an
> umbrella — 2 Lite `gemini-3.1-flash-lite-image`, NB2 `gemini-3.1-flash-image`,
> **Pro `gemini-3-pro-image`** (GA 2026-05-28; `-preview` id DEAD 2026-06-25), legacy
> `gemini-2.5-flash-image`. Imagen shut down 2026-08-17. Dict claims must be Pro-true,
> not family-true.

- **model name**: `gemini-3-pro-image`. Never emit `-preview`, never 2.5/Lite ids.
- **prompting**: narrative scene description, hyper-specific, context+intent first;
  formulas: `[Subject]+[Action]+[Location]+[Composition]+[Style]` and
  `[References]+[Relationship]+[New scenario]`. Camera language officially encouraged
  (contrast with GPT's "interpreted loosely" — this is a genuine per-model difference
  the two renderers must encode).
- **references (Pro row)**: **6 object images + 5 character images + 3 style refs**;
  "supports 5 images with high fidelity, and up to 14 images in total" (legacy-doc
  phrasing — treat 6+5+3 as the working limits). Replace flat "14 references".
- **face_lock** (replace "100% accuracy"): "Ensure the person's face and features
  remain completely unchanged." Official cap: consistency/resemblance of **up to five
  characters**; model card admits small-face/spelling/fine-detail struggles.
- **green_screen**: DELETE (not in any official source). Real workflows: semantic-mask
  edits ("change only the blue sofa… keep everything else unchanged"), conversational
  removal, step-by-step construction ("First… Then… Finally…").
- **semantic_negatives**: restate positively ("an empty, deserted street with no signs
  of traffic").
- **text**: per-line font specification works ("'GLOW' in Brush Script; '10% OFF' in
  Impact"); docs advise text-first-then-image for complex text; **interleaved
  text+image is Pro-only** (a Pro strength to exploit). Arabic = ar-EG listed among
  best languages.
- **ratios (Pro)**: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 — the 1:4/4:1/
  1:8/8:1 extremes are **3.1 Flash only, NOT Pro**. Resolutions 1K/2K/4K.
- **Pro-only strengths to route toward**: premium world knowledge, localization
  (translate-text-in-image workflows), brand consistency, interleaved text+image.
- **NOT Pro** (do not emit): thinking_level (3.1 Flash only), video-to-image and
  Image-Search grounding (3.1 Flash only), 512px output (3.1 Flash only).
- **cost**: output 1120 tok (1K/2K) ≈ $0.134, 2000 tok (4K) ≈ $0.24; input images
  fixed at 560 tokens each; multi-turn editing via `previous_interaction_id`.
- **limits**: won't always honor exact output counts; blending can artifact; verify
  factual content.

## 5. Exclusion/negative adapter (two active rows — scope is locked)

| Target | Channel |
|---|---|
| **gpt-image-2** | positive-first + inline "without any clouds" clause |
| **Nano Banana Pro** | semantic positive rewrite ("empty deserted street with no signs of traffic") |
| Midjourney / SD / Qwen / FLUX.2 / Ideogram / Recraft | ~~out of scope~~ — reference only (`competing-models-landscape.md`) |

## 6. Router corrections

`_recommend_model()` returns exactly two values with correct product framing:
`gpt_image_2` (gpt-image-2, snapshot 2026-04-21) | `nano_banana_pro` (gemini-3-pro-image).
Not "Higgsfield models" — Higgsfield is the aggregator the requests go through; it also
offers its own prompt-light `Soul` flow (Soul IDs, Popcorn, Cinema Studio camera
vocabulary), but model routing stays two-model. Routing signals: layout/UI/text-dense →
lean gpt-image-2 (quotes/CAPS text levers, quality=high); reference-heavy compositing,
up-to-5-character consistency, localization, brand work → lean Nano Banana Pro.

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
| 14 reference images (flat) | under-specified | **Pro: 6 objects + 5 characters + 3 style refs** |
| Face lock "100% accuracy" | refuted | "completely unchanged" phrasing |
| Green-screen workflow | folklore | semantic masking / conversational edit |
| "exactly 4 cards" always honored | overstated | small-N reliable; layout cues for larger |
| Booster tokens | no evidence | drop from any emitted vocabulary |

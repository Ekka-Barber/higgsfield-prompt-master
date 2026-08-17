# Independent Research — Image Generation Prompting (2026-08-17)

Primary-source research conducted independently of this repo's corpus and existing
`intelligence.py` claims. **Every claim below carries an evidence tier.**

- **[VENDOR]** — official vendor documentation. Authoritative.
- **[PAPER]** — peer-reviewed or arXiv, with measured numbers.
- **[PRACTITIONER]** — self-reported testing by a named practitioner. Suggestive, not proof.
- **[CORPUS]** — derived from this repo's 7,613-prompt corpus. **Measures prevalence, not efficacy.**

> The single most important methodological point in this document: **[CORPUS] evidence
> cannot establish that a technique works.** It establishes only that people posted it to
> a gallery. The current `intelligence.py` repeatedly treats corpus frequency as proof of
> effectiveness. That inference is invalid and is the root cause of most errors below.

---

## 1. The headline finding: negative prompts are dead on every model this skill targets

Four independent sources agree:

| Source | Statement | Tier |
|---|---|---|
| OpenAI prompting guide | Negative prompts **never mentioned**. Instead: state exclusions inline — *"no watermark," "no extra text," "no logos/trademarks"* | [VENDOR] |
| Google Gemini image docs | Negative prompts **"Not supported"** — no such parameter exists | [VENDOR] |
| Black Forest Labs official skill | *"**NO negative prompts** — FLUX does not support negative prompts; describe what you want"* | [VENDOR] |
| Prompture (practitioner, Aug 2026) | *"Neither family exposes a true negative-prompt channel the way older Stable Diffusion interfaces did"* | [PRACTITIONER] |

BFL adds the mechanism: *"Negative prompts can actually make models focus MORE on unwanted
elements."* Prompture independently reports the same — negation *"asks the model to hold a
concept in mind and then suppress it. Frequently it summons the thing instead."*

**Impact on this repo:** `intelligence.py` ships a 7-entry `negative_prompt_library` and
asserts *"always include one"* and *"'negative prompt:' must be a labeled closing block."*
This is Stable-Diffusion-era practice applied to models with no negative-prompt channel.
It is not merely useless — the vendor evidence says it is **actively counterproductive**.

### The validated replacement: positive-state description

BFL publishes a full substitution table. The rule: *identify what you don't want → ask
"what would be there instead?" → describe that.*

| Instead of | Use |
|---|---|
| `no people` | `empty`, `deserted`, `solitary` |
| `no text` | `clean surfaces`, `unmarked`, `pristine` |
| `no blur` | `sharp focus`, `crisp details`, `tack-sharp` |
| `no bright colors` | `muted earth tones`, `desaturated palette` |
| `no clutter` | `organized`, `minimal`, `streamlined` |

Worked example [VENDOR]:
- ✗ `A beach scene, no people`
- ✓ `A deserted beach at dawn, pristine untouched sand, solitary seagull`

---

## 2. JSON is an authoring format, not a wire format

This repo emits raw JSON **as the prompt**. No vendor endorses that.

- **OpenAI** [VENDOR]: *"Minimal prompts, descriptive paragraphs, JSON-like structures,
  instruction-style prompts, and tag-based prompts **can all work well**."* And:
  *"For production systems, prioritize a skimmable template over clever prompt syntax."*
- **BFL** [VENDOR] publishes a JSON prompting guide — and its own instruction is:
  **"Flatten your JSON into flowing prose for the actual prompt."** Best-practice #5 is
  literally *"Flatten for Execution — Convert to natural language before sending to model."*

So JSON's legitimate role is **organizing, templating, and variable substitution** —
then you flatten before sending. That is close to the opposite of what this repo does.

**Impact:** `GPT_IMAGE_2["preferred_structures"]` claims JSON is the PRIMARY structure
because *"54% of corpus"*. That is [CORPUS] prevalence reasoning. No vendor supports JSON
superiority, and one explicitly says to flatten it.

---

## 3. Verified model facts

### OpenAI GPT Image 2 [VENDOR]
- Model `gpt-image-2`, snapshot `gpt-image-2-2026-04-21`, released 2026-04-21
- Endpoints `v1/images/generations`, `v1/images/edits`
- **Size constraints:** max edge < 3840px · both edges multiple of **16** · aspect ratio ≤ **3:1**
  · total pixels ≤ **8,294,400** and ≥ **655,360**
- Above **2560×1440** is officially **"experimental"** — more variable results
- Common sizes: `1024x1024`, `1024x1536`, `1536x1024`, `2560x1440`, `3840x2160` (round to `3824x2144`)
- `quality`: `low` | `medium` | `high`. Start `low`; use `medium`/`high` for **small text,
  dense information panels, multi-font layouts, identity-sensitive edits**
- `input_fidelity` is **disabled** on gpt-image-2 (legacy `gpt-image-1`/`1.5` only)
- Rate limits: tier 1 = 5 img/min → tier 5 = 250 img/min

### Google "Nano Banana" family [VENDOR]
| Name | Model ID |
|---|---|
| Nano Banana 2 Lite | `gemini-3.1-flash-lite-image` |
| Nano Banana 2 | `gemini-3.1-flash-image` |
| **Nano Banana Pro** | `gemini-3-pro-image` |
| Nano Banana (legacy) | `gemini-2.5-flash-image` |

- Aspect ratios: `1:1 3:2 2:3 3:4 4:3 4:5 5:4 9:16 16:9 21:9`
- `image_size`: `512px` / `1K` / `2K` / `4K` (uppercase K). Lite = 1K only
- Reference limits — 3.1 Flash: **10 objects / 4 characters / 3 style refs**;
  3 Pro: **6 objects / 5 characters**; Lite: 14 objects, no multi-reference
- `thinking_level`: `minimal` (default) | `high`
- Multi-turn editing via `previous_interaction_id`
- All output carries **SynthID** watermark

**Impact:** `_recommend_model()` returns the strings `"nano_banana_2"` and `"gpt_image_2"`.
Neither is a real model ID. `higgsfield.ai` is an **aggregator** of 50+ third-party models
and also ships its own image model, **Soul**, which this repo never mentions.

---

## 4. Text rendering — the real technique

The repo asserts *"headlines ≤6 words, body ≤12 words, garbles beyond."* No vendor states
any such limit. What vendors actually say:

- **OpenAI** [VENDOR]: put literal text **in quotes or ALL CAPS**; for tricky words
  (brand names, uncommon spellings) **spell them out letter-by-letter**; specify typography
  as constraints; **raise `quality` to medium/high for small or dense text**
- **BFL** [VENDOR]: *"Quote text — use `"quoted text"` for typography rendering"*
- **Google** [VENDOR]: *"Describe the text, the font style (descriptively), and the overall
  design."* **No maximum character count stated**

**Impact:** the repo's invented word limits are unsupported, and it is **missing all four
real levers** (quoting, ALL CAPS, letter-by-letter spelling, the `quality` parameter).

---

## 5. Camera/photography vocabulary is model-specific, not universal

This is where naive corpus mining misleads most.

- **OpenAI** [VENDOR]: *"detailed camera specs **may be interpreted loosely**, so use them
  mainly for high-level look and composition rather than exact physical simulation."*
  Prefers the literal word **`photorealistic`**, or `real photograph` / `taken on a real
  camera` / `professional photography` / `iPhone photo`
- **BFL** [VENDOR]: the *opposite* — its own reference example is
  `Shot on Hasselblad with 85mm lens at f/2.8 … Kodak Portra 400 color science`,
  and lists *"Specify lighting — lighting has the biggest impact on quality"*

**Conclusion:** lens/film-stock vocabulary is a **FLUX-family** lever, weak on GPT Image.
Portable across all families: **lighting, composition, framing, medium, mood**.
A skill targeting GPT Image 2 + Nano Banana Pro should **not** lead with lens specs.

---

## 6. Behavioural differences that should drive routing [PRACTITIONER]

From repeated side-by-side testing (Prompture, Jul–Aug 2026). Suggestive, not proof —
but it is the only direct comparative source found, and it is internally consistent.

| Dimension | GPT-Image | Gemini / Nano Banana |
|---|---|---|
| Core behaviour | literal instruction-following, clause by clause | holistic interpretation of intent |
| Underspecified prompt | centred, evenly lit, catalogue-like, *"correct, literal and uninteresting"* | compositional opinion, angle, depth; less predictable |
| Exact counts | more reliable — *"though neither is dependable much past five"* | reorganises for visual balance |
| Rendered text | usually stronger | weaker |
| Reference vs text conflict | **weights the text more** | **weights the image more** |
| Reference strength | holds layout/pose tightly → structure preservation | takes colour/grade/atmosphere → style transfer |
| Framing | centres subject, fills symmetrically | uses full frame, off-centre |

**Porting rule** [PRACTITIONER]: Gemini → GPT-Image, *add specification*. GPT-Image →
Gemini, *trim contradictions* — "it resolves conflicts by picking one, not attempting both."

**Prompt length** [PRACTITIONER]: under ~30 words GPT-Image goes flat while Gemini is
surprisingly good; **60–120 words is the sweet spot for both**; past ~200 words GPT-Image
weakens later clauses and Gemini starts dropping tail details. Universal rule:
**"if a detail is essential, it does not belong in the last sentence."**

Note this contradicts the repo's `token_budget_guidance` (200–450 tokens, drift past 650),
which is unsourced. The practitioner figures are word counts from actual testing.

---

## 7. Reference-image syntax

- **OpenAI** [VENDOR]: reference by **index and description** —
  `"Image 1: product photo… Image 2: style reference"`;
  `"place the dog from the second image into the setting of image 1"`
- **Google** [VENDOR]: separate image blocks in the input array, typed by role
  (object / character / style) with per-model caps
- **Universal** [VENDOR + PRACTITIONER]: **state the reference's job** —
  *"use the attached image for lighting and colour only; the subject and pose come from the text"*

**Impact:** the repo's `REFERENCE_0` / `REFERENCE_1` token convention appears in no vendor
documentation. It is invented syntax.

### Editing invariants [VENDOR]
OpenAI: use **"change only X" + "keep everything else the same"**, and **repeat the preserve
list on every iteration** to reduce drift. For surgical edits also pin saturation, contrast,
layout, labels, camera angle.

---

## 8. Prompt ordering

**OpenAI** [VENDOR]: `background/scene → subject → key details → constraints`
**BFL** [VENDOR]: `[Subject] + [Action/Pose] + [Style/Medium] + [Context/Setting] + [Lighting] + [Camera/Technical]`

These genuinely differ (OpenAI puts scene first; BFL puts subject first), so **ordering is
model-specific**. The repo's single hardcoded flat order matches neither, and it places
background near the end — the opposite of OpenAI's guidance for the model it primarily targets.

---

## 9. Scoring and diversity — evidence-based redesign

Full agent research retained separately. Key results:

- **No published metric scores a prompt without generating the image.** CLIPScore,
  ImageReward, PickScore, HPSv2/v3, VQAScore, TIFA, DSG all require `(image, text)` [PAPER]
- **But prompt outcome IS predictable from text alone** — Bizzozzero et al. (arXiv 2306.08915)
  reach Pearson **r = 0.53–0.84** from text embeddings only [PAPER]
- **Text-side lexical diversity predicts visual diversity** — De Rosa Palmini & Cetinic
  (arXiv 2504.14125): compression ratio ρ=**0.62**, effective-number-of-words ρ=**0.52**,
  self-repetition ρ=**−0.54** vs Vendi score of resulting images. Prompt-pair token
  similarity **≥0.8 → visually homogeneous output** [PAPER]
- **Pre-retrieval Query Performance Prediction** (IR, since 2004) scores a query using only
  corpus statistics — AvIDF, Simplified Clarity Score, query scope. Pure Python over the
  existing 7,613-prompt SQLite corpus [PAPER]
- **Brysbaert concreteness norms** — 37,058 words rated 1–5 for concreteness, free CSV.
  Model-free specificity proxy [PAPER]
- **Aggregate with a geometric mean** — ImagenHub (ICLR 2024) uses `O = √(SC × PQ)`
  explicitly so one failed dimension cannot be masked by another [PAPER]
- **LLM judges: pairwise, never pointwise** — GenArena (2026) reports Spearman
  **0.36 → 0.86** switching from pointwise to pairwise [PAPER]
- **Do not let an LLM write the rubric** — human-authored rubrics improve judgment accuracy
  **+27%**; model-written rubrics *"gravitate toward surface features such as format and
  length"* (arXiv 2606.08625) [PAPER] — an exact description of the current scorer

### Why the current scorer cannot be fixed by tuning
`_quality_score(prompt_text, category)` **never receives the user's `goal`**. It is therefore
structurally incapable of detecting that generation ignores its input, no matter how the
weights are set. Additional defects: 40% of the score is raw length (rewards padding), and
substring matching produces false positives — `"mm"` matches *co**mm**ercial*, `"fill"`
matches *ful**fill***.

**Required fix:** add a goal-fidelity term (IDF-weighted recall of goal terms in the output),
weight it highest, and combine via geometric mean so it cannot be masked. Grade by
**percentile against the corpus**, not hardcoded cutoffs.

### Duplication detector
Best single measure for this repo's known bug — **cross-goal discrimination**:
`Δ = mean G(pᵢ,gᵢ) − mean G(pᵢ,gⱼ≠ᵢ)`. If the generator ignores input, Δ → 0 regardless of
how polished the prompts look. Target **Δ ≥ 0.30**. Pair with a goal-swap hard-fail:
if two prompts have Jaccard ≥0.70 while their goals have Jaccard <0.20, fail the build.

---

## 10. Net verdict on `intelligence.py` Layers 4/5

| Claim in repo | Status |
|---|---|
| `negative_prompt_library`, "always include one" | **Refuted** by 3 vendors — counterproductive |
| JSON is PRIMARY / prose drifts | **Unsupported**; BFL says flatten JSON to prose |
| `REFERENCE_0` / `REFERENCE_1` syntax | **Invented** — no vendor uses it |
| Headline ≤6 / body ≤12 words | **Unsupported**; real levers missing |
| Token budget 200–450, drift past 650 | **Unsourced** |
| Flat order SUBJECT→…→BACKGROUND | **Contradicts** OpenAI ordering |
| Name the lens (`Panavision anamorphic 70mm`) | **Model-specific** — FLUX yes, GPT Image "interpreted loosely" |
| Exact counts honored | **Partially true** — "neither dependable much past five" |
| Model IDs `nano_banana_2` / `gpt_image_2` | **Not real IDs** |

**Do not wire Layers 4/5 into generation as written.** They must be rebuilt from vendor
sources first, or the plan's P1-1 converts 333 lines of inert code into 333 lines of
actively wrong guidance embedded in every generated prompt.

---

## Sources

**Vendor**
- https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
- https://developers.openai.com/api/docs/models/gpt-image-2
- https://ai.google.dev/gemini-api/docs/image-generation
- Black Forest Labs official skills — `npx skills add black-forest-labs/skills`
  (`flux-image-best-practices`: core-principles, json-structured-prompting,
  negative-prompt-alternatives, typography-text, multi-reference-editing)

**Papers** — full citation list in the evaluation research appendix
- Bizzozzero, Bendidi & Risser-Maroix, *Prompt Performance Prediction for Image Generation*, arXiv 2306.08915
- De Rosa Palmini & Cetinic, *Language Patterns of Prompts … Visual Diversity*, arXiv 2504.14125
- Ku et al., *ImagenHub*, ICLR 2024, arXiv 2310.01596
- Ross et al., *What makes a good metric?*, COLM 2024, arXiv 2412.13989
- Rassin et al., *GRADE: Quantifying Sample Diversity*, arXiv 2410.22592
- Brysbaert, Warriner & Kuperman, *Concreteness ratings for 40k English lemmas*, Behav Res Methods 46:904–911
- Hauff, Hiemstra & de Jong, *Survey of pre-retrieval query performance predictors*, CIKM 2008
- *From Holistic Evaluation to Structured Criteria*, arXiv 2606.08625

**Practitioner**
- Prompture, *GPT-Image vs Gemini: how prompting actually differs*, Jul–Aug 2026 — https://prompture.app

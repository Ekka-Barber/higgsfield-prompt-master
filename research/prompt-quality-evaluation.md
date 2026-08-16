# Prompt Quality Evaluation — Research Report

> Completed research agent from Claude session 0f5f4f48 (2026-08-17), preserved verbatim.
> The other 5 research agents in that session died on the usage limit before writing output.

I have enough primary sources. Writing up the findings.

# Evaluating & Scoring Image-Generation Prompts and Outputs
**Research report — 2026-08-17.** Focus: evidence-based design for a *text-only* prompt scorer + duplication detector.

---

## 0. Bottom line up front

1. **Nearly every published metric requires the image.** CLIPScore/BLIPScore/ImageReward/PickScore/HPSv2-v3/VQAScore/TIFA/DSG all take `(image, text)`. None can score a prompt alone.
2. **But the *decomposition* half of TIFA/DSG is text-only** — turning a prompt into atomic assertions is pure NLP. That is the single most transferable idea for a prompt-side scorer, and it is nothing like keyword counting.
3. **There is direct evidence that prompt outcome is predictable from text alone**: Bizzozzero et al. reach Pearson **r = 0.53–0.84** predicting image aesthetics/memorability/compositionality from *text embeddings only*.
4. **There is direct evidence that text-side lexical diversity predicts visual diversity**: De Rosa Palmini & Cetinic report ρ = 0.62 (compression ratio), ρ = 0.52 (effective number of words), ρ = −0.54 (self-repetition) against Vendi scores of the resulting images.
5. **The mature analogue for "score a query before running it" is pre-retrieval Query Performance Prediction (QPP)** from IR — IDF/SCS/scope predictors, pure Python, needing only corpus statistics. Your repo already has a 7,613-prompt SQLite corpus, which is exactly the collection statistic those predictors need.
6. **Your current scorer's dominant defect is that it has no goal-conditioned term.** Length + technique-count + keyword-hits are all computable without ever looking at what the user asked for — which is precisely why it cannot see the duplicate-output bug.

---

## 1. Automated image-text alignment metrics

### 1.1 The families

| Metric | Year | Mechanism | Needs image? | Headline number |
|---|---|---|---|---|
| CLIPScore | 2021 | cosine(CLIP img emb, CLIP txt emb), rescaled `2.5·max(cos,0)` | Yes | Spearman **0.30** / Kendall **0.16** vs human preference — weakest of all tested |
| BLIP/BLIP2Score | 2022–23 | ITM head score | Yes | Superseded by FGA-BLIP2 |
| ImageReward | 2023 | BLIP backbone + preference head on 137k expert comparisons | Yes | **65.1%** pairwise accuracy (vs CLIP 54.8%, aesthetic 57.4%, HPS 60.8%, PickScore 62.8%) |
| PickScore | 2023 | CLIP-H fine-tuned on Pick-a-Pic user prefs | Yes | **70.2–70.5%** on Pick-a-Pic val — *above* expert humans (68.0%) |
| HPSv2 | 2023 | CLIP-H + HPD v2 | Yes | Spearman 0.87, Kendall 0.76 (per HPSv3 paper); "limited discriminative power" |
| **HPSv3** | Aug 2025 | Qwen2-VL-7B + 1.08M pairs / 1.17M comparisons, uncertainty-aware ranking loss | Yes | Spearman **0.94**, Kendall **0.82**, 76.9% pairwise; **87% win-rate over ImageReward** |
| TIFA | ICCV 2023 | LM generates QA pairs from prompt → VQA answers on image → % correct | Yes (VQA half) | 4k prompts / 25k questions, 12 categories |
| DSG | ICLR 2024 | Same, but questions form a *dependency DAG*; a question counts only if its parents were answered correctly | Yes (VQA half) | Spearman **0.463**, Kendall **0.380** vs Likert |
| VQAScore | 2024 | `P("Yes" \| image, "Does this figure show '{text}'? answer yes or no")` via CLIP-FlanT5 | Yes | Beats ImageReward/PickScore/HPSv2 on TIFA160, Pick-a-Pic, DrawBench, EditBench, COCO-T2I, Flickr8K; **10×** CLIPScore on counting/logic |
| FGA-BLIP2 (EvalMuse-40K) | AAAI 2025 | BLIP2 fine-tuned to emit token-level element alignment | Yes | Fine-grained per-element scores; beats CLIPScore/BLIP2Score |
| UnifiedReward / VisionReward | 2025 | LLaVA-OneVision-7B, pointwise + pairwise, multi-dimensional | Yes | NeurIPS 2025 |
| GenArena (pairwise VLM judge) | 2026 | Pairwise instead of pointwise VLM scoring | Yes | Spearman **0.86** vs **0.36** for pointwise baselines |
| Arena-T2I Hard | Jul 2026 | Dependency-aware checklist, successor to DSG/TIFA | Yes (checklist eval) | Models relational structure DSG treats atomically |

### 1.2 Known weaknesses (strong evidence)

The most important critical paper is **Ross, Hall, Romero Soriano & Williams, "What makes a good metric? Evaluating automatic metrics for text-to-image consistency" (COLM 2024)**. Findings:
- **No tested metric (CLIPScore, TIFA, VPEval, DSG) satisfies all reasonable desiderata.**
- All show **insufficient sensitivity to language and visual properties**.
- TIFA/VPEval/DSG **correlate highly with each other** but add information beyond CLIPScore.
- **All three VQA-based metrics exploit text shortcuts, notably yes-bias** in the QA model. This is a direct warning against naive VQA scoring.

Additional documented weaknesses:
- **PickScore tracks aesthetics more than prompt fidelity** — it "often chooses more aesthetically pleasing images than CLIP-H; at times, at the cost of faithfulness to the prompt."
- **ImagenHub (ICLR 2024) found essentially no automatic metric works**: "None of the existing automatic metrics has a Spearman's correlation higher than 0.2 except subject-driven image generation," with correlations spanning −0.2 to +0.4.
- HPSv2 gives **identical scores to Playgroundv2.5, Infinity, and Flux-dev** — non-discriminative at the top of the range. This is the same disease your scorer has.

### 1.3 Can any be computed without running the image model? — No, with one important nuance

Every metric above consumes an image. **However**, TIFA/DSG/Arena-T2I split cleanly into two halves:

- **Half 1 (text-only):** prompt → atomic questions / scene-graph tuples / dependency DAG.
- **Half 2 (needs image):** VQA answering.

Half 1 is a legitimate, publication-grounded **text-only measure of how much checkable content a prompt contains**. Use it. See §8.

---

## 2. LLM-as-a-judge / VQA-based evaluation

**How it's done:** a VLM reads prompt + image and either (a) gives a pointwise Likert/rubric score, (b) answers a decomposed checklist, or (c) does pairwise A/B.

**Reliability — mixed and paradigm-dependent (strong evidence):**
- MLLM-as-a-Judge (ICML 2024, arXiv 2402.04788): MLLMs show "remarkable human-like discernment in **Pair Comparison**" but **significant divergence from humans in pointwise scoring and batch ranking**.
- **GenArena (2026)** quantifies exactly this: switching open-source VLMs from pointwise to pairwise raises Spearman from **0.36 → 0.86**, a +20% accuracy boost that beats top proprietary models. ⇒ **Always use pairwise, never pointwise Likert, for VLM judges.**
- **Parthasarathy, Collins & Stephenson (arXiv 2509.12750, Sep 2025)** measured per-attribute alignment across aesthetic quality, diffusion artifacts, anatomy, composition, object adherence, style:

  | | GPT-4o | Claude | PickScore |
  |---|---|---|---|
  | Overall Pearson | 0.461 | 0.407 | **0.498** |
  | Object adherence | 0.501 | 0.467 | — |
  | Anatomy | 0.398 | 0.390 | — |
  | Aesthetic | 0.376 | 0.338 | — |

  A **specialized 1B-scale reward model beat frontier LLMs**. On anatomy, humans hit 78.2% accuracy vs 57.6% for the best fine-tuned model. Also found: humans show strong inter-attribute correlations; GPT-4o shows "extremely weak correlations between each pair of non-overall tasks" — i.e. the judge is not modelling the same latent structure humans are.
- General LLM-judge agreement of **~83.7%** with humans (comparable to human-human) has been reported, but only when the quality gap between candidates is large.
- Known biases: sensitivity to prompt phrasing and candidate order, self-enhancement bias (exclude the evaluated model from judging), and adversarial manipulability ("Fooling the LVLM Judges", arXiv 2505.15249).

**Rubric quality matters enormously (important, 2026):** "From Holistic Evaluation to Structured Criteria" (arXiv 2606.08625) reports that **replacing model-generated rubrics with human-annotated ones improves judgment accuracy by 27% on average**, and that model-generated rubrics "gravitate toward surface features such as format and length while systematically neglecting core implicit constraints." **Do not let an LLM write your rubric.** (This is also a precise description of your current scorer's failure mode: it rewards format and length.)

---

## 3. Prompt-side (text-only) quality assessment — the key question

### 3.1 Direct evidence it works

**Bizzozzero, Bendidi & Risser-Maroix, "Prompt Performance Prediction for Image Generation" (arXiv 2306.08915, Jun 2023).** Defines the task **PPP**: predict prompt performance *before* generating. Method: 8 pre-trained text encoders (CLIP ViT-B/32 & ViT-L/14, BART, GPT-2, BLOOM-560M, Sentence-T5 base/large/XL) → **linear probe** → predicted score. Targets: aesthetic appeal (CLIP aesthetic predictor), memorability (ResMem, ViTMem), compositionality (SAMPNet).

Results (Pearson, all p < 0.01):
- DALL·E 2: **0.575–0.717**
- Midjourney: **0.636–0.835**
- Stable Diffusion: **0.525–0.811**

Conclusion: prompt performance **is** predictable from text alone, best with CLIP embeddings. *Caveat: this predicts aesthetics/memorability, not prompt-intent fidelity, and needs a labelled training set to fit the probe.*

### 3.2 The IR analogue: pre-retrieval Query Performance Prediction

A 40-year-old, well-validated literature on scoring a query **without running retrieval**, using only query terms + collection statistics. (Hauff, Hiemstra & de Jong, *A survey of pre-retrieval query performance predictors*, CIKM 2008; He & Ounis, *Inferring query performance using pre-retrieval predictors*, SPIRE 2004.)

Best-performing predictors, all pure Python given a corpus:
- **AvIDF / MaxIDF** — `idf(t) = log(N / df(t))`. MaxIDF gave the best correlation on TREC web data.
- **AvICTF** — average inverse collection term frequency; one of the two best predictors.
- **Simplified Clarity Score (SCS)** — the other best predictor:
  `SCS = Σ_{t ∈ Q} P_ml(t|Q) · log₂( P_ml(t|Q) / P_coll(t) )` where `P_ml(t|Q) = tf(t,Q)/|Q|`.
  (Full Clarity Score = KL divergence of query model from collection model; correlates positively with average precision.)
- **Query scope** — fraction of the collection containing any query term.
- **SCQ** — similarity/collection-query variance evidence (Zhao, Scholer & Tsegay, ECIR 2008).
- 16 linguistic features on TREC queries showed significant correlations with recall/precision.

**This maps 1:1 onto your problem.** Your 7,613-prompt corpus = the collection. A prompt whose terms are all high-frequency ("beautiful", "high quality", "detailed") has low AvIDF ⇒ low specificity. This is the principled replacement for `sum(1 for w in specificity_words if w in prompt_lower)`.

### 3.3 Lexical resources for specificity (pure lookup, no model)

**Brysbaert, Warriner & Kuperman (2014), "Concreteness ratings for 40 thousand generally known English word lemmas", *Behavior Research Methods* 46:904–911.** 37,058 words + 2,896 two-word expressions, 4,000+ participants, 25 ratings each, 1 (abstract) – 5 (concrete). Free CSV. Concreteness = "the degree to which a word's meaning is understood through perception and action" — which is *exactly* what an image model can render. Mean concreteness of content words is a strong, model-free specificity proxy.

### 3.4 Ambiguity / underspecification

- **GRADE (Rassin, Slobodkin, Ravfogel, Elazar & Goldberg, arXiv 2410.22592, Oct 2024)**: "textual prompts are inherently underspecified." Measured 720,000 images across 12 models on 400 concept-attribute pairs; **all models show limited variation with clear deterioration in stronger models**, e.g. **98% of generated cookies are round**. Root cause traced to underspecified training captions. GRADE achieves **>90% human agreement** while showing **weak correlation to commonly used diversity metrics** (i.e. the standard metrics are missing this).
- Prompt underspecification taxonomy (arXiv 2606.05486 and related): omitted constraints, multiple plausible readings, vague references.
- **Test-time Prompt Refinement (arXiv 2507.22076)**: making spatial relations, object attributes, and stylistic constraints *explicit* substantially improves generation quality — direct support for scoring slot-explicitness.
- **Promptist (Hao et al., NeurIPS 2023, arXiv 2212.09611)**: RL-optimized prompt rewriting; "by generating more detailed and informative prompts, Promptist improves text-to-image consistency" — supports informativeness as a scoring axis, *but* its reward is aesthetics-weighted, which is how "masterpiece, 4k, trending on artstation" boosterism got normalized. Don't reward booster tokens.

### 3.5 Honest limits

- **No published, validated, model-free prompt-quality score exists** for text-to-image. What exists: (a) PPP with learned probes, (b) QPP predictors from IR, (c) lexical-diversity→visual-diversity correlations, (d) commercial rubrics (weak evidence). The design in §8 composes (a)–(c) with a goal-fidelity term that is novel but trivially verifiable.
- **Predictive Prompt Analysis / SPA (arXiv 2501.18883, 2025)** predicts LLM behaviour from sparse-autoencoder activations, r = 0.918, 99.6% compute reduction — impressive but requires white-box model access. Not applicable to closed image models.

---

## 4. Rubric design

### 4.1 Published / research-grade

- **ImagenHub (Ku et al., ICLR 2024, arXiv 2310.01596)** — two dimensions, each on a 3-point scale `{0, 0.5, 1}`:
  - **SC** — Semantic Consistency (alignment with prompt/conditions)
  - **PQ** — Perceptual Quality (artifacts, distortions, naturalness)
  - **Final score: `O = √(SC × PQ)` — geometric mean, chosen explicitly because it penalizes a model when either dimension fails, preventing high PQ from masking semantic failure.** ← Steal this aggregation rule.
- **HPDv3 / HPSv3 (arXiv 2508.03789, Aug 2025)** — three annotator criteria: **Prompt Alignment**, **Aesthetic Quality / technical execution**, **Overall Coherence** (logical consistency and naturalness).
- **Parthasarathy et al. (2509.12750)** — six validated attributes: aesthetic quality, diffusion artifacts, anatomical accuracy, compositional correctness, object adherence, style.
- **TechImage-Bench (arXiv 2512.12220)** — rubric-based evaluation for technical image generation, deliberately beyond aesthetics.
- **DSG/Arena-T2I** — the checklist/dependency-DAG *is* the rubric, auto-derived per prompt rather than fixed.

### 4.2 Practitioner consensus (weak evidence — blogs, no validation)

Six recurring dimensions: **subject, style, lighting, composition, mood, technical**. A commonly cited priority stack: purpose/subject → environment/action → composition/lighting → color/material/style → camera shorthand → tool controls (aspect ratio, quality).

A commercial LLM-judge prompt rubric (SurePrompts, 7×5=35) uses: role clarity, context sufficiency, instruction specificity, format structure, example quality, constraint tightness, output validation. **Treat as unvalidated.**

### 4.3 What is actually validated

**Validated:** prompt alignment / semantic consistency; perceptual quality; overall coherence; object adherence; compositional correctness; geometric-mean aggregation; pairwise > pointwise.
**Not validated:** "negative space", "technical params", and the specific 6-slot photography taxonomy. These are craft conventions, not measured constructs. Use them as *coverage slots*, not as evidence-backed quality predictors — and say so in your docs.

---

## 5. Human evaluation protocols

- **Raters per item:** ImagenHub used **3**, after testing up to 10. Krippendorff's α *decreases* with more raters (≈0.70 at 3 → 0.64 at 10) while the mean score stays stable — so 3 is the efficiency sweet spot, not a compromise.
- **Sample size:** ImagenHub used **102–197 instances per task** across 7 tasks and ~30 models.
- **Agreement achieved:** ImagenHub α > 0.4 for 76% of models (reports both Krippendorff α and Fleiss κ). VQAScore human ratings: **α = 0.72 (images), 0.70 (videos)**. HPDv3: **9–19 annotators per pair**, 76.5% average convergence at a 95% threshold, plus a 600-person validation set at 80% convergence. A typical in-house 3-annotator T2I study lands around **α ≈ 0.60**.
- **Interpretation bands:** <0.4 poor · 0.4–0.6 moderate · 0.6–0.8 substantial · >0.8 excellent. For LLM-judge validation, common targets are **weighted κ > 0.6** and **α ≈ 0.8**.
- **Practical protocol:** 3 raters, 100–200 stratified items, report α **and** ICC(2,k), use pairwise comparisons, randomize order, exclude self-judging models.

---

## 6. Diversity / duplication metrics — detecting your exact bug

### 6.1 Text-side measures and their evidence

**De Rosa Palmini & Cetinic (Univ. of Zurich), "Exploring Language Patterns of Prompts in Text-to-Image Generation and Their Impact on Visual Diversity" (arXiv 2504.14125, Apr 2025)** is the single most useful paper here. They computed four **text-only** metrics and correlated them against **Vendi Score** visual diversity of the generated images:

| Text metric | Definition | Spearman ρ vs visual diversity |
|---|---|---|
| **Compression Ratio (CR)** | uncompressed size / gzip size | **+0.620** (p = 0.012) |
| **Effective Number of Words (ENW)** | `exp(H(unigram distribution))` | **+0.521** (p = 0.005) |
| **Self-Repetition Score (SRS)** | recurrence of longer n-grams across the set | **−0.536** (p = 0.003) |
| TTR | unique words / total words | (reported, weaker) |

Also: **prompt-pair token similarity ≥ 0.8 → visually homogeneous outputs**; **0.5–0.7 → greater visual diversity**; token↔image similarity Pearson 0.33 (R² = 0.182). Vendi scores declined after Feb 2024 alongside declining lexical diversity.

**This is your justification: text-only batch diversity metrics genuinely predict output diversity, and 0.8 token similarity is an empirically grounded homogeneity threshold.**

### 6.2 The measures, with caveats

| Measure | Formula | Cost | Caveat |
|---|---|---|---|
| **distinct-n** | `#unique n-grams / #n-grams` | O(n) | **Biased against long texts** — normalize or fix length. See "Rethinking and Refining the Distinct Metric" (arXiv 2202.13587): it measures n-gram *duplication*, not diversity per se. |
| **Self-BLEU** | mean BLEU of each item vs all others | **O(n²)** — "extremely time-consuming" | Fine at n ≤ 200; use `nltk` |
| **TTR** | types/tokens | O(n) | Strongly length-sensitive |
| **MTLD** | mean length of sequences maintaining TTR ≥ **0.72** | O(n) | **Least affected by text length**; requires **≥100 tokens** |
| **MATTR** | TTR averaged over sliding window | O(n) | Good for fluctuation *within* a long text; questionable for overall diversity (Bestgen 2024) |
| **Compression Ratio** | `len(text)/len(gzip(text))` | O(n), stdlib | Validated ρ=0.62 above |
| **NCD** | `(C(xy) − min(C(x),C(y))) / max(C(x),C(y))` | O(n²) but stdlib `zlib` only | Parameter-free; from the gzip-kNN line of work |
| **MinHash / Jaccard on shingles** | LSH over k-gram sets | ~O(n) with LSH | `datasketch`. Standard corpus threshold **J ≥ 0.8 = near-duplicate**; a study on real user prompts at J ≥ 0.9 caught 31.3% duplicates vs 5.8% for byte-exact |
| **Vendi Score** | `exp(Shannon entropy of eigenvalues of similarity matrix K)` | O(n³) eigendecomp | Friedman & Dieng, TMLR 2023, arXiv 2210.02410. Needs a similarity function — **can use n-gram kernel instead of embeddings**, keeping it GPU-free. Conditional Vendi Score (arXiv 2411.02817) adds prompt-awareness. |
| Embedding cosine | `cos(e_i, e_j)` | needs a model | Catches paraphrase that n-grams miss |

---

## 7. A/B and regression testing for prompt systems

Consensus practice (industry sources — moderate evidence; the arXiv work here is thin):

- **Golden set**: a reviewed, versioned dataset of representative inputs + expected outputs + rubrics. "Small enough to run constantly, representative enough to catch meaningful regressions."
- **Regression loop**: rerun fixed prompts/datasets/evaluator thresholds after *every* model, prompt, retriever, or tool change; compare candidate vs **last passing baseline**.
- **Two drift types**: *prompt drift* (accumulated wording edits) and *model drift* (upstream provider changes with no code change). Only continuous eval against historical baselines catches the latter.
- **Canary prompts**: test cases probing characteristic behaviors — they "reveal when a model's personality has shifted." Deploy pattern: **test → canary → monitor → rollback**.
- **Production sampling**: score 5–10% of real traffic with an automated evaluator, watch for drift.
- **The evaluation pyramid**: vibes → human review → LLM-as-judge → regression → observability. Each layer cheaper per item and noisier than the one above; all five needed.
- **Caution**: "When Generic Prompt Improvements Hurt" (arXiv 2601.22025) — generic prompt-engineering advice applied without eval-driven iteration *degrades* application performance.

---

## 8. Recommended scorer design

### 8.0 Diagnosis of the current scorer

`higgsfield_prompt.py:600-659` — `_quality_score(prompt_text, category)`. Three concrete defects:

1. **40% of the score is raw length.** `len_ratio = min(gen_len/avg_len, 1.5); len_score = int(len_ratio/1.5*40)` — monotonically rewards padding up to 1.5× corpus average. Textbook Goodhart, and exactly the "surface features such as format and length" failure that arXiv 2606.08625 measured at −27% judgment accuracy.
2. **Substring keyword matching produces false positives.** `spec_count = sum(1 for w in specificity_words if w in prompt_lower)` with `"mm"` in the list matches **"co*mm*ercial"**, **"su*mm*er"**, **"reco*mm*ended"**; `"fill"` matches **"fulfill"**, **"filling"**; `"color"` matches **"colorless"**. Then it saturates at 15 of 31 keywords, so most templated prompts hit the cap.
3. **No goal-conditioned term at all.** Every input to `_quality_score` is `(prompt_text, category)`. The user's `goal` never enters. **A generator that emits the same prompt for every goal scores identically and perfectly.** This is why the scorer is blind to the duplication bug — it is structurally incapable of detecting it.

Note `scripts/verify-generation-diversity.py` already checks unique `source_prompt_ids` sets (line 66-72) but never compares the *prompt texts*, so identical prompts from different source IDs pass.

---

### 8.1 Prompt Quality Score (PQS) — text-only, pure Python

Six components in [0,1], aggregated by **weighted geometric mean** (ImagenHub's `O = √(SC×PQ)` rationale, generalized), then a multiplicative penalty.

```
PQS = 100 · (C^0.20 · S^0.20 · A^0.20 · R^0.10 · G^0.30) · (1 − X)
```
with `X ∈ [0, 0.5]`. Every factor floored at 0.01 so a single zero tanks the score rather than NaN-ing it. **G carries the largest weight because it is the only term that detects the duplication bug.**

---

**C — Slot Coverage (0.20).** Replace the flat keyword list with a **typed slot schema** and per-category required masks.

Slots: `subject`, `subject_attrs`, `action_pose`, `setting`, `composition`, `lighting`, `color`, `style_medium`, `technical` (aspect ratio / lens / render engine), `constraints_negative`, `text_in_image`.

Per-category masks — a UI-design prompt must not be penalized for lacking `lighting`, and a portrait must not be rewarded for `design system`:

```python
REQUIRED = {
  "Portrait / Selfie":   {"subject","subject_attrs","lighting","composition","style_medium","technical"},
  "App / Web Design":    {"subject","setting","composition","color","style_medium","text_in_image","constraints_negative"},
  "Product Marketing":   {"subject","subject_attrs","lighting","setting","composition","color","technical"},
  "Infographic / Edu Visual": {"subject","composition","color","style_medium","text_in_image"},
}
C = sum(w_s for s in REQUIRED[cat] if filled(s)) / sum(w_s for s in REQUIRED[cat])
```

`filled(s)` must require a **modified noun phrase**, not a bare token: use `re.search(r'\b(\w+ing|\w+ed|[a-z]+)\s+(light|lighting)\b')`-style patterns, or a spaCy `en_core_web_sm` noun-chunk check that the head noun in the slot lexicon carries ≥1 `amod`/`compound` child. Binary per slot — no counting, no saturation games.

**S — Specificity (0.20).** Pre-retrieval QPP over your own corpus. Build once:

```python
# one-off: build DF table from the 7,613-prompt corpus
# df[t] = #prompts containing lemma t ; N = total prompts
idf = lambda t: math.log(N / (1 + df.get(t, 0)))

content = [lemma(w) for w in tokens if w not in STOP and w.isalpha()]
avidf   = mean(idf(t) for t in set(content))
scs     = sum(p*math.log2(p / max(p_coll[t], 1e-9))
              for t, p in unigram_dist(content).items())     # Simplified Clarity Score
conc    = mean(brysbaert.get(t, 2.5) for t in content)       # 1..5, default = corpus mean

S = 0.4*clip01(avidf / AVIDF_P90) \
  + 0.3*clip01(scs   / SCS_P90) \
  + 0.3*clip01((conc - 2.0) / (4.5 - 2.0))
```
Percentiles `AVIDF_P90`, `SCS_P90` computed once over the corpus — never hand-tuned constants. Brysbaert CSV is ~2 MB, `dict` lookup, zero dependencies.

**A — Atomic Assertion Density (0.20).** The text-only half of TIFA/DSG. Extract `(entity, attribute)` and `(entity, relation, entity)` tuples.

- *With spaCy `en_core_web_sm` (12 MB, CPU, no torch):* one atom per `amod`/`compound`/`nummod` dependency on a noun; one per `prep`+`pobj` chain between two noun chunks. This is a shallow scene-graph parse — the same construct DSG builds.
- *Pure-regex fallback:* count `ADJ+ NOUN` bigrams via a POS-free heuristic (adjective suffix list + slot lexicons) and preposition-linked noun pairs.

```python
A = min(1, atoms / T[cat]) * min(1, (atoms / max(words,1)) / RHO)
```
`T[cat]` = corpus median atom count for the category. `RHO` = corpus 25th-percentile atoms-per-word. **The second factor is the anti-padding term**: a prompt that doubles in length without adding assertions gets *worse*, directly inverting the current length reward.

**R — Non-redundancy (0.10).** Internal repetition:
```python
tri  = list(ngrams(tokens, 3))
d3   = len(set(tri)) / max(len(tri), 1)          # distinct-3, within-prompt
cr   = len(text.encode()) / len(gzip.compress(text.encode()))
R    = 0.6*d3 + 0.4*clip01((CR_P90 - cr) / (CR_P90 - CR_P10))
```
Compression ratio direction is grounded in ρ = +0.620 (De Rosa Palmini & Cetinic). Prompts that compress well are repetitive.

**G — Goal Fidelity (0.30). The new, load-bearing term.** IDF-weighted recall of the user's goal in the produced prompt:
```python
goal_terms = {lemma(w) for w in tokenize(goal) if w not in STOP and w.isalpha()}
G = sum(idf(t) for t in goal_terms if t in prompt_lemmas) \
  / max(sum(idf(t) for t in goal_terms), 1e-9)
```
Optionally add a soft-match arm for synonyms via the corpus co-occurrence matrix (no model needed). A prompt copied from a template that ignores the goal scores **G ≈ 0**, and the geometric mean drives PQS toward zero. This alone would have caught the June 2026 bug.

**X — Contradiction & vagueness penalty (multiplicative, cap 0.5).**
```python
MUTEX = [ {"golden hour","studio softbox","moonlight","overcast"},   # lighting
          {"daytime","night","dusk"},                                 # time
          {"photograph","3d render","watercolor","vector illustration","oil painting"},
          {"no text","headline reads","caption reads"} ]
VAGUE = {"beautiful","nice","high quality","detailed","4k","8k",
         "masterpiece","stunning","amazing","various","some","professional"}

conflicts = sum(1 for grp in MUTEX if len(grp & present) > 1)
ar_dupes  = max(0, len(re.findall(r'\b\d{1,2}:\d{1,2}\b', text)) - 1)
vague_frac= len([w for w in tokens if w in VAGUE]) / max(len(tokens),1)

X = min(0.5, 0.12*conflicts + 0.10*ar_dupes + 2.0*vague_frac)
```
The `VAGUE` set is deliberately the Promptist-era booster vocabulary — high frequency, near-zero IDF, no renderable content.

**Calibration & grading — do not hardcode cutoffs.** Score all 7,613 corpus prompts once, store the per-category PQS distribution, and report the **percentile**:
```
A+ ≥ p90 · A ≥ p75 · B ≥ p50 · C ≥ p25 · D < p25
```
This makes the scorer discriminative *by construction* (uniform percentile spread) and self-recalibrating when the corpus grows — fixing the "identical scores for different models" disease that afflicts HPSv2 and your current grades.

**Dependencies:** stdlib (`gzip`, `zlib`, `math`, `re`, `sqlite3`) + `datasketch` + optional `spacy`+`en_core_web_sm` + optional `textstat`. **No torch, no GPU.**

---

### 8.2 Diversity / duplication check

Run over a batch of N prompts generated from N *different* goals. All pure Python.

```python
def shingles(t, k=5):
    w = normalize(t).split()
    return {" ".join(w[i:i+k]) for i in range(max(1, len(w)-k+1))}

def jaccard(a, b): return len(a & b) / max(len(a | b), 1)

def ncd(x, y):                       # stdlib only, no deps
    cx, cy = len(zlib.compress(x.encode())), len(zlib.compress(y.encode()))
    cxy    = len(zlib.compress((x + " " + y).encode()))
    return (cxy - min(cx, cy)) / max(cx, cy)
```

**Metric panel:**

| Metric | Formula | FAIL | WARN |
|---|---|---|---|
| **Max pairwise Jaccard**, 5-gram shingles, across *different* goals | `max J(pᵢ,pⱼ)` | **≥ 0.70** | ≥ 0.50 |
| **Mean pairwise Jaccard** | `mean J(pᵢ,pⱼ)` | **≥ 0.35** | ≥ 0.25 |
| **batch distinct-3** | `|unique trigrams| / |trigrams|` over concatenated batch | **< 0.50** | < 0.65 |
| **Self-BLEU-4** (n ≤ 200) | mean BLEU-4 of each vs rest | **≥ 0.45** | ≥ 0.30 |
| **Batch compression ratio** | `len(concat)/len(gzip(concat))` normalized by single-prompt mean CR | **≥ 1.6×** | ≥ 1.3× |
| **ENW** | `exp(H(unigram dist))` over batch | < 60% of corpus ENW | < 75% |
| **Source-ID entropy** | `H(source_prompt_ids) / log(N)` | **< 0.5** | < 0.7 |
| **Mean goal fidelity** | `mean G(pᵢ, gᵢ)` | **< 0.40** | < 0.55 |
| **Cross-goal discrimination Δ** | `mean G(pᵢ,gᵢ) − mean_{j≠i} G(pᵢ,gⱼ)` | **< 0.15** | < 0.30 |

**The single best detector for your bug is the last one.** Δ measures whether a prompt matches *its own* goal better than someone else's. If the generator ignores input, Δ → 0 regardless of how pretty the prompts are. Target **Δ ≥ 0.30**.

**Second-best: the goal-swap test.** For every pair, if `J(pᵢ,pⱼ) ≥ 0.70` while `J(gᵢ,gⱼ) < 0.20`, hard-fail — outputs are near-identical for unrelated inputs. Threshold anchored to the empirical finding that prompt token similarity ≥ 0.8 yields visually homogeneous outputs (ρ evidence in §6.1); 0.70 is a deliberately conservative alarm.

**Threshold provenance — be honest in your docs:** J ≥ 0.8 for near-duplicate is standard corpus-dedup practice (published). The ≥0.8 similarity → visual homogeneity finding is published (ρ evidence, n small, p = 0.012). The specific FAIL/WARN numbers above are **engineering heuristics** — calibrate them by running the panel over your 7,613-prompt corpus (which is human-authored and genuinely diverse) to get the "healthy" reference distribution, then set FAIL at roughly corpus p95 of pairwise similarity.

**What genuinely requires a model:** true paraphrase detection (same meaning, disjoint vocabulary) is invisible to n-grams. If needed, `sentence-transformers/all-MiniLM-L6-v2` (~90 MB, CPU, ms/sentence) with near-dup at **cos ≥ 0.95** and paraphrase at **0.80–0.95**; or the numpy-only static-embedding route (`model2vec` / potion-base-8M) to avoid torch entirely — *verify current availability before committing*. Plug either into a **Vendi Score** with a linear kernel for a single principled batch-diversity number. Everything else above is GPU-free.

---

### 8.3 Validation & regression harness

**Adversarial unit tests — hard assertions, run in CI.** For each, PQS must drop by the stated margin:

| Perturbation | Expected |
|---|---|
| Pad prompt to 2× with filler clauses, no new atoms | PQS **decreases** (currently: increases) |
| Keyword-stuff all 31 specificity words with no structure | PQS decreases vs the clean original |
| Swap the goal, keep the prompt | PQS drops **≥ 25 points** (G collapses) |
| Truncate to 40% | PQS drops ≥ 15 points |
| Insert lighting contradiction | PQS drops ≥ 8 points |
| Replace concrete nouns with hypernyms ("man" → "person" → "figure") | PQS decreases monotonically |

Target: **≥ 90% pairwise ranking accuracy** on these synthetic pairs. This is cheap, deterministic, and catches Goodharting before humans are involved.

**Human validation:** 3 raters × 150 prompts stratified by category, pairwise A/B (not Likert — GenArena's 0.36→0.86 result), report Spearman(PQS, human) plus Krippendorff α and ICC(2,k). Accept at **α ≥ 0.6** and **Spearman ≥ 0.5** (for reference: DSG achieves 0.463 against Likert, and no ImagenHub automatic metric exceeded 0.2).

**Golden set / canaries:** freeze ~200 goals stratified across your 7 categories. On every corpus or template change: rerun, store per-dimension distributions, alarm on a two-sample **KS test p < 0.01** vs the last passing baseline. Keep the diversity panel from §8.2 as a **release gate**, not a report — the June 2026 bug shipped because diversity was a printout, not an assertion.

---

## 9. Full citations

**Alignment metrics**
- Hu, Liu, Kasai, Wang, Ostendorf, Krishna & Smith. *TIFA: Accurate and Interpretable Text-to-Image Faithfulness Evaluation with Question Answering.* ICCV 2023. https://arxiv.org/abs/2303.11897
- Cho, Hu, Garg, Anderson, Krishna, Baldridge, Bansal, Pont-Tuset & Wang. *Davidsonian Scene Graph: Improving Reliability in Fine-grained Evaluation for Text-to-Image Generation.* ICLR 2024. https://arxiv.org/html/2310.18235v3 · code https://github.com/j-min/DSG
- Lin, Pathak et al. *Evaluating Text-to-Visual Generation with Image-to-Text Generation* (VQAScore). 2024. https://arxiv.org/pdf/2404.01291
- Xu et al. *ImageReward: Learning and Evaluating Human Preferences for Text-to-Image Generation.* NeurIPS 2023. https://www.semanticscholar.org/paper/1b2355c3c674b26a977768a91a164384ad51bbb1
- Kirstain et al. *Pick-a-Pic: An Open Dataset of User Preferences for Text-to-Image Generation* (PickScore). 2023. https://arxiv.org/html/2305.01569
- Ma et al. *HPSv3: Towards Wide-Spectrum Human Preference Score.* Aug 2025. https://arxiv.org/html/2508.03789v1
- *EvalMuse-40K / FGA-BLIP2.* AAAI 2025. https://arxiv.org/abs/2412.18150 · https://github.com/DYEvaLab/EvalMuse
- *Unified Reward Model for Multimodal Understanding and Generation.* NeurIPS 2025. https://arxiv.org/html/2503.05236v2 · https://github.com/CodeGoat24/UnifiedReward
- Ban, Xie, An, Hong, Frick, Hsu, Chiang, Stoica & Hsieh. *Arena-T2I Hard: Benchmarking and Improving Faithfulness with Dependency-Aware Checklist.* Jul 2026. https://arxiv.org/pdf/2606.31711
- *A Survey on Quality Metrics for Text-to-Image Generation.* https://arxiv.org/abs/2403.11821
- Awesome-Evaluation-of-Visual-Generation (living index). https://github.com/ziqihuangg/Awesome-Evaluation-of-Visual-Generation

**Metric criticism**
- Ross, Hall, Romero Soriano & Williams. *What makes a good metric? Evaluating automatic metrics for text-to-image consistency.* COLM 2024. https://arxiv.org/abs/2412.13989
- Ku et al. *ImagenHub: Standardizing the Evaluation of Conditional Image Generation Models.* ICLR 2024. https://arxiv.org/pdf/2310.01596

**LLM/VLM judges**
- Chen et al. *MLLM-as-a-Judge: Assessing Multimodal LLM-as-a-Judge with Vision-Language Benchmark.* ICML 2024. https://arxiv.org/pdf/2402.04788 · https://mllm-judge.github.io/
- Parthasarathy, Collins & Stephenson. *What Makes a Good Generated Image? Investigating Human and Multimodal LLM Image Preference Alignment.* Sep 2025. https://arxiv.org/pdf/2509.12750
- *GenArena: How Can We Achieve Human-Aligned Evaluation for Visual Generation Tasks?* 2026. https://arxiv.org/html/2602.06013
- *ImagenWorld: Stress-Testing Image Generation Models with Explainable Human Evaluation.* Mar 2026. https://arxiv.org/html/2603.27862v1
- *Fooling the LVLM Judges: Visual Biases in LVLM-Based Evaluation.* 2025. https://arxiv.org/pdf/2505.15249
- *From Holistic Evaluation to Structured Criteria: Rubrics Across the Evolving LLM Landscape.* 2026. https://arxiv.org/pdf/2606.08625

**Prompt-side scoring**
- Bizzozzero, Bendidi & Risser-Maroix. *Prompt Performance Prediction for Image Generation.* Jun 2023. https://arxiv.org/pdf/2306.08915
- Hauff, Hiemstra & de Jong. *A survey of pre-retrieval query performance predictors.* CIKM 2008. https://dl.acm.org/doi/10.1145/1458082.1458311
- He & Ounis. *Inferring Query Performance Using Pre-retrieval Predictors.* SPIRE 2004. https://terrierteam.dcs.gla.ac.uk/publications/spire_final.pdf
- Brysbaert, Warriner & Kuperman. *Concreteness ratings for 40 thousand generally known English word lemmas.* Behav Res Methods 46:904–911, 2014. https://link.springer.com/article/10.3758/s13428-013-0403-5 · data https://github.com/ArtsEngine/concreteness
- Hao et al. *Optimizing Prompts for Text-to-Image Generation* (Promptist). NeurIPS 2023. https://arxiv.org/abs/2212.09611
- *Predictive Prompt Analysis.* 2025. https://arxiv.org/html/2501.18883v2
- *Test-time Prompt Refinement for Text-to-Image Models.* 2025. https://arxiv.org/html/2507.22076v1

**Diversity**
- Rassin, Slobodkin, Ravfogel, Elazar & Goldberg. *GRADE: Quantifying Sample Diversity in Text-to-Image Models.* Oct 2024. https://arxiv.org/abs/2410.22592
- De Rosa Palmini & Cetinic. *Exploring Language Patterns of Prompts in Text-to-Image Generation and Their Impact on Visual Diversity.* Apr 2025. https://arxiv.org/pdf/2504.14125
- Friedman & Dieng. *The Vendi Score: A Diversity Evaluation Metric for Machine Learning.* TMLR 2023. https://arxiv.org/abs/2210.02410
- *Conditional Vendi Score: Prompt-Aware Diversity Evaluation.* https://arxiv.org/pdf/2411.02817
- *Rethinking and Refining the Distinct Metric.* ACL 2022. https://arxiv.org/pdf/2202.13587
- Bestgen. *Estimating lexical diversity using MATTR: Pros and cons.* 2024. https://www.sciencedirect.com/science/article/abs/pii/S2772766124000740
- Wang et al. *DiffusionDB.* ACL 2023. https://arxiv.org/abs/2210.14896

**Testing/ops (industry, weaker evidence)**
- Braintrust, *LLM evaluation guide.* https://www.braintrust.dev/articles/llm-evaluation-guide
- *When Generic Prompt Improvements Hurt: Evaluation-Driven Iteration for LLM Applications.* 2026. https://arxiv.org/html/2601.22025v2
- textstat. https://github.com/textstat/textstat · datasketch (MinHash LSH)

---

## Summary for the caller

- **Nothing published scores a prompt without an image** — but three separate literatures each supply a validated piece: PPP (text embeddings → r 0.53–0.84 for outcome prediction), pre-retrieval QPP (IDF/SCS specificity, pure Python over your existing corpus), and prompt-lexical→visual-diversity correlations (ρ 0.52–0.62).
- **The current scorer's fatal flaw is structural, not parametric**: `_quality_score()` never receives the user's `goal`, so it cannot detect duplicate outputs no matter how the weights are tuned. It also puts 40% of the score on raw length and has real substring false positives (`"mm"` matches "commercial", `"fill"` matches "fulfill").
- **Recommended replacement**: six-factor weighted **geometric** mean (Coverage, Specificity, Atomic-density, Non-redundancy, **Goal-fidelity @ 0.30**, minus a contradiction/vagueness penalty), graded by **percentile against the corpus** rather than hardcoded cutoffs. GPU-free; only optional deps are `datasketch`, `spacy/en_core_web_sm`, `textstat`.
- **Duplication check**: MinHash/Jaccard 5-gram panel + batch distinct-3 + compression ratio + source-ID entropy, with **cross-goal discrimination Δ = mean G(pᵢ,gᵢ) − mean G(pᵢ,gⱼ≠ᵢ) ≥ 0.30** as the single best detector for the exact bug, and a goal-swap hard-fail at J ≥ 0.70.
- **Only true paraphrase detection needs a model** (MiniLM CPU, cos ≥ 0.95 near-dup); everything else is stdlib.
- Two protocol rules worth adopting verbatim: **pairwise, never pointwise** for any LLM/VLM judge (Spearman 0.86 vs 0.36), and **geometric-mean aggregation** so one failed dimension cannot be masked (ImagenHub).
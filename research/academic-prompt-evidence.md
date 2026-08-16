# Academic Evidence: T2I Prompt Construction (2022–2026)

> Research report 4/5 of the 2026-08-17 sweep. Evaluation/diversity metrics excluded (covered in prompt-quality-evaluation.md). All arXiv ids verified this session.

## Evidence table (topic | finding | citation | strength)

| Topic | Finding | Citation | Strength |
|---|---|---|---|
| Structure | Constituency parsing + cross-attention biasing improves binding/composition (training-free, SD era) | 2212.05032 ICLR'23 | Moderate |
| Structure/layout | LLM → captioned bounding boxes ≈ **2× accuracy** on numeracy/spatial/negation tasks | 2305.13655 TMLR'24 | Strong |
| Structure/layout | CSS-style structured layouts beat direct T2I by **20–40%** on numerical/spatial | 2305.15393 NeurIPS'23 | Strong |
| Format mix | Mixed "core tags + concise NL" beats pure tags; but expansion narrows diversity (Vendi 13.99→18.29 direction) | 2411.08127 | Moderate |
| Length | CLIP 77-token truncation loses signal; Long-CLIP recovery +~20% retrieval | 2403.15378 ECCV'24 | Strong |
| Length | Long dense prompts (~285 tok) degrade ALL tested models incl. GPT-Image-1, Gemini 2.0 Flash ("attribute leakage"); need both token headroom AND long-prompt training | 2505.16915 ICML'26 | Strong |
| Length | CLIP-as-encoder "constrains dense-prompt comprehension"; LLM adapter (ELLA) fixes | 2403.05135 | Mod-strong |
| Word order | SD biased to render the FIRST-mentioned object; spatial success tracks training co-occurrence | 2212.10015 | Strong |
| Word order | CLIP ≈ bag-of-words; order-restorable (TENOR); human spatial captions themselves ambiguous (SCOP) | 2412.13195 ICCV'25 | Strong |
| Negation | Encoders barely distinguish negated vs affirmative | 2401.06209 CVPR'24 | Strong |
| Negation | T2I-CompBench++ negation category: models score poorly on "X without Y" | 2307.06350 TPAMI | Strong |
| Negation field | Negative prompts ≠ logical negation: act LATE via latent neutralization | 2406.02965 ECCV'24 | Strong |
| Negation field | Fail outright in few-step models (no CFG); attention-steering restores 92–100% | 2412.02687 | Strong |
| Style tokens | "Quality boosters" taxonomy (masterpiece/4k/artstation) is **prevalence ethnography, zero efficacy measurement** | 2204.13988 | Taxonomy only |
| Style tokens | Individual tokens carry large non-obvious effects; rare tokens dominate/hijack | 2306.00966 · 2211.02408 | Mod/Strong |
| Style tokens | **Rare/uncommon wording FAILS more; frequent common wording wins** (R2F substitution improves generation) | 2410.22376 ICLR'25 | Strong |
| Binding | GenEval: color-binding 0.06–0.35, counting 0.35–0.66, position 0.04–0.15 vs single-object 0.97+ | 2310.11513 NeurIPS'23 | Strong |
| Binding | "Catastrophic neglect" of whole subjects; inference-time fixes exist | 2301.13826 SIGGRAPH'23 | Strong |
| Counting | Exact counts only small N; degrades per successive number; quantifiers/zero/fractions poor | 2406.14774 | Strong |
| Counting fix | LLM layout grounding strongly improves count accuracy | 2406.10210 CVPR'25 | Strong |
| Spatial | Prepositions severely limited; boxes/coordinates/LLM-planned layouts substantially better | 2212.10015 · 2301.07093 · 2307.10816 · 2211.15558 | Strong |
| Multilingual | Spanish mildly degrades; Basque/Latin dramatically ("completely unrelated"); translate-to-English recommended | 2208.09333 | Moderate (2022 models) |
| Multilingual | LLM text encoders much less English-bound | 2405.12914 | Mod-strong |
| Multilingual | Multilingual prompting magnifies stereotypes | 2401.16092 ACL'25 | Strong |
| Refinement | Closed-loop generate→VLM-check→rewrite beats one-shot (training-free) | 2507.22076 ICCVW'25 | Mod-strong |
| Refinement | LLM evolutionary prompt search vs reference image → transferable prompts | 2403.19103 TMLR'25 | Mod-strong |
| Diversity tradeoff | RL-style optimization collapses diversity (repetitive suffixes); GFlowNet keeps effective AND diverse | 2502.11477 CVPR'25 | Strong |
| Templates | Unknown/nonsense tokens produce recurring "default images" across unrelated prompts (750k MJ images) | 2505.09166 | Strong (phenomenon) |

## Direct answers

1. **JSON vs prose: NO controlled study exists on any model.** The efficacious ingredient is *semantic structure + explicit attribute/layout slots* (per-entity grouping, zones, boxes), renderable in either syntax. LMD's 2× and LayoutGPT's +20–40% come from explicit layouts, not JSON syntax. If we keep JSON internally, justify it as slot-enforcement for the generator, not as model-facing improvement.
2. **Length:** not monotonic. ~30–80 dense tokens for CLIP-backbone targets (77-token truncation); LLM-backbone models tolerate hundreds but leak attributes beyond training distribution (2505.16915 tested GPT-Image-1 + Gemini 2.0 Flash).
3. **Ordering:** front-load critical content (truncation + first-object bias). No controlled subject-first-vs-scene-first T2I ablation exists; vendor guidance (OpenAI scene→subject; FLUX/Seedream subject-first) conflicts — treat as model-preference, not law.
4. **Negation:** the paradox is multiply documented. Works: dedicated negative field (late latent neutralization — know the mechanism), exclude-by-omission, positive restatement. "no X" inline = the one consistently failing strategy.
5. **Boosters:** zero efficacy evidence; rare-token risk; common wording wins. Style NOUNS (watercolor, film noir) steer; quality ADJECTIVES don't. Camera/lens efficacy: unstudied academically (FLUX.2 officially endorses camera refs for photoreal — vendor evidence).
6. **Specificity/binding:** binding is a core failure mode; per-object attribute grouping + common vocabulary are the prompt-level fixes. Exact counts: small N only; encode as layout/repetition cues.
7. **Spatial:** prepositions near-uniformly weak; zones/boxes strong — the strongest academic support for our zone-schema direction.
8. **Multilingual:** degradation documented; translate-then-prompt is the evidence-backed default for CLIP-backbone targets; **Arabic T2I prompting specifically: no peer-reviewed study** (gap).
9. **Refinement:** 2–4 rounds with visual verification beats one-shot; reward-maximizing loops reduce diversity.
10. **Template reuse:** no direct study; convergent indirect evidence (2502.11477, 2411.08127, 2505.09166) that static templates + slot variation narrow output diversity — supports varied structure selection, not one fixed template.

## Keep / Drop for our engine

**Keep (evidence-backed):** per-entity attribute grouping + explicit zone/layout slots · front-loading + first-mention of primary subject · positive-only phrasing, exclusion by omission · common vocabulary over rare tokens · small-N counts as layout cues · translate-to-English for CLIP targets · optional 1–3 round visual-feedback loop for high stakes.

**Drop/demote:** "JSON is better" as such · quality boosters · camera jargon as a *quality* lever (keep as photoreal style content) · spatial prepositions as sole layout mechanism · "longer is better" (cap ~75 tokens CLIP targets) · one fixed template forever (diversity cost).

## Gaps (no good evidence)

JSON-vs-prose controlled comparison (any model) · Arabic T2I prompting · camera-term efficacy · booster-token efficacy · subject-first vs scene-first ablation · concrete-vs-abstract binding head-to-head · template-reuse→diversity direct measurement · prose-zones vs coordinates as isolated variable.

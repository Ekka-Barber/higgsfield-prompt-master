# Image-Generation Prompting Landscape, Aug 2026 (Competing Models)

> Research report 3/5 of the 2026-08-17 sweep. Primary sources preferred; [secondary] marked.

## Per-model summary

| Model | Official docs | Prompt style | Text-in-image | Negative prompts | Standout |
|---|---|---|---|---|---|
| FLUX.2 [pro/max] (Mistral-3 24B VLM + flow transformer) | docs.bfl.ml/guides/prompting_guide_flux2 | prose OR **official JSON schema** (scene/subjects/style/color_palette/lighting/camera); 30–80 words; early tokens weighted most | quotes + placement/typography/hex | NOT supported — positive phrasing | hex colors; prompt_upsampling; 10 ref images; ≤4MP ÷16; guidance 1.5–10 [flex] |
| FLUX.1 family incl. Krea | docs.bfl.ml/guides/prompting_unified_basics | natural language; template [SUBJECT],[LOCATION],[STYLE],[CAMERA],[LIGHTING],[COLORS],[EFFECT] | quotes signal literal | steer positively | Kontext: 10 input images; Krea anti-AI-look |
| Midjourney V7→V8.2 | docs.midjourney.com | **short simple phrases** (V8 tolerates longer); [img URL]+text+--params (params last, no punctuation) | **double quotes REQUIRED** (single fails); short Latin | `--no` param | --ar, --sref/--sw, --oref, --p, --raw, --hd+--q 4 (V8) |
| Ideogram 4 (open weights Jun 2026) | github.com/ideogram-oss/ideogram4/docs/prompting.md | **trained exclusively on structured JSON captions** (3 fields, strict key order); app users write prose, Magic Prompt converts | `{"type":"text","bbox":[…0–1000],"text":"literal","desc":"…"}`; multi-line \n | not documented | bboxes honored via MRoPE; OCR 0.97; #2 overall behind GPT Image 2 |
| Seedream 4/4.5 (ByteDance) | seed.bytedance.com/seedream4_0 · arXiv 2509.20427 | prose, subject→style→composition→lighting→technical; 30–100 words [secondary: fal] | dense text/formulas/charts headline feature | no param; prose negations tolerated [secondary] | PE model auto-rewrites prompts; native 1K–4K; adaptive AR |
| Stable Diffusion 3.5 (SD4 does NOT exist mid-2026) | stability.ai | natural language, moderate length | moderate; quotes convention | **yes — classic negative-prompt field** | open ecosystem ControlNet/LoRA |
| Recraft V3 | recraft.ai blog/docs | style-first: `A <style> of <content>. <details>. <background>. <style details>` | long multi-word text claimed best-in-class; Positioning Control | no param; negation risky | style refs/custom styles are PRIMARY control; SVG |
| Qwen-Image (2512/2.0/3.0) | github.com/QwenLM/Qwen-Image | prose; scene/style then per-text-element location + quoted content; 1k-token layout instructions (2.0) | quotes + placement + font; bilingual (Chinese strongest) | **yes — negative_prompt field**; pass `" "` if unused; true_cfg_scale 4.0 | Edit-2509 compositing; official rewrite() tools (editing unstable without) |
| Reve 2.0 | reve.art | LLM planning over code-like layout + diffusion | explicit via layout code | not documented | native 4K²; edit layout = edit image |
| Grok Imagine | docs.x.ai | plain natural language | not documented | not documented | 10 imgs/request; 3-ref edits |
| Higgsfield Soul 2.0 | higgsfield.ai/soul-intro | "pick a vibe, type a prompt" — deliberately prompt-LIGHT | not documented | not documented | Soul ID (≥20 photos); Soul HEX palettes; moodboards |

## Universal techniques (evidence-backed across vendors)

1. **Front-load the subject; early tokens weighted most** — FLUX.2 official; Seedream guidance; Recraft; MJ community. (Academic support: first-object bias, VISOR.)
2. **Specificity: precise synonyms, concrete counts, collective nouns** — identical official wording in MJ + Recraft docs ("three cats" not "cats").
3. **Positive phrasing, never in-prompt negation** — FLUX.2 ("sharp focus throughout" not "no blur"), MJ ("no cake" may render cake), Recraft same.
4. **Cover the same 7 facets** — MJ and Recraft list the IDENTICAL checklist: Subject, Medium, Environment, Lighting, Color, Mood, Composition.
5. **Literal text in DOUBLE quotes** — MJ explicitly rejects single quotes; FLUX/Qwen/OpenAI all use quotes. Double quotes = portable choice.
6. **Typography descriptors alongside literal text** (font, size, color, placement) — FLUX.2, OpenAI, Ideogram (desc field), Qwen.
7. **Camera/film references beat generic quality words for photorealism** — FLUX.2 official ("Shot on Hasselblad X2D, 80mm, f/2.8" outperforms "professional photo"); Seedream. Photography targets only.
8. **Iterative refinement beats one perfect prompt** — FLUX, Recraft, Seedream.
9. **English most precise** except Qwen (Chinese first-class).

## The architecture discriminator

Not "diffusion vs AR" — the question is **"does the model have an LLM-grade text path (or trained JSON format)?"**
- YES → structured/labeled/JSON prompts safe, often optimal: GPT Image, FLUX.2 (official JSON), Ideogram 4 (trained JSON), Reve, Qwen-Image (long layout instructions)
- NO → concise prose + 7 facets: MJ, SD3.5, Recraft, Grok, Soul; Seedream normalizes through a VLM anyway

## JSON prevalence reality check (corrects our original error)

JSON is *required* only for Ideogram 4 open weights, *officially sanctioned* for FLUX.2 precision work, *implicit* for Reve. Gallery/prevalence of JSON outside gpt-image/Ideogram ecosystems: **near zero. Prose is the portable lingua franca.** Even OpenAI's cookbook says any format works.

## Negative-concept handling is heterogeneous (adapter required)

- MJ → `--no item` · SD3.5/Qwen → negative-prompt field · FLUX.2/Ideogram/Recraft/Grok → **invert to positive phrasing** · GPT Image → trailing constraint sentence · Gemini → semantic positive rewrite

## Engine design implications (adopted into SOURCE_TRUTH.md)

1. Structured internal IR (subject/action/environment/style/lighting/color/mood/composition/text_elements/negative_concepts/ratio/references/output_intent photo-vs-art), rendered per model — never one shared string.
2. Three renderer families: prose (default), JSON (FLUX.2/Ideogram schemas), parameter (MJ).
3. Negative concepts get a per-adapter transform.
4. Text elements: always double quotes + typography + placement; route dense/bilingual text to Ideogram/Qwen/Seedream 4.5/FLUX.2, not MJ.
5. Disable model-side rewriters (Magic Prompt, prompt_upsampling, PE rewrite, Qwen rewrite()) when our engine already emits fully-specified prompts — double augmentation is the main portability failure.
6. Aspect-ratio mapping per model (MJ --ar; FLUX ÷16 ≤4MP; Qwen fixed presets; GPT flexible; Seedream adaptive).
7. Adapters carry model_version fields — the field moves fast (MJ V8→V8.2, Qwen 2512→3.0 in months).

Sources: docs.bfl.ml (prompting_guide_flux2, prompting_summary, unified_basics) · bfl.ai/blog/flux-2 · docs.midjourney.com (Prompt Basics, Parameter List, Text Generation) · updates.midjourney.com/v8-alpha · github.com/ideogram-oss/ideogram4 · ideogram.ai/blog/ideogram-4.0 · seed.bytedance.com · arXiv 2509.20427 · docs.byteplus.com · recraft.ai blog+docs · github.com/QwenLM/Qwen-Image · qwenlm.github.io · reve.art · docs.x.ai · higgsfield.ai/soul-intro · [secondary] fal.ai guides, promptomania, 3daistudio, geekycuriosity

# OpenAI GPT Image 2 — Official-Docs Audit of the Skill's Hardcoded Rules

> Claude session 0f5f4f48 (2026-08-17), preserved verbatim. Basis for the P1-0 source-truth correction task.

Six agents are still running. Here's what I've verified myself from primary sources in the meantime — and it's more consequential than the code bugs.

## I fetched OpenAI's official prompting guide and compared it to the skill's hardcoded rules

The skill's `GPT_IMAGE_2` dictionary — the 109-line block that the improvement plan wants to wire into generation — **contradicts OpenAI's own documentation on six points.** Wiring it in as-is would have propagated wrong guidance into every generated prompt.

| Skill asserts | OpenAI official says | Verdict |
|---|---|---|
| JSON is the primary structure; *"prose drifts — prefer JSON for layouts"* | *"Minimal prompts, descriptive paragraphs, JSON-like structures, instruction-style prompts, and tag-based prompts **can all work well**"* | Unsupported |
| A `negative_prompt_library` + *"must be a labeled closing block"* | Negative prompts are **never mentioned**. Use inline exclusions: *"no watermark," "no extra text"* | Cargo cult |
| `REFERENCE_0` / `REFERENCE_1` numbering required | *"Reference each input by index and description"* — `"Image 1: product photo"`, `"the second image"` | Invented syntax |
| Headlines ≤6 words, body ≤12 words, garbles beyond | No such limit. Put literal text **in quotes or ALL CAPS**; spell tricky words letter-by-letter; raise `quality` | Invented limits |
| Flat order: SUBJECT → STYLE → … → BACKGROUND | *"background/scene → subject → key details → constraints"* | Order reversed |
| Name the lens — *"Panavision anamorphic 70mm"* | *"detailed camera specs may be interpreted loosely… use them mainly for high-level look rather than exact physical simulation"* | Overrated |

The single biggest methodological error: the skill infers *"JSON is better"* from **54% of the corpus being JSON**. That's prevalence, not efficacy — it measures what people posted to a gallery, not what produces better images. The entire structure-selection logic rests on that confusion.

## Real levers the skill doesn't have at all

Verified from [the model page](https://developers.openai.com/api/docs/models/gpt-image-2) and [the cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide):

- **Hard size constraints**: max edge <3840px, both edges a multiple of 16, ratio ≤3:1, total pixels between 655,360 and 8,294,400. Anything above 2560×1440 is officially *"experimental."* The skill emits bare ratio strings like `"16:9"` and never validates against any of this.
- **`quality` (low/medium/high)** — the documented fix for small text and dense panels. Absent from the skill.
- **`input_fidelity` is disabled** on `gpt-image-2`. Any guidance referencing it is dead.
- Model is `gpt-image-2`, snapshot `gpt-image-2-2026-04-21`.

## A naming problem worth flagging

`_recommend_model()` returns `"nano_banana_2"` and `"gpt_image_2"` as *"Higgsfield models."* Higgsfield is an **aggregator** of 50+ third-party models — and it has its **own image model, Soul**, which the skill never mentions. The router knows two names, one of which doesn't match any vendor's actual product name. I'll confirm the correct Nano Banana designation when the Google research lands.

## What this changes about the plan

The improvement plan's P1-1 says "wire Layers 4/5 into generation." **That instruction is now unsafe as written.** Layers 4/5 need to be *corrected against primary sources* before they're wired in — otherwise you'd convert 333 lines of dead-but-harmless code into 333 lines of actively wrong guidance shipped in every prompt. That's a real change to the roadmap, and it's better to have found it now than after the commit.

I'll hold the full synthesis until the six agents report — they're covering Google/Nano Banana, competing models and which prompt techniques are model-specific vs universal, the academic benchmark evidence, production workflows, and evaluation design for a scorer that actually discriminates. When they land I'll reconcile everything into a single sourced knowledge base, flag every place the current corpus-derived folklore conflicts with vendor documentation, and give you a revised build order.

Sources: [OpenAI GPT Image prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide), [GPT Image 2 model spec](https://developers.openai.com/api/docs/models/gpt-image-2), [Higgsfield features overview](https://geo.higgsfield.ai/higgsfield-ai-features-full-guide-2026)
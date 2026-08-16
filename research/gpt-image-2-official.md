# GPT Image 2 — Official OpenAI Guidance (Complete)

> Research report 1/5 of the 2026-08-17 sweep (continues Claude session 0f5f4f48's unfinished work).
> All sources are official OpenAI properties unless marked [non-primary]. Fetched 2026-08-17.

## Verified claims table

| Claim (phrased as guidance for our engine) | Source | Confidence |
|---|---|---|
| Default prompt structure is a cohesive descriptive paragraph pairing each element with its details; structured sections (Subject, Style, Composition, Color Palette, Lighting, Mood, Additional Details) are optional, NOT required; JSON never recommended | cookbook prompting guide | High (verbatim) |
| Text to render must be in double quotes; ALL CAPS signals heading/label emphasis; spell letter-by-letter to fix garbled text; keep user's casing verbatim; avoid hyphenation within words; simple modern sans-serif fonts for infographics | cookbook | High (verbatim) |
| NO negative-prompt parameter; exclusions go inline ("without any clouds"); positive-first: "a bright, sunny sky" beats "not a cloudy sky" | cookbook §2.5 + API reference | High |
| Reference images addressed by ordinal + description ("the first image…", "using the second image as reference for the character"), NOT REFERENCE_0 tokens; up to 16 input images on /v1/images/edits | cookbook §3.6, §5 + guide | High |
| NO official word limits for text in images; official levers: quotes, simple fonts, quality=high. Excessive text warned against for cost/clutter only | cookbook (absence verified) | High |
| `quality=high` recommended for text-heavy visuals; improves text rendering accuracy; `low` for fast iteration, `high` for final | cookbook + launch announcement | High |
| Prompt max length 32,000 characters | API reference | High |
| Size: standard 1024x1024, 1536x1024, 1024x1536, `auto`, OR arbitrary W×H with both edges ÷16, ratio 1:3–3:1, total pixels 262,144–5,529,600, edge 512–3840px; >2560×1440 "experimental"; max 3840×2160 | API reference (cookbook page says 512–4096 — STALE, use API numbers) | High |
| Size heuristics: 1024x1024 social/avatars; 1024x1536 posters/stories; 1536x1024 banners/hero sections | cookbook (verbatim table) | High |
| `quality` low/medium/high/auto; `n` 1–10; `output_format` png/jpeg/webp (+compression 0–100); `background` transparent/opaque/auto (not jpeg); `moderation` low/auto | API reference | High |
| `input_fidelity` (edits): high/low; high recommended for fine-grained edits like text rendering; costs more input tokens | API ref + guide + announcement | High |
| Masks via alpha channel (transparent = edit here), PNG, same dimensions | API reference | High |
| Edits replace the ENTIRE image each call — batch multiple changes into ONE edit call, never sequential | cookbook (verbatim "Important") | High |
| Blending multiple refs: merge into one image first (external tool) OR explicitly ask to combine elements from all images | cookbook (verbatim) | High |
| Well-known logos/objects need NO reference image (world knowledge); name them instead of describing | cookbook + images-vision guide | High |
| UI mockups: lean on world knowledge of real products; wireframe-mode screenshots; specify interactive states (hover, clicked); portrait 1024x1536 or custom | cookbook | High |
| Write prompts in English for reliability; for non-Latin text IN the image: generate English first, then localize via edit (reference screenshot, "text layer fully editable", natural translations) | cookbook | High |
| Snapshots: `gpt-image-2` (latest) and `gpt-image-2-2026-04-21` (pinned) | model page | High |
| Deprecations: gpt-image-1 → 2026-10-23; gpt-image-1-mini/1.5/chatgpt-image-latest → 2026-12-01; dall-e-2/3 → 2026-05-12. gpt-image-2 is the sole target | deprecations page | High |
| Pricing: text in $5/1M, image in $8/1M, image out $30/1M; per-image ≈ $0.006 low / $0.053 med / $0.211 high @1MP; 2.0x @2K, 3.5x @4K; edits slightly more; Batch 50% off | pricing + announcement | High |
| Official common mistakes: overloading single prompt; vague descriptions; conflicting instructions ("minimalist"+"highly detailed"); unspecified aspect ratio; excessive text (cost/clutter); low-res edit inputs | cookbook §2.6 | High |
| Complex requests → break into a series of simpler prompts/images; start simple (single clean subject, simple background) and iterate | cookbook | High |

## Per-use-case official guidance (cookbook worked examples)

- **Infographic**: global style first (tone, "simple geometric style", palette), per-section specs, sans-serif fonts, break data-heavy visuals into multiple images, keep layout simple, quality=high.
- **Localization**: reference screenshot → "text layer should be fully editable" → "translate to [language] with translations that fit naturally within the design" → "match the original style".
- **Photorealistic portrait**: specify type of camera, lens, lighting (generic terms — no official endorsement of exact lens incantations).
- **Isometric art**: explicit "parallel, 45-degree" projection language.
- **Logo**: skip reference for well-known brands; include all elements (mark + text); monochrome palette for simple shapes; standard/high quality suffices.
- **Story→comic**: character reference image + panel-by-panel descriptions for consistency.
- **Slides**: reference previous deck image; name theme + slide type; consistent typography/identity.
- **Edits**: product ad (swap background, keep pose); collectible toy (state what stays identical: "same hair, expression, and outfit details"); children's book (character ref + described clothing).

## Contradictions with folklore (do NOT encode)

1. "JSON-structured prompts best" — not official (paragraph default; sections optional)
2. "Negative prompt block" — no such parameter
3. "REFERENCE_0/1 tokens" — invented; ordinals + role descriptions
4. "≤6-word headlines / ≤12-word body" — invented; no numeric limits exist
5. Strict subject→background ordering — not mandated
6. Exact lens-name incantations — only generic "camera, lens, lighting" endorsed
7. "Only 3 size presets" — arbitrary sizes official for gpt-image-2
8. "quality doesn't matter for text" — contradicted; quality=high documented for text-heavy

## Gaps

- Cookbook size numbers (512–4096) vs API reference (512–3840, 262,144–5,529,600 px) — cookbook stale; use API numbers
- No gpt-image-2 model card / safety evals published yet
- Edits-endpoint size enum may lag (lists only presets; custom sizes on edits unconfirmed)
- input_fidelity "auto" listed in cookbook, absent from API enum
- No dedicated inpainting cookbook example; outpainting = size extension + edit describing beyond-border content

Sources: developers.openai.com cookbook prompting guide · api/docs/models/gpt-image-2 · api/docs/guides/image-generation · api/reference/resources/images · api/docs/pricing · api/docs/deprecations · openai.com/index/introducing-chatgpt-images-2-0 · community.openai.com launch announcement (2026-04-21)

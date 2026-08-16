# Nano Banana (Gemini Image Models) — Official Google Guidance

> Research report 2/5 of the 2026-08-17 sweep. Google-owned sources only (ai.google.dev, blog.google, deepmind.google, cloud.google.com). Docs page last updated 2026-08-10; verified 2026-08-17.

## Model lineage (critical correction)

"Nano Banana" is an **umbrella over four models**:

| Tier | Model id | Notes |
|---|---|---|
| Nano Banana 2 Lite | `gemini-3.1-flash-lite-image` | fastest/cheapest; NOT optimized for multi-reference/multi-turn editing; 1K only; GA May 19 2026 |
| Nano Banana 2 | `gemini-3.1-flash-image` | "generalist workhorse"; 4K; reliable text rendering; best multi-reference handling; GA May 28 2026 |
| Nano Banana Pro | `gemini-3-pro-image` | premium world knowledge, localization, brand consistency; GA May 28 2026. **`-preview` id DEAD (shut down 2026-06-25)** |
| Legacy Nano Banana | `gemini-2.5-flash-image` | Aug 2025; Google "strongly recommend" migrating to 2 Lite |

**Imagen models shut down 2026-08-17 (today) — Nano Banana family is the only Google image routing.**

## Reference images (per-tier table — our "14 references" claim needs rewrite)

| Tier | Objects | Characters | Style refs |
|---|---|---|---|
| 2 Lite | up to 14 | none | none |
| 3.1 Flash | 10 | 4 | — |
| 3 Pro | 6 | 5 | 3 |
| Legacy 2.5 | "works best with up to 3 images" | | |

Headline "mix up to 14 reference images" decomposes per tier. A flat "14 refs" claim fails for character/style refs on Lite/2.5.

## Prompt style (official)

- **Prose-first CONFIRMED**: "A simple list of keywords won't cut it; you need to describe the scene narratively" (Cloud blog). No official page mentions JSON prompting at all.
- Best practices (docs, verbatim topics): "Be hyper-specific" · "Provide context and intent" ('Create a logo for a high-end, minimalist skincare brand' > 'Create a logo') · iterate conversationally · break complex scenes into steps · **semantic negative prompts** ("an empty, deserted street with no signs of traffic" instead of "no cars") · **"Control the camera: Use photographic and cinematic language"** (f/1.8, golden hour officially encouraged — contrast with OpenAI's "interpreted loosely").
- Official formulas (Cloud blog):
  - Text-to-image: `[Subject]+[Action]+[Location/context]+[Composition]+[Style]`
  - With references: `[Reference images]+[Relationship instruction]+[New scenario]`
  - Search-grounded: `[Source/Search request]+[Analytical task]+[Visual translation]`

## Validation of our current NANO_BANANA dict

| Dict claim | Verdict | Evidence |
|---|---|---|
| "Up to 14 reference images" | Under-specified | per-tier table above |
| Face-lock "maintain exact facial structure… 100% accuracy" | **REFUTED** | Official phrasing: "Ensure the woman's face and features remain completely unchanged"; marketing caps at "up to five characters"; model card admits struggles with small faces. No "100%" anywhere |
| Green-screen workflow | **REFUTED** | Zero occurrences of "green screen"/"chroma" in any official source. Real workflow: semantic masking ("change only the blue sofa… keep everything else unchanged") and conversational removal ("Remove the man from the photo") |
| Prose-first preferred | CONFIRMED | every official example/template is narrative prose |
| Framework recommendations | CONFIRMED but different content | docs template families (photorealistic scene, stickers, text-in-image, product, minimalist/negative-space, sequential art) + the three formulas above |

## Resolutions, ratios, cost

- 1K default; 2K/4K on all Gemini 3 models; 512px on 3.1 Flash only; 2 Lite 1K-only; `image_size` "K" uppercase or rejected.
- Aspect ratios (all): 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9; 3.1 Flash adds 1:4, 4:1, 1:8, 8:1. Default output matches input size or 1:1.
- Output tokens scale with resolution — Pro: $0.134 (1K/2K) → $0.24 (4K); 3.1 Flash: ≈$0.045/$0.067/$0.101/$0.151 (0.5K/1K/2K/4K); thinking tokens billed; interim thought-images not charged.

## Editing capabilities (official)

Add/remove/modify elements · semantic-mask inpainting ("change only the blue sofa") · style transfer · multi-image blending · sketch-to-photo · multi-turn editing via `previous_interaction_id` · interleaved text+image (Pro) · video-to-image and Image-Search grounding (3.1 Flash) · thinking_level minimal/high (3.1 Flash).

## Documented limitations (official admissions)

- "won't always follow the exact number of image outputs the user explicitly asks for" — no parameter forces N
- Text-in-image: "Gemini works best if you first generate the text and then ask for an image with the text"
- Best languages: EN, ar-EG, de-DE, es-MX, fr-FR, hi-IN, id-ID, it-IT, ja-JP, ko-KR, pt-BR, ru-RU, ua-UA, vi-VN, zh-CN (Arabic = Egyptian variant listed)
- Model card: struggles with small faces, accurate spelling, fine details; blending may produce artifacts; character consistency "may not always get it right"; factual outputs "always verify"

## Official example prompts worth mimicking

- Photorealistic template: "A photorealistic [type of shot] of a [subject] in a [setting]. [Light]. Shot from a [camera angle] with a [lens]. Aspect ratio 16:9."
- Minimalist: "A minimalist composition featuring a single, delicate red maple leaf positioned in the bottom-right… vast off-white canvas… negative space for text. Soft, diffused lighting from the top left. Square image."
- E-comm blending: "Take the blue floral dress from the first image and let the woman from the second image wear it." (references by ordinal)
- Preservation: "Add the logo from the second image onto her black t-shirt. Ensure the woman's face and features remain completely unchanged."
- Semantic edit: "…change only the blue sofa to be a vintage, brown leather chesterfield sofa. Keep the rest…unchanged."
- Step-by-step: "First, create a background of a serene, misty forest at dawn. Then, in the foreground, add a moss-covered ancient stone altar. Finally, place a single, glowing sword on top."
- Reframe with lock: "change aspect ratio to 1:1 by reducing background. The character remains exactly locked in its current position."
- Group consistency: "Put these five people and this dog into a single image, they should fit into a stunning award-winning shot."
- Consistency instruction (NB2 launch): "It is strictly important to keep identity consistent of all the 14 characters and items." / "Generate 6 images one at a time."
- Product text rendering: "For the top line, the word 'GLOW' in a flowing, elegant Brush Script font. For the middle line, '10% OFF' in a heavy, blocky Impact font…" (per-line font specification works)

## Gaps

- Which Gemini snapshot Higgsfield's "Nano Banana" routes to is undocumented — determines which reference-count row applies [non-primary]
- "Floating astronaut"/"coffee splash" world-model demos: no citable official text; treat as unverifiable
- No official prompt-length guidance (token ceilings: 131,072 in for 3.1 Flash; 65,536 for 3 Pro)
- Counting/spatial limits not officially named for Gemini 3 models (absence ≠ capability)

Sources: ai.google.dev/gemini-api/docs/image-generation · /docs/changelog · /docs/pricing · blog.google (nano-banana-pro, nano-banana-2, prompting-tips-nano-banana-pro) · cloud.google.com ultimate prompting guide · deepmind.google/models/gemini-image/pro · developers.googleblog.com

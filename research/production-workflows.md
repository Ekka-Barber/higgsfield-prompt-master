# Production AI-Image Workflows (2025–2026)

> Research report 5/5 of the 2026-08-17 sweep. Source quality marked (official case study / practitioner / vendor marketing).

## Workflow patterns by domain

### E-commerce / product photography — the dominant pattern
**One anchor photo + locked "style system" + parameterized rollout** (NOT per-SKU prompting):
1. ONE strong anchor image per SKU (clean lighting, neutral background, capture text/reflective parts).
2. Lock a visual system: Photography Style · Composition · Fashion Model (identity continuity) · Background (hex value / scene ref).
3. Save as team-shared **"Recipe"** (intent/style/composition/model/background/count/AR/resolution/format) — explicitly replaces "per-SKU re-briefing, prompt-history archaeology, tribal knowledge" [Nightjar, vendor but concrete].
4. Roll out: hex recolors (20 SKUs × 5 colors on one setup), 4-angle sets, lifestyle scenes, channel crops (1:1 PDP, 4:5 IG, 9:16 Stories, 16:9 banner), edit board with @image refs.
5. QA: spot-check every Nth image against checklist (lighting consistency, identity, proportions, label legibility, background hue), regenerate on the same recipe.
- **"No-prompt" hybrid** [Scene4]: MJ for scene/mood only; compositing tool rebuilds scene around the real product photo. Pure-gen AI never sells the real product.
- Hero campaigns / regulated categories (food, beauty claims, medical) / large furniture stay traditional — "shoot the hero once, expand via AI".
- Practitioner consistency rule: keep six elements identical across a set, vary only the subject.

### UI/UX mockups
- Practitioner pattern: ChatGPT WRITES a numbered-section natural-language spec (status bar / header / carousel / nav / filters / list, with labels-fonts-colors per section), separate chat generates. Verdict: concept/PM communication tool, not production design.
- Google Stitch: low-mid fidelity single screens; weak edit adherence; standout = Copy-to-Figma preserving nested layers.
- **No evidence of JSON-layout→image as a standard pro technique.** Structured approaches = numbered-section prose specs, or code-gen UI tools (Stitch, Figma First Draft, Uizard).

### Marketing / brand campaigns [Superside case studies, self-reported]
- Custom brand models trained on 10–15 refs (logos, product, guidelines) delivered **as Figma plugins** (Sailun, Maven, Sisense).
- D2L: 114 on-brand ad variations via MJ, 70% design-time cut, variants feed A/B testing. Independence Pet: 750+ assets in 11.5h.
- H&M digital twins: consent + compensation + watermarking. Coca-Cola: human-curated to billboards.
- Art directors final-say; humans catch artifacts/bias/copyright; AI-disclosure policies.
- Brand style as reusable saved object: Recraft Style Remixing (5 styles blended, weight sliders, team-shared); FLUX finetuning APIs; "prompt style guide" locking lighting/palette/framing/style.

## Template & versioning conventions

- Community formula: [Subject/Action]→[Environment]→[Mood]→[Lighting]→[Style/Medium]→[Camera]→[Params]. MJ officially pushes back ("short and simple prompts").
- Slot-based templates exist as products: Notion prompt generators with fill-in fields; Recipes = production-grade saved templates.
- **Versioning/A-B is mature for LLM prompts (PromptHub Git-style, PromptLayer variables) and IMMATURE for image prompts** — image "A/B" happens at asset level, not prompt level. Genuine gap our engine can fill.

## Tooling landscape

Prompt management (LLM-oriented): PromptHub, Langfuse, PromptLayer, Braintrust — none image-aware (no seed/model/ref tracking). DIY: Notion databases + complaint threads ("prompts divorced from the images/params that produced them"). Embedded: Superside Figma plugins, Nightjar recipes + semantic search, Recraft styles, Krea realtime.

## Common failure modes + workarounds

1. **Text/label rendering** (most-cited): garbled labels → add text in post, or route text-critical assets to Ideogram/gpt-image ("add text in post" flag).
2. **Consistency drift across batches** → locked style systems, recipes, srefs, brand LoRAs.
3. **Product fidelity** (logos/labels mutate) → "get close, finish packaging in Photoshop".
4. **Hands/anatomy** → explicit QA checklist item.
5. **Weak edit adherence** → iteration loops; budget 3–5× cost.
6. **Scale QA collapse** (600 images on a wrong setup) → checklist sampling.
7. **Cost unpredictability on Higgsfield** [competitor review, caution]: credits 6→70/output by model; iteration 3–5× base; consistency breaks at profile/overhead/dramatic angles; avatar identity not persistent across Marketing Studio sessions.

## Higgsfield documented workflow (2026)

- **Soul ID**: persistent identity from 20+ photos (up to 80; 940px+; varied angles; no sunglasses) — train 3–5 min, then apply across image AND video models.
- **Popcorn**: storyboard generator with frame-to-frame consistency, visual memory of faces/props/lighting, first-frame style lock; exports to video models.
- **Cinema Studio**: camera moves (dolly/orbit/tracking) defined IN the prompt — cinematography vocabulary is the differentiator, steep learning curve.
- **Marketing Studio**: product URL → multi-format ads (identity doesn't persist across sessions).
- Net: Higgsfield is **identity/camera-first and prompt-light** — prompts routed through it should be short, cinematography-flavored, paired with trained Soul IDs/style presets.

## Features our engine should have (prioritized)

1. **Reference/identity-aware generation** (highest): accept reference context (what refs exist, what type), complement conditioning instead of re-describing; know when to emit almost no text.
2. **Slot templates with a locked style block**: reusable versioned "style block"/brand profile constant across a batch; per-channel AR expansion from one master prompt.
3. **Provenance metadata on every prompt**: text + model + params + seed + ref IDs + style-block version (the #1 stated management pain; no tool does it for images).
4. **Failure-mode routing**: tag intents (critical text? close-up hands? product label?) → route/annotate (text-critical → Ideogram/gpt-image; "add text in post" flags).
5. **Batch-consistency contract**: identical style/params across a set; vary ONLY the subject slot.
6. **Higgsfield parameter mapping**: camera-move vocabulary, preset selection, Soul ID linkage, credit-cost awareness.
7. **QA checklist hooks** attached to generated sets.
8. **A/B variant generation with labels + prompt-level diffs** (fills the image-side versioning gap).
9. **Compliance flags**: disclosure/labeling, consent/licensing for likeness, licensed-data preference for regulated categories.

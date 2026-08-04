# GPT Image 2 Prompting Techniques

Condensed from [awesome-gpt-image-2](https://github.com/YouMind-OpenLab/awesome-gpt-image-2) (14,394+ prompts, 9.0k stars — crossed 9K milestone Aug 2026, updated daily) plus analysis of the full youmind.com gallery corpus via scraping (see `references/gpt-image2-prompt-database.md`).

**Important corpus finding:** The curated README (120 prompts, capped by GitHub content-length limits) skews toward flat photography prompts (83% flat, 3% JSON). The actual full corpus is **54% JSON-structured** and dominated by UI/UX designs. Weight JSON structure as the primary pattern, not the exception.

## Three Prompt Structures

### Structure A: JSON Object (PRIMARY — 54% of corpus)
GPT Image 2 parses JSON with high fidelity. Keys: `type`, `subject`, `style`, `background`, `header`, `layout` (with `centerpiece`, `left_section`, `right_section`, `footer`), `callout_labels`. Best for: UI mockups, exploded diagrams, infographics, posters, complex multi-zone layouts. This is the dominant structure in the full corpus.

### Structure B: Flat Paragraph (46% of corpus)
Single-subject, single-composition. `[SUBJECT] [STYLE] [TECHNICAL] [COMPOSITION] [BACKGROUND] [DETAILS] [CONSTRAINTS]`. Used for portraits, cinematic shots, simple illustrations.

### Structure C: Goal + Canvas + Sections (niche)
Complex multi-zone designs. Define `Goal:`, `Canvas:`, named sections with element counts, closing `Visual style:` paragraph as style guard. Used for dashboards and structured layouts.

## Key Techniques

- **Exact Counting**: "exactly 4 cards", "exactly 8 rows" — prevents arbitrary additions
- **Spatial Anchoring**: "top-left header", "bottom-right product card" — positions by name
- **Visual Style Guard**: Closing paragraph summarizing full aesthetic — prevents drift
- **Face Lock**: "maintain exact facial structure from reference with 100% accuracy, preserve micro-details, no beautification"
- **Negative Prompts**: "negative prompt: distorted face, plastic skin, beauty filter effect"
- **Cross-Reference Mapping**: "REFERENCE_0 as identity, REFERENCE_1 as layout" — number references explicitly
- **Color Science**: "ultra-clean cinematic color grading with high color separation, natural saturation, deep contrast, HDR dynamic range"
- **Subsurface Scattering**: "soft natural skin with visible pores, smooth tonal transitions, subtle subsurface scattering"

## Featured Patterns (top community outputs)

1. **Exploded Product Diagram** — JSON with `centerpiece: vertically stacked exploded view` + `callout_labels` split left/right
2. **Broadcast UI Mockup** — Goal/Canvas/Sections: `top_header`, `mid_left`, `bottom_left_chat`, `bottom_right_product_card`, `bottom_bar`
3. **Illustrated Map** — JSON with `sections[]` array of landmarks/food spots + `legend` + `centerpiece` mascot
4. **Recipe Card** — Goal/Canvas with `Info badges`, `Ingredients section` (exact counts + icons), `Steps` (numbered badge grid)
5. **Before/After** — Cross-reference: "Using REFERENCE_1 as current, REFERENCE_0 as identity. Keep [elements] unchanged. Only correction is [fix]."
6. **Cinematic Action** — Labeled sections: Shot Type / Subject + Face Lock / Setting / Action / Attire / Lighting & Color / Technical / negative prompt

## Camera Spec Depth (from top cinematic prompts)

- "Shot on Panavision anamorphic lens (70mm) with noticeable horizontal lens flare and heavy cinematic grain"
- "full-frame Sony A7R, 24mm wide-angle to exaggerate height and perspective"
- "Shallow DoF, rendering background in beautifully blurred moody bokeh"
- "Sharp foreground subject with slight depth falloff into the city below"

## Auto-Update Monitoring

Daily watchdog (`gpt-image2-repo-watchdog.py`, cron 26c2c68477b8) checks the repo for new commits and prompt count changes. Silent when no changes. When alerted, reply "review updates" to analyze new techniques and patch this skill.

Weekly system report (`ff3b28988559`) also shows the repo under "Remote Repos Monitored" section with commit diff and prompt count.

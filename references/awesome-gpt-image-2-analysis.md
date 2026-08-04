# Awesome GPT Image 2 Prompt Library Analysis

**Source:** https://github.com/YouMind-OpenLab/awesome-gpt-image-2
**Gallery:** https://youmind.com/gpt-image-2-prompts
**Stats (as of 2026-08-02):** 14,394 prompts, 9.0k stars (crossed 9K milestone Aug 1), 833 forks (growing ~75-850 prompts and ~200-300 stars per week)
**Update cadence:** Every 4 hours via GitHub Actions (bot auto-commits `docs: auto-update README [skip ci]` — these are noise from CMS syncs, not real technique changes)
**License:** CC BY 4.0
**Public README:** 120 curated prompts with full text (capped by GitHub content-length limits); remaining 13,000+ behind private Payload CMS but **fully accessible** via youmind.com gallery pages at predictable URLs: `https://youmind.com/prompts/{any-slug}-{ID}`. GPT Image 2 prompts are at IDs ~13440–26917. See `references/gpt-image2-prompt-database.md` for scraping approach and scripts.

## youmind.com Gallery Structure (discovered via investigation)

- **URL pattern:** `/prompts/{slug}-{numericID}` — the slug is ignored; only the numeric ID resolves the prompt
- **ID ranges by model:** IDs 101-1000 = Nano Banana Pro; 1000-5000 = Seedream 4.5; 5000-13400 = Nano Banana Pro; 13440-26917 = GPT Image 2 (our target); 25000+ = some claude-fable mixed in
- **Prompt text location:** Rendered in DOM (Next.js RSC flight data). The `.whitespace-pre-wrap` CSS selector contains the full prompt text. Server-side RSC chunks (T-chunks) are unreliable for extraction — use CloakBrowser CDP DOM extraction instead.
- **Meta tags reliable via curl:** `<title>` contains prompt name + model + category. `<meta name="keywords">` contains category taxonomy. These extract reliably without a browser.

## Key Prompting Techniques Discovered

### 1. JSON-Structured Prompts (top featured technique)
GPT Image 2 parses JSON objects with high fidelity. Keys like `type`, `subject`, `style`, `background`, `layout`, `header`, `footer` map directly to generated elements. Best for posters, UI mockups, exploded diagrams, infographics.

### 2. Goal + Canvas + Sections Pattern
```
Goal: [One sentence]
Canvas: [Dimensions, background]
[Section]: [Elements with exact counts]
Visual style: [Closing style guard paragraph]
```

### 3. Exact Counting
Always specify element counts: "exactly 4 image cards", "exactly 8 rows". Prevents GPT Image 2 from adding/removing elements.

### 4. Spatial Anchoring
Name positions explicitly: "top-left header", "bottom-right product card", "arranged in two columns and three rows".

### 5. Visual Style Guard
End complex prompts with a closing paragraph summarizing the complete aesthetic. Prevents style drift across multi-element designs.

### 6. Face Lock / Identity Preservation
```
face lock: maintain exact facial structure, proportions, skin tone, hairstyle,
and identity from reference with 100% accuracy. Preserve micro-details and
natural imperfections, no beautification.
```

### 7. Cross-Reference Mapping
Number references explicitly: "Using REFERENCE_1 as the current thumbnail and REFERENCE_0 as the identity reference"

### 8. Negative Prompts
For photorealistic work: `negative prompt: distorted face, changed identity, altered hairstyle, flat lighting, plastic skin, beauty filter effect`

### 9. Detailed Color Science
`color science: ultra-clean cinematic color grading with high color separation, natural saturation, deep contrast, HDR dynamic range`

### 10. Layered Composition
Break UI mockups into named layers: `top_header → mid_left → bottom_left → bottom_right → bottom_bar`. Describe each independently.

## Featured Prompt Patterns (Reusable Templates)

### Exploded Product Diagram
```json
{
  "type": "exploded view product diagram poster",
  "subject": "[product]",
  "style": "clean high-tech 3D render, studio lighting, glowing accents",
  "layout": {
    "centerpiece": "vertically stacked exploded view showing [N] layers",
    "callout_labels": {
      "count": [N],
      "left_side": ["[feature]: [desc]"],
      "right_side": ["[feature]: [desc]"]
    }
  }
}
```

### Broadcast UI Mockup
```
Goal: Create a [clean] screenshot showing [purpose].
Canvas: [dimensions], [background], minimal modern UI.
Top [header]: [exact element counts]
Main [content]: [exact counts]
Bottom [bar]: [exact element counts]
Visual style: [complete aesthetic]
```

### Before/After + Face Correction
```
Using REFERENCE_1 as the current [design] and REFERENCE_0 as the identity reference,
regenerate with the same [layout], but [specific change].
Keep [preserved elements] unchanged. Preserve exactly [N] visible text areas.
Do not redesign; the only correction is [fix].
```

### Cinematic Action Portrait
```
[Shot type]: [Wide Cinematic Medium-Full Shot]
[Subject with face lock]: matching exact reference...
[Setting & Atmosphere]: [detailed environment]
[Lighting & Color]: [specific light sources, directions]
[Technical]: [camera, lens, film stock, grain, DoF]
negative prompt: [avoid list]
```

## Monitoring
Daily watchdog cron job (11am, job `26c2c68477b8`) checks for new commits and prompt count changes. Silent when no changes. Weekly system report also tracks this repo under "Remote Repos Monitored".

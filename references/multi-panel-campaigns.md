# Multi-Panel Campaign Grids

> **Discovered:** August 2026 corpus harvest
> **Prevalence:** Growing rapidly (2% of new batch, but highest complexity)
> **Status:** Emerging premium pattern for marketing campaigns

## Overview

A new high-complexity pattern has emerged: **multi-panel campaign grids** — single images that contain multiple panels showing different products, characters, or scenes in a unified brand campaign layout.

These prompts are the longest and most structurally complex in the corpus (5,000-6,500 chars), combining:
- Exact panel division specifications (3×2, 4×1, 5×1, 2×2 grids)
- Per-panel content descriptions
- Character consistency requirements across panels
- Unified brand/color/lighting rules that span all panels
- Typography and text placement per panel

## Anatomy of a multi-panel campaign prompt

```
Goal: Create a [N]-panel [TYPE] campaign for [BRAND], designed as a 
[GRID_STRUCTURE]...

Canvas: A [RATIO] divided into exactly [N] equal [SHAPE] panels in a 
[COLS]-column by [ROWS]-row grid, with thin white borders between panels.

Panel 1: [DETAILED DESCRIPTION OF FIRST PANEL]
Panel 2: [DETAILED DESCRIPTION OF SECOND PANEL]
...

Character Rules: The same [CHARACTER TYPE] appears in each panel but 
with [WHAT CHANGES]. Maintain [CONSISTENCY REQUIREMENTS].

Color Palette: [BRAND COLORS applied across all panels]
Typography: [FONT and TEXT treatment per panel]
Lighting: [UNIFIED LIGHTING RULE]
```

## Real examples from corpus

### Example 1: 4-panel athletic campaign (ID: 28598, 6442 chars)
> "Create the seventh poster in a unified campaign series for Lululemon Athletica, 
> designed as a bold four-panel editorial sports poster with four different athlete 
> characters, four distinct movement themes..."

### Example 2: 6-panel bedtime stages (ID: 26978)
> "Create a cozy 6-panel lifestyle photo collage showing the stages of trying to 
> fall asleep on a weekend, featuring the same young child in each panel."
> Canvas: "A 4:3 horizontal collage divided into exactly 6 equal rectangular panels 
> in a 3-column by 2-row grid"

### Example 3: 5-panel beverage campaign (ID: 28496, 5593 chars)
> "Create an ultra-premium horizontal 5-panel campaign system for Fanta Fruit 
> Flavored Soda, reimagined as a trendy festive promotional series..."

## Key techniques within multi-panel prompts

1. **Grid Specification** — Explicit column × row structure ("3-column by 2-row grid")
2. **Per-Panel Storytelling** — Each panel gets its own mini-scene while maintaining overall coherence
3. **Character Lock** — "same character/athlete/model in each panel" — using GPT Image 2's face consistency
4. **Brand Continuity** — Consistent color palette, typography, and lighting across all panels
5. **Series Numbering** — "the seventh poster in a series" — implies sequential generation with consistent rules

## When to use this pattern

- Brand marketing campaigns (multiple products in one image)
- Before/after comparison grids
- Step-by-step tutorial visualizations
- Storyboard sequences
- Product line showcases (different flavors/colors/variants)
- Social media carousel-style content compressed into one image

## Impact on the skill

When a user requests a campaign, brand showcase, or multi-product image, the generator should use this pattern. The complexity is high but the results are premium — these are the most impressive GPT Image 2 outputs in the corpus.

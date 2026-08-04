# Branded Content — Research & Design Patterns

Session-derived patterns for generating branded marketing images for real businesses.

---

## Business Research Workflow

When given a Google Maps link or business URL:

1. **Navigate to the Maps listing** via `browser_navigate` (Camofox preferred for session persistence)
2. **Extract from the listing:**
   - Business name (Arabic + English if both exist)
   - Category (espresso bar, restaurant, salon, etc.)
   - Rating + review count (confirms legitimacy)
   - Price tier
   - Top review topics (review topic tags)
   - Owner response style and emoji (reveals brand personality)
3. **Browse photos** — click "Vibe", "By owner" tabs to see branded interiors, cups, signage
4. **Use `browser_vision`** to analyze brand colors from interior/branding photos
5. **Compile brand DNA** = primary color + secondary colors + aesthetic keywords + personality

### Brand DNA Extraction Checklist

| Signal | Where to find it | What it tells you |
|--------|-----------------|-------------------|
| Business name | Maps heading | Brand identity, language |
| Primary color | Interior photos, logo, owner responses | Core palette |
| Secondary colors | Furniture, packaging, decor | Supporting palette |
| Aesthetic keywords | Review topics (quietness, cozy, modern, vintage) | Design style |
| Price tier | Maps price range | Luxury vs casual vs budget |
| Owner personality | Response language and emoji | Brand voice |
| Signature products | Review topic tags | Hero items to feature |

---

## Prompt Templates for Branded Content

### Instagram Story — Holiday Invitation (Arabic)

```
Instagram story invitation card, full vertical 9:16. Modern minimalist design in [PRIMARY COLOR] and [SECONDARY COLOR] color palette. [BRAND NAME] logo placed at top center.

Large elegant Arabic typography headline: "[ARABIC GREETING]" in modern Arabic font, centered. Below it, smaller warm text: "[WELCOME PHRASE]".

Illustrated hospitality spread (ضيافة) arranged elegantly at bottom half: [ITEM 1], [ITEM 2], [ITEM 3], [ITEM 4]. Each item labeled with its name in Arabic. Clean modern illustration style, no religious symbols, no Islamic gestures, no crescents, no mosques.

Color scheme strictly [BRAND PRIMARY] + white + warm beige. Generous whitespace. Contemporary aesthetic. Pixel-perfect Arabic typography. Commercial-grade illustration.
```

### Key Constraints for Arabic Holiday Content

- **No Islamic gestures/symbols** is a common and strict constraint — not even subtle ones
- "Modern" means: clean lines, sans-serif fonts, geometric layouts, minimal decoration
- ضيافة (hospitality) = elegant food arrangement, not religious scene
- Brand colors override any seasonal color conventions (e.g., don't default to green for Eid if brand is blue)
- Use the brand's actual aesthetic (cozy/modern/luxury) to match the illustration style

---

## Case: bluecups (Tabuk, Saudi Arabia)

- **Business:** bluecups — espresso bar in Tabuk
- **Brand colors:** Light blue/teal (primary), white, natural wood/beige
- **Aesthetic:** Modern minimalist, clean, bright, airy
- **Personality:** Cozy, welcoming, 💙 emoji in all responses
- **Price tier:** SAR 20–40 (mid-range specialty coffee)
- **Known for:** Coffee of the day (Indonesian single origin), Yemeni espresso, quiet atmosphere
- **Google Maps:** https://maps.app.goo.gl/ufA3MVCWQkAhixo8A

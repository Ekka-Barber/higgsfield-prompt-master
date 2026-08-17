---
name: hf-menu
description: >
  Restaurant, café and hospitality visuals — menu boards, dish hero shots, menu
  photography and food styling. Arabic-first, Saudi/Gulf hospitality context.
  Use for /hf-menu, "منيو", "قائمة طعام", "مطعم", "كافيه", "طبق", "menu",
  "restaurant", "cafe", "food photography", "dish shot".
---

# /hf-menu — hospitality, menus & food

Two different jobs live here. Decide which one first, because they route to
different models.

| Job | What it is | Model |
|---|---|---|
| **A. Dish / food photography** | one plate, styled, no text | Nano Banana Pro |
| **B. Menu layout** | a board or card with many text items | see §Menu layouts |

## A. Dish photography

Food is lighting and texture before it is anything else.

**The levers that actually change the image:**
- **Light:** soft directional window light from behind-left at 45° (the
  restaurant-photography default); hard light only for drinks and ice.
- **Angle:** 45° for plated mains, straight-down 90° for flat lays and spreads,
  eye-level for burgers, layered drinks and anything with height.
- **Freshness cues:** steam, condensation, a glisten of oil, crumb scatter,
  herb flecks, a torn edge showing interior texture.
- **Surface:** dark stone / walnut / brushed steel / linen.
- **Depth:** shallow focus with the front third of the plate sharp.

**Gulf & Saudi dishes worth naming precisely:** kabsa (كبسة) on a wide
communal platter, mandi, mutabbaq, jareesh, saleeg, harees, shawarma, mutabbal,
Saudi (qahwa) coffee in a dallah with finjan cups and dates, kunafa, luqaimat
drizzled with dibs, karak chai. Naming the dish beats "Middle Eastern food".

**Serving context:** communal platter dining, dallah + finjan for qahwa,
sufra floor spread, majlis seating.

## B. Menu layouts — read this before promising one

A full menu is **dozens of short text strings**. That is the worst case for AI
text rendering, and worse still in Arabic.

**Say this plainly:** for a real menu that customers will read, generate the
*design* — background, framing, decorative system, empty text zones — and set
the actual items in Illustrator/Figma/Canva with a proper Arabic font. This is
what working designers do, and it is the only way prices and dish names are
guaranteed correct.

What AI *is* good for here:
- A menu board **look** with 4–8 items maximum
- A single **feature panel** ("today's special")
- **Background art / texture** for a menu you will typeset
- A **hero dish** photo to sit inside a menu you build

If they insist on a full rendered menu: cap it at ~6 items, keep every string
2–4 words, and warn that prices need proofreading.

## Arabic menu specifics

- **Numerals: always ask.** Saudi commercial menus overwhelmingly use Western
  `0-9` for prices; heritage/traditional concepts sometimes use `٠-٩`.
  A menu with mixed systems reads as an error.
- **Currency:** "ر.س" or "SAR" or the ﷼ symbol — pick one and state it.
- **Bilingual is the norm** in Saudi hospitality: Arabic dish name primary,
  English beneath, both right-aligned, Arabic ~115% of the Latin size, on
  separate lines — never interleaved.
- **Register:** premium concepts lean MSA (فصحى); casual/street concepts lean
  Gulf (خليجي) and playful.
- Dish names in **Naskh** or a modern sans (Cairo/Tajawal); a calligraphic
  **Diwani** or **Thuluth** header over a clean body is a strong combination.

## Grill

1. Dish photo, menu board, or background art for typesetting?
2. Exact dish names / items (verbatim, Arabic + English if bilingual)?
3. Concept register — premium, casual, traditional heritage, modern specialty?
4. Prices shown? If so, numeral system and currency mark.

Follow-up: is there an existing brand palette or an interior look to match?

## Routing

- Dish photography, any Arabic text → **Nano Banana Pro** (`gemini-3-pro-image`)
- English-only menu board with many exact items → **GPT Image 2**
  (`gpt-image-2`), `quality: high`, and still cap the item count

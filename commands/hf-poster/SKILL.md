---
name: hf-poster
description: >
  Posters, flyers, banners, signage and event announcements — Arabic-first, with
  print-safe sizing and RTL typographic hierarchy. Use for /hf-poster, "بوستر",
  "ملصق", "فلاير", "لوحة", "إعلان", "poster", "flyer", "banner", "signage",
  "event announcement".
---

# /hf-poster — posters, flyers, signage

Posters are a **typographic hierarchy** problem before they are an image
problem. Get the levels right and the rest follows.

Read `../_shared/arabic-rules.md` and `../_shared/model-routing.md`.
Also read `../_shared/typography.md` — font names are style hints,
descriptors are the real control.

## The hierarchy — name every level explicitly

A poster prompt that says "with text" produces mush. Specify:

1. **Hero line** — 2–5 Arabic words. The thing read from across the room.
2. **Subhead** — up to ~8 words. Context.
3. **Detail block** — date, time, venue. Short discrete lines, never a paragraph.
4. **Footer** — logo, handle, sponsor lockup.

> "Typographic hierarchy: hero line '...' dominant at the top-right; subhead
> beneath at roughly one third the size; a short detail block of three separate
> lines; sponsor logos in a single row along the bottom edge."

## RTL poster layout

The entry point is **top-right**. Hero line right-aligned. Date/venue block
right-aligned. Sponsor row reads right to left. Any arrow or "then" sequence
flows right to left.

## Sizes

| Use | Ratio | Notes |
|---|---|---|
| A-series print (A3/A4/A2) | ~1:1.414 | closest valid: `1024x1440` |
| Cinema / event one-sheet | 2:3 | `1024x1536` |
| Roll-up / pull-up banner | ~1:2.5 | exceeds GPT Image 2's 3:1 only past 1:3 — check |
| Social flyer | 4:5 | `1080x1350` |
| Wide street banner | 21:9 | Nano Banana Pro supports `21:9` natively |

GPT Image 2: validate with `renderers.validate_gpt_image_2_size(w, h)` — edges
multiple of 16, ratio ≤ 3:1, 655,360–8,294,400 px.

**Print caveat:** these models output screen-resolution RGB. For real print,
generate the composition and rebuild at scale in a layout tool, or upscale and
set live type. Say so when the user mentions printing.

## Arabic specifics

- Hero line in **Kufi** for modern/geometric, **Thuluth** or **Diwani** for
  ceremonial and prestige, **Ruqʿah** for street-casual.
- Detail blocks: short separate lines beat one wrapped paragraph, every time.
- Dates: confirm Hijri (هـ) vs Gregorian (م), and the numeral system.
- Long body copy → text-free plate + real typography.

## Seasonal Saudi/Gulf vocabulary

- **Ramadan:** crescent, fanoos lanterns, warm gold on deep green/navy, geometric
  interlace, night sky.
- **Eid:** brighter, celebratory, sweets, family, gifting.
- **Saudi National Day (Sept 23):** green/white, palm & swords motif — but do
  **not** render the flag itself (shahada).
- **Founding Day (Feb 22):** Najdi heritage, mud-brick, historical dress,
  earthen palette.

## Grill

1. Verbatim hero line + any date/venue detail?
2. Print or screen — and what size?
3. Photographic plate or flat graphic/illustration?
4. Occasion (Ramadan / opening / concert / sale)?

Follow-up: is there a logo or brand palette to lock to?

## Routing

Arabic text → **Nano Banana Pro**. Dense English event poster with many exact
elements → **GPT Image 2**, `quality: high`.

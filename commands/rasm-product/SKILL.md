---
name: rasm-product
description: >
  Product and e-commerce imagery — packshots, hero shots, lifestyle context and
  marketplace-compliant listing images. Arabic-first for packaging and labels.
  Use for /rasm-product, "صورة منتج", "تصوير منتجات", "باكشوت", "متجر",
  "product shot", "packshot", "ecommerce image", "product photography".
---

# /rasm-product — product & e-commerce

Three distinct shots. Ask which one; they are not interchangeable.

| Shot | Purpose | Background |
|---|---|---|
| **Packshot** | marketplace listing | pure white, no props |
| **Hero** | ads, banners, launch | styled, dramatic light |
| **Lifestyle** | social, context, story | in-use, real environment |

## Packshot — marketplace rules

Listing images are governed by platform rules, not taste:

- **Pure white background** (`#FFFFFF`), product filling ~85% of the frame
- **Square 1:1** — `1024x1024` or `2048x2048`
- No props, no text, no watermarks, no logos beyond the product's own
- Even, shadowless or soft-contact-shadow lighting
- Full product visible, nothing cropped

> "Centred product on a pure white seamless background, filling about 85% of
> the frame, even soft studio lighting, subtle contact shadow beneath, no props
> and no added text, colour-accurate materials."

Amazon/Noon/marketplace listings additionally want the *main* image free of any
added graphics — secondary images can carry callouts.

## Hero shot — the levers

- **Light:** single large softbox for clean premium; hard rim light for
  contrast and edge definition; gradient sweep behind for depth.
- **Surface:** polished stone, brushed metal, sand, water, seamless colour.
- **Angle:** three-quarter for volume; straight-on for symmetry and packaging
  faces; low angle for stature.
- **Material accuracy is the whole game** — say the finish explicitly: matte
  soft-touch, high-gloss lacquer, brushed aluminium, frosted glass, kraft board.

## Lifestyle

Name the environment, the light, and the human action — not just "in use".
For Saudi/Gulf context: majlis interior, desert golden hour, modern Riyadh
apartment, coastal Red Sea light, café with mashrabiya screens.

Modesty defaults apply for the Gulf market unless specified otherwise.

## Arabic on packaging & labels

This is the hard part. Arabic on a curved bottle or a folded box is text
rendering *plus* perspective distortion — the highest failure mode combination.

- Keep label copy to **1–3 Arabic words**.
- Flat faces render far better than curved ones. Prefer a box front over a
  cylinder if you have the choice.
- All four Arabic clauses still apply (verbatim, shaping, RTL, no tashkeel).
- **For real packaging artwork:** generate the product form and setting, then
  apply the label design as a flat file in a mockup tool. Say so.
- Saudi retail packaging is commonly **bilingual** — Arabic primary, English
  secondary, both on the same face.

## Grill

1. Packshot, hero, or lifestyle?
2. Product category and exact material/finish?
3. Any Arabic text on the packaging — verbatim?
4. Marketplace with rules (Amazon, Noon, Salla, Zid) or free creative?

Follow-up: single product or a range that must look consistent? A range means
locking one lighting setup and varying only the product.

## Routing

- Packaging with Arabic text → **Nano Banana Pro** (`gemini-3-pro-image`)
- Clean white packshot, no text → either; **GPT Image 2** holds geometry tighter
- Placing a real product photo into a new scene → **Nano Banana Pro**, using
  the reference by ordinal: *"the product in the first image, unchanged"*

# Typography & Fonts — what these models actually respond to

Evidence tiers: **[VENDOR]** official docs · **[TEST]** documented testing ·
**[PAPER]** published research · **[CRAFT]** design practice.

---

## 0. The finding that matters most

**Naming a font does not set that font.** Research on typographic control finds
that prompts describing typographic intent are *"often ignored or only weakly
reflected"*, leaving users on trial-and-error **[PAPER]**. Practitioner guidance
for GPT Image 2 says the same thing plainly: exact names like Helvetica or Inter
work as **style hints, not precise specifications** **[TEST]**.

So the control surface is **descriptors**, not names:

| Instead of | Write |
|---|---|
| `Futura` | `geometric sans-serif inspired by Futura` |
| `Cairo` | `modern Arabic sans-serif, clean and geometric, Cairo style` |
| `use Thuluth font` | `Thuluth calligraphic script, tall vertical strokes, ornate` |

A name *appended to* a descriptor helps. A name *alone* is a coin flip.

**Arabic exception worth knowing:** script-style names — **Kufi, Naskh,
Thuluth, Diwani, Ruqʿah, Nastaliq** — are far more reliable than font names,
because they name a whole *script category* densely represented in training
data, not one foundry's file **[CRAFT]**. Lead with the script style.

---

## 1. The six ways to describe type [TEST]

Combine two or three. Method 1 is mandatory; the rest add flavour.

1. **Functional** — `bold geometric sans-serif`, `condensed sans with tight tracking`
2. **Style / emotion** — `minimalist Bauhaus sans-serif`, `Art Deco display with metallic strokes`
3. **Era / scenario** — `1970s vinyl-cover psychedelic display`, `90s grunge zine lettering`
4. **Brand atmosphere** — `editorial fashion-magazine serif, Vogue style`
5. **Physical material** — `glowing neon tube letters with visible glass tubing`
6. **Reference name as a hint** — `clean sans-serif, Inter style`

---

## 2. The structured Typography block — use this shape

Structured beats adjectives scattered through the prompt **[TEST]**:

```
Typography:
- Headline: EXACT text "افتتاح قريباً", geometric Kufi, heavy weight,
  large, warm gold on deep green, right-aligned upper third.
- Subhead: EXACT text "الرياض · ٢٠٢٦", modern Arabic sans, regular weight,
  one third the headline size, right-aligned beneath.
```

Per level, specify: **exact text → script/style → weight → size tier → colour
& contrast → placement.**

- Keep to a **2–3 level hierarchy**. More levels dilute every one of them.
- **Contrast below ~4.5:1 blurs small text** — state the pairing explicitly
  ("warm white on deep teal, maximum contrast") **[TEST]**.
- Always wrap literal strings in quotes; `EXACT text` before the string reduces
  invented characters **[VENDOR]**.
- On GPT Image 2, raise `quality` to **high** for small or dense type **[VENDOR]**.

---

## 3. Arabic script styles — the reliable tokens

Lead with one of these. They work.

| Token | Arabic | Character | Use for |
|---|---|---|---|
| `Naskh` | نسخ | rounded, even, highly legible | body, editorial, books |
| `geometric Kufi` | كوفي | angular, modular, grid-based | logos, modern minimal, architecture |
| `Thuluth` | ثلث | tall verticals, ornate, ceremonial | titles, prestige, religious-adjacent |
| `Diwani` | ديواني | flowing, dense, decorative | luxury, invitations, certificates |
| `Ruqʿah` | رقعة | compact everyday handwriting | casual, street signage |
| `Maghribi` | مغربي | wide sweeping bowls | North African context |
| `Nastaliq` | نستعليق | steeply sloped, Persian | Persian/Urdu contexts, not Gulf |

Strengthen with stroke language: `high stroke contrast`, `thick-to-thin
modulation`, `flat pen angle`, `extended kashida strokes`, `tight counters`.

---

## 4. Arabic typeface names — as hints only

Pair with a descriptor. Grouped by the feeling the name carries **[CRAFT]**:

| Feel | Names to hint with |
|---|---|
| Modern UI / corporate | Cairo, Tajawal, Almarai, IBM Plex Sans Arabic, Readex Pro |
| Gulf / Saudi commercial | GE SS, Dubai, Frutiger Arabic, Neue Helvetica Arabic |
| Traditional Naskh | Amiri, Noto Naskh Arabic, Scheherazade |
| Geometric Kufi | Reem Kufi, Kufam |
| Display / playful | Changa, Lalezar, Baloo Bhaijaan, Rubik Arabic |

Example: `modern Arabic sans-serif, clean geometric letterforms, Tajawal style,
medium weight`.

**Amiri** and **Noto Naskh Arabic** are the safest hints for traditional Naskh;
**Reem Kufi** for geometric Kufi.

---

## 5. Latin names for bilingual work

Same rule — hint, plus descriptor.

| Feel | Hint with |
|---|---|
| Neutral modern | Inter, Helvetica, Univers |
| Geometric | Futura, Poppins, Circular |
| Editorial serif | Playfair, Tiempos, Freight |
| Technical / mono | JetBrains Mono, IBM Plex Mono |
| Luxury serif | Didot, Bodoni |

For bilingual harmony, ask for it directly: *"Arabic and Latin visually
harmonised — matched weight, matched stroke contrast, matched terminal style."*
Arabic set **110–125%** of the Latin size to read as optically equal.

---

## 6. Known limits

- **Perspective + text is the worst combination.** Type on a curved bottle or a
  steeply angled sign degrades sharply. Prefer flat faces.
- **Small + dense + diacritised Arabic:** ~1 glyph error in 20 even on GPT
  Image 2 **[TEST]**. Large and short is safe; body copy is not.
- **More than 2–3 type levels** dilutes the hierarchy.
- **Exact font reproduction is not available.** If the brand *requires* a
  licensed typeface, generate the artwork text-free and set the type properly —
  that is the only way to guarantee it.

---

## 7. Copy-ready Arabic typography block

```
Typography:
- Headline: EXACT text "<النص هنا>", geometric Kufi, heavy weight, large,
  <colour> on <colour>, maximum contrast, right-aligned in the upper right.
- Subhead: EXACT text "<النص>", modern Arabic sans-serif (Tajawal style),
  regular weight, one third the headline size, right-aligned beneath.
Script: fully connected cursive Arabic, correct initial/medial/final forms,
proper ligatures, no broken or detached letters, no diacritics.
Layout: right-to-left composition, reading entry top-right.
Language: Arabic only — no Latin text anywhere in the image.
```

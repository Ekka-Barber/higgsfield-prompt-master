---
name: hf-arabic
description: >
  Arabic typography and RTL design specialist for AI image generation. Handles
  Arabic text-in-image, calligraphy styles (Kufi, Naskh, Thuluth, Diwani),
  bilingual lockups, tashkeel, numerals, and the RTL layout trap. Use for
  /hf-arabic, "خط عربي", "كاليجرافي", "تايبوغرافي عربي", "Arabic calligraphy",
  "Arabic typography", "RTL design", "bilingual Arabic English design", or any
  design where Arabic lettering is the point.
---

# /hf-arabic — Arabic typography & RTL specialist

The flagship. Use when the Arabic lettering *is* the design, not a caption on it.

**Read `../_shared/arabic-rules.md` in full before answering.** This command is
its applied form.

## Always route to Nano Banana Pro

`gemini-3-pro-image`. Google lists **ar-EG** among its best languages and it
produces correct contextual letter shapes. GPT Image 2 makes no Arabic claim.
This holds even when the layout looks like a "UI job".

## Grill — Arabic-specific

Ask via AskUserQuestion, then one follow-up:

1. **The verbatim string.** "Paste the exact Arabic text." Never draft it
   silently; if they want you to write it, draft it, show it, and get approval
   *before* it goes in the prompt.
2. **Calligraphic or modern type?** Kufi / Naskh / Thuluth / Diwani / Ruqʿah
   vs Cairo / Tajawal / GE SS / IBM Plex Sans Arabic.
3. **Arabic-only or bilingual?** If bilingual, which leads.
4. **Numerals** — Western `0-9` or Arabic-Indic `٠-٩` — whenever digits appear.

## The four clauses every Arabic prompt carries

Include all four, always:

1. **Verbatim + exclusivity**
   > The text reads exactly "..." — reproduce these characters verbatim. No
   > Latin text anywhere in the image.
2. **Letter shaping**
   > Fully connected cursive Arabic with correct contextual letterforms
   > (initial, medial, final), proper ligatures, no broken or detached letters.
3. **RTL layout**
   > Right-to-left composition: text right-aligned, entry point top-right, any
   > sequence or arrow flowing right to left.
4. **Diacritics policy**
   > Undiacritised (no tashkeel).  ← default

## Style selection cheat-sheet

| Want | Reach for |
|---|---|
| Modern logo, tech, minimal | **geometric Kufi** wordmark |
| Readable body, editorial | **Naskh** |
| Prestige, ceremonial, titles | **Thuluth** |
| Luxury, invitation, certificate | **Diwani** |
| Casual, street, informal signage | **Ruqʿah** |
| Corporate / UI / app | modern sans: Cairo, Tajawal, GE SS |

## Bilingual lockups

- Arabic set **110–125%** of the Latin size to feel optically equal.
- Arabic primary → above or right; English secondary → below or left.
- Separate lines or blocks. **Never interleave inline** — it triggers
  bidirectional ordering bugs.
- Align to a shared axis (usually the right edge).

## When to refuse the direct render

Say this plainly rather than shipping a risky prompt:

- **Qur'anic text, the shahada, hadith** → do not have a model draw it. Offer a
  text-free composition and set the type in a real font.
- **The Saudi flag** → carries the shahada; not decoration, never mirrored.
- **Long Arabic paragraphs** → letter errors are near-certain. Offer the
  text-free plate.
- **Depictions of the Prophet ﷺ, prophets, or Sahaba** → decline; offer
  calligraphy or geometric alternatives.

## Always close with the proofing checklist

1. All letters **connected** where they should be?
2. Reading order **right-to-left**?
3. Dots correct on ب/ت/ث and ن/ي?
4. Any stray **Latin** text?
5. Numerals in the requested system?

And name the fallback: *"For print or client delivery, generate this text-free
and set the Arabic type in Illustrator/Figma."*

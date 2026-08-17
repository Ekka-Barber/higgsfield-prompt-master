---
name: rasm-help
description: >
  Index of all /rasm-* commands — what each one does and when to reach for it.
  One-shot reference card, not a mode. Use for /rasm-help, "المساعدة", "الأوامر",
  "وش الأوامر", "rasm help", "what commands", "list commands", "how do I use rasm".
---

# /rasm-help — command index

Arabic-first AI image prompt system. Two models: **Nano Banana Pro**
(`gemini-3-pro-image`) and **GPT Image 2** (`gpt-image-2`).

## Commands

| Command | Use it for |
|---|---|
| **`/rasm`** | Start here. Grills you, routes, generates. |
| **`/rasm-arabic`** | Arabic lettering *is* the design — calligraphy, wordmarks, RTL typography. |
| **`/rasm-brief`** | Interrogation only. Produces a locked spec, no prompt. |
| **`/rasm-social`** | Instagram, Snap, TikTok, X, LinkedIn, YouTube — ratios & safe zones. |
| **`/rasm-poster`** | Posters, flyers, banners, signage, event announcements. |
| **`/rasm-menu`** | Restaurants & cafés — dish photography, menu boards, food styling. |
| **`/rasm-brand`** | Logos, Arabic wordmarks, monograms, identity systems. |
| **`/rasm-product`** | Packshots, hero shots, lifestyle, marketplace listings. |
| **`/rasm-edit`** | Edit an existing image — references, face lock, background swap, localisation. |
| **`/rasm-search`** | Explore the 7,315-prompt corpus for real exemplars. |
| **`/rasm-model`** | Which model, and is my size valid? |
| **`/rasm-help`** | This card. |

## Defaults

- **Arabic is the default.** English needs `--en` or "in English" / "بالإنجليزي".
- **Arabic text → Nano Banana Pro.** It officially supports ar-EG with correct
  letter shaping; GPT Image 2 claims no Arabic support.
- Every command grills 2–4 questions, then one confirmation follow-up.

## The rules that apply everywhere

- **No negative prompts.** No model here has one. Describe the positive state:
  not "no cars" → "an empty, deserted street, bare asphalt".
- **Quote literal text** exactly. Spell out unusual names letter-by-letter.
- **Never `REFERENCE_0`.** Say "the first image (product)".
- **No booster tokens** — "masterpiece, 8k, trending on artstation" are noise.
- **60–120 words** is the sweet spot; never put a critical detail last.
- **RTL is not automatic.** Models render Arabic glyphs correctly and still lay
  the page out left-to-right. State the RTL clause every time.

## Arabic quick reference

| | |
|---|---|
| Script styles | Kufi (modern/geometric) · Naskh (readable) · Thuluth (ceremonial) · Diwani (luxury) · Ruqʿah (casual) |
| Modern type | Cairo · Tajawal · Almarai · GE SS · IBM Plex Sans Arabic |
| Numerals | Western `0-9` (Gulf commercial) vs Arabic-Indic `٠-٩` (traditional) |
| Tashkeel | omit by default |
| Length | headline 2–5 words · label 1–3 · never a paragraph |
| Bilingual | Arabic leads, ~115% of Latin size, separate lines |

## Sacred content

Qur'anic text, the shahada, and the Saudi flag are **never** rendered by a
model — an AI letter error in sacred text is genuinely offensive. Generate the
artwork text-free and set the type properly. Depictions of the Prophet ﷺ,
prophets, or Sahaba are declined outright.

## For anything going to print or a client

Generate the artwork **text-free**, then set the Arabic type in
Illustrator/Figma with a real Arabic font. Even at 94–96% text accuracy, the
failures land on letter connections — exactly what a native reader sees first.

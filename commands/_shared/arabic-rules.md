# Arabic Design Rules — the core of every `/hf-*` command

Load this before writing any prompt whose image contains Arabic text.
These are the rules that separate an Arabic design prompt from a translated
English one. Evidence tier is marked: **[VENDOR]** official docs, **[TESTED]**
reproducible community/practitioner reports, **[CRAFT]** design practice.

---

## 0. The one-line routing rule

**Arabic text inside an image → GPT Image 2 (`gpt-image-2`).**

GPT Image 2 renders Arabic through a **typographic pathway that composes glyphs
as vector shapes and rasterises them into the scene**, instead of inferring
letterforms pixel-by-pixel during diffusion **[TEST]**. Correct contextual
shaping is therefore structural rather than lucky — which is why it reports
~99% character-level accuracy against Nano Banana Pro's ~94%, and why
independent comparisons put it close to a full generation ahead on RTL work.
Nano Banana Pro shows Arabic **character-spacing** problems that need manual
correction before an asset is publish-ready **[TEST]**.

> **Correction, 2026-08-17.** An earlier version of this file routed Arabic to
> Nano Banana Pro because Google documents ar-EG support and OpenAI's docs never
> mention Arabic. That was an argument from silence, and it was wrong. Absence
> of a vendor claim is not evidence of weakness. Tested behaviour wins.

**Send Arabic to Nano Banana Pro only when the job is driven by something it
owns** — reference-image compositing, character consistency across a series, or
translate-text-in-image localisation — and accept that the Arabic may need a
typographic pass.

### Known Arabic limits on GPT Image 2 **[TEST]**

- **Full tashkeel at small point sizes in dense paragraphs: ~1 glyph error in
  20.** Headings, signage and short strings are reliable; diacritised body copy
  is not. This is the sharpest reason for §3 and §4 below.

---

## 1. The RTL layout trap — the single most common failure

Models render Arabic **glyphs** correctly and then lay the **page** out
left-to-right anyway **[TESTED]**. You get correct words in a Western
composition: logo top-left, text ragged-left, arrows pointing the wrong way,
timelines running the wrong direction.

The model will not infer this. State it explicitly, every time:

> "Right-to-left layout: the composition reads from the right. Arabic text is
> right-aligned, the logo sits top-right, and any sequence, arrow, or timeline
> flows right to left."

Things that must mirror in an RTL composition **[CRAFT]**:

| Element | LTR | Arabic RTL |
|---|---|---|
| Primary text alignment | left | **right** |
| Logo / brand mark | top-left | **top-right** |
| Reading entry point | top-left | **top-right** |
| Numbered steps, timelines | left → right | **right → left** |
| Arrows, chevrons, progress | point right | **point left** |
| Quote marks, bullets | left of text | **right of text** |
| Nav / menu order | first item left | **first item right** |

Do **not** mirror: photographs of real people and places, product shots, logos
containing Latin text, and anything with embedded Latin signage. Mirroring an
image flips faces and text into nonsense.

---

## 2. Letter shaping — say it, or get broken words

Arabic is cursive. Every letter takes up to **four contextual forms** —
isolated, initial, medial, final — and adjacent letters join **[TESTED]**. The
documented failure modes are broken connections, dropped letters, and
duplicated glyphs.

Always include a shaping clause:

> "Arabic text must be fully connected cursive script with correct contextual
> letterforms (initial, medial, final), proper ligatures, and no broken or
> detached letters."

Two letters that most often break, worth naming when they appear in the copy:
**ل + ا → لا** (lam-alef ligature, must be a single glyph) and the dotted
family **ب ت ث ن ي** (dot count and placement get scrambled).

---

## 3. Tashkeel (diacritics) — omit by default

Every diacritic is an additional error surface, and misplaced tashkeel is
immediately visible as wrong to a native reader **[TESTED]**.

- **Default: no tashkeel.** Modern Arabic design overwhelmingly sets text
  undiacritised. Say "no diacritics / undiacritised text".
- Measured cost of ignoring this: full diacritics at small sizes in dense
  paragraphs run **~1 glyph error in 20** even on GPT Image 2 **[TEST]**.
  Diacritics are safe only large and short.
- **Include only for:** Qur'anic text, classical poetry, children's literacy
  material, or where meaning is genuinely ambiguous.
- When required, keep the string extremely short and expect to fix it manually.

---

## 4. String length — error rate scales with length

Keep each Arabic string as short as the design allows **[TESTED]**. Long Arabic
paragraphs degrade far faster than the equivalent English.

| Role | Target |
|---|---|
| Headline | 2–5 words |
| Subhead | up to ~8 words |
| Button / label / badge | 1–3 words |
| Body block | avoid; if unavoidable, split into short discrete blocks |

Never ask for a paragraph of running Arabic body copy. Ask for a placeholder
block and set the real copy in a design tool (§9).

---

## 5. Quote the exact string

Both vendors are explicit that literal text belongs in quotes **[VENDOR]**.
For Arabic, this matters more: paraphrasing invites the model to invent words.

> The headline reads exactly "**افتتاح قريباً**" — reproduce these characters
> verbatim, no additional words, no transliteration.

Add `no Latin text anywhere in the image` when the design is Arabic-only —
models love to sneak in English.

---

## 6. Script style — name one

Naming a calligraphic or type style is the highest-leverage single word in an
Arabic prompt **[CRAFT]**.

**Calligraphic (traditional):**

| Style | Arabic | Character | Use for |
|---|---|---|---|
| Naskh | نسخ | rounded, highly legible | body text, editorial, books |
| Kufi | كوفي | angular, geometric, architectural | logos, monograms, modern minimal |
| Thuluth | ثلث | tall, ornate, ceremonial | titles, religious, prestige |
| Diwani | ديواني | flowing, dense, decorative | luxury, invitations, certificates |
| Ruqʿah | رقعة | compact, everyday handwriting | casual, signage, informal |
| Maghribi | مغربي | wide sweeping bowls | North African context |

**Modern typeface families** (for contemporary/brand work): Cairo, Tajawal,
Almarai, IBM Plex Sans Arabic, Noto Naskh Arabic, GE SS (common in the Gulf),
Neue Helvetica Arabic, Frutiger Arabic, 29LT families.

Say the *style*, not just "Arabic font" — "geometric Kufi wordmark" produces a
categorically different result from "Arabic text".

---

## 6b. Kashida — Arabic justifies by stretching letters, not spaces

Latin text justifies by widening **word spaces**. Arabic justifies with
**kashida (كشيدة / tatweel)** — elongating the connecting stroke *inside* a word
at specific joins **[CRAFT]**. A model that stretches Arabic word-spacing to fill
a line has produced something a native reader clocks instantly as wrong.

When a design needs justified or edge-to-edge Arabic:

> "Justify the Arabic line using kashida elongation of the connecting strokes,
> not by widening the spaces between words. Keep word spacing even."

Kashida is also a *decorative* device — deliberately extended strokes in
Thuluth and Diwani for rhythm and grandeur:

> "Extended kashida strokes on the connecting letters for a flowing ceremonial
> rhythm."

Never apply kashida to Kufi (it is angular and modular, not cursive-stretched),
and never stretch a letter that does not take a connecting stroke.

## 7. Numerals — pick a system

Arabic-Indic **٠١٢٣٤٥٦٧٨٩** vs Western **0123456789**. Both are "Arabic
numerals"; mixing them in one design looks like an error **[CRAFT]**.

- **Saudi / Gulf modern commercial design:** Western digits dominate — prices,
  phone numbers, dates.
- **Egypt, Levant, traditional or governmental:** Arabic-Indic is common.
- **Religious, classical, heritage:** Arabic-Indic.

State it: `prices in Western numerals (0-9)` or `numbers in Arabic-Indic
numerals (٠-٩)`. Never leave it unspecified on a menu, price tag, or poster.

---

## 8. Bilingual Arabic + English lockups

Arabic and Latin have different vertical metrics; set at the same point size
Arabic reads visually smaller **[CRAFT]**.

- Arabic typically needs **~110–125% of the Latin size** to feel balanced.
- Hierarchy: Arabic primary → **above or to the right**; English secondary →
  below or to the left.
- Do not centre-align mixed scripts against each other; align to a shared axis
  (usually the right edge for Arabic-primary work).
- Keep the two languages on **separate lines or in separate blocks**. Inline
  mixing triggers bidirectional ordering bugs.
- Say: "bilingual lockup, Arabic primary above English, Arabic set slightly
  larger, both right-aligned, clearly separated — not interleaved."

---

## 9. The professional fallback — say this out loud when it matters

For anything going to print, a client, or a paying customer, the honest
workflow is **[CRAFT]**:

> Generate the artwork with **no text** (or with text areas left as clean
> negative space), then set the real Arabic type in Illustrator / InDesign /
> Figma with a proper Arabic font.

Even at 94–96% text accuracy, the failures land on *letter connections* — the
part a native reader notices instantly. Offer the text-free plate as a variant
whenever the job is commercial. This is not a limitation to hide; it is what
working Arabic designers actually do.

---

## 10. Always end with a verification instruction

Arabic output must be proofread by someone who reads Arabic. Close every
Arabic generation with a short check:

1. Are all letters **connected** where they should be?
2. Is the word order and reading direction **right-to-left**?
3. Are dots correct in count and position (ب/ت/ث, ن/ي)?
4. Did any **Latin** text sneak in?
5. Do the numerals match the requested system?

---

## 11. Cultural motifs — Gulf and Saudi vocabulary

Reach for these instead of generic "Middle Eastern" **[CRAFT]**:

- **Pattern:** arabesque (توريق), girih geometric interlace, eight-point star
  (نجمة ثمانية), muqarnas vaulting, mashrabiya lattice screen, Sadu weaving
  (Bedouin geometric, red/black/white).
- **Saudi architecture:** Najdi mud-brick with triangular crenellation,
  Diriyah / At-Turaif earthen walls, Hejazi rawasheen carved wooden balconies,
  AlUla sandstone, Red Sea modernism.
- **Landscape:** palm groves, Empty Quarter dunes, basalt harrat, wadi.
- **Contemporary Saudi:** Vision 2030 minimalism, desert-neutral palettes
  (sand, terracotta, deep green), heritage green.
- **Seasonal:** Ramadan (crescent, lanterns/fanoos, warm gold on deep blue or
  green), Eid, Saudi National Day (green/white, Sept 23), Founding Day (Feb 22).

---

## 12. Cultural and religious care

Non-negotiable, and worth stating in the prompt when relevant:

- **Never** generate depictions of the Prophet ﷺ, other prophets, or the
  Sahaba. Decline and offer calligraphy or geometric alternatives.
- **Qur'anic verses and the shahada:** an AI-rendered letter error in sacred
  text is genuinely offensive. Strongly prefer the §9 fallback — set these in a
  real font, never leave them to the model.
- **The Saudi flag** carries the shahada and must not be distorted, mirrored,
  draped, or placed on the floor/merchandise. Avoid generating it as decoration.
- **Modesty:** for Saudi and Gulf commercial work, default to modest dress and
  culturally appropriate framing unless the user specifies otherwise.
- Do not mirror an image containing the shahada or any sacred text.

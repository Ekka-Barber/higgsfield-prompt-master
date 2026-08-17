# The Grill — adaptive interrogation before generating

A vague brief produces a generic image. The job of the grill is to convert
"اعملي بوستر" into a specification precise enough that the output is *the*
image the user pictured, not *an* image about the topic.

**Not a form.** Ask only what is missing and load-bearing. If the user already
said it, or it is safely inferable, do not ask.

---

## Rule 1 — Ask 2–4 questions, then one follow-up round

- **Round 1:** 2–4 questions covering only unresolved, output-changing gaps.
- **Round 2 (always):** one short confirmation pass. Play back the resolved
  spec and ask a single targeted follow-up on whatever the answers *opened up*.
  An answer often creates a new fork — "Ramadan campaign" raises the question
  of which night, which is a different image.
- Then generate. Do not open a third interrogation round; refine after output.

If the brief is already rich, skip to Round 2 and just confirm.

---

## Rule 2 — Use the AskUserQuestion tool, not prose

Present real options with concrete previews. A user recognises the right answer
far faster than they can produce it from nothing. Every option must be a
distinct, buildable direction — never "Option A / Option B / Other".

Always offer a recommended default first, marked `(Recommended)`.

---

## Rule 3 — What is actually worth asking

Ask about a slot only when the answer changes the image. Ranked by leverage:

1. **The exact text.** For any design carrying words, the single highest-value
   question. Never invent Arabic copy — get the verbatim string. Wrong copy
   makes a beautiful image useless.
2. **Purpose & surface.** Instagram story ≠ printed A3 ≠ menu board. Drives
   ratio, safe zones, text size, resolution.
3. **Audience & register.** Luxury restaurant vs street food; government vs
   startup. Drives type style, palette, formality.
4. **Photographic or graphic?** A photo-real plate and a flat vector poster are
   different jobs; models handle them differently.
5. **Brand constraints.** Existing colours (hex), logo, an established look to
   match.
6. **Mood, in two adjectives.** Cheap to ask, high leverage.

Do **not** ask about: lens/aperture (weak on both models), negative prompts
(they do not exist), token budgets, or anything already implied by the category.

---

## Rule 4 — Arabic-specific questions

Because this skill is Arabic-first, these come up constantly. Ask them when the
copy is Arabic and the answer is not already given:

- **Verbatim Arabic string** — always. Ask them to paste it.
- **Numerals** — Western `0-9` or Arabic-Indic `٠-٩`? Never guess on a menu,
  price, or date.
- **Script style** — modern sans (Cairo / Tajawal / GE SS) or calligraphic
  (Kufi / Naskh / Thuluth / Diwani)? Two very different products.
- **Arabic-only or bilingual?** If bilingual, which language leads.
- **Dialect / register** — MSA (فصحى) vs Gulf (خليجي) vs Egyptian, when *you*
  are drafting the copy rather than receiving it.

---

## Rule 5 — Detect and stop bad premises

Say so immediately, before generating, when:

- The Arabic string is long enough that letter errors are near-certain →
  recommend the text-free plate + real typography (arabic-rules §9).
- The job involves Qur'anic text, the shahada, or the Saudi flag → do not let a
  model render sacred text; offer the safe alternative.
- The request needs exact counts above ~5 → warn that neither model is reliable
  there and propose a composition that does not depend on the count.
- The brief is internally contradictory (e.g. "minimal" + eleven required
  elements) → surface the conflict and ask which wins.

---

## Rule 6 — Always play back the spec before generating

One compact block, so the user can catch a wrong assumption in one glance:

```
Language   Arabic only · MSA
Text       "افتتاح قريباً" (verbatim) · no diacritics · Western numerals
Surface    Instagram story · 9:16 · 1080×1920
Style      Geometric Kufi wordmark, desert-neutral palette
Mood       Calm, premium
Model      Nano Banana Pro (gemini-3-pro-image) — Arabic text-in-image
Layout     RTL · right-aligned · logo top-right
```

Then generate.

---

## Rule 7 — Deliver more than the prompt

Every generation ends with:

1. The prompt, in a copyable block.
2. **Model + exact model id**, and one line on why it was routed there.
3. Ratio / size (validated against the model's real limits).
4. The **Arabic proofing checklist** when Arabic is present.
5. One concrete next lever — what to change if the first result misses.

# Model Routing — two models, one decision

This skill targets exactly two models. Every `/hf-*` command must name the
routed model and its exact model id in its output.

| | **Nano Banana Pro** | **GPT Image 2** |
|---|---|---|
| Model id | `gemini-3-pro-image` | `gpt-image-2` |
| Snapshot | — | `gpt-image-2-2026-04-21` |

---

## The decision, in priority order

Evaluate top to bottom. **First match wins.**

1. **Any readable Arabic (or other non-Latin) text in the image → GPT Image 2.**
   It composes glyphs as **vector shapes** through a dedicated typographic
   pathway rather than inferring letterforms during diffusion, giving ~99%
   character accuracy vs Nano Banana Pro's ~94%, and independent comparisons put
   it roughly a generation ahead on RTL. Nano Banana Pro shows Arabic
   character-spacing errors needing manual fixes [TEST].
   *Exception:* full tashkeel at small sizes in dense paragraphs still runs ~1
   glyph error in 20 — keep diacritised text large and short.
2. **Reference images / compositing / character consistency → Nano Banana Pro.**
   Typed reference slots: up to 6 objects, 5 characters, 3 style refs (Pro).
   It weights the reference image over the text when they conflict. This
   outranks rule 1 — accept a typographic pass on any Arabic.
3. **Translate-text-in-image / localisation → Nano Banana Pro.** A documented
   strength; same caveat as rule 2.
4. **Exact element counts and precise spatial arrangement → GPT Image 2.**
   "Exactly 6 nav items", "4 cards in a grid". More literal about enumerated
   instructions. Neither model is dependable much past five.
5. **English text-dense layouts → GPT Image 2.** UI mockups, infographics,
   dense information panels, slides.
6. **Structure-preserving edits → GPT Image 2.** It holds layout and pose from
   a reference more tightly; use it when geometry must survive.
7. **Mood-led, atmospheric, colour-led work → Nano Banana Pro.** It composes
   with more opinion from a thinner brief.
8. **Default for this skill → GPT Image 2** (Arabic-first, and Arabic text is
   its strongest suit). Reach for Nano Banana Pro when the brief is a *mood* or
   a *reference* rather than a *specification*.

---

## Behavioural differences that change how you write the prompt

| | Nano Banana Pro | GPT Image 2 |
|---|---|---|
| Reads the brief | holistically, for intent | literally, clause by clause |
| Thin brief | composes with opinion | flat, centred, catalogue-like |
| Conflicting clauses | picks one | attempts both |
| Reference vs text conflict | trusts the **image** | trusts the **text** |
| Framing | uses the full frame, off-centre | centres and fills symmetrically |
| Camera/lens vocabulary | responds well | "interpreted loosely" [VENDOR] |

**Porting rule:** moving a prompt *to* GPT Image 2, add specification — it
defaults badly on anything you leave out. Moving *to* Nano Banana Pro, remove
contradictions — it resolves conflict by choosing, not by blending.

---

## Universal rules — true on both

- **There is no negative prompt.** Neither model exposes a negative channel.
  OpenAI never mentions one; Google's docs say "not supported"; Black Forest
  Labs states it outright for FLUX [VENDOR]. Negation inside the prompt often
  *summons* the thing. **Describe the positive state instead:**
  not `"no cars"` → `"an empty, deserted street, bare asphalt"`.
- **Literal text goes in quotes** (or ALL CAPS). Spell out unusual brand names
  letter-by-letter [VENDOR].
- **Never emit `REFERENCE_0` / `REFERENCE_N`.** Address references in natural
  language by ordinal and role: `"the first image (product)"`,
  `"use the second image for colour and mood only"`.
- **State the reference's job.** "Use the attached image for lighting and colour
  only; subject and pose come from the text." Both models respond to this.
- **60–120 words is the sweet spot.** Below ~30 GPT Image 2 goes flat; past
  ~200 both weaken on later clauses.
- **Never put an essential detail in the last sentence** — the tail of a long
  prompt is the least reliable part on both models.
- **No booster tokens.** "masterpiece, 4k, 8k, trending on artstation, highly
  detailed" are Stable-Diffusion-era noise with near-zero information.
- **Edits:** "change only X" + "keep everything else the same", and repeat the
  preserve list on every iteration to stop drift [VENDOR].

---

## GPT Image 2 output-size constraints [VENDOR, verified 2026-08-17]

Validate with `renderers.validate_gpt_image_2_size(w, h)`.

- Both edges a multiple of **16**
- Longest edge **under 3840px**
- Total pixels between **655,360** and **8,294,400**
- Long:short ratio no greater than **3:1**
- Above **2560×1440** is officially **experimental** — more variable
- `quality`: `low` | `medium` | `high` — use **high** for small text, dense
  panels, multi-font layouts and identity-sensitive edits
- `input_fidelity` is **disabled** on gpt-image-2

Common valid sizes: `1024x1024`, `1536x1024`, `1024x1536`, `2560x1440`,
`3824x2144` (4K rounded to keep the edge under 3840).

## Nano Banana Pro output controls [VENDOR]

- Aspect ratios: `1:1 3:2 2:3 3:4 4:3 4:5 5:4 9:16 16:9 21:9`
- `image_size`: `1K` | `2K` | `4K`
- Reference caps (Pro): up to **6 objects**, **5 characters**, 3 style refs
- All output carries a **SynthID** watermark

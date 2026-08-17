---
name: rasm-model
description: >
  Choose between GPT Image 2 and Nano Banana Pro, and validate output sizes
  against each model's real API limits. Use for /rasm-model, "أي موديل", "وش
  أستخدم", "which model", "gpt image or nano banana", "model comparison",
  "what size", "aspect ratio", "is this size valid", "image dimensions".
---

# /rasm-model — pick the model, validate the size

Read `../_shared/model-routing.md` for the full table. This command applies it
and checks sizes.

## The two targets

| | Nano Banana Pro | GPT Image 2 |
|---|---|---|
| id | `gemini-3-pro-image` | `gpt-image-2` |
| snapshot | — | `gpt-image-2-2026-04-21` |
| default for | **Arabic, references, mood** | English text-dense, exact counts |

## Decision, first match wins

1. Readable **Arabic** or other non-Latin text in the image → **Nano Banana Pro**
2. Reference images / compositing / character consistency → **Nano Banana Pro**
3. Translate-text-in-image / localisation → **Nano Banana Pro**
4. **Exact element counts**, precise spatial arrangement → **GPT Image 2**
5. English text-dense layouts, UI, infographics → **GPT Image 2**
6. Structure-preserving edits → **GPT Image 2**
7. Mood-led, colour-led, thin brief → **Nano Banana Pro**
8. Otherwise → **Nano Banana Pro** (this skill is Arabic-first)

Neither model is reliable on exact counts much past **five**.

## GPT Image 2 — hard size limits [verified 2026-08-17]

- Both edges a multiple of **16**
- Longest edge **under 3840px**
- Total pixels **655,360 – 8,294,400**
- Long:short ratio **≤ 3:1**
- Above **2560×1440** is officially **experimental**

Validate any size:

```bash
python -c "from renderers import validate_gpt_image_2_size as v; print(v(1536,1024) or 'OK')"
```

Known-good: `1024x1024`, `1536x1024`, `1024x1536`, `2560x1440`, `3824x2144`.

Other params: `quality` = `low` | `medium` | `high` — use **high** for small
text, dense panels, multi-font layouts, identity-sensitive edits. Start `low`
while iterating. `input_fidelity` is **disabled** on this model.

## Nano Banana Pro — output controls

- Ratios: `1:1 3:2 2:3 3:4 4:3 4:5 5:4 9:16 16:9 21:9`
- `image_size`: `1K` | `2K` | `4K`
- References: up to **6 objects**, **5 characters**, 3 style refs
- Best languages include **ar-EG** — the reason Arabic routes here
- All output carries a **SynthID** watermark

## Writing differences

| | Nano Banana Pro | GPT Image 2 |
|---|---|---|
| reads the brief | holistically | literally, clause by clause |
| thin brief | composes with opinion | flat and centred |
| conflicts | picks one | attempts both |
| reference vs text | trusts the **image** | trusts the **text** |
| camera vocabulary | responds well | "interpreted loosely" |

**Porting:** to GPT Image 2, *add specification*. To Nano Banana Pro, *remove
contradictions*.

## True on both

No negative prompt exists — describe the positive state. Quote literal text.
No `REFERENCE_N`. 60–120 words is the sweet spot. Never put an essential detail
in the last sentence.

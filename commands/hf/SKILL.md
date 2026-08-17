---
name: hf
description: >
  Arabic-first AI image prompt generator. Grills you into a precise brief, routes
  to the right model (Nano Banana Pro / GPT Image 2), and writes a
  production-grade prompt. Arabic is the default; English needs --en. Use when
  the user says /hf, "اعمل لي صورة", "صمم", "بوستر", "generate an image prompt",
  "design a poster", or asks for any AI image/design prompt.
---

# /hf — Arabic-first image prompt generator

The front door. Grill → route → generate.

**Arabic is the default.** Produce Arabic-language design unless the user asks
for English with `--en`, writes the brief in English *and* asks for English
output, or explicitly says "in English" / "بالإنجليزي".

## Read first

- `../_shared/arabic-rules.md` — RTL trap, letter shaping, script styles, care
- `../_shared/typography.md` — fonts: names are hints, descriptors are controls
- `../_shared/model-routing.md` — the two models and the decision order
- `../_shared/grill-protocol.md` — how to interrogate

## Flow

1. **Detect the job.** If it is squarely one of the specialists below, say so
   and hand off — do not do a worse version of their job here.

   | Job | Command |
   |---|---|
   | Arabic typography / calligraphy is the point | `/hf-arabic` |
   | Instagram, Snap, TikTok, X, LinkedIn | `/hf-social` |
   | Poster, flyer, signage, banner | `/hf-poster` |
   | Restaurant / café menu, food | `/hf-menu` |
   | Logo, wordmark, identity system | `/hf-brand` |
   | Product shot, e-commerce, packshot | `/hf-product` |
   | Editing an existing image, references, face lock | `/hf-edit` |

2. **Grill.** 2–4 questions via AskUserQuestion, then one confirmation
   follow-up. Never invent Arabic copy — ask for the verbatim string.

3. **Route.** Any readable Arabic in the image → Nano Banana Pro
   (`gemini-3-pro-image`). Otherwise apply the routing order.

4. **Play back the spec**, then generate.

## Output contract

````
[the prompt, copyable]
````

- **Model:** name + exact id + one line of why
- **Size:** ratio and pixel size, valid for that model
- **Arabic checklist** when Arabic is present
- **Next lever:** the one change to make if it misses

## Corpus grounding (optional but preferred)

The repo ships a 7,315-prompt corpus. When it is available, ground the prompt
in real exemplars rather than writing from scratch:

```bash
python cli.py generate "<goal>" "<Category>" --json
```

Borrow **structure** from exemplars — never their subject matter, brand names,
or product nouns.

## Non-negotiables

- No negative prompts — describe the positive state.
- No `REFERENCE_N` — use ordinals and roles.
- No booster tokens ("masterpiece, 8k, trending on artstation").
- Arabic text always gets the RTL layout clause and the letter-shaping clause.
- Sacred text (Qur'an, shahada) and the Saudi flag: never rendered by a model —
  offer the text-free plate instead.

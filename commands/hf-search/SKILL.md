---
name: hf-search
description: >
  Search and explore the 7,315-prompt corpus — find real exemplars, category
  guides, technique breakdowns and structure patterns. Use for /hf-search,
  "ابحث", "أمثلة", "search prompts", "find examples", "show me prompts",
  "corpus", "category guide", "what techniques".
---

# /hf-search — explore the corpus

7,315 searchable prompts plus 62 curated master prompts. Use this to ground a
design in real exemplars instead of inventing from scratch.

## Commands

```bash
python cli.py search "glassmorphism dashboard" --limit 5
```
```bash
python cli.py guide "Poster / Flyer"
```
```bash
python cli.py stats
```
```bash
python cli.py random --category "Product Marketing"
```

Add `--json` to any of them for structured output.

## Categories

App / Web Design · Product Marketing · Social Media Post · Poster / Flyer ·
Comic / Storyboard · Profile / Avatar · Game Asset · Infographic / Edu Visual ·
YouTube Thumbnail · E-commerce Main Image · Portrait / Selfie ·
Landscape / Nature · Architecture / Interior · Cinematic / Film Still ·
Abstract / Background · Animal / Creature · Group / Couple · Sketch / Line Art

Aliases normalise automatically (`app/web design` → `App / Web Design`).

## The corpus is English-only — and that is fine

2,240 non-English prompts were removed by policy. **This does not limit Arabic
work**, because of how the pipeline is meant to be used:

> The **prompt** is written in English (both models handle English instructions
> best, and the corpus is English). The **text rendered inside the image** is
> Arabic, quoted verbatim.

So search in English for the *structure and craft* — lighting, composition,
layout patterns — then apply the Arabic rules on top.

Searching with Arabic terms returns nothing and will warn you. Translate the
concept to English first: `مطعم فخم` → `luxury restaurant interior`.

## Read structure, not content

The single most important habit: **borrow how an exemplar is built, never what
it depicts.** A fitness-app template teaches you zone structure and element
counts; it must not put "PulseFit" or "calories burned" in your restaurant
poster. The generator enforces this, and you should too when reading by hand.

Worth extracting from an exemplar:
- Which zones exist and what they are called
- Element counts ("exactly 4 cards")
- How the style/mood block is phrased
- Aspect ratio and framing conventions

Worth ignoring: its brand names, its product nouns, its specific copy.

## Structure types

| Type | Count | Meaning |
|---|---|---|
| Template | 6,269 | carries `{argument}` slots |
| Other | 439 | prose, unclassified |
| Flat prose | 254 | single-paragraph description |
| Template-JSON | 252 | JSON that also has argument slots |
| JSON | 101 | strict-parsing JSON objects |

**Note:** JSON in the corpus is an *authoring* format. Black Forest Labs' own
guidance is to flatten JSON to prose before sending, and OpenAI says all formats
work but to prefer a skimmable template. Do not send raw JSON as a prompt.

## Maintenance

```bash
python scripts/refresh.py --apply
```
```bash
python scripts/calibrate_pqs.py
```

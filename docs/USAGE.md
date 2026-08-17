# Using Rasm · دليل الاستخدام

Everything the [README](../README.md) summarises, in working detail.

- [The 60-second version](#the-60-second-version)
- [How a session actually goes](#how-a-session-actually-goes)
- [The 12 commands](#the-12-commands)
- [Writing Arabic that renders](#writing-arabic-that-renders)
- [Choosing a model](#choosing-a-model)
- [The corpus & CLI](#the-corpus--cli)
- [Reading the quality score](#reading-the-quality-score)
- [Installing & staying in sync](#installing--staying-in-sync)
- [Troubleshooting](#troubleshooting)

---

## The 60-second version

1. Type `/rasm` and say what you want, in Arabic or English.
2. Answer 2–4 questions. Paste your **exact** Arabic copy when asked — Rasm
   will not invent it.
3. Confirm the spec it plays back.
4. Take the prompt, the model name, and the size. Generate.
5. Run the proofing checklist on the Arabic before you ship it.

```
/rasm بوستر لافتتاح مقهى في الرياض
```

Jump straight to a specialist when you already know the job:

```
/rasm-poster       /rasm-menu        /rasm-social
/rasm-arabic       /rasm-brand       /rasm-product
```

---

## How a session actually goes

### 1 · You ask, vaguely. That's fine.

> **You:** `/rasm بوستر لمقهى`

### 2 · The grill — 2 to 4 questions

Only what's missing and load-bearing. Anything you already said is skipped.
Questions arrive as pickable options, not an interrogation in prose.

> **Rasm:**
> - What exactly should the poster say? *(paste the verbatim Arabic)*
> - Where does it live — Instagram story, printed A3, or shopfront?
> - Photographic plate or flat graphic?
> - Occasion — opening, Ramadan, seasonal offer?

### 3 · One follow-up round — always

Your answers create new forks. This round catches them.

> **Rasm:** You said Ramadan. Which moment — the crescent announcement, an
> iftar invitation, or Eid? They're three different images.

### 4 · The spec, played back

One glance to catch a wrong assumption before anything is generated.

```
Language   Arabic only · MSA
Text       "افتتاح قريباً" (verbatim) · no tashkeel · Western numerals
Surface    Instagram story · 9:16 · 1080×1920
Style      Geometric Kufi, desert-neutral palette
Model      GPT Image 2 (gpt-image-2) — Arabic text-in-image
Layout     RTL · right-aligned · logo top-right
```

### 5 · The output

A copyable prompt, plus:

- **Model** + exact id + why it was routed there
- **Size** validated against that model's real limits
- **Arabic proofing checklist**
- **One next lever** — the single change to make if it misses

---

## The 12 commands

### `/rasm` — the front door
Grills, routes, generates. Hands off to a specialist when the job clearly
belongs to one. Start here when unsure.

### `/rasm-arabic` — when lettering *is* the design
Calligraphy, wordmarks, RTL typography, bilingual lockups. Carries the four
mandatory Arabic clauses and the script-style cheat sheet.

```
/rasm-arabic خط ثلث لكلمة "كرم" لشعار مطعم
```

### `/rasm-brief` — grill only, no prompt
Produces a **locked brief** you can review, edit, or hand to someone else.
Use when the request is vague or several people must agree first.

### `/rasm-social` — ratios and safe zones
Knows the 250px top / 350px bottom story safe zone, TikTok's right rail,
the YouTube duration chip, and the LinkedIn banner avatar cutout.

| Surface | Ratio | Pixels |
|---|---|---|
| IG feed square | 1:1 | 1080×1080 |
| IG feed portrait | 4:5 | 1080×1350 |
| Story / Reel / TikTok / Snap | 9:16 | 1080×1920 |
| YouTube thumbnail | 16:9 | 1280×720 |
| LinkedIn banner | ~4:1 | 1584×396 |

### `/rasm-poster` — typographic hierarchy first
Hero line (2–5 Arabic words) → subhead → detail block → footer. Print sizing,
Hijri vs Gregorian dates, and Saudi seasonal vocabulary.

### `/rasm-menu` — hospitality
Two jobs: **dish photography** (lighting, angle, freshness cues, Gulf dish
names) and **menu layout** — where it tells you the truth that a full rendered
menu is dozens of short strings, i.e. the worst case for AI text.

### `/rasm-brand` — logos and identity
Wordmark / lettermark / lockup / emblem. Says plainly that a rendered logo is a
*concept*, not a production asset, and offers the low-risk single-letter Kufi
monogram route.

### `/rasm-product` — packshot, hero, lifestyle
Marketplace rules (pure white, 85% fill, no props), material accuracy, and the
hard truth about Arabic on curved packaging.

### `/rasm-edit` — references and identity
The preserve-list pattern, ordinal reference addressing, face preservation, and
English→Arabic localisation of an existing image.

### `/rasm-search` — the corpus
### `/rasm-model` — routing + size validation
### `/rasm-help` — the index

---

## Writing Arabic that renders

### The four clauses

Every Arabic prompt Rasm writes carries all four. If you write prompts by hand,
copy this shape:

```
The text reads exactly "افتتاح قريباً" — reproduce these characters verbatim.
No Latin text anywhere in the image.

Fully connected cursive Arabic with correct contextual letterforms
(initial, medial, final), proper ligatures, no broken or detached letters.

Right-to-left composition: text right-aligned, entry point top-right,
any sequence or arrow flowing right to left.

Undiacritised — no tashkeel.
```

### Length ceilings

| Role | Target |
|---|---|
| Headline | 2–5 words |
| Subhead | ≤ 8 words |
| Button / label | 1–3 words |
| Body paragraph | **don't** — split into short blocks |

### Script styles — the reliable tokens

| Token | Use for |
|---|---|
| `geometric Kufi` | logos, modern minimal, architecture |
| `Naskh` | body text, editorial, readable |
| `Thuluth` | titles, ceremonial, prestige |
| `Diwani` | luxury, invitations, certificates |
| `Ruqʿah` | casual, street signage |

Font *names* (Cairo, Tajawal, Amiri, Reem Kufi) are **style hints**, not
specifications. Pair them with a descriptor:

> `modern Arabic sans-serif, clean geometric letterforms, Tajawal style`

### Numerals

Western `0-9` for Gulf commercial work; Arabic-Indic `٠-٩` for traditional,
heritage, or Egyptian/Levantine contexts. **Never mix them** in one design.

### Bilingual

Arabic leads, set **110–125%** of the Latin size, on separate lines, aligned to
a shared axis. Never interleaved inline — that triggers bidi ordering bugs.

### The proofing checklist

Run this on every Arabic output:

1. Are all letters **connected** where they should be?
2. Is the reading order **right-to-left**?
3. Are dots correct on ب/ت/ث and ن/ي?
4. Did any **Latin** text sneak in?
5. Do the numerals match the system you asked for?

### When to go text-free

For print, a client, or a paying customer — generate the artwork **without
text** and set the Arabic type in Illustrator/Figma. Even at high accuracy the
failures land on letter connections, which is exactly what a native reader sees
first. This is what working Arabic designers do.

**Always** for Qur'anic text, the shahada, and the Saudi flag.

---

## Choosing a model

Ask `/rasm-model`, or apply the order yourself — first match wins:

1. Readable **Arabic** in the image → **GPT Image 2**
2. Reference images / character consistency → **Nano Banana Pro**
3. Translate-text-in-image → **Nano Banana Pro**
4. **Exact element counts**, precise arrangement → **GPT Image 2**
5. English text-dense layouts → **GPT Image 2**
6. Structure-preserving edits → **GPT Image 2**
7. Mood-led from a thin brief → **Nano Banana Pro**

Neither model is reliable on exact counts much past **five**.

### GPT Image 2 size limits

- Both edges a multiple of **16**
- Longest edge **under 3840px**
- Total pixels **655,360 – 8,294,400**
- Ratio **≤ 3:1**; above 2560×1440 is officially experimental

```bash
python -c "from renderers import validate_gpt_image_2_size as v; print(v(1536,1024) or 'OK')"
```

Set `quality: high` for small text, dense panels, and identity-sensitive edits.

### Porting a prompt between them

- **To GPT Image 2:** *add specification.* It defaults badly on anything you leave out.
- **To Nano Banana Pro:** *remove contradictions.* It resolves conflict by picking one.

---

## The corpus & CLI

```bash
python cli.py search "glassmorphism dashboard" --limit 5
python cli.py guide "Poster / Flyer"
python cli.py generate "cafe opening poster" "Poster / Flyer"
python cli.py random --category "Product Marketing"
python cli.py stats
python cli.py feedback
```

Add `--json` to any command for structured output.

**Search in English.** The corpus is English-only by policy, and that is not a
limitation for Arabic work — the *prompt* is written in English because both
models handle English instructions best, while the *text rendered inside the
image* is Arabic, quoted verbatim. Translate the concept first:
`مطعم فخم` → `luxury restaurant interior`.

**Read structure, not content.** Borrow how an exemplar is built — zones,
element counts, framing — never what it depicts.

---

## Reading the quality score

Six factors, geometric mean, percentile-graded against the generator's own
output:

| Factor | Weight | Measures |
|---|---|---|
| Goal fidelity | **0.30** | does the prompt actually reflect your ask |
| Coverage | 0.20 | required slots filled for this category |
| Specificity | 0.20 | rare, concrete terms vs filler |
| Atomic density | 0.20 | checkable assertions per word (anti-padding) |
| Non-redundancy | 0.10 | internal repetition |
| Penalty | ×  | contradictions, vague booster words |

A **longer goal scoring lower** is correct signal, not a bug — goal fidelity is
telling you the renderer dropped part of your ask.

---

## Installing & staying in sync

```bash
python scripts/install-global.py            # link everywhere
python scripts/install-global.py --dry-run  # preview
python scripts/install-global.py --list     # show discovered agents
```

Covers 9 agents across two shapes: directory-based get junctions, opencode gets
hard links (one inode), zcode gets a generated pointer. Idempotent, prunes old
names, never clobbers a real directory you installed by hand.

**Edit the repo → live in every agent instantly.** No copy step.

### Corpus maintenance

```bash
python scripts/fetch-db.py                    # pinned release + checksum
python scripts/refresh.py --apply             # scrape new ids, upsert, rebuild FTS
python scripts/calibrate_pqs.py               # re-fit scoring after corpus changes
```

Every DB script is copy-safe by default and needs `--apply` to touch the live
database.

---

## Troubleshooting

**Commands don't appear.** Re-run `install-global.py`, then restart the agent —
most scan their skills directory at startup.

**`no such table: prompts`.** The corpus isn't downloaded. Run
`python scripts/fetch-db.py`, or point `HIGGSFIELD_DB` at the file.

**Arabic comes out broken.** Check you're on **GPT Image 2**, that the RTL and
letter-shaping clauses are present, that the string is short, and that tashkeel
is off. If it still breaks, the string is likely too long — go text-free.

**The layout is left-to-right.** The RTL clause is missing. Models render Arabic
glyphs correctly and still default the page to LTR.

**Output ignores part of my ask.** Look at the goal-fidelity factor in the
score — that's it telling you which part got dropped. Put the essential detail
earlier; the tail of a long prompt is the least reliable part.

**Arabic search returns nothing.** Expected — the corpus is English-only.
Translate the concept, or set `translate_hook`.

**Non-English goal warning.** Working as intended: rather than returning a
confident irrelevant result, it says retrieval was skipped. Supply a translation
hook or an English goal.

---

## Contributing knowledge

Model claims live in `data/*.json` and `profiles/*.yaml`, each carrying
`_source`, `_date`, and `_confidence`. Anything you add needs all three, and a
vendor URL beats a blog post.

Design rules live in `commands/_shared/`. Label the evidence tier — `[VENDOR]`,
`[TEST]`, `[PAPER]`, `[CRAFT]` — so the next person knows how much weight it
carries.

Corpus statistics are **not** evidence that a technique works. They measure what
people posted to a gallery.

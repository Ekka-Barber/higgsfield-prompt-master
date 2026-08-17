<div align="center">

# رسم · Rasm

**Arabic-first prompt engineering for AI image models**

*rasm* (رسم) — *drawing, design.* Literally what it makes.

[![tests](https://img.shields.io/badge/tests-156%20passing-2ea44f?style=flat-square)](#testing)
[![corpus](https://img.shields.io/badge/corpus-7%2C315%20prompts-1B4332?style=flat-square)](#the-corpus)
[![models](https://img.shields.io/badge/models-GPT%20Image%202%20·%20Nano%20Banana%20Pro-4A5568?style=flat-square)](#model-routing)
[![python](https://img.shields.io/badge/python-3.10+%20·%20stdlib%20only-3776AB?style=flat-square)](#requirements)
[![license](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

**12 specialist slash-commands · 9 AI agents · zero dependencies**

</div>

---

## What this is

Most AI image prompts fail the same way: they describe a subject and stop. Rasm
turns a vague ask into a specification — by interrogating you, grounding the
result in a corpus of 7,315 real prompts, and routing to the model that will
actually render it.

It is **Arabic-first**. Not translated-English-with-Arabic-bolted-on: it knows
that models render Arabic glyphs correctly and *still lay the page out
left-to-right*, that Arabic letters take four contextual forms, that Arabic
justifies by stretching letters rather than spaces, and that a diacritic at
small size is a coin flip. English is fully supported — it just isn't the
default.

```
اعمل لي بوستر لافتتاح مقهى
        │
        ▼
  ┌───────────────┐   2-4 questions, then one confirmation follow-up
  │   THE GRILL   │   never invents your Arabic copy
  └───────┬───────┘
          ▼
  ┌───────────────┐   7,315 exemplars — borrows STRUCTURE, never subject
  │   RETRIEVAL   │   scrubs the donor's brand out of your prompt
  └───────┬───────┘
          ▼
  ┌───────────────┐   Arabic text → GPT Image 2 (vector glyph pathway)
  │    ROUTING    │   references/mood → Nano Banana Pro
  └───────┬───────┘
          ▼
  ┌───────────────┐   RTL clause · letter-shaping clause · verbatim text
  │    RENDER     │   validated size · proofing checklist
  └───────────────┘
```

---

## Quick start

```bash
git clone https://github.com/Ekka-Barber/rasm.git && cd rasm
```

Fetch the corpus (57 MB → 30 MB, distributed via Releases, not git):

```bash
python scripts/fetch-db.py
```

Install into every AI agent on your machine:

```bash
python scripts/install-global.py
```

Then, in any agent:

```
/rasm-help
```

That's it. No pip install, no API key, no dependencies — the whole engine is
Python standard library.

---

## The 12 commands

| Command | For |
|---|---|
| **`/rasm`** | Start here. Grills, routes, generates. |
| **`/rasm-arabic`** | When the Arabic lettering *is* the design — calligraphy, wordmarks, RTL typography |
| **`/rasm-brief`** | Interrogation only. Produces a locked spec, no prompt |
| **`/rasm-social`** | Instagram, Snapchat, TikTok, X, LinkedIn, YouTube — ratios and safe zones |
| **`/rasm-poster`** | Posters, flyers, banners, signage, event announcements |
| **`/rasm-menu`** | Restaurants and cafés — dish photography, menu boards, food styling |
| **`/rasm-brand`** | Logos, Arabic wordmarks, monograms, identity systems |
| **`/rasm-product`** | Packshots, hero shots, lifestyle, marketplace listings |
| **`/rasm-edit`** | Edit an existing image — references, face lock, background swap, localisation |
| **`/rasm-search`** | Explore the corpus for real exemplars |
| **`/rasm-model`** | Which model, and is my size valid? |
| **`/rasm-help`** | The index |

Full walkthrough with worked examples → **[docs/USAGE.md](docs/USAGE.md)**

---

## What makes it Arabic-first

Six things a generic prompt tool doesn't know.

**1 · The RTL layout trap.** Models render Arabic *glyphs* correctly and then
lay the *page* out left-to-right anyway — logo top-left, ragged-left text,
arrows pointing the wrong way. Every Arabic prompt carries an explicit RTL
clause because the model will not infer it.

**2 · Letter shaping.** Arabic is cursive; each letter takes up to four
contextual forms (isolated, initial, medial, final) and neighbours join. The
documented failures are broken connections and scrambled dots on ب/ت/ث.

**3 · Kashida.** Arabic justifies by elongating the connecting stroke *inside*
a word — not by widening word spaces. A model that stretches Arabic spacing
produces something a native reader clocks instantly.

**4 · Tashkeel economics.** Every diacritic is another error surface: full
tashkeel at small sizes in dense paragraphs runs **~1 glyph error in 20**, even
on the best model. Omitted by default, and the reason is stated.

**5 · Script styles beat font names.** Naming a font barely works — research
finds typographic intent is *"often ignored or only weakly reflected."* But
**Kufi, Naskh, Thuluth, Diwani, Ruqʿah** are script *categories*, densely
present in training data, and they work.

**6 · Numerals are a decision.** Western `0-9` (Gulf commercial) vs Arabic-Indic
`٠-٩` (traditional). Mixed in one design, it reads as a mistake. Never guessed
on a menu, price, or date.

Plus the part most tools skip: **sacred content is never rendered by a model.**
Qur'anic text, the shahada, and the Saudi flag get the artwork-without-text
treatment, because an AI letter error in sacred text isn't a quality bug.

---

## Model routing

Two targets, one decision, first match wins.

| | **GPT Image 2** | **Nano Banana Pro** |
|---|---|---|
| id | `gpt-image-2` | `gemini-3-pro-image` |
| **Arabic text** | **~99% char accuracy** | ~94%, spacing errors |
| Exact counts, spatial control | ✅ | reorganises for balance |
| Reference compositing | text wins conflicts | **image wins — up to 6 obj / 5 chars** |
| Mood from a thin brief | flat, centred | **composes with opinion** |
| Reads your brief | literally, clause by clause | holistically, for intent |

**Arabic text-in-image → GPT Image 2.** It composes glyphs as *vector shapes*
through a dedicated typographic pathway rather than inferring letterforms
during diffusion, so contextual shaping is structural rather than lucky.

> **This was corrected.** Rasm originally routed Arabic to Nano Banana Pro,
> reasoning that Google documents `ar-EG` support while OpenAI's docs never
> mention Arabic. That is an argument from silence, and it was wrong. Tested
> behaviour beats absent documentation. The correction is recorded in
> [`commands/_shared/arabic-rules.md`](commands/_shared/arabic-rules.md) rather
> than quietly rewritten.

### Universal rules

- **Negative prompts do not exist.** Not on GPT Image 2, not on Nano Banana Pro,
  not on FLUX — all three vendors say so. Negation often *summons* the thing.
  Describe the positive state: not `"no cars"` → `"an empty, deserted street"`.
- **Never `REFERENCE_0`.** Address inputs by ordinal and role.
- **No booster tokens.** `masterpiece, 8k, trending on artstation` is
  Stable-Diffusion-era noise.
- **60–120 words** is the sweet spot; never put a critical detail last.

---

## The corpus

| | |
|---|---|
| Searchable prompts | **7,315** |
| Curated master prompts | 62 |
| Categories | 18 |
| Database | 30.7 MB SQLite + FTS5 |

Retrieval borrows **structure** — zone schemas, element counts, framing
conventions — and never subject matter. A fitness-app template teaches layout;
it must not put *"PulseFit"* or *"calories burned"* into your restaurant poster.
That scrubbing is enforced in code and covered by tests.

```bash
python cli.py search "glassmorphism dashboard" --limit 5
python cli.py guide "Poster / Flyer"
python cli.py generate "cafe opening poster" "Poster / Flyer" --json
python cli.py stats
```

---

## Quality scoring

Every generated prompt is scored by **PQS** — six factors combined with a
*geometric* mean, so one failed dimension can't be masked by the others:

`coverage · specificity · atomic density · non-redundancy · goal fidelity · − penalty`

Goal fidelity carries the heaviest weight, because it is the only factor that
notices when a generator ignores its input. Grades are percentiles against the
generator's own output distribution — not hardcoded cutoffs.

```
'x'                                     10  D   0.0
'moody cinematic portrait'              84  C   41.7
'analytics dashboard, 4 KPI cards'      73  A   75.0
'luxury watch hero shot'                92  A+  91.7
```

The release gate is **cross-goal discrimination**: does each prompt match *its
own* goal better than someone else's? Currently **0.862** against a 0.30 target.

---

## How it stays in sync across 9 agents

`install-global.py` links — never copies. Copies drift, and a missed copy means
an agent silently runs yesterday's rules.

| Shape | Agents | Mechanism |
|---|---|---|
| Directory | `.agents` `.claude` `.codex` `.cursor` `.hermes` `.gemini`×2 | junction / symlink |
| Flat file | **opencode** | hard link — one inode |
| Flat file | **zcode** | generated pointer, nothing duplicated |

**A commit here is a release to every agent.** Idempotent, never clobbers a
hand-installed directory, prunes links from previous names, and has `--dry-run`.

---

## Requirements

Python **3.10+**. That's the whole list — `sqlite3`, `re`, `json`, `pathlib`
from the standard library. No torch, no transformers, no API keys, no network
calls at runtime.

Optional: `pytest` to run the suite.

## Testing

```bash
python -m pytest -q                              # 156 tests
python scripts/verify-generation-diversity.py    # release gate
```

## Evidence policy

Every model claim carries `_source`, `_date`, and `_confidence`. Claims from
vendor documentation are marked separately from practitioner testing and from
corpus statistics — because **corpus frequency is not evidence that a technique
works.** It measures what people posted to a gallery.

That distinction is the reason this project exists in its current form: an
earlier version inferred *"JSON prompts are best"* from 54% of the corpus being
JSON. Vendor docs say otherwise, and Black Forest Labs explicitly instructs
users to flatten JSON to prose before sending.

Research trail → [`RESEARCH-2026-08.md`](RESEARCH-2026-08.md) ·
[`research/SOURCE_TRUTH.md`](research/)

## Credits & licence

Corpus harvested from public prompt galleries on youmind.com. Model guidance
derived from OpenAI, Google and Black Forest Labs documentation plus published
comparative testing — all cited inline.

Not affiliated with OpenAI, Google, or any model vendor.

MIT — see [LICENSE](LICENSE).

<div align="center">

**صُنع للمصممين العرب** · Built for Arabic designers

</div>

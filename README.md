# Higgsfield Prompt Master

> GPT Image 2 / Nano Banana Pro prompt reference & generation engine — built from **7,613 real prompts** scraped from youmind.com.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Prompts](https://img.shields.io/badge/corpus-7%2C613%20prompts-green)](#corpus)
[![Categories](https://img.shields.io/badge/categories-26-orange)](#categories)

## What this is

A stdlib-only Python engine that retrieves, scores, and generates image-generation prompts:

1. **Corpus** — 7,613 scraped prompts in a SQLite DB with an FTS5 full-text index. 6,337 curated rows are searchable by default; 1,276 harvested rows become searchable after running the migration scripts (see [Maintenance](#maintenance)).
2. **Retrieval** — FTS5 search with quote-safe sanitization and 3-strategy progressive fallback, plus filtered `search()`.
3. **Generation** — retrieves goal-relevant exemplars, extracts a prompt IR (`ir.py`), fills slots from your goal + intelligence layers, and renders model-native prose (`renderers.py`).
4. **Quality scoring** — PQS 6-factor weighted score (`pqs.py`), graded as percentiles against the corpus distribution (`pqs_calibration.json`).
5. **Model routing** — exactly two targets: `gpt-image-2` and `gemini-3-pro-image` (Nano Banana Pro).

Works standalone or as an agent skill (copy the repo anywhere; nothing is installed).

## Requirements

- **Python 3.10+** — standard library only, no pip dependencies, no `requirements.txt`.
- The corpus DB at `references/gpt-image2-prompts-full.db` (~55 MB, gitignored). It ships with the working tree you obtained; if missing, point `HIGGSFIELD_DB` at a copy or run `python scripts/fetch-db.py` (downloads the pinned GitHub Release asset and SHA-256-verifies it against the committed `references/checksums.txt`).

> Note: this repo is **not** an importable Python package (the directory name is hyphenated). `import higgsfield_prompt` resolves to the module `higgsfield_prompt.py` once the repo root is on `sys.path`. There is deliberately no `__init__.py`; the version lives only in `SKILL.md` frontmatter.

### Database path resolution

`HiggsfieldPromptMaster()` locates the corpus in this order (first existing file wins; a missing DB raises `FileNotFoundError` listing every candidate — it never silently creates one):

1. `HIGGSFIELD_DB` env var — explicit override (must exist; no fallback if it doesn't).
2. `<repo root>/references/gpt-image2-prompts-full.db` — relative to `higgsfield_prompt.py`.
3. Legacy skill locations: `~/.hermes/skills/higgsfield-prompt-master/references/…`, then `~/.agents/skills/higgsfield-prompt-master/references/…`.

Reads open the DB via a read-only URI (`file:…?mode=ro`); only `enrich_all()` reopens read-write.

## Usage

Run everything from the repo root.

### Search the corpus

```python
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()

# Filtered search (query terms OR'd across title/description/prompt_text)
for p in hpm.search("minimalist product photography", limit=5):
    print(f"[{p.id}] {p.title} ({p.structure_type}, {p.length_chars} chars)")

# Full-text search (FTS5, quote-safe, progressive fallback)
hits = hpm.fts_search("dashboard glassmorphism", limit=10)

# Filters: category / model / structure / techniques
ui = hpm.search(category="App / Web Design", structure="JSON", limit=5)
cam = hpm.search(techniques=["Camera Specs", "Lighting details"], limit=5)
```

`search()` / `fts_search()` return `Prompt` dataclass objects (`id`, `title`, `description`, `prompt_text`, `categories`, `model`, `slug`, `structure_type`, `length_chars`, `techniques`).

### Generate a prompt

```python
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()
result = hpm.generate_prompt(
    goal="Premium skincare serum product shot",
    category="Product Marketing",   # drives photo + marketing intelligence
    structure="Template",           # biases exemplar selection only
    style="Clean, clinical, premium",
    aspect_ratio="4:5",             # auto-detected from marketing layer if omitted
)

result["prompt"]               # the rendered prompt text
result["model_recommendation"] # {"id": "gpt_image_2"|"nano_banana_pro", "model_id": ..., "display_name": ..., "signal": ...}
result["quality_score"]        # PQS dict: {"total": float, "grade": "A+".."F", ...}
result["source_prompt_ids"]    # real corpus IDs used as retrieval evidence
result["aspect_ratio"], result["length"], result["intelligence"]
```

Pipeline: goal-relevant FTS retrieval → IR extraction + donor merge (`ir.py`) → slot fill (goal lead, style, mood, aspect ratio, photo/marketing layers; camera fragments scrubbed for non-photo categories) → model-native rendering (`render_gpt_image_2` / `render_nano_banana_pro`) → PQS scoring.

### Analytics

```python
hpm.stats()                                  # corpus-wide counts
hpm.category_guide("App / Web Design")       # structure/technique/length deep-dive
hpm.compare_models("GPT Image 2", "Nano Banana")
hpm.random_prompt(category="Comic / Storyboard")
```

Module-level convenience wrappers (`search_prompts`, `get_templates`, `analyze_patterns`, `generate_prompt`, `random_prompt`) and a CLI (`python higgsfield_prompt.py stats|search|guide|generate|random|enrich`) also exist.

### Run the demo

```bash
python demo.py
```

## Corpus

| Metric | Value |
|---|---|
| Total rows | **7,613** |
| Searchable (curated) | 6,337 — the other 1,276 harvested rows unlock via `scripts/migrate_status.py` + `scripts/rebuild_corpus.py` |
| GPT Image 2 | 5,008 (79.0% of searchable) |
| Nano Banana | 1,329 (21.0%) |
| Categories | 26 |
| Structures | Template 4,846 · JSON 636 · Other 606 · Flat prose 249 |
| Avg prompt length | ~1,457 chars |
| ID range | 13,440 – 28,686 |

Counts from `hpm.stats()` on the shipped DB (legacy schema, searchable = `has_prompt = 1`). English-only: 2,240 non-English prompts were removed after analysis showed zero unique value ([`references/non-english-analysis.md`](references/non-english-analysis.md)).

## Categories

Top categories by searchable prompt count: Social Media Post (1,978) · Product Marketing (1,230) · Poster / Flyer (799) · Profile / Avatar (658) · Comic / Storyboard (570) · Game Asset (450) · Infographic / Edu Visual (318) · App / Web Design (133) — plus 18 more (full list in [`references/gpt-image2-categories.json`](references/gpt-image2-categories.json)). Category deep-dive guides live in [`references/`](references/).

## Architecture

```
higgsfield_prompt.py    # engine: read-only DB open, search/FTS, generation pipeline, model routing, CLI
ir.py                   # prompt intermediate representation + extract_ir (JSON/template/prose parsers)
renderers.py            # render_gpt_image_2 / render_nano_banana_pro prose renderers
pqs.py                  # 6-factor prompt quality scorer (+ pqs_calibration.json percentiles)
intelligence.py         # loader/accessors for the intelligence layers below
data/                   # editable intelligence JSON (photography, marketing, art direction, gpt_image_2, nano_banana_pro; claims source-cited)
                        # plus categories.json — the category registry (canonical names, aliases, photo/marketing routing)
profiles/               # versioned capability profiles (gpt-image-2@<date>.yaml, nano-banana-pro@<date>.yaml) — source of truth for the model claim JSONs; sync via scripts/sync_profiles.py
demo.py                 # runnable tour
scripts/                # scraper, corpus maintenance, regression tests, diversity gate
references/             # corpus DB, category guides, scraping + analysis write-ups
research/               # SOURCE_TRUTH.md knowledge base the v2 rebuild was verified against
```

## Maintenance

```bash
# Re-scrape new prompts (RSC flight-data extractor, no browser)
python scripts/rsc-prompt-extractor.py --start 27000 --end 30000

# All maintenance scripts are copy-safe by default; add --apply to touch the live DB
python scripts/purge_boilerplate.py   # remove share-widget garbage + exact duplicates
python scripts/migrate_status.py      # add status column; harvested rows become searchable
python scripts/rebuild_corpus.py      # enrich all rows + FTS rebuild + VACUUM

# Gates — run after any pipeline change
python scripts/verify-generation-diversity.py   # diversity + duplication regression gate
python demo.py
```

## Reproducible build

The corpus DB is rebuildable from the scraped JSONL export — no binary blob is
required to reproduce it. The 55 MB DB and the JSONL export are **distributed
via [GitHub Releases](https://github.com/USER/higgsfield-prompt-master/releases)
only** (both are gitignored); the build script reproduces the DB from committed
code either way.

```bash
# 1. Export the live DB to the JSONL export (the Releases artifact)
python scripts/build-db.py --export          # -> references/gpt-image2-prompts.jsonl

# 2. Rebuild: create schema -> ingest JSONL -> enrich -> FTS rebuild -> VACUUM
#    -> checksum report + stats-parity gate (row ids, category/model/structure
#    counts vs the JSONL). Copy-safe: builds to a temp DB, live DB untouched.
python scripts/build-db.py

# Replace the live DB with a verified rebuild (previous copy kept as *.db.bak)
python scripts/build-db.py --apply
```

The rebuild is byte-deterministic (same JSONL + same code → same DB sha256) and
prints the DB sha256, JSONL sha256, and a row-content digest — compare the JSONL
sha256 against the published Releases checksum to verify an export's authenticity.

Installers can fetch the pinned release DB directly (refuses on any SHA-256
mismatch against `references/checksums.txt`; `--tag` overrides the default pin):

```bash
python scripts/fetch-db.py
```

## License

MIT — see [`LICENSE`](LICENSE). The prompt corpus is scraped from publicly accessible web pages and is provided for research and educational purposes.

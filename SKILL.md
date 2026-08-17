--- 
name: rasm-engine
description: "Rasm (رسم) — Arabic-first prompt engineering for AI image models. Corpus-grounded prompt generation for GPT Image 2 and Nano Banana Pro. The /rasm-* commands are the user-facing surface; this is the engine and corpus."
version: 2.2.0  # single source of truth — the only version declaration in this repo
category: media
---

# Rasm · رسم — the engine
## Arabic-first prompt engineering for AI image models

> **This is the engine and corpus.** The user-facing surface is the twelve
> `/rasm-*` commands in `commands/` — start at `/rasm` or `/rasm-help`.
> See [README.md](README.md) and [docs/USAGE.md](docs/USAGE.md).

> Built from **7,315 searchable** English-only prompts harvested from public
> galleries on youmind.com, plus 62 curated master prompts. Non-English prompts
> were removed after analysis found no techniques absent from the English set.
>
> The corpus being English is not a limitation for Arabic work: the **prompt**
> is written in English because both target models handle English instructions
> best, while the **text rendered inside the image** is Arabic, quoted verbatim.

---

## 📊 Corpus Statistics (English-Only — verified August 2026)

> **English-only policy:** Non-English prompts (2,240 Japanese/Korean/Arabic) were permanently removed after analysis confirmed they contained zero unique techniques, categories, or structures not present in the English corpus. The scraper (`scripts/rsc-prompt-extractor.py`) has a shared `langcheck.is_english()` filter and will never save non-English prompts. See `references/non-english-analysis.md` for the comparison data.

| Metric | Value |
|--------|-------|
| **Total Prompts** | 7,613 rows = 6,337 curated searchable + 1,276 harvested (Aug 2026; unlock via `scripts/migrate_status.py` + `scripts/rebuild_corpus.py`) |
| GPT Image 2 | 5,008 (79.0% of searchable) |
| Nano Banana | 1,329 (21.0%) |
| **Categories** | 26 |
| **Avg Prompt Length** | ~1,457 chars (searchable rows) |
| **ID Range** | 13,440 – 28,686 |

> Generated from `hpm.stats()` on the shipped DB (legacy schema, searchable = `has_prompt = 1`).

### Structure Distribution (searchable rows, from `hpm.stats()`)
- **Template (76.5%)** — 4,846 prompts with `{argument name="..." default="..."}` syntax. See `references/parameterized-templates.md`, `references/multi-panel-campaigns.md`
- **JSON (10.0%)** — 636 prompts as structured JSON objects with type/style/layout
- **Other (9.6%)** — 606 hybrid/mixed formats
- **Flat Prose (3.9%)** — 249 natural language descriptions

### Top Techniques (from `hpm.stats()`, % of 6,337 searchable)
| Technique | Frequency | Description |
|-----------|-----------|-------------|
| Arguments/Templates | 84.8% | `{argument}` parameterized syntax — dominant paradigm |
| Mood/Atmosphere | 77.3% | Cinematic, moody, vibrant, ethereal, gritty |
| Material/Texture | 73.6% | Glass, metal, matte, glossy, fabric, organic |
| Layout/Composition | 68.2% | Grid, alignment, center, balanced, rule of thirds |
| Lighting details | 61.8% | Golden hour, studio, soft, dramatic, volumetric |
| Camera specs | 53.1% | Lens mm, aperture, depth of field |
| UI/UX terms | 28.4% | Dashboard, component, navbar, design system |
| Aspect ratio specs | 24.6% | `--ar` flags and N:N ratios |
| Color palette | 22.6% | Palettes, gradients, monochrome, complementary |
| Reference images | 18.5% | "inspired by", "style of" |
| Typography | 18.1% | Font styles, hierarchy, lettering, text effects |
| Negative prompts | 13.0% | What to avoid, exclusions |
| JSON structure | 10.0% | Leading-`{` structured specs |
| Step-by-step | 0.6% | First/then/next sequences |

**Avg techniques per prompt:** 5.5.

### Top Categories (searchable rows)
1. **Social Media Post** (1,978) — Instagram, LinkedIn, Twitter/X, TikTok
2. **Product Marketing** (1,230) — E-commerce, ads, hero shots
3. **Poster / Flyer** (799) — Event, movie, concert, promotional
4. **Profile / Avatar** (658) — Character, headshot, identity
5. **Comic / Storyboard** (570) — Sequential art, panels, narrative
6. **Game Asset** (450) — Sprites, UI, environments, items
7. **Infographic / Edu Visual** (318) — Data viz, charts, explanations
8. **App / Web Design** (133) — UI mockups, dashboards, landing pages

## 🔧 Skill Usage

### Search Prompts
```python
from higgsfield_prompt import search_prompts

# Search by category
results = search_prompts(category="App / Web Design", limit=10)

# Search by technique
results = search_prompts(techniques=["JSON structure", "Arguments/Templates"])

# Full-text search
results = search_prompts(query="dashboard UI glassmorphism", limit=5)

# Search by model
results = search_prompts(model="GPT Image 2")
```

### Get Prompt Templates by Category
```python
from higgsfield_prompt import get_templates

# Get best templates for a category
templates = get_templates("App / Web Design", structure="JSON")
templates = get_templates("Product Marketing", structure="Template")
templates = get_templates("Social Media Post", structure="Flat prose")
```

### Analyze Prompt Patterns
```python
from higgsfield_prompt import analyze_patterns

# What techniques work best for a category?
patterns = analyze_patterns(category="App / Web Design")
# Returns: technique frequencies, avg length, structure preferences, example prompts
```

### Generate Optimized Prompts (Corpus-Grounded + Model-Native Rendering)

**`generate_prompt()` returns a DICT, not a string.** The generator retrieves goal-relevant corpus exemplars, extracts their intermediate representation, and renders model-native prose for the routed model (GPT Image 2 or Nano Banana Pro).

```python
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()
result = hpm.generate_prompt(
    goal="Premium skincare serum product shot",
    category="Product Marketing",     # drives photo + marketing intelligence
    structure="Template",             # biases exemplar selection only
    style="Clean, clinical, premium", # drives mood inference
    aspect_ratio="4:5"                # auto-detected from marketing layer if omitted
)

# result is a DICT with:
result["prompt"]              # → the rendered prompt text
result["model_recommendation"] # → {"id": "gpt_image_2"|"nano_banana_pro", "model_id": "gpt-image-2"|"gemini-3-pro-image", "display_name": ..., "signal": why-routed}
result["aspect_ratio"]         # → "4:5"
result["quality_score"]        # → PQS dict: {"total": <float>, "grade": "A+".."F", ...}
result["intelligence"]         # → {"photography": True, "marketing": True, "mood": "..."}
result["source_prompt_ids"]    # → [18464, 20293, ...] real corpus IDs used as reference
result["length"]               # → 1812 (chars)
```

**How it works (pipeline — rebuilt US-013):**
1. **Keyword extraction** — `_extract_keywords()` strips stop words AND domain filler, prioritizes design-relevant terms, returns top 6 keywords from the goal
2. **Retrieval** — FTS progressive fallback search: (a) all keywords together, (b) top 3 longest keywords, (c) each word individually with OR semantics + deduplication. Category templates are used only as a last-resort single primary when FTS finds nothing (never as donors — see Pitfalls)
3. **IR extraction** — `ir.extract_ir()` parses the primary exemplar, then merges fragments from the top donors (`ir.PromptIR`, 14 canonical slots)
4. **Slot fill + intelligence layers** — goal leads the subject; style/mood/aspect ratio fill slots; photography specs injected for photo categories; camera fragments scrubbed for non-photo categories; marketing framework layered in
5. **Model-native rendering + scoring** — `render_gpt_image_2()` or `render_nano_banana_pro()` (by `_recommend_model()`), then PQS quality scoring (percentile grades vs corpus distribution)

**Intelligence layers** (data as `data/*.json`, loaded + evidence-validated by `intelligence.py`; every claim group carries `_source`/`_date`/`_confidence`/`_review_after`):
- **Photography**: 8 shoot types (product, food, portrait, fashion, beauty, lifestyle, automotive, architectural) — each with camera body, lens, lighting setup, color science, bokeh, post-processing, background
- **Marketing**: 7 frameworks (Instagram feed/story, YouTube thumbnail, LinkedIn, poster, ecommerce, billboard) — each with AIDA layers, safe zones, color strategy
- **Art Direction**: composition systems, color theory, contrast modes, style references
- **Mood inference**: 8 mood profiles auto-detected from style keywords (luxury, vibrant, minimalist, cinematic, playful, corporate, natural, futuristic)

**Structure & routing:**
- `structure` only biases exemplar selection (e.g. "Template" prefers 2–4 `{argument}` exemplars, corpus avg 2.7) — rendered output is always model-native prose
- Model routing (`_recommend_model`): layout/UI/text-dense goals + App/Web, Infographic, Thumbnail, Poster categories → `gpt_image_2`; reference compositing, consistency, localization, brand + Profile/Portrait/E-commerce categories → `nano_banana_pro`
- Non-photo categories skip camera/lens specs and get design specs instead

## 📚 Technique Library (Extracted from the Corpus)

### 1. JSON Structure (10.0% — 636 prompts)
```json
{
  "type": "SaaS landing page hero graphic",
  "style": "Modern UI/UX, light theme, soft shadows, glassmorphism, purple and blue gradients",
  "header": {
    "headline": "Run your work with AI clarity.",
    "subheadline": "Coordinate tasks, context, and execution across your tools in one intelligent workspace."
  },
  "layout": {
    "center_dashboard": { ... },
    "left_integrations": { ... }
  }
}
```
**Best for:** Complex UI mockups, multi-component designs, structured specifications

### 2. Template/Arguments (76.5% — DOMINANT PATTERN)
```
A polished promotional mockup showing 3 tall smartphone screens displayed side by side in a vertical triptych layout, each displaying a {argument name="app screen" default="different dashboard view"} with {argument name="color theme" default="dark mode with neon accents"}. The screens float on a {argument name="background" default="subtle gradient"} with {argument name="lighting" default="soft studio lighting"}.
```
**Best for:** Reusable prompts, A/B variations, parameterized generation

### 3. Flat Prose with Embedded Directives (3.9%)
```
Cinematic portrait of a cyberpunk character in neon-lit alleyway, volumetric fog, rain-slicked streets reflecting magenta and cyan signs. Shot on 35mm f/1.4, shallow depth of field, subject centered with rule of thirds. Moody atmospheric lighting, high contrast, 8K detail. --ar 9:16
```
**Best for:** Artistic/creative generation, photography-style, cinematic

## 🎯 Category-Specific Best Practices

> Prompt counts are searchable-row counts; structure/technique preferences summarized from `references/CORPUS-ANALYSIS-REPORT.md`.

### App / Web Design (133 prompts)
- **Preferred structure:** Template (54%) or JSON (35%)
- **Must-have techniques:** Layout (78%), UI/UX terms (68%), Material (52%)
- **Avg length:** 2,044 chars

### Product Marketing (1,230 prompts)
- **Preferred structure:** Template (90% use arguments)
- **Must-have techniques:** Material (79%), Mood (76%), Layout (71%), Lighting (69%)
- **Avg length:** ~1,500 chars

### Social Media Post (1,978 prompts)
- **Preferred structure:** Template (86% use arguments)
- **Must-have techniques:** Mood (73%), Material (66%), Camera (64%), Lighting (58%)
- **Note:** Camera specs much higher here — photography-heavy category

### Poster / Flyer (799 prompts)
- **Preferred structure:** Template (88% use arguments)
- **Must-have techniques:** Layout (78%), Mood (77%), Material (74%)
- **Avg length:** ~1,700 chars

### Comic / Storyboard (570 prompts)
- **Preferred structure:** Template (84%) or JSON for panel specs
- **Must-have techniques:** Layout (69%), Mood (75%), Material (60%)
- **Avg length:** ~2,100 chars (multi-panel specs drive length up)

## 💾 Database Schema (SQLite FTS5)

```sql
-- Main prompts table (columns as shipped; structure/techniques/inferred_category/
-- complexity are legacy scrape columns)
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    prompt_text TEXT,
    categories TEXT,        -- pipe-separated
    model TEXT,
    slug TEXT,
    scraped_at TEXT,
    has_prompt INTEGER,     -- 1 = curated (searchable gate on legacy DBs)
    structure_type TEXT,    -- Template | JSON | Flat prose | Other (enrichment)
    length_chars INTEGER,   -- enrichment
    technique_tags TEXT     -- JSON array of detected techniques (enrichment)
);

-- Full-text search index: 3 indexed columns, external content, default
-- unicode61 tokenizer (no tokenize= option is set)
CREATE VIRTUAL TABLE prompts_fts USING fts5(
    prompt_text, title, model,
    content='prompts', content_rowid='id'
);

-- Pre-computed technique index
CREATE TABLE prompt_techniques (
    prompt_id INTEGER,
    technique TEXT,
    PRIMARY KEY (prompt_id, technique)
);
```

> Migrated DBs (`scripts/migrate_status.py`) additionally carry `status` (`curated`/`harvested`/`excluded`) + `excluded_reason`; the searchable gate becomes `status IN ('curated','harvested')`.

## 🚀 Quick Start

```bash
# From the repo root. The DB auto-loads at references/gpt-image2-prompts-full.db
# (override with HIGGSFIELD_DB). Python 3.10+, stdlib only. This repo is not an
# importable package (hyphenated dir name) — import the module with the repo
# root on sys.path. There is no __init__.py by design; version lives only in
# this file's frontmatter.

# In your agent session (repo root on sys.path):
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()

# Search
results = hpm.search("dashboard glassmorphism", limit=5)

# Get category guide
guide = hpm.category_guide("App / Web Design")

# CRITICAL: Always use generate_prompt() for image generation — never hand-write prompts
# The pipeline does: keyword extraction → FTS retrieval → IR extraction + donor merge →
# slot fill + intelligence layers → model-native rendering → PQS scoring
result = hpm.generate_prompt(
    goal="Analytics dashboard with real-time charts",
    category="App / Web Design",
    style="Modern, glassmorphism, dark theme"
)
prompt_text = result["prompt"]        # the actual prompt
model = result["model_recommendation"]["id"] # "gpt_image_2" or "nano_banana_pro"
score = result["quality_score"]["grade"]  # percentile grade "A+".."F"
source_ids = result["source_prompt_ids"]  # real corpus IDs used as evidence

# Verify diversity: source_prompt_ids should differ across different goals
# If they're identical, the FTS fallback is misfiring (see Pitfalls)
```

## 📖 Advanced: Prompt Engineering Patterns from Corpus

### Pattern 1: The "Spec Sheet" JSON (Best for UI/UX)
```json
{
  "type": "{component type}",
  "style": "{design system + theme}",
  "layout": { "grid": "...", "spacing": "...", "breakpoints": [...] },
  "components": [
    { "name": "...", "variant": "...", "props": {...} }
  ],
  "tokens": { "colors": {...}, "typography": {...}, "shadows": {...} }
}
```

### Pattern 2: The "Creative Brief" Template (Best for Marketing)
```
{argument name="product" default="premium skincare serum"}
{argument name="vibe" default="clean, clinical, trustworthy"}
{argument name="hero_shot" default="product floating on gradient background with soft caustics"}
{argument name="accent_color" default="pearlescent white and rose gold"}
{argument name="composition" default="centered hero, rule of thirds for supporting elements"}
Professional product photography, {hero_shot}, {vibe} aesthetic, {accent_color} palette,
studio lighting with subtle rim light, 8K, commercial quality. --ar 4:5
```

### Pattern 3: The "Cinematic Spec" (Best for Art/Photo)
```
{argument name="subject" default="lone traveler"}
{argument name="environment" default="misty mountains at dawn"}
{argument name="camera" default="85mm f/1.2"}
{argument name="lighting" default="golden hour, volumetric rays"}
{argument name="mood" default="contemplative, epic scale"}
{subject} in {environment}, {camera}, {lighting}, {mood} atmosphere,
hyperrealistic, 8K, cinematic color grading. --ar 21:9
```

### Pattern 4: The "Poster System" (Best for Print/Posters)
```
{argument name="event" default="Tech Conference 2025"}
{argument name="headline" default="BUILD THE FUTURE"}
{argument name="subheadline" default="Where developers shape tomorrow"}
{argument name="date_venue" default="March 15-17, San Francisco"}
{argument name="style" default="brutalist typography, high contrast, grid-based"}
Poster design for {event}. Bold {style}. Hero headline: "{headline}".
Subheadline: "{subheadline}". Details: {date_venue}.
Strong visual hierarchy, clear information architecture, print-ready CMYK. --ar 2:3
```

## 🔍 Search Examples

```python
# Find all JSON-structured dashboard prompts
hpm.search(structure="JSON", category="App / Web Design")

# Find template prompts with camera specs for product photography
hpm.search(techniques=["Arguments/Templates", "Camera Specs"], category="Product Marketing")

# Find flat prose prompts for cinematic portraits
hpm.search(structure="Flat prose", techniques=["Camera Specs", "Lighting", "Mood/Atmosphere"])

# Full-text search for "glassmorphism"
hpm.fts_search("glassmorphism", limit=20)

# Get random inspiration
hpm.random_prompt(category="Comic / Storyboard")
hpm.random_prompt(model="GPT Image 2")
```

## 📈 Analytics & Insights

```python
# Corpus-wide statistics
hpm.stats()

# Category deep-dive (structure breakdown, technique freq, length stats, top examples)
guide = hpm.category_guide("App / Web Design")

# Model comparison
hpm.compare_models("GPT Image 2", "Nano Banana")
# Returns: structure preferences, technique usage, category distribution
```

## 🛠️ Scripts

- `scripts/rsc-prompt-extractor.py` — **RSC Flight Data Extractor**: Extracts prompts from Next.js App Router sites via curl (no browser). 50x faster than CDP. Usage:
  ```bash
  python3 scripts/rsc-prompt-extractor.py --start 27000 --end 30000
  python3 scripts/rsc-prompt-extractor.py --url https://youmind.com/prompts/x-13440
  ```
- `scripts/verify-generation-diversity.py` — **Pipeline Health Check**: Verifies `generate_prompt()` produces diverse, goal-specific results with no contamination. Run after any changes to the generation pipeline. Catches FTS fallback misfires, exemplar contamination, and wrong-category spec injection; gates cross-goal duplication (pairwise 5-gram Jaccard >= 0.70 fails, goal-swap hard-fail, goal-discrimination delta < 0.30 fails) and reports batch distinct-3 + source-ID entropy.
- Regression checks: `scripts/test_fts_quotes.py`, `scripts/test_recommend_model.py`, `scripts/test_photo_truthfulness.py`, `scripts/test_extract_ir.py`, `scripts/test_renderers.py`, `scripts/test_generation_pipeline.py`, `scripts/test_pqs.py`.
- Corpus maintenance (copy-safe; `--apply` for live DB): `scripts/purge_boilerplate.py`, `scripts/migrate_status.py`, `scripts/rebuild_corpus.py`, `scripts/calibrate_pqs.py`, `scripts/build-db.py` (reproducible rebuild from the JSONL export — `--export` dumps it; Releases stay the distribution channel), `scripts/fetch-db.py` (installer: download the pinned Release DB + SHA-256 verify against `references/checksums.txt`; `--tag` override), `scripts/refresh.py` (refresh pipeline: probe ids past the `prompt-id-map.json` watermark -> scrape via the RSC extractor -> language/boilerplate/model guards -> idempotent upsert + FTS rebuild + diff summary; watermark = max(map range end, DB max id); writes the DB `scrape_log` table + a `references/refresh-<range>.jsonl` artifact; dry-run on a temp copy via HIGGSFIELD_DB, `--apply` for the live DB).

## 🛠️ Maintenance

**Ingestion guard:** youmind.com share-widget text (`Just found a great AI prompt: "{title}"! This site also has thousands...`) gets scraped in as `prompt_text` when a page has no real prompt. After any re-scrape, run `python3 scripts/purge_boilerplate.py` (copy-safe; add `--apply` to fix the live DB) to remove it plus exact-duplicate rows.

```bash
# All commands run from the repo root. Maintenance scripts are copy-safe by
# default (operate on a temp copy); add --apply to touch the live DB.

# Re-scrape new prompts (run monthly) — use the RSC extractor script
python scripts/rsc-prompt-extractor.py --start 27000 --end 30000

# Purge share-widget boilerplate + exact duplicates (after any re-scrape)
python scripts/purge_boilerplate.py

# Migrate schema (harvested rows become searchable) + rebuild corpus
python scripts/migrate_status.py --apply
python scripts/rebuild_corpus.py --apply

# Re-run enrichment (detect techniques, structure, categories)
python -c "
import sys; sys.path.insert(0, '.')
from higgsfield_prompt import HiggsfieldPromptMaster
HiggsfieldPromptMaster().enrich_all()
"

# Full corpus analytics: see references/CORPUS-ANALYSIS-REPORT.md

# Run interactive demo
python demo.py
```

## 📝 License & Attribution

Prompts sourced from **youmind.com** public gallery.
This skill is for reference, learning, and prompt engineering research.
Respect original creators and platform terms of service.

*Built with the Higgsfield Master Prompt Skill — the largest GPT Image 2 prompt corpus ever structured.*

## 📄 Deep Analysis Report & References

- `references/CORPUS-ANALYSIS-REPORT.md` — comprehensive 16-section analytics report (note: stats reflect pre-filter 8,596 corpus; proportions stable in English-only subset)
- `references/rsc-extraction-technique.md` — **reusable scraping pattern**: how to extract content from any Next.js App Router site via curl RSC flight data (50x faster than browser automation, Cloudflare-safe)
- `references/non-english-analysis.md` — analysis justifying the English-only policy (non-English prompts had zero unique value)
- `intelligence.py` (skill root, not references/) — **loader + accessors** for the intelligence data in `data/*.json`: photography presets (8 shoot types), marketing frameworks (7 platforms), art direction (composition, color theory, contrast, style) + per-model guidance (`get_gpt_image_2_intelligence`, `get_nano_banana_pro_intelligence`; loader rejects claim groups missing `_source`/`_date`/`_confidence`/`_review_after`). Imported by `higgsfield_prompt.py` at generation time. Edit the JSON, not the module — and for the two model files, edit `profiles/gpt-image-2@<date>.yaml` / `profiles/nano-banana-pro@<date>.yaml` (versioned capability profiles: evidence URL, confidence, `review_after` per claim) and regenerate with `python scripts/sync_profiles.py --apply` (default mode validates profile ↔ data sync, exit 1 on drift).

## 🔑 Key Insights from Full Analytics

> The full analytics were run on the original 8,596-prompt corpus before English-only filtering. The English-only reduction (6,337 prompts) preserves all categories, techniques, and structures — non-English prompts had zero unique elements. Category and technique percentages below reflect the full corpus but proportions are stable in the English-only subset.

- **Language policy:** English-only (6,337 prompts). Non-English prompts permanently excluded — `get_templates()` and `generate_prompt()` never return non-English content. Scraper has a shared `langcheck.is_english()` guard.
- **Model divergence:** GPT Image 2 prompts are layout-focused (Layout 71%). Nano Banana prompts are camera-focused (Camera 62%) and concentrate in Social Media (46%).
- **Argument vocabulary:** Top 5 argument names are `subject` (14%), `hair color` (10%), `outfit` (7%), `character name` (6%), `headline text` (4%).
- **JSON canonical schema:** `type` (92%) → `layout` (74%) → `style` (62%) → `subject` (30%) → `composition` (20%).
- **Complexity:** 40% of prompts are "Detailed" (score 10-15). Only 1.3% are "Expert" (score 20+).
- **Spatial vocabulary:** "right" and "left" each appear 10,000+ times — GPT Image 2 prompting is layout specification, not description.

## ⚠️ Pitfalls

### CRITICAL: Always Use `generate_prompt()` — Never Hand-Write Prompts
The entire point of this skill is the corpus-grounded pipeline: goal-relevant FTS retrieval → IR extraction → slot fill with intelligence layers → model-native rendering (paragraph-primary for GPT Image 2, narrative scene descriptions for Nano Banana Pro) → PQS percentile scoring. Hand-writing prompts bypasses corpus grounding, the model-specific text levers (quotes/CAPS/letter-spelling; ordinals+role reference addressing), and quality scoring. **If you skip `hpm.generate_prompt()`, you are not using this skill.** Output diversity is regression-gated by `scripts/verify-generation-diversity.py` — run it after any pipeline change.

```python
# RIGHT — always do this
result = hpm.generate_prompt(goal="...", category="...", style="...")
prompt_text = result["prompt"]

# WRONG — never do this
prompt_text = "A warm cream Arabic website hero with..."  # no corpus grounding, no intelligence
```

### FTS5 Search: Progressive Fallback (FIXED — June 2026)
SQLite FTS5 treats common English words like `time`, `near`, `and`, `not`, `or` as **operators or column references**. The old `fts_search()` wrapped each term in quotes but had no fallback when the full query returned zero results — common words killed the search silently.

**Bug found:** When FTS returned empty (too many common words in the goal description), `generate_prompt()` fell back to `get_templates(category)` which sorts by `length_chars + technique_count` — always returning the SAME 5 longest templates regardless of the goal. All 8 anasaq.me sections got identical source IDs `[21732, 26157, 23501, 26260, 14559]` because FTS failed and the fallback was deterministic.

**Fix (3-layer progressive fallback):**
1. **Keyword extraction** (`_extract_keywords()`): Strips stop words AND domain filler ("website", "section", "showing", "Arabic", "personal", "brand"), prioritizes design terms ("hero", "gallery", "masonry", "dark", "contact"), returns top 6 keywords
2. **Strategy 1**: Search all extracted keywords together
3. **Strategy 2**: Search top 3 longest keywords
4. **Strategy 3**: Search each word individually with OR semantics and deduplication

### Template Argument Contamination (class: June 2026 "Y2K Scream")
**Bug class:** merging category-template exemplars into generation as donors leaks off-domain fragments into every same-category goal — the "Y2K Futurist Scream Desktop" template (id 23501) injected Munch/vaporwave argument defaults into unrelated App/Web goals when FTS fell back to longest-templates.

**Current fix (US-013):** retrieval donors must be **goal-relevant FTS hits**; category templates serve only as a last-resort single primary when FTS finds nothing. `scripts/verify-generation-diversity.py` gates this continuously (cross-goal 5-gram Jaccard, goal-swap hard-fail, goal-discrimination delta).

### Non-Photo Categories Stay Camera-Free
Categories like `App / Web Design`, `Infographic / Edu Visual`, `YouTube Thumbnail`, `Comic / Storyboard`, `Game Asset` should NOT receive camera/lens/lighting specs. Mechanism (US-010 + US-013): `get_photo_intelligence()` returns `None` for explicitly non-photo categories (goal-keyword inference can't override a mapped category), and `generate_prompt()` strips camera-bearing corpus fragments (`renderers._CAMERA_RE`) before rendering, so even camera-language exemplars can't leak in. Regression: `scripts/test_photo_truthfulness.py`.

### FTS5 Query Sanitization (Background)
SQLite FTS5 treats `time`, `near`, `and`, `not`, `or` as operators/column references. The `fts_search()` method wraps each term in double quotes (embedded quotes doubled). Never pass raw user input to FTS5 MATCH — always go through `fts_search()` or `_extract_keywords()`.
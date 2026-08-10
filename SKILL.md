--- 
name: higgsfield-prompt-master
description: The Ultimate GPT Image 2 Prompt Reference & Generation Tool — built from 7,613 English-only prompts scraped from youmind.com
version: 2.1.1
category: media
---

# Higgsfield Master Prompt Skill
## The Ultimate GPT Image 2 Prompt Reference & Generation Tool

> Built from **7,613** real **English-only** prompts scraped from youmind.com (6,337 original + 1,276 harvested Aug 2026). Non-English prompts (2,240 Japanese/Korean/Arabic) were removed after analysis confirmed they contain zero unique techniques not present in the English corpus.

---

## 📊 Corpus Statistics (English-Only — verified August 2026)

> **English-only policy:** Non-English prompts (2,240 Japanese/Korean/Arabic) were permanently removed after analysis confirmed they contained zero unique techniques, categories, or structures not present in the English corpus. The scraper (`scripts/rsc-prompt-extractor.py`) has an `is_non_english()` filter and will never save non-English prompts. See `references/non-english-analysis.md` for the comparison data.

| Metric | Value |
|--------|-------|
| **Total Prompts** | 7,613 (+1,276 from Aug 2026 harvest) |
| GPT Image 2 | 6,095 (80.1%) |
| Nano Banana Pro | 1,514 (19.9%) |
| **Categories** | 26 |
| **Avg Prompt Length** | ~1,536 chars |
| **ID Range** | 51 – 28,686 |

### Structure Distribution (from clean English-only corpus)
- **Parameterized Templates (91% of new batch)** — `{argument name="..." default="..."}` syntax. See `references/parameterized-templates.md`
- **Multi-Panel Campaign Grids (emerging)** — 3×2, 4×1, 5×1 panel campaigns. See `references/multi-panel-campaigns.md`
- **JSON (10.0%)** — 636 prompts as structured JSON objects with type/style/layout, avg ~2,496 chars (longest)
- **Other (9.6%)** — 606 hybrid/mixed formats, avg ~923 chars
- **Flat Prose (3.9%)** — 249 natural language descriptions, avg ~1,572 chars

**Length sweet spot:** 1,000–2,000 chars (39.5% of corpus). Below 500 = low quality.

### Top Techniques (verified from full 7,613-prompt analytics)
| Technique | Frequency | Description |
|-----------|-----------|-------------|
| Parameterized Templates | 91% (new) | `{argument}` syntax — dominant paradigm in latest prompts |
| Spatial Anchoring | 78% (new) | Left/right/center/top/bottom positioning |
| Resolution/Quality | 70% (new) | 4k, 8k, ultra-detail, photorealistic |
| Negative Prompts | 55% (new) | What to avoid, exclusions |
| Face/Character Lock | 44% (new) | Consistency across panels/generations |
| Camera Specs | 42% (new) | Lens mm, aperture, depth of field |
| Mood/Atmosphere | 70.1% | Cinematic, moody, vibrant, ethereal, gritty |
| Material/Texture | 67.6% | Glass, metal, matte, glossy, fabric, organic |
| Layout/Composition | 66.8% | Grid, alignment, center, balanced, rule of thirds |
| Lighting | 54.3% | Golden hour, studio, soft, dramatic, volumetric |
| Typography | 23.1% | Font styles, hierarchy, lettering, text effects |

**The "Golden Pentagon"** — 50%+ of prompts combine all 5 core techniques: Arguments + Mood + Material/Texture + Layout + Lighting. This is the baseline quality standard.
**Avg techniques per prompt:** 5.5 (max: 12).

### Top Categories
1. **Social Media Post** (2,409) — Instagram, LinkedIn, Twitter/X, TikTok
2. **Product Marketing** (1,550) — E-commerce, ads, hero shots
3. **Poster / Flyer** (1,185) — Event, movie, concert, promotional
4. **Comic / Storyboard** (819) — Sequential art, panels, narrative
5. **Profile / Avatar** (738) — Character, headshot, identity
6. **Game Asset** (649) — Sprites, UI, environments, items
7. **Infographic / Edu Visual** (647) — Data viz, charts, explanations
8. **App / Web Design** (253) — UI mockups, dashboards, landing pages

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

### Generate Optimized Prompts (V2 — Corpus-Grounded + Intelligence Layers)

**`generate_prompt()` returns a DICT, not a string.** The V2 generator uses RAG (retrieval-augmented generation) from the 6,337-prompt corpus PLUS three intelligence layers (photography, marketing, art direction) to synthesize production-grade prompts.

```python
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()
result = hpm.generate_prompt(
    goal="Premium skincare serum product shot",
    category="Product Marketing",     # drives photo + marketing intelligence
    structure="Template",             # "Template" | "JSON" | "Flat prose"
    style="Clean, clinical, premium", # drives mood inference
    aspect_ratio="4:5"                # auto-detected from marketing layer if omitted
)

# result is a DICT with:
result["prompt"]              # → the full crafted prompt text (1200-2000 chars)
result["model_recommendation"] # → "nano_banana_2" or "gpt_image_2"
result["aspect_ratio"]         # → "4:5"
result["quality_score"]        # → {"total": 91, "grade": "A+", ...}
result["intelligence"]         # → {"photography": True, "marketing": True, "mood": "..."}
result["source_prompt_ids"]    # → [18464, 20293, ...] real corpus IDs used as reference
result["length"]               # → 1812 (chars)
```

**How it works (V2 pipeline — updated June 2026):**
1. **Keyword extraction** — `_extract_keywords()` strips stop words AND domain filler, prioritizes design-relevant terms, returns top 6 keywords from the goal
2. **RAG retrieval** — FTS progressive fallback search: (a) all keywords together, (b) top 3 longest keywords, (c) each word individually with OR semantics + deduplication
3. **Argument synthesis** — Goal-specific arguments generated from goal content (NOT copied from source template — see Pitfalls)
4. **Intelligence injection** — Photography specs for photo categories, design system specs for UI categories. Marketing framework (AIDA, safe zones), and mood are layered in
5. **Quality scoring** — Prompt is scored A+ to D against corpus benchmarks (length, techniques, vocabulary density)

**Intelligence layers** (in `intelligence.py`):
- **Photography**: 8 shoot types (product, food, portrait, fashion, beauty, lifestyle, automotive, architectural) — each with camera body, lens, lighting setup, color science, bokeh, post-processing, background
- **Marketing**: 7 frameworks (Instagram feed/story, YouTube thumbnail, LinkedIn, poster, ecommerce, billboard) — each with AIDA layers, safe zones, color strategy
- **Art Direction**: composition systems, color theory, contrast modes, style references
- **Mood inference**: 8 mood profiles auto-detected from style keywords (luxury, vibrant, minimalist, cinematic, playful, corporate, natural, futuristic)

**Category → structure mapping:**
- Photography categories (Product, Social Media, Profile/Avatar) → Template or Flat prose
- UI/Graphics categories (App/Web Design, Infographic) → JSON (gets design specs, NOT photography specs)
- Non-photo categories skip camera/lens specs and get UI/design specs instead

## 📚 Technique Library (Extracted from 8,596 Prompts)

### 1. JSON Structure (15.2% of corpus)
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

### 2. Template/Arguments (72.4% — DOMINANT PATTERN)
```
A polished promotional mockup showing 3 tall smartphone screens displayed side by side in a vertical triptych layout, each displaying a {argument name="app screen" default="different dashboard view"} with {argument name="color theme" default="dark mode with neon accents"}. The screens float on a {argument name="background" default="subtle gradient"} with {argument name="lighting" default="soft studio lighting"}.
```
**Best for:** Reusable prompts, A/B variations, parameterized generation

### 3. Flat Prose with Embedded Directives (3.7%)
```
Cinematic portrait of a cyberpunk character in neon-lit alleyway, volumetric fog, rain-slicked streets reflecting magenta and cyan signs. Shot on 35mm f/1.4, shallow depth of field, subject centered with rule of thirds. Moody atmospheric lighting, high contrast, 8K detail. --ar 9:16
```
**Best for:** Artistic/creative generation, photography-style, cinematic

## 🎯 Category-Specific Best Practices

### App / Web Design (253 prompts)
- **Preferred structure:** Template (54%) or JSON (35%)
- **Must-have techniques:** Layout (78%), UI/UX terms (68%), Material (52%)
- **Avg length:** 2,044 chars

### Product Marketing (1,550 prompts)
- **Preferred structure:** Template (90% use arguments)
- **Must-have techniques:** Material (79%), Mood (76%), Layout (71%), Lighting (69%)
- **Avg length:** ~1,500 chars

### Social Media Post (2,409 prompts)
- **Preferred structure:** Template (86% use arguments)
- **Must-have techniques:** Mood (73%), Material (66%), Camera (64%), Lighting (58%)
- **Note:** Camera specs much higher here — photography-heavy category

### Poster / Flyer (1,185 prompts)
- **Preferred structure:** Template (88% use arguments)
- **Must-have techniques:** Layout (78%), Mood (77%), Material (74%)
- **Avg length:** ~1,700 chars

### Comic / Storyboard (819 prompts)
- **Preferred structure:** Template (84%) or JSON for panel specs
- **Must-have techniques:** Layout (69%), Mood (75%), Material (60%)
- **Avg length:** ~2,100 chars (multi-panel specs drive length up)

## 💾 Database Schema (SQLite FTS5)

```sql
-- Main prompts table
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    prompt_text TEXT,
    categories TEXT,        -- pipe-separated
    model TEXT,
    slug TEXT,
    scraped_at TEXT,
    has_prompt INTEGER,
    structure_type TEXT,    -- JSON, Template, Flat, Other
    length_chars INTEGER,
    technique_tags TEXT     -- JSON array of detected techniques
);

-- Full-text search index
CREATE VIRTUAL TABLE prompts_fts USING fts5(
    id, title, description, prompt_text, categories,
    tokenize='porter unicode61'
);

-- Pre-computed technique index
CREATE TABLE prompt_techniques (
    prompt_id INTEGER,
    technique TEXT,
    PRIMARY KEY (prompt_id, technique)
);
```

## 🚀 Quick Start

```bash
# The skill auto-loads the database at:
~/.hermes/skills/higgsfield-prompt-master/references/gpt-image2-prompts-full.db

# Intelligence layers are in:
~/.hermes/skills/higgsfield-prompt-master/intelligence.py

# In your agent session:
import sys; sys.path.insert(0, str(__import__('pathlib').Path.home() / ".hermes/skills/higgsfield-prompt-master"))
from higgsfield_prompt import HiggsfieldPromptMaster

hpm = HiggsfieldPromptMaster()

# Search
results = hpm.search("dashboard glassmorphism", limit=5)

# Get category guide
guide = hpm.category_guide("App / Web Design")

# CRITICAL: Always use generate_prompt() for image generation — never hand-write prompts
# The pipeline does: keyword extraction → FTS progressive fallback → RAG retrieval →
# goal-specific argument synthesis → intelligence layers → quality scoring
result = hpm.generate_prompt(
    goal="Analytics dashboard with real-time charts",
    category="App / Web Design",
    structure="JSON",
    style="Modern, glassmorphism, dark theme"
)
prompt_text = result["prompt"]        # the actual prompt
model = result["model_recommendation"] # "gpt_image_2" or "nano_banana_2"
score = result["quality_score"]["grade"]  # "A+", "A", "B", etc.
source_ids = result["source_prompt_ids"]  # real corpus IDs used as reference

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
- `scripts/verify-generation-diversity.py` — **Pipeline Health Check**: Verifies `generate_prompt()` produces diverse, goal-specific results with no contamination. Run after any changes to the generation pipeline. Catches FTS fallback misfires, argument contamination, and wrong-category spec injection.

## 🛠️ Maintenance

```bash
# Re-scrape new prompts (run monthly) — use the RSC extractor script
python3 scripts/rsc-prompt-extractor.py --start 27000 --end 30000

# Re-run enrichment (detect techniques, structure, categories)
cd ~/.hermes/skills/higgsfield-prompt-master && python3 -c "
import sys; sys.path.insert(0, '.')
from higgsfield_prompt import HiggsfieldPromptMaster
hpm = HiggsfieldPromptMaster()
hpm.enrich_all()
"

# Run full corpus analytics
python3 ~/.hermes/scripts/full-analytics-pt1.py
python3 ~/.hermes/scripts/full-analytics-pt2.py
python3 ~/.hermes/scripts/full-analytics-pt3.py

# Run interactive demo
cd ~/.hermes/skills/higgsfield-prompt-master && python3 demo.py
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
- `intelligence.py` (skill root, not references/) — **V2 intelligence layers**: photography presets (8 shoot types), marketing frameworks (7 platforms), art direction (composition, color theory, contrast, style). Imported by `higgsfield_prompt.py` at generation time.

## 🔑 Key Insights from Full Analytics

> The full analytics were run on the original 8,596-prompt corpus before English-only filtering. The English-only reduction (6,337 prompts) preserves all categories, techniques, and structures — non-English prompts had zero unique elements. Category and technique percentages below reflect the full corpus but proportions are stable in the English-only subset.

- **Language policy:** English-only (6,337 prompts). Non-English prompts permanently excluded — `get_templates()` and `generate_prompt()` never return non-English content. Scraper has `is_non_english()` guard.
- **Model divergence:** GPT Image 2 prompts are layout-focused (Layout 71%). Nano Banana prompts are camera-focused (Camera 62%) and concentrate in Social Media (46%).
- **Argument vocabulary:** Top 5 argument names are `subject` (14%), `hair color` (10%), `outfit` (7%), `character name` (6%), `headline text` (4%).
- **JSON canonical schema:** `type` (92%) → `layout` (74%) → `style` (62%) → `subject` (30%) → `composition` (20%).
- **Complexity:** 40% of prompts are "Detailed" (score 10-15). Only 1.3% are "Expert" (score 20+).
- **Spatial vocabulary:** "right" and "left" each appear 10,000+ times — GPT Image 2 prompting is layout specification, not description.

## ⚠️ Pitfalls

### CRITICAL: Always Use `generate_prompt()` — Never Hand-Write Prompts
The entire point of this skill is the RAG-grounded generation pipeline. Hand-writing prompts bypasses the 6,337-prompt corpus, intelligence layers, and quality scoring — producing generic, repetitive output. **If you skip `hpm.generate_prompt()`, you are not using this skill.** Every batch of images must route through the pipeline. The user WILL notice duplication.

```python
# RIGHT — always do this
result = hpm.generate_prompt(goal="...", category="...", structure="...", style="...")
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

### Template Argument Contamination (FIXED — June 2026)
**Bug found:** `_synthesize_template()` copied argument names and defaults from the source corpus prompt. When FTS fell back to longest templates (see above), the "best template" was "Y2K Futurist Scream Desktop" (4020 chars) — so EVERY prompt got `{argument name="painting subject" default="Edvard Munch's The Scream"}` and `{argument name="style phrase" default="Y2K futurism, cyberpunk vaporwave"}`. The old filter only blocked sports/movie/anime terms.

**Fix:** `_synthesize_template()` no longer copies source arguments at all. It generates **goal-specific** arguments by scanning the goal text for keywords:
- Color mentions → `color_palette` argument
- Layout terms → `layout` argument
- Typography/Arabic mentions → `typography` argument
- Device mentions → `viewport` argument
- Always includes `aesthetic` argument from the style parameter

### Non-Photo Categories — Design Specs (FIXED — June 2026)
Categories like `App / Web Design`, `Infographic / Edu Visual`, `YouTube Thumbnail`, `Comic / Storyboard`, `Game Asset` should NOT receive camera/lens/lighting specs. The `_generate_flat_v2()` and `_generate_json_v2()` methods already checked `non_photo_categories`, but `_synthesize_template()` (the Template structure generator) **did not** — it always injected photography specs. Now all three V2 generators check the `non_photo_categories` list. Template structure now emits design system specs (8px grid, component-based UI, WCAG AA contrast, glassmorphism materials) for non-photo categories.

### FTS5 Query Sanitization (Background)
SQLite FTS5 treats `time`, `near`, `and`, `not`, `or` as operators/column references. The `fts_search()` method wraps each term in double quotes. Never pass raw user input to FTS5 MATCH — always go through `fts_search()` or `_extract_keywords()`.

### Old V1 Generators Still Exist
`_generate_json()`, `_generate_template()`, `_generate_flat()` (V1 methods) still exist in the code but are NOT called by `generate_prompt()` — the V2 methods (`_generate_*_v2()`) are used instead. The V1 methods produce ~300 char prompts with hardcoded strings. Do not call V1 methods directly.
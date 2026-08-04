# GPT Image 2 Structured Prompt Database

## What This Is

All 126 curated prompts from [awesome-gpt-image-2](https://github.com/YouMind-OpenLab/awesome-gpt-image-2), fully extracted and structurally organized into a searchable database.

**Note:** The repo claims 11,143+ prompts but only 126 are published in the public README. The rest are behind a private Payload CMS (`CMS_HOST` + `CMS_API_KEY` required). The watchdog cron (`26c2c68477b8`) monitors for new README additions.

## Files

| File | Format | Purpose |
|------|--------|---------|
| `gpt-image2-prompts.json` | JSON array | Full structured data — every prompt with text, metadata, classification |
| `gpt-image2-prompts.db` | SQLite + FTS5 | Full-text searchable database — query by technique, category, structure |
| `gpt-image2-categories.json` | JSON | Indexes by category, structure, and technique with stats |

## Structural Classification

### Three Prompt Structures (from 126 prompts)

**Flat (104 prompts, 83%)** — Single paragraph descriptions, most common for portraits, product shots, and illustrations. Template: `[SUBJECT] [STYLE] [TECHNICAL] [COMPOSITION]`

**Goal+Canvas+Sections (18 prompts, 14%)** — Complex multi-zone UI mockups and dashboards. Template: `Goal:` → `Canvas:` → Named sections → `Visual style:` guard

**JSON (4 prompts, 3%)** — Structured object prompts for exploded diagrams, infographics, and complex layouts. Keys: `type`, `subject`, `style`, `layout` (with `centerpiece`, `callout_labels`)

### Categories (sorted by frequency)

1. **Photography & Cinematic** (34) — Portraits, cinematic shots, profile avatars
2. **UI/UX Mockups** (31) — App interfaces, dashboards, e-commerce, live streams
3. **Product/Industrial Design** (26) — Exploded diagrams, product posters, hardware
4. **Maps & Illustrations** (19) — City maps, food maps, infographic illustrations
5. **Marketing & Posters** (4) — Brand posters, promotional designs
6. **Anime & Manga** (3) — Anime-style illustrations, battle scenes
7. **Game Art** (3) — Character art, game assets
8. **Other** (1 each) — Food, Fashion, Architecture, Education, Social Media

### Techniques Detected (top 10)

| Technique | Count | Description |
|-----------|-------|-------------|
| Raycast Args `{argument}` | 117 | Parameterized prompts with defaults |
| Cinematic Portrait | 55 | Camera specs, film stock, shallow DoF |
| UI Mockup | 49 | Interface design with sections |
| Labeled Sections | 36 | Named sections (Shot Type, Subject, etc.) |
| Anime Illustration | 30 | Anime/manga style markers |
| Poster Design | 29 | Marketing/promotional output |
| Goal+Canvas Pattern | 21 | Structured layout specification |
| Visual Style Guard | 18 | Closing aesthetic paragraph |
| Spatial Anchoring | 14 | Position naming (top-left, bottom-right) |
| Color Science | 12 | HDR, color grading, saturation specs |

## How to Query the Database

### SQLite (full-text search)
```bash
DB=~/.hermes/skills/higgsfield-prompt-master/references/gpt-image2-prompts.db

# Search by keyword
sqlite3 "$DB" "SELECT number, title, category FROM prompts WHERE rowid IN (SELECT CAST(number AS INT) FROM prompts_fts WHERE prompts_fts MATCH 'cinematic lighting');"

# Get all JSON-structured prompts
sqlite3 "$DB" "SELECT number, title FROM prompts WHERE structure='JSON';"

# Get prompts by category
sqlite3 "$DB" "SELECT number, title FROM prompts WHERE category='UI/UX Mockups' LIMIT 5;"

# Get featured prompts
sqlite3 "$DB" "SELECT number, title FROM prompts WHERE is_featured=1;"

# Full prompt text
sqlite3 "$DB" "SELECT prompt_text FROM prompts WHERE number=1 LIMIT 1;"
```

### JSON (programmatic access)
```python
import json
with open("~/.hermes/skills/higgsfield-prompt-master/references/gpt-image2-prompts.json") as f:
    prompts = json.load(f)

# Filter by technique
json_prompts = [p for p in prompts if "json_structure" in p["techniques"]]

# Filter by category
ui_prompts = [p for p in prompts if p["category"] == "UI/UX Mockups"]
```

## Full Corpus Scraping (youmind.com Gallery)

The README only has 126 curated prompts. The remaining ~11,000 are on youmind.com but accessible via individual prompt pages at predictable URLs: `https://youmind.com/prompts/{any-slug}-{ID}`. The slug doesn't matter — only the numeric ID at the end resolves the prompt.

### Key Discoveries

- **GPT Image 2 prompts are at IDs ~13440–26917** on youmind.com (earlier IDs are Nano Banana Pro / Seedream models — NOT GPT Image 2)
- **~85% of IDs in range are valid** (15% are 404 gaps)
- **Prompt text is in rendered DOM** (Next.js RSC) — curl HTML parsing is unreliable for the text; CloakBrowser CDP DOM extraction (`.whitespace-pre-wrap` selector) gives 100% accuracy
- **Meta tags (title, description, category) extract reliably via curl** — only the prompt TEXT needs browser rendering

### Corpus Stats (from ~60 prompts scraped so far, growing)

| Metric | README (126) | Scraped Corpus |
|--------|-------------|----------------|
| JSON structure | 3% | **54%** |
| Flat text | 83% | 46% |
| Top category | Photography | **UI/UX & Web Design** |
| Avg prompt length | 1,675 chars | 1,274 chars |

**Key insight:** The curated README over-represents flat/photography prompts. The actual corpus is heavily JSON-structured UI/UX designs. Skill prompting guidance should weight JSON structure higher.

### Scraper Scripts (in ~/.hermes/scripts/)

| Script | Purpose |
|--------|---------|
| `gpt-image2-cdp-scraper.py` | Full scraper: curl meta tags (parallel) + CloakBrowser CDP prompt text extraction. Usage: `python3 gpt-image2-cdp-scraper.py --start 13440 --end 27000` |
| `gpt-image2-enrich.py` | Enriches scraped DB with structure classification, technique detection (25+ patterns), category inference, complexity scoring. Re-run after scraping new prompts. |
| `parse-gpt-image2-prompts.py` | Parses README into the small curated 126-prompt database (JSON + SQLite + FTS5) |

### Databases

| File | Format | Scope |
|------|--------|-------|
| `gpt-image2-prompts.db` | SQLite + FTS5 | 126 README prompts — fully structured |
| `gpt-image2-prompts.json` | JSON | Same 126 prompts as JSON array |
| `gpt-image2-prompts-full.db` | SQLite + FTS5 | **Full ~11K corpus** (growing as scraper runs) — includes enrichment columns |

### Running the Full Scrape

```bash
# 1. Start CloakBrowser CDP server
~/.hermes/scripts/cloakbrowser-cdp.sh start

# 2. Run scraper (background, ~8s/prompt, ~22h for 11K)
python3 ~/.hermes/scripts/gpt-image2-cdp-scraper.py --start 13440 --end 27000

# 3. Enrich after scraping
python3 ~/.hermes/scripts/gpt-image2-enrich.py

# 4. Query
DB=~/.hermes/skills/higgsfield-prompt-master/references/gpt-image2-prompts-full.db
sqlite3 "$DB" "SELECT id, title FROM prompts WHERE prompt_text MATCH 'JSON' LIMIT 10;"
```

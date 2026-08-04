# YouMind Gallery Scraping — Bulk Prompt Extraction

## The Problem

The awesome-gpt-image-2 README only publishes **126 curated prompts**. The remaining 11,000+ are stored in a **private Payload CMS** (`CMS_HOST` + `CMS_API_KEY` env vars, not public). However, all prompts are accessible via the public gallery at youmind.com.

## URL Pattern (Discovered 2026-06-27)

Every prompt has a predictable URL:
```
https://youmind.com/prompts/{slug}-{ID}
```

**Key insight:** The slug doesn't matter — the ID at the end is what resolves. Any slug works:
```
https://youmind.com/prompts/x-13460        ← works, redirects to correct page
https://youmind.com/prompts/vr-headset-exploded-view-13460  ← also works
```

**ID range:** ~1,000 to ~26,918 (not all IDs are valid — some return 404). The site also has prompts for other models (Seedream, etc.) — filter by the `keywords` meta tag containing "GPT Image 2 prompt".

## Extraction Methods (Validated)

### Method A: Meta Tags via curl (Fast — title, description, category)

```bash
curl -sf "https://youmind.com/prompts/x-{ID}" | \
  grep -oP '<meta name="description" content="\K[^"]+'
curl -sf "https://youmind.com/prompts/x-{ID}" | \
  grep -oP '<meta name="keywords" content="\K[^"]+'
```

- **Title:** `<title>` tag (format: "Prompt Name - GPT Image 2 AI Prompt for Category | YouMind")
- **Description:** `<meta name="description">` (short summary of what the prompt generates)
- **Category:** `<meta name="keywords">` (e.g., "GPT Image 2 prompt,Infographic / Edu Visual prompt,image prompt,AI prompt")
- **Reliability:** 100% — always present in server-rendered HTML

### Method B: DOM Extraction via CloakBrowser CDP (Full prompt text)

The full prompt text is rendered in a div with class `whitespace-pre-wrap` (specifically `max-h-[min(58vh,620px)] overflow-auto whitespace-pre-wrap`).

```bash
# Start CloakBrowser CDP server
~/.hermes/scripts/cloakbrowser-cdp.sh start

# Navigate and extract
npx agent-browser --cdp http://localhost:9222 --json open "https://youmind.com/prompts/x-{ID}"
npx agent-browser --cdp http://localhost:9222 --json eval \
  "document.querySelector('.whitespace-pre-wrap').innerText"
```

- **Reliability:** 100% for prompt text extraction
- **Speed:** ~3 seconds per prompt (navigate + eval)
- **Full scrape estimate:** ~26,000 IDs × 3s = ~22 hours (filter 404s to reduce)

### Method C: RSC Flight Data (Attempted — unreliable)

The page uses React Server Components (RSC) with streaming. The prompt text appears in an RSC chunk after a `PromptContentTabs` marker (`NN:T844,<content>`). However, parsing this reliably across different prompt formats (JSON vs plain text) proved fragile — the DOM method is more reliable.

## Bulk Scraper Design

For a production bulk scrape:

1. **Phase 1 — ID discovery (curl, fast):** Loop IDs 1000-27000, check HTTP status code. Build list of valid IDs. (~0.3s each, ~2 hours)

2. **Phase 2 — Metadata extraction (curl, fast):** For each valid ID, extract title + description + category from meta tags. (~0.5s each, ~3 hours)

3. **Phase 3 — Full prompt text (CloakBrowser CDP):** For each valid ID, navigate and extract `.whitespace-pre-wrap` text. (~3s each, ~22 hours)

4. **Output:** Feed into the existing SQLite+FTS5 database at `references/gpt-image2-prompts.db`.

**Practical approach:** Run Phase 1+2 first (gets title/description/category for all prompts in ~5 hours), then Phase 3 in batches for the prompts most relevant to the user's needs.

## Parser Script

The README parser is at `~/.hermes/scripts/parse-gpt-image2-prompts.py`. It:
1. Downloads the raw README.md
2. Extracts all 126 `### No. N:` entries with full prompt text
3. Classifies each by structure (Flat / Goal+Canvas+Sections / JSON)
4. Detects 23 techniques via regex patterns
5. Infers 12 categories from keywords
6. Builds SQLite+FTS5 database + JSON + category index

Re-run when the watchdog detects new README prompts:
```bash
curl -sf 'https://raw.githubusercontent.com/YouMind-OpenLab/awesome-gpt-image-2/main/README.md' > /tmp/gpt-image2-readme.md
python3 ~/.hermes/scripts/parse-gpt-image2-prompts.py
```

## Why Not CodeGraph?

CodeGraph indexes **code symbols and function call graphs** — it's for understanding codebases (how `functionA()` calls `functionB()`). Prompts are natural-language documents. The right tool for prompt organization is **SQLite + FTS5** for searchable structured data — same approach Hermes uses for session search.

## Watchdog Integration

The daily watchdog cron (`26c2c68477b8`) checks for README changes. When new prompts appear in the README, it should trigger a re-parse. The watchdog already patches the technique reference and updates the state file. To extend it to also rebuild the database, add a step that runs the parser script after detecting prompt count changes.

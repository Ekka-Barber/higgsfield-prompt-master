# RSC Flight Data Extraction Technique

## The Problem
Next.js App Router sites (youmind.com, many SaaS dashboards) render content via React Server Components (RSC). The content is NOT in the HTML DOM — it's embedded in serialized "flight data" chunks injected via `self.__next_f.push([1,"..."])` calls. Traditional scraping (BeautifulSoup, Selenium text extraction) misses it entirely.

## The Solution
Extract directly from the RSC flight data via curl — **no browser needed**.

### Step 1: Fetch via curl
```bash
curl -sf -L --max-time 10 "https://site.com/page/123"
```
This works even when Cloudflare blocks browser automation, because curl with default headers passes CF's basic checks.

### Step 2: Extract RSC chunks
```python
chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
```
Each chunk is a JSON-escaped string segment.

### Step 3: Unescape and join
```python
full_rsc = ""
for chunk in chunks:
    try:
        unescaped = json.loads('"' + chunk + '"')  # JSON-unescape
        full_rsc += unescaped
    except:
        full_rsc += chunk  # Fallback: append raw
```

### Step 4: Find content fields
The actual content (prompts, articles, data) is in `"text":"..."` fields:
```python
text_matches = re.findall(r'"text"\s*:\s*"((?:[^"\\]|\\.){50,})"', full_rsc)
```
The `{50,}` quantifier filters out short UI labels and navigation text.

### Step 5: Unescape the matched content
```python
prompt = json.loads('"' + best_match + '"')
```

## Performance Comparison
| Method | Speed | Browser Required | Cloudflare Safe |
|--------|-------|-----------------|----------------|
| CDP (browser DOM) | ~8s/prompt | Yes | No (blocked) |
| Playwright | ~5s/prompt | Yes | No (blocked) |
| **RSC curl extraction** | **~0.3s/prompt** | **No** | **Yes** |

**50x faster than CDP**, works when browsers are blocked.

## Applicability
This pattern works on ANY Next.js App Router site that uses RSC:
- `__next_f` is the universal RSC flight data marker
- Content is always in escaped JSON within `push([1,"..."])` calls
- The `"text":"..."` field pattern is common but not universal — inspect the raw RSC data to find the right field name for each site

## English-Only Filter
For prompt corpora, apply this filter before saving:
```python
def is_non_english(text):
    for ch in text:
        if ('\u3040' <= ch <= '\u309f' or   # Hiragana
            '\u30a0' <= ch <= '\u30ff' or   # Katakana
            '\u4e00' <= ch <= '\u9fff' or   # CJK Unified
            '\uac00' <= ch <= '\ud7af' or   # Hangul
            '\u0600' <= ch <= '\u06ff'):    # Arabic
            return True
    return False
```

## Production Implementation
The full production scraper is at `~/.hermes/scripts/gpt-image2-rsc-scraper.py` with:
- Parallel workers (25 concurrent curl requests)
- Progress tracking and resume capability
- SQLite + FTS5 storage
- The `is_non_english()` guard
- Meta tag extraction (title, model, category)

The minimal reusable pattern is in `scripts/rsc-prompt-extractor.py` within this skill.

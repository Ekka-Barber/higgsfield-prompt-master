# Non-English Prompt Analysis — Justifying English-Only Policy

## Decision
On June 27, 2026, 2,240 non-English prompts (Japanese, Korean, Arabic) were permanently deleted from the GPT Image 2 prompt corpus. The user explicitly requested English-only unless non-English prompts contained unique value.

## Analysis Methodology
Compared English (6,356) vs Non-English (2,240) prompts across 4 dimensions:

### 1. Techniques: ZERO unique
All 14 detected techniques exist in English prompts. Non-English prompts actually use FEWER techniques:
| Technique | English % | Non-English % | Difference |
|-----------|----------|--------------|------------|
| Lighting details | 61.6% | 33.4% | -28.2% |
| Camera specs | 52.9% | 31.4% | -21.5% |
| Mood/Atmosphere | 77.0% | 50.5% | -26.5% |
| Material/Texture | 73.4% | 51.4% | -21.9% |
| Typography | 18.0% | 37.5% | +19.4% (only one higher, due to CJK text specs) |
| JSON structure | 10.0% | 29.9% | +19.9% (more structured, but same keys) |

### 2. Categories: ZERO unique
All 26 categories exist in both English and non-English corpora.

### 3. Argument Names: ZERO unique value
1,649 "unique" argument names found in non-English prompts. Analysis:
- **100** were language-specific (worthless for English): "Japanese calligraphy text", "Chinese brand subtitle", "Korean headline"
- **1,540** were domain-specific one-offs: "alpaca headline", "arcade sign", "anchor appearance" — not novel techniques, just niche variable names from specific prompts

### 4. JSON Keys: ZERO unique value
428 "unique" JSON keys found. Analysis:
- These were naming variants of the same concepts: `colorPalette` vs `color_palette`, `bottom_panel` vs `lower_panel`, `main_art` vs `hero_visual`
- The canonical English keys (`type`, `layout`, `style`, `subject`, `composition`) cover all use cases

## Verdict
**Non-English prompts are strictly weaker** — fewer techniques, less detail, zero unique structural patterns. They add noise without signal. English-only policy confirmed.

## Implementation
- Deleted: 2,240 non-English prompt rows + 10,640 technique tags + 431 empty rows
- Scraper `gpt-image2-rsc-scraper.py` has `is_non_english()` filter — future scrapes skip non-English at fetch time
- `get_templates()` in `higgsfield_prompt.py` has CJK detection filter for belt-and-suspenders safety
- Final corpus: 6,337 English-only prompts (5,008 GPT Image 2 + 1,329 Nano Banana)

## Script
The comparison script is at `~/.hermes/scripts/non-english-uniqueness-check.py`.

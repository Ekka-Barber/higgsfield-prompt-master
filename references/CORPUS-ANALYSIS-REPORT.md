# Deep Study: GPT Image 2 Prompt Corpus Analysis
## Full Analytics Report — 8,596 Real Prompts from youmind.com

---

## Executive Summary

This report presents the complete analytical breakdown of **8,596 production-grade AI image prompts** scraped from youmind.com, the public prompt marketplace for GPT Image 2 (OpenAI) and Nano Banana Pro (Google Gemini). The corpus represents the largest structured collection of expert-authored image generation prompts available, spanning IDs 13,440–26,923 across 26 categories and 14 detectable techniques. This report also documents how the **Higgsfield Prompt Master** skill transforms this raw data into a searchable, generative system.

---

## 1. Corpus Overview

| Metric | Value |
|--------|-------|
| **Total prompts** | 8,596 (with full text) |
| Total rows scraped | 9,027 |
| Extraction rate | 95.2% |
| ID range | 13,440 – 26,923 |
| Valid IDs mapped | 23,847 (range 51–26,926) |
| Database size | 57 MB (SQLite + FTS5) |

### Model Distribution

| Model | Count | Share |
|-------|------:|------:|
| GPT Image 2 | 7,213 | 83.9% |
| Nano Banana Pro | 1,362 | 15.8% |
| Unlabeled | 21 | 0.2% |

**Key insight:** GPT Image 2 dominates the corpus by 5:1, reflecting its earlier launch and larger community. Nano Banana prompts skew more toward photography (Profile/Avatar = 12% vs 2.6% for GPT Image 2) and social media (46.2% vs 24.7%).

---

## 2. Structure Analysis — How Prompts Are Built

Four distinct structural paradigms exist in the corpus:

| Structure | Count | Share | Avg Length | Description |
|-----------|------:|------:|-----------:|-------------|
| **Template** | 6,221 | 72.4% | 1,458 chars | Uses `{argument name="..." default="..."}` placeholders |
| **JSON** | 1,306 | 15.2% | 2,496 chars | Structured JSON objects with typed keys |
| **Other** | 750 | 8.7% | 923 chars | Mixed/hybrid formats |
| **Flat prose** | 319 | 3.7% | 1,572 chars | Natural language paragraphs |

### The Three Architectures

**1. Template Architecture (72.4% of corpus)**
The dominant pattern. Prompts use argument placeholders that users fill in:
```
{argument name="subject" default="man in his early 30s"}
{argument name="location" default="European city sidewalk"}
{argument name="outfit" default="Oversized vintage black leather biker jacket"}
```
Average 2.7 arguments per prompt. 4,892 unique argument names exist, but a core vocabulary dominates (see §5).

**2. JSON Architecture (15.2% of corpus)**
Structured prompts using typed JSON objects. Longest on average (2,496 chars). Canonical schema:
```json
{
  "type": "character reference sheet",
  "style": "...",
  "layout": {...},
  "composition": "...",
  "lighting": "..."
}
```
Top keys: `type` (91.9%), `layout` (73.5%), `style` (61.5%), `subject` (29.8%).

**3. Prose Architecture (3.7% of corpus)**
Natural language paragraphs, typically starting with "Create a..." or "Photorealistic...". Shorter average length but highly descriptive.

---

## 3. Length Distribution

| Metric | Value |
|--------|-------|
| Mean | 1,573 chars |
| Median | 1,402 chars |
| Std dev | 1,061 chars |
| P25 | 788 chars |
| P75 | 2,151 chars |
| P95 | 3,576 chars |
| Max | 15,954 chars |

```
<200       639   7.4%  █████
200-500    632   7.4%  █████
500-1K   1,513  17.6%  █████████████
1K-2K    3,398  39.5%  ██████████████████████████████  ← MAJORITY
2K-3K    1,421  16.5%  ████████████
3K-4K      846   9.8%  ███████
4K-5K      107   1.2%
5K+         40   0.5%
```

**Key insight:** The sweet spot is 1,000–2,000 characters (39.5% of corpus). Prompts below 500 chars tend to be low-complexity social media posts. Prompts above 3,000 chars are typically multi-panel storyboards or complex UI mockups with per-section specifications.

---

## 4. Category Distribution

26 categories, but the distribution is heavily long-tailed:

| Category | Count | Share |
|----------|------:|------:|
| Social Media Post | 2,409 | 28.0% |
| Product Marketing | 1,550 | 18.0% |
| Poster / Flyer | 1,185 | 13.8% |
| Comic / Storyboard | 819 | 9.5% |
| Profile / Avatar | 738 | 8.6% |
| Game Asset | 649 | 7.6% |
| Infographic / Edu Visual | 647 | 7.5% |
| App / Web Design | 253 | 2.9% |
| YouTube Thumbnail | 65 | 0.8% |
| E-commerce Main Image | 47 | 0.5% |
| All others (16 cats) | 234 | 2.7% |

**Key insight:** The top 3 categories (Social Media, Product Marketing, Poster/Flyer) account for **59.8%** of all prompts. These are commercial/marketing use cases — the community is overwhelmingly creating prompts for business applications, not artistic exploration.

### Category × Technique Cross-Tabulation

Each category has distinct technique fingerprints:

| Category | Dominant Technique Pattern |
|----------|---------------------------|
| **Social Media Post** | Arguments (86%) + Camera specs (64%) + Mood (73%) |
| **Product Marketing** | Arguments (90%) + Material/Texture (79%) + Layout (71%) |
| **Poster / Flyer** | Arguments (88%) + Layout (78%) + Mood (77%) |
| **Comic / Storyboard** | Arguments (84%) + Layout (69%) + Mood (75%) |
| **App / Web Design** | Arguments (84%) + Layout (78%) + **UI/UX terms (68%)** |
| **Infographic** | Arguments (81%) + Layout (76%) + **Typography (46%)** |

**Insight:** Camera specifications are notably higher in Social Media (64%) and Profile/Avatar categories — these are photography-heavy. Typography and UI/UX terms are the signature techniques of Infographic and App/Web Design categories respectively.

---

## 5. Technique Analysis

14 techniques detected across the corpus, averaging **5.5 techniques per prompt** (max: 12):

| Technique | Count | Share |
|-----------|------:|------:|
| Arguments/Templates | 7,339 | 85.4% |
| Mood/Atmosphere | 6,029 | 70.1% |
| Material/Texture | 5,815 | 67.6% |
| Layout/Composition | 5,746 | 66.8% |
| Lighting details | 4,666 | 54.3% |
| Camera specs | 4,066 | 47.3% |
| UI/UX terms | 2,319 | 27.0% |
| Aspect ratio specs | 2,179 | 25.3% |
| Typography | 1,986 | 23.1% |
| Color palette | 1,834 | 21.3% |
| Reference images | 1,389 | 16.2% |
| JSON structure | 1,306 | 15.2% |
| Negative prompts | 1,047 | 12.2% |
| Step-by-step | 57 | 0.7% |

### Technique Co-occurrence (Top Pairs)

The most common technique pairings reveal prompt architecture patterns:

| Pair | Count |
|------|------:|
| Arguments + Mood/Atmosphere | 5,320 |
| Arguments + Material/Texture | 5,128 |
| Arguments + Layout/Composition | 5,010 |
| Material/Texture + Mood/Atmosphere | 4,938 |
| Layout/Composition + Mood/Atmosphere | 4,730 |

**Insight:** The "golden pentagon" of prompt engineering is: **Arguments + Mood + Material/Texture + Layout + Lighting**. Over 50% of prompts combine all five. This is the baseline quality standard for GPT Image 2 prompts.

---

## 6. Vocabulary & Phrase Analysis

### Top Content Words (excluding stop words and template syntax)

| Word | Count | % of Corpus |
|------|------:|------------:|
| background | 5,306 | 61.7% |
| texture | 3,706 | 43.1% |
| cinematic | 3,398 | 39.5% |
| portrait | 2,652 | 30.9% |
| depth of field | 1,944 | 22.6% |
| illustration | 1,903 | 22.1% |
| glossy | 1,872 | 21.8% |
| elegant | 1,860 | 21.6% |
| modern | 1,842 | 21.4% |
| poster | 1,690 | 19.7% |
| premium | 1,639 | 19.1% |
| photorealistic | 1,624 | 18.9% |
| typography | 1,622 | 18.9% |
| render | 1,585 | 18.4% |
| logo | 1,563 | 18.2% |
| anime | 1,468 | 17.1% |
| luxury | 1,166 | 13.6% |
| headline | 986 | 11.5% |
| brand | 927 | 10.8% |

### Recurring Instruction Phrases

| Phrase | Count | % |
|--------|------:|---:|
| depth of field | 1,944 | 22.6% |
| photorealistic | 1,624 | 18.9% |
| shallow depth | 1,583 | 18.4% |
| no watermark | 1,013 | 11.8% |
| highly detailed | 963 | 11.2% |
| no text | 744 | 8.7% |
| professional | 740 | 8.6% |
| bokeh | 713 | 8.3% |
| minimalist | 705 | 8.2% |
| rim light | 635 | 7.4% |
| color grading | 610 | 7.1% |
| studio lighting | 549 | 6.4% |
| symmetrical | 535 | 6.2% |

### Spatial Vocabulary

The corpus is heavily spatial. Key positional words and their frequencies:

| Word | Count | | Word | Count |
|------|------:|-|------|------:|
| right | 10,877 | | center | 4,287 |
| left | 10,644 | | top | 5,920 |
| bottom | 5,256 | | upper | 1,795 |
| vertical | 4,247 | | lower | 2,043 |

**Insight:** GPT Image 2 prompts are extremely spatial — creators treat the canvas as a grid with explicit zone assignments. "Right" and "left" appear more than "the" relative to prompt length. This is a defining characteristic: **GPT Image 2 prompting is layout specification, not description.**

---

## 7. Argument Template Deep Dive

4,892 unique argument names across 6,574 template prompts (76.5% of corpus).

### Top 30 Argument Names

| Argument | Count | % of Corpus |
|----------|------:|------------:|
| subject | 1,226 | 14.3% |
| hair color | 817 | 9.5% |
| outfit | 629 | 7.3% |
| character name | 534 | 6.2% |
| headline text | 344 | 4.0% |
| location | 300 | 3.5% |
| clothing | 291 | 3.4% |
| setting | 276 | 3.2% |
| background | 233 | 2.7% |
| style | 223 | 2.6% |
| brand name | 212 | 2.5% |
| hair style | 178 | 2.1% |
| color palette | 131 | 1.5% |
| lighting | 120 | 1.4% |
| character description | 104 | 1.2% |

**Insight:** The top arguments cluster around 4 axes:
1. **Identity**: subject, character name, character description
2. **Appearance**: hair color, hair style, outfit, clothing
3. **Environment**: location, setting, background
4. **Design**: style, brand name, headline text, color palette

### Default Value Patterns

Default values are heavily domain-specific:
- `background` defaults: "white background" (most common), "clean white background"
- `brand name` defaults: "BRAND NAME", "[BRAND NAME]", "SECURE-IP", "AUREUS", "LOEWE"
- `product name` defaults: "IP ADDRESS CLEANSER", "Banas™", "Creative Cloud"
- `mood` defaults: "cozy, wholesome, gentle", "confident, playful, expressive"

---

## 8. JSON Schema Analysis

903 valid JSON prompts were parsed and analyzed.

### Canonical JSON Schema

```
┌─ type (91.9%) ──────── Short descriptor: "character reference sheet"
├─ layout (73.5%) ────── Grid/zone specifications
├─ style (61.5%) ─────── Visual aesthetic descriptor
├─ subject (29.8%) ───── Main subject definition
├─ composition (20.3%) ─ Framing/composition instructions
├─ format (16.7%) ────── Output format specification
├─ quality (15.4%) ───── Quality/resolution directives
├─ canvas (11.8%) ────── Physical canvas description
├─ theme (11.7%) ─────── Thematic descriptor
├─ color_palette (11%) ─ Explicit color specification
├─ header (10.7%) ────── Header section (UI/poster)
├─ character (10.7%) ─── Character definition object
├─ rendering (10.2%) ─── Render style specification
├─ typography (9.2%) ─── Font/text specifications
├─ background (8.7%) ─── Background specification
├─ lighting (7.6%) ───── Lighting setup
└─ camera (7.2%) ─────── Camera/lens specifications
```

### Most Common "type" Values

| Type | Count |
|------|------:|
| anime character reference sheet | 17 |
| website landing page mockup | 6 |
| character reference sheet | 4 |
| Japanese infographic poster | 4 |
| educational infographic | 3 |
| video game screenshot | 3 |
| manga page | 3 |
| medical infographic poster | 3 |

**Insight:** JSON prompts are used primarily for complex, multi-section compositions (character sheets, infographics, UI mockups) where structured specification of each element is needed. The `type` field serves as the prompt's category label.

---

## 9. Language Distribution

| Language | Count | Share |
|----------|------:|------:|
| English | 6,356 | 73.9% |
| Japanese | 2,129 | 24.8% |
| Korean | 96 | 1.1% |
| Arabic | 15 | 0.2% |

**Insight:** Nearly a quarter of all prompts contain Japanese text. This reflects youmind.com's origin as a Japanese prompt marketplace. The skill filters to English-only prompts by default when generating, but the full multilingual corpus remains searchable.

---

## 10. Prompt Opening Patterns

| Opening Pattern | Count | % |
|-----------------|------:|---:|
| Other (various) | 2,974 | 34.6% |
| "Create..." | 1,895 | 22.0% |
| "A..." (article) | 1,759 | 20.5% |
| JSON ({...}) | 1,306 | 15.2% |
| "Goal:..." | 592 | 6.9% |
| Other directives | 70 | 0.8% |

**Insight:** "Create" is the most common verb opener (22%), followed by article-led descriptions (20.5%). The "Goal:" pattern (6.9%) is a distinctive template format that provides a goal statement followed by structured Canvas/Style/Layout sections.

---

## 11. Complexity Scoring

Prompts were scored on a composite metric (length + techniques + structure bonus):

| Complexity | Count | % |
|-----------|------:|---:|
| Simple (score <5) | 1,092 | 12.7% |
| Moderate (5-10) | 2,680 | 31.2% |
| Detailed (10-15) | 3,470 | 40.4% |
| Complex (15-20) | 1,243 | 14.5% |
| Expert (20+) | 111 | 1.3% |

The "Detailed" tier (10-15 score) is the modal complexity — these are professional-grade prompts with 5-7 techniques, 1,000-2,000 characters, and template/JSON structure.

### Top 5 Most Complex Prompts

| Score | ID | Title | Chars | Techs |
|------:|-----|-------|------:|------:|
| 42.9 | 22544 | Glitch Aesthetic Anime Illustration | 15,954 | 8 |
| 27.2 | 19298 | AI Ad and Infographic Capability Collage | 6,598 | 11 |
| 26.2 | 20861 | AI Infrastructure Infographic Poster | 7,108 | 10 |
| 26.1 | 25741 | Sydney Sweeney Biometric Portrait | 8,025 | 7 |
| 24.9 | 17134 | Luxury Footwear Brand Identity Board | 5,471 | 11 |

---

## 12. Model Comparison: GPT Image 2 vs Nano Banana

| Dimension | GPT Image 2 | Nano Banana |
|-----------|------------|-------------|
| **Count** | 7,213 (84%) | 1,362 (16%) |
| **Avg length** | 1,634 chars | 1,267 chars |
| **Template %** | 72.8% | 71.0% |
| **JSON %** | 14.4% | 19.6% |
| **Camera specs** | 44.6% | 62.0% |
| **Layout/Comp** | 70.7% | 47.3% |
| **Lighting** | 52.8% | 63.1% |
| **Top category** | Social Media (24.7%) | Social Media (46.2%) |
| **Profile/Avatar** | 2.6% | 12.0% |

**Key Differences:**
- **Nano Banana** prompts are shorter, more photography-focused (Camera 62% vs 45%), and concentrate heavily in Social Media (46%) and Profile/Avatar (12%)
- **GPT Image 2** prompts are longer, more layout-focused (Layout 71% vs 47%), and spread more evenly across design categories (Posters, Infographics, Comics)
- **Nano Banana uses more JSON** (19.6% vs 14.4%) — suggesting the Gemini community prefers structured prompting

---

## 13. Aspect Ratio Distribution

| Ratio | Count | % | Use Case |
|-------|------:|---:|----------|
| 16:9 | 574 | 6.7% | Landscape, YouTube, dashboards |
| 9:16 | 560 | 6.5% | Stories, Reels, TikTok |
| 3:4 | 406 | 4.7% | Portrait, posters |
| 4:5 | 401 | 4.7% | Instagram feed |
| 2:3 | 348 | 4.0% | Portrait photography |
| 1:1 | 228 | 2.7% | Square, avatars |

**Insight:** Most prompts do NOT specify an explicit aspect ratio (75%+ have no `--ar` flag or ratio mention). The aspect ratio is instead embedded in the prompt's layout description (e.g., "vertical 9:16", "wide landscape").

---

## 14. How the Higgsfield Prompt Master Skill Uses This Corpus

The skill transforms raw prompt data into an actionable system through **6 core capabilities**:

### 14.1 Search & Retrieval

**`search(query, category, model, structure, techniques, limit)`**
- Multi-term OR search across title, description, and full prompt text
- Filters by category (26 options), model (GPT Image 2 / Nano Banana), structure type, and detected techniques
- Returns `Prompt` objects with all metadata

**`fts_search(query, limit)`**
- SQLite FTS5 full-text search for complex multi-word queries
- Better ranking than LIKE-based search
- Tokenized and indexed for sub-millisecond queries

**Use case:** "Find all glassmorphism dashboard prompts in JSON format" → returns the 3-5 best real-world examples to study or adapt.

### 14.2 Category Intelligence

**`category_guide(category)`**
Returns a complete intelligence brief for any category:
- Total prompt count
- Average length statistics (mean, median, range)
- Structure breakdown (Template/JSON/Flat/Other percentages)
- Top 10 techniques with frequency
- Best example prompts

**Use case:** Before generating a "Product Marketing" prompt, the agent calls `category_guide("Product Marketing")` to learn that 90% of prompts in this category use argument templates, 79% specify materials/textures, and the average length is 1,500+ characters. This sets quality expectations.

### 14.3 Pattern Analysis

**`analyze_patterns(category)`**
Extracts structural patterns from a category:
- Most common argument names and default values
- JSON key frequency and schema shapes
- Vocabulary frequency
- Opening patterns

### 14.4 Prompt Generation

**`generate_prompt(goal, category, structure, style, aspect_ratio)`**

Three generation modes, each grounded in real corpus patterns:

**JSON Mode:** Selects the highest-scoring (longest + most techniques) English JSON prompt from the target category, parses it, and injects the user's `goal` into the `type` field and `style` into the `style` field. This produces a structurally complete, production-grade JSON prompt.

**Template Mode:** Builds an argument-template prompt using category-specific argument vocabularies. For "Product Marketing" it includes `product`, `hero_shot`, `accent_color`. For "App / Web Design" it includes `screen`, `theme`, `components`.

**Flat Prose Mode:** Assembles a natural-language prompt using the user's goal + style + technique-based directives (lighting setup, depth of field, color grading, etc.) derived from the most frequent phrases in the corpus.

### 14.5 Model Comparison

**`compare_models(model1, model2)`**
Side-by-side comparison of structure distribution, technique frequency, and category distribution. Used to decide which model's patterns to follow for a given task.

### 14.6 Random Inspiration

**`random_prompt(category, model, structure)`**
Returns a random real prompt for creative inspiration. Useful for exploring patterns outside the user's usual categories.

### Data Flow Architecture

```
User Request
    │
    ▼
┌─────────────────────────┐
│  HiggsfieldPromptMaster │
├─────────────────────────┤
│  1. Parse intent        │
│  2. category_guide()    │ ← Learns category conventions
│  3. get_templates()     │ ← Gets best real examples (English-filtered)
│  4. generate_prompt()   │ ← Synthesizes new prompt from patterns
│  5. fts_search()        │ ← Optionally finds similar real prompts
└────────────┬────────────┘
             │
             ▼
     Generated Prompt
     (grounded in 8,596 real examples)
```

---

## 15. Key Findings & Actionable Insights

### 15.1 The GPT Image 2 Prompting Standard

Based on the corpus, a high-quality GPT Image 2 prompt has:
- **1,000–2,000 characters** (the modal range)
- **5–7 techniques** from the detected set of 14
- **Argument templates** for customizability (72% use them)
- **Explicit layout instructions** with spatial positioning (66.8%)
- **Material/texture specifications** (67.6%)
- **Mood/atmosphere directives** (70.1%)
- **Lighting specifications** (54.3%)

### 15.2 The Argument Vocabulary

The core argument vocabulary across all categories:
1. **subject** (14.3%) — The main subject/person/character
2. **hair color** (9.5%) — Hair customization
3. **outfit** (7.3%) — Clothing specification
4. **character name** (6.2%) — Named character branding
5. **headline text** (4.0%) — Poster/advertising text
6. **location** (3.5%) — Setting/environment
7. **style** (2.6%) — Visual aesthetic override
8. **brand name** (2.5%) — Commercial branding

### 15.3 The JSON Schema Standard

For structured prompts, the canonical key hierarchy:
```
type → layout → style → subject → composition → format → quality
```
91.9% of JSON prompts have `type`. 73.5% have `layout`. 61.5% have `style`.

### 15.4 Category-Specific Best Practices

| Category | Recommended Structure | Key Techniques | Avg Length |
|----------|----------------------|----------------|-----------:|
| Social Media Post | Template | Camera, Mood, Material | 1,500 chars |
| Product Marketing | Template | Material, Layout, Lighting | 1,800 chars |
| Poster / Flyer | Template | Layout, Mood, Typography | 1,700 chars |
| Comic / Storyboard | Template or JSON | Layout, Mood, Material | 2,000 chars |
| App / Web Design | JSON | UI/UX, Layout, Material | 2,000 chars |
| Infographic | JSON | Layout, Typography, Material | 2,200 chars |
| Game Asset | Template | Layout, Material, Mood | 1,600 chars |
| Profile / Avatar | Template | Material, Mood, Lighting | 1,500 chars |

---

## 16. Limitations & Notes

1. **Source bias:** 24.8% of prompts are Japanese-language, reflecting youmind.com's origin. The skill filters to English by default but the full corpus remains accessible.

2. **Extraction gap:** 431 prompts (4.8%) have metadata but no full text — these were pages where RSC extraction failed (likely due to dynamic rendering or rate limiting).

3. **Technique detection:** The 14 detected techniques use keyword matching, which may miss synonyms or novel techniques. Step-by-step instructions (0.7%) are likely undercounted.

4. **Category assignment:** Each prompt has exactly 1 category. Some prompts could reasonably belong to multiple categories (e.g., an "Instagram product ad" could be both Social Media Post and Product Marketing).

5. **Temporal bias:** Prompts span a ~2-year period. Earlier prompts may reflect less mature prompting techniques. The corpus does not include timestamps for temporal analysis.

---

## Appendix: Database Schema

```sql
-- Main table
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    prompt_text TEXT,
    categories TEXT,        -- pipe-separated
    model TEXT,
    slug TEXT,
    has_prompt INTEGER,
    structure_type TEXT,
    length_chars INTEGER,
    technique_tags TEXT     -- JSON array
);

-- Technique junction table
CREATE TABLE prompt_techniques (
    prompt_id INTEGER,
    technique TEXT,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id)
);

-- Full-text search
CREATE VIRTUAL TABLE prompts_fts USING fts5(
    title, description, prompt_text, categories,
    content='prompts', content_rowid='id'
);
```

---

*Report generated from 8,596 prompts in the Higgsfield Prompt Master corpus.*
*Database: `~/.hermes/skills/higgsfield-prompt-master/references/gpt-image2-prompts-full.db`*
*Skill: `~/.hermes/skills/higgsfield-prompt-master/`*

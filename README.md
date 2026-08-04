# 🎨 Higgsfield Prompt Master

> The Ultimate GPT Image 2 Prompt Reference & Generation Tool — built from **7,613 real prompts** scraped from youmind.com, with photography, marketing, and art-direction intelligence layers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Prompts](https://img.shields.io/badge/corpus-7%2C613%20prompts-green)](#corpus)
[![Categories](https://img.shields.io/badge/categories-26-orange)](#categories)

## What this is

A production-grade GPT Image 2 prompt engineering system that combines:

1. **A curated corpus** of 6,337 real, scraped, and categorized GPT Image 2 prompts (English-only, cleaned, enriched)
2. **A retrieval system** (FTS5-backed) to find similar prompts by intent, structure, and technique
3. **An intelligent generator** that adapts corpus patterns to your specific use case
4. **Photography / marketing / art-direction intelligence layers** that inject expert specs into prompts
5. **Quality scoring** to grade generated prompts before they're sent to the model
6. **Model auto-selection** (GPT Image 2 vs. Nano Banana 2) based on prompt category

This is a **Hermes Agent skill** — designed to run inside the [Higgsfield MCP workflow](https://github.com/Ekka-Barber/higgsfield-mcp) for native Telegram image delivery.

## ✨ Key features

- **RAG-based generation** — retrieves real corpus prompts via FTS5 search and adapts them, rather than guessing from scratch
- **English-only corpus** — non-English prompts were analyzed and removed (zero unique value; see [`references/non-english-analysis.md`](references/non-english-analysis.md))
- **26 categories** — from `abstract` and `architecture` to `portraits`, `posters`, `infographics`, and `branded-content`
- **14 techniques tagged** — "Exact Counting", "Spatial Anchoring", "Face Lock", "Style References", and more
- **3 prompt structures** identified and reproduced — Flat, Goal+Canvas+Sections, and JSON
- **Quality scoring** — grades prompts A+ to F on 8 dimensions before generation
- **Multi-model routing** — auto-selects the best Higgsfield model for the prompt type

## 📦 Installation

### As a Hermes Agent skill

Copy this directory into `~/.hermes/skills/higgsfield-prompt-master/` and Hermes will auto-discover it.

### Standalone (without Hermes)

```bash
git clone https://github.com/Ekka-Barber/higgsfield-prompt-master.git
cd higgsfield-prompt-master
pip install -r requirements.txt  # see dependencies below

# Download the prompt corpus (57 MB, distributed via Releases)
# See: https://github.com/Ekka-Barber/higgsfield-prompt-master/releases
```

### Dependencies

```
torch>=2.0
transformers>=4.40
sentence-transformers>=2.5
sqlite-utils
```

## 🚀 Usage

### Generate a prompt

```python
from higgsfield_prompt import HiggsfieldPromptGenerator

gen = HiggsfieldPromptGenerator()

# Generate a product photography prompt
prompt, model = gen.generate(
    intent="product_shot",
    subject="luxury perfume bottle",
    style="editorial fashion magazine",
    quality="high"
)
print(f"Model: {model}")
print(f"Prompt: {prompt}")
```

### Search the corpus

```python
from higgsfield_prompt import HiggsfieldPromptGenerator

gen = HiggsfieldPromptGenerator()
results = gen.search("minimalist product photography with hands", limit=5)
for r in results:
    print(f"[{r['quality_score']}] {r['prompt'][:100]}...")
```

### Run the demo

```bash
python demo.py
```

## 📚 Corpus

The prompt corpus is the heart of this tool. It contains **7,613 prompts** scraped from youmind.com (a public GPT Image 2 prompt gallery) using a custom RSC flight-data extraction technique.

### What's in it

| Attribute | Value |
|---|---|
| Total prompts | **7,613** |
| GPT Image 2 prompts | 5,008 |
| Nano Banana prompts | 1,329 |
| Categories | 26 |
| Techniques tagged | 14 |
| Prompt structures identified | 3 (Flat, Goal+Canvas+Sections, JSON) |
| Avg. prompt length (sweet spot) | 1,000–2,000 chars |
| Template-heavy prompts | 72.4% of corpus |

### Download the corpus

The corpus is distributed as a SQLite database with FTS5 full-text search, via GitHub Releases (too large for the repo itself):

| File | Size | Contents |
|---|---|---|
| `gpt-image2-prompts-full.db` | 56 MB | Full corpus (7,613 prompts, FTS5 index) with FTS5 index, enriched metadata |
| `gpt-image2-prompts.db` | 912 KB | Compact subset (top 1,000 by quality score) |
| `prompt-id-map.json` | 246 KB | 23,847 valid prompt IDs for re-scraping |

➡️ **[Download from Releases](../../releases/latest)**

### Why English-only?

We analyzed all 2,240 non-English prompts in the original corpus and found they contributed **zero unique techniques, categories, or structures** beyond what the English prompts already covered. The full analysis is in [`references/non-english-analysis.md`](references/non-english-analysis.md). Short version: GPT Image 2 doesn't understand non-English prompts any better than English, and English prompts produce more predictable results.

## 🗂️ Categories

The corpus covers 26 categories, each with its own reference guide:

`abstract` · `architecture` · `avatars` · `branded-content` · `branded-social-invitation` · `cinematic` · `ecommerce` · `fashion` · `food` · `game-assets` · `infographics` · `interior-design` · `photo-editing` · `portraits` · `posters` · `social-media`

Each category has a dedicated reference file in [`references/`](references/) with expert guidance, camera specs, lighting setups, and example prompts.

## 🧠 Architecture

```
higgsfield_prompt.py     # Core: corpus loading, FTS5 search, generation, scoring
intelligence.py          # Expert layers: photography, marketing, art direction
demo.py                  # Usage examples
references/              # Category guides + scraping techniques + corpus analysis
scripts/                 # RSC prompt extractor + diversity verifier
```

### How generation works

1. **Intent classification** — your request is mapped to one of 26 categories
2. **Corpus retrieval** — FTS5 searches the 6,337-prompt corpus for similar prompts
3. **Intelligence injection** — photography/marketing/art-direction specs are added based on category
4. **Structure selection** — Flat, Goal+Canvas+Sections, or JSON, based on corpus patterns
5. **Quality scoring** — the final prompt is graded on 8 dimensions
6. **Model routing** — the best Higgsfield model is selected (GPT Image 2 vs. Nano Banana 2)

## 📖 References

The [`references/`](references/) directory contains deep-dive guides:

- [`CORPUS-ANALYSIS-REPORT.md`](references/CORPUS-ANALYSIS-REPORT.md) — full statistical analysis of the corpus
- [`gpt-image-2-techniques.md`](references/gpt-image-2-techniques.md) — the 14 identified prompting techniques
- [`rsc-extraction-technique.md`](references/rsc-extraction-technique.md) — how we scraped the corpus
- [`gpt-image2-gallery-scraping.md`](references/gpt-image2-gallery-scraping.md) — gallery scraping methodology
- Category guides (16 files) — expert specs per category

## 🔗 Related

- **[higgsfield-mcp](https://github.com/Ekka-Barber/higgsfield-mcp)** — The companion Hermes skill that uses this tool to generate images via Higgsfield MCP and deliver them as native Telegram photos
- **[Higgsfield](https://higgsfield.ai)** — The AI image generation platform this tool targets
- **[Hermes Agent](https://github.com/NousResearch/hermes-agent)** — The AI agent runtime this skill runs inside

## 📝 License

MIT — see [`LICENSE`](LICENSE). The prompt corpus itself is scraped from publicly accessible web pages and is provided for research and educational purposes.

## 🙏 Acknowledgments

- The youmind.com community for publishing their GPT Image 2 prompts
- The Hermes Agent project by Nous Research
- OpenAI for GPT Image 2 (the model this tool targets)

---

*Built by [Majed](https://github.com/Ekka-Barber) for the Hermes Agent ecosystem.*

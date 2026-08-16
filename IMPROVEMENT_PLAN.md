# Improvement Plan — higgsfield-prompt-master

*Generated 2026-08-17 by a four-agent deep study (code review, architecture, AI-engine
evaluation, data engineering). Every finding below was verified empirically against the
live code and database — crashes were reproduced, queries were run, outputs were compared.
File:line references point at this working tree.*

---

## Executive summary

The corpus is real and the retrieval layer is healthy (6,337 curated prompts, FTS index
fresh, English-only policy verifiably held, DB byte-identical to the v2.1.1 GitHub Release
asset). But the product currently delivers a fraction of its own story:

1. **The "RAG" is decorative** — retrieved corpus prompts never reach the generated text.
   Proven: different retrieval inputs produce byte-identical outputs.
2. **71% of `intelligence.py` is dead code** — Layers 3/4/5 (`ART_DIRECTION`,
   `GPT_IMAGE_2`, `NANO_BANANA`, incl. the un-pushed Layer 4 work) are never imported by
   the generation pipeline.
3. **Two guaranteed crashes** ship in the advertised paths: FTS5 search on inputs
   containing `"` and `demo.py` (broken since the V2 cutover).
4. **17% of the corpus is invisible** — 1,276 text-bearing harvest rows have
   `has_prompt=0` and are filtered out of every query, and `enrich_all()` can never fix
   them.
5. **~4% of the "curated" set is scrape garbage** — 253 rows of share-widget boilerplate.
6. **The DB is not rebuildable** — no committed script writes to the database; the
   production scraper it references doesn't exist in the repo.

The single highest-leverage change: **wire Layers 4/5 into `generate_prompt()` and make
generation actually consume retrieval** (Phase 1, item 1). ~40 lines activates 460 lines
of the best curated knowledge and the corpus the system already pays to search.

---

## P0 — Critical bugs (fix before anything else)

### P0-1. FTS5 crash on embedded double quotes 🔴
`higgsfield_prompt.py:265` — `" ".join(f'"{t}"' for t in terms)`. An embedded `"` in any
term terminates the FTS5 phrase → `sqlite3.OperationalError: unterminated string`.
Reproduced: `hpm.fts_search('dashboard "glass')` and
`generate_prompt(goal='grunge wo"rd aesthetic poster')` both crash. SKILL.md claims this
is "FIXED" — it isn't.
**Fix:** double embedded quotes when wrapping (`t.replace('"', '""')`), and wrap each
`_do_search` strategy in `try/except sqlite3.OperationalError` so a bad term degrades to
the next fallback instead of crashing. Regression test: `'dashboard "glass'`.

### P0-2. demo.py cannot run 🔴
`demo.py:70,79,89` — slices `generate_prompt()`'s dict result as a string →
`KeyError: slice(...)`. Advertised in SKILL.md's maintenance section; broken since V2.
**Fix:** `result['prompt'][:300]` in the three generation examples; drop duplicate
`from pathlib import Path` (lines 9, 13).

### P0-3. Un-pushed Layer 4/5 work is only in git-untracked copies 🔴
`intelligence.py` (+331 lines: GPT_IMAGE_2 + NANO_BANANA layers) exists nowhere in git
history. Two copies exist on disk (skill hub + this clone) — zero in version control.
**Fix:** commit it in this clone and push.

### P0-4. Silent empty-DB creation on bad path 🔴
`higgsfield_prompt.py:133–173` — a typo'd `HIGGSFIELD_DB` creates a 0-byte DB, then fails
with a confusing `no such table: prompts`. Also: DDL + `commit()` run on *every*
instantiation, so reads require write access to the 57MB shared DB.
**Fix:** raise `FileNotFoundError` listing candidate paths when nothing exists; open
read-only (`file:...?mode=ro`) unless enriching; move enrichment DDL out of `__init__`.

---

## P1 — Make the product match its story

### P1-1. Wire retrieval + Layers 3/4/5 into generation (highest leverage)
- `higgsfield_prompt.py:718–806` `_synthesize_template` receives `sections`/`real_args`
  from the retrieved corpus prompt and never uses them. Same for `_generate_flat_v2`
  (834–887) and `_generate_json_v2` (889–957). `source_prompt_ids` is provenance theater.
- `generate_prompt()` imports only photo/marketing/mood (lines 499–506). Never wired:
  `ART_DIRECTION` (intelligence.py:185–219), `GPT_IMAGE_2` + accessor (328–484),
  `NANO_BANANA` + accessor (501–645). `_recommend_model()` output (line 542) is computed
  and discarded.
- Evidence of the quality gap: for goal "analytics dashboard", the retrieved exemplar
  (id 13440) has a real zone schema with element counts; the generated JSON has zero
  zones/counts — the generator is strictly worse than its own retrieval.

**Fix (S, ~40 lines + synthesizer work):**
1. Slot-fill: borrow the top retrieved exemplar's zone skeleton / section names /
   argument names (2–4 arguments — corpus average is 2.7; current output emits 1).
2. Keyed off `_recommend_model()`, inject the model layer: negative-prompt block,
   exact-count phrases, JSON zone schema, token-budget check; `REFERENCE_N`/face-lock
   clauses when routed to Nano Banana.
3. Check goal platform keywords *before* the category map (fixes LinkedIn goal →
   Instagram safe-zones mismatch).

### P1-2. Repair the corpus pipeline (the 1,276 invisible rows)
- All Aug-2026 harvest rows have real text (avg 1,499 chars) but `has_prompt=0` →
  excluded by `search()`, `fts_search()`, `get_templates()`, `category_guide()`, `stats()`.
- `enrich_all()` filters `has_prompt=1` (line 178) → the documented maintenance command
  can never repair them. SKILL.md/README advertise 7,613; every feature serves 6,337.
- Categories format split: June rows use pipe-separated strings, Aug rows use
  JSON-stringified arrays (`["Social Media Post"]`) — `Prompt.from_row` splits on `|`
  only, so aggregation paths split every category in two.

**Fix:** set `has_prompt=1` for the 1,276 text-bearing rows (or better: migrate to a
`status` column: curated/harvested/excluded), normalize categories to one canonical form,
change `enrich_all()` filter to `WHERE (structure_type IS NULL OR technique_tags IS NULL)`,
rebuild FTS, re-run enrichment.

### P1-3. Purge boilerplate contamination
291 rows share the identical 101-char share-widget text `Just found a great AI prompt:
"{title}"...` — **253 inside the curated set**, across every major category. Root cause:
the extractor's "longest `"text"` field" heuristic grabbed the wrong RSC field.
**Fix:** delete by signature `prompt_text LIKE 'Just found a great AI prompt%'`; add an
ingestion-time guard rejecting the pattern; dedupe 4 exact-dup pairs.

### P1-4. Make the quality score discriminative
`_quality_score` gives `goal="x"` → A+ 90/100. Specificity vocabulary is 100% photography
words, so UI/JSON categories cap at 68–83 while any photo goal lands 87–100.
**Fix:** rubric-based scoring — structure-vs-category preference match, JSON zone/count
specificity, Layer-4 checklist coverage (negative block present, text-block lengths within
limits), balanced UI + photography vocabularies, length band.

### P1-5. Honest metadata & docs
- README documents a phantom API (`HiggsfieldPromptGenerator`, `gen.generate(...)`) and
  fiction dependencies (torch/transformers; `requirements.txt` doesn't exist). Code is
  pure stdlib. Rewrite README around the real API (60% shorter).
- SKILL.md's FTS schema section is fiction (claims 5 columns + porter; actual: 3 columns,
  unicode61, external-content). Stats table matches neither the 6,337 usable subset nor
  the 7,613 total. `__init__.py` claims `__version__ 1.0.0` / corpus 8,596 — both wrong,
  and the file is unreachable anyway (hyphenated dir name can't be a package).
- ID range claim "51–28,686" wrong (actual min 13,440).
**Fix:** single-source version + generate SKILL.md stats block from `hpm.stats()`.

---

## P2 — Structural & data quality

| # | Item | Notes | Effort |
|---|------|-------|--------|
| P2-1 | `get_photo_intelligence()` never returns `None` (intelligence.py:253–271) — explicit "not photography" mappings fall through to the `lifestyle` default; camera specs leak into abstract/UI categories; `intelligence.photography` always `True` | Distinguish explicit-none from unmapped; add the missing non-photo guard to `_build_from_intelligence` (808–832) — the one generator without it | S |
| P2-2 | Delete dead code: V1 generators (959–1044, incl. a bare `except:`), unused `count`/`platform` params, triplicated `non_photo_categories` (770/848/915) → one module constant | | S |
| P2-3 | `search()` orders by `length_chars DESC` (248) — "longest = best", the heuristic behind the June diversity bug; `%`/`_` wildcards unescaped in LIKE (218–229) | Relevance ordering + `ESCAPE '\'` | S |
| P2-4 | Structure misclassification: 44.7% of `structure_type='JSON'` prompts fail `json.loads`; `{argument`-prefixed templates classified JSON | Check Template before JSON; require parse success for the JSON label | S |
| P2-5 | 4 rows `model=''` (claude-fable-5 slipped past the model regex); 6 orphan `prompt_techniques` rows; 265 curated prompts with no technique rows (can't distinguish "none" from "not enriched") | Whitelist + capture-unknown quarantine; FK cascade; coverage marker | S |
| P2-6 | No indexes on `prompts` (model/structure/has_prompt all full-scan LIKE); 52% of the file is freelist bloat (28.7 MB reclaimable by VACUUM) | Add indexes; VACUUM before next Release → halves the asset | S |
| P2-7 | Externalize the 5 intelligence dicts to `data/*.json` with thin accessors; import the ~16 `references/*.md` category-guide master prompts (e.g. portraits.md P1–P6) into a `curated_prompts` table so they enter retrieval | Converts prose knowledge into corpus; wording tweaks stop being code changes | M |
| P2-8 | Split `higgsfield_prompt.py` (1,160 lines, 5 responsibilities) into db/retrieval/generate/analytics/cli; one `cli.py` with argparse subcommands + `--json` | Only alongside P2-7 — splitting without moving data just relocates the mess | M |
| P2-9 | Tests + CI: `tests/conftest.py` builds a ~50-row fixture DB via `HIGGSFIELD_DB`; port `verify-generation-diversity.py` to pytest parameterized over goals; golden-set assertions + pairwise output-similarity ceiling (current verifier passes a 95%-boilerplate generator — it asserts the wrong invariant) | The pure functions are all testable as-is | M |
| P2-10 | Silent `ImportError` degradation (499–506): package-style import always fails → quietly worse prompts; try relative import fallback, warn loudly | | S |
| P2-11 | Scraper hardening (scripts/rsc-prompt-extractor.py): unvalidated URL → curl (`file://` read, flag injection, SSRF); `--start 0` breaks; prints but never writes to DB; extend language filter (Cyrillic/Thai/Hebrew/Devanagari); unify the two divergent `is_english` implementations | | M |

---

## P3 — Bigger investments

1. **Build/refresh pipeline (the Data verdict's top item):** committed `scripts/build-db.py`
   (schema + JSONL ingest + enrichment + FTS rebuild + checksums) and `scripts/refresh.py`
   (re-probe id range since the `prompt-id-map.json` watermark → scrape → idempotent
   upsert → diff summary). Until this exists the corpus is a frozen snapshot; SKILL.md's
   "re-scrape monthly" instruction cannot work — the production scraper
   (`~/.hermes/scripts/gpt-image2-rsc-scraper.py`) exists nowhere in the repo.
2. **Hybrid BM25 + embedding retrieval:** one local sentence-transformer, numpy cosine
   over 6.3k prompts, fused with FTS + category prior. Fixes the semantic gap (Arabic
   queries like `مشرقي` currently return 0 results silently; 'dashboard UI' ranks
   "Mr Bean Mini Cooper Chaos" #4). The one place ML cleanly beats rules.
3. **Versioned, evidenced model capability profiles:** replace static dicts with
   `profiles/gpt-image-2@2026-08.yaml` (evidence link + confidence + review date per
   claim), scheduled capability probes (text-length tolerance, count adherence), and
   corpus-drift alarms on the monthly scrape.
4. **Outcome feedback loop:** log (generated prompt, model, accepted/edited/regenerated),
   aggregate acceptance per injected spec, auto-demote failing dict entries.
5. **Category registry:** one `categories.json` generating `CATEGORY_NORMALIZE`, the
   photo/marketing maps, and docs tables — today adding a category takes six coordinated
   edits across both modules.
6. **Non-English bridge:** detect non-Latin goals → translate-then-retrieve with an
   explicit warning instead of silent degradation to category templates.

---

## Dev → distribution workflow (do this now)

Current state: edits happen in this clone, but the 5 agent installs (ZCode + 4 junctions)
read the separate copy at `~/.agents/skills/higgsfield-prompt-master`. Every improvement
requires a manual copy step; a missed step = agents silently running yesterday's code.

**Recommended (S):** invert the direction of truth —
1. Ensure this clone has the newest files (done — synced 2026-08-17),
2. Replace the hub *directory* with a junction pointing here:
   `cmd /c mklink /J C:\Users\alazi\.agents\skills\higgsfield-prompt-master <this clone>`
   (after moving the hub copy aside),
3. The 4 existing agent symlinks then resolve to this live tree automatically;
   commit = release to all agents. DB resolves module-relative → one shared copy.

**DB backup note (verified):** the DB *is* remotely backed up — GitHub Releases
v2.1.1 asset is byte-identical (SHA-256 match). Keep Releases as the channel (LFS not
worth it at 57 MB → ~28 MB after VACUUM). Missing: a `fetch-db.py` that pins the tag and
verifies the checksum.

---

## Suggested order of attack

1. **P0-3** commit un-pushed work → **P0-1/P0-2/P0-4** crash fixes (one sitting)
2. **P1-1** wire layers + slot-filling (the product-changing commit)
3. **P1-2/P1-3** corpus repair (has_prompt, categories, boilerplate purge) + re-enrich
4. Junction flip (distribution) + README/SKILL.md truth pass (**P1-5**)
5. **P1-4** scoring + **P2-9** tests, then the P3 pipeline work

# PRD: higgsfield-prompt-master v2 — Evidence-Based Rebuild

> Source of truth: `IMPROVEMENT_PLAN.md` (Rev 3) + `research/SOURCE_TRUTH.md`.
> Engine scope is LOCKED: **GPT Image 2** (`gpt-image-2`) and **Nano Banana Pro**
> (`gemini-3-pro-image`) only. Every model claim traces to `research/*.md`.

## Overview

The skill ships a strong 6,337-prompt corpus behind a generator that ignores it:
retrieval is discarded before output, 52% of `intelligence.py` is dead code, the dead
Layer 4/5 dicts contradict official vendor docs, and two advertised paths crash. This
PRD converts the improvement plan into 33 independently-completable stories: fix the
crashes, repair the corpus, rebuild both model dicts from verified primary sources,
make generation actually consume retrieval through an internal representation with two
prose renderers, replace the goal-blind scorer with a validated design, and harden the
data pipeline (reproducible build, refresh, tests, CI).

## Goals

- Zero crashes on any documented entry point (FTS quotes, demo.py, bad DB path)
- Retrieval demonstrably shapes generated output (goal-swap test fails if it doesn't)
- Both model dicts claim-by-claim sourced (URL + date + confidence per claim)
- Full 7,613-row corpus visible, cleaned (0 boilerplate), normalized, re-enriched
- Quality score discriminates by construction (percentile-calibrated, goal-conditioned)
- DB reproducible from committed scripts; live DB never mutated without explicit apply

## Quality Gates

These commands must pass for every user story (run from the repo root):

- `python -m py_compile <changed .py files>` — syntax check on every file the story touched
- `python -c "from higgsfield_prompt import HiggsfieldPromptMaster; HiggsfieldPromptMaster().stats()"` — module imports and DB loads
- `python scripts/verify-generation-diversity.py` — exits 0
- `python demo.py` — completes without traceback

DB-mutating stories additionally operate copy-safe: scripts default to a temp copy via
`HIGGSFIELD_DB` and require an explicit `--apply` flag to touch the live DB.

## User Stories

### Phase P0 — crashes & safety (US-001 … US-004)

### US-001: Fix demo.py (two crashes)
**Description:** As a developer, I want the documented demo to run on Windows so I can showcase the skill.
**Acceptance Criteria:**
- [ ] `sys.stdout.reconfigure(encoding='utf-8')` at entry (fixes cp1252 UnicodeEncodeError at demo.py:22)
- [ ] All three generation examples print `result['prompt'][:300]`, not dict slices (demo.py:70,79,89)
- [ ] Duplicate `from pathlib import Path` removed (lines 9,13)

### US-002: Fix FTS5 quote crash + fallback degradation
**Description:** As an agent, I want any search input to be safe so ordinary quotes never crash the skill.
**Acceptance Criteria:**
- [ ] Embedded `"` doubled when wrapping terms (higgsfield_prompt.py:265)
- [ ] Each `_do_search` strategy wrapped in try/except sqlite3.OperationalError, degrading to next fallback
- [ ] `fts_search('dashboard "glass')` returns results, no exception
- [ ] Regression check added (tests or scripts) covering quoted and empty-term inputs

### US-003: Safe DB open (no silent empty DB, read-only by default)
**Description:** As a user, I want bad DB paths to fail loudly and reads to not require write access.
**Acceptance Criteria:**
- [ ] `_resolve_db_path` raises FileNotFoundError listing candidate paths when nothing exists (higgsfield_prompt.py:133-173)
- [ ] Connections open with `file:...?mode=ro` URI unless enriching
- [ ] Enrichment DDL moved out of `__init__` into the enrich path
- [ ] `HIGGSFIELD_DB=/nonexistent python -c "...stats()"` raises FileNotFoundError, never creates a file

### US-004: Boilerplate purge script (copy-safe)
**Description:** As a data owner, I want share-widget garbage out of the curated corpus.
**Acceptance Criteria:**
- [ ] `scripts/purge_boilerplate.py` deletes rows matching `prompt_text LIKE 'Just found a great AI prompt%'` (291 rows, 253 curated) + dedupes 4 exact-dup pairs
- [ ] Defaults to a temp copy via HIGGSFIELD_DB; live DB touched only with `--apply`
- [ ] Prints before/after counts; ingestion-guard note added to SKILL.md maintenance section

### Phase P1 — the product (US-005 … US-016)

### US-005: Rebuild GPT_IMAGE_2 dict from SOURCE_TRUTH
**Description:** As the engine, I want GPT Image 2 guidance that matches OpenAI's official docs.
**Acceptance Criteria:**
- [ ] intelligence.py GPT_IMAGE_2 rebuilt per research/SOURCE_TRUTH.md §3
- [ ] Deleted: JSON-supremacy, negative_prompt block, REFERENCE_N syntax, word limits, lens incantations
- [ ] Added: paragraph-primary structure, ordinals+role references, quotes/CAPS/letter-spelling text levers, quality=high guidance, size heuristics + constraints table, common-mistakes list
- [ ] Every claim carries `_source` (URL), `_date`, `_confidence` fields

### US-006: Rebuild NANO_BANANA dict as NANO_BANANA_PRO
**Description:** As the engine, I want Nano Banana Pro guidance that matches Google's official docs.
**Acceptance Criteria:**
- [ ] Renamed/retargeted to `gemini-3-pro-image` per SOURCE_TRUTH §4
- [ ] Deleted: green-screen workflow, "100% accuracy" face-lock, flat "14 refs"
- [ ] Correct: 6 objects + 5 characters + 3 style refs; "completely unchanged" phrasing; up-to-5-character cap; semantic negative rewrites; 10 standard ratios (no 1:4/8:1); 1K/2K/4K; Pro-only interleaved text+image; NOT-Pro markers (thinking_level, video-to-image = 3.1 Flash)
- [ ] Every claim carries `_source`, `_date`, `_confidence`

### US-007: Two-model router
**Description:** As an agent, I want `_recommend_model()` to return the two real targets with routing signals.
**Acceptance Criteria:**
- [ ] Returns exactly `gpt_image_2` or `nano_banana_pro` (ids + display names correct)
- [ ] Routing signals per SOURCE_TRUTH §6: layout/UI/text-dense → gpt_image_2; reference compositing / ≤5-char consistency / localization / brand → nano_banana_pro
- [ ] "Higgsfield models" framing removed (aggregator note)

### US-008: Corpus repair A — status migration + category normalization (copy-safe)
**Description:** As the engine, I want all 7,613 rows visible with one canonical category format.
**Acceptance Criteria:**
- [ ] Migration: `has_prompt` → `status` (curated/harvested/excluded + excluded_reason); 1,276 text-bearing harvested rows become searchable
- [ ] Categories normalized to single pipe-separated canonical form (strip JSON-array wrappers from Aug rows)
- [ ] Copy-safe via HIGGSFIELD_DB default; `--apply` for live DB; before/after report printed

### US-009: Corpus repair B — re-enrich, FTS rebuild, VACUUM (copy-safe)
**Description:** As the engine, I want the repaired rows enriched and the DB compacted.
**Acceptance Criteria:**
- [ ] `enrich_all()` filter relaxed to cover rows with NULL structure_type/technique_tags regardless of old flags
- [ ] Full re-enrichment run; FTS rebuilt (`INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')`); VACUUM executed
- [ ] `stats()['total_prompts']` reflects 7,613 (or documented curated count) consistently
- [ ] Copy-safe default + `--apply`; DB size reduction reported

### US-010: Photo-intelligence truthfulness
**Description:** As an agent, I want camera specs to never leak into non-photo categories.
**Acceptance Criteria:**
- [ ] `get_photo_intelligence()` returns None for explicit non-photo categories (intelligence.py:253-271 sentinel semantics)
- [ ] `_build_from_intelligence` gets the missing non-photo guard (higgsfield_prompt.py:808-832)
- [ ] `result['intelligence']['photography']` reflects what was actually injected
- [ ] App/Web/Infographic/Abstract outputs contain no camera bodies/lenses

### US-011: Internal representation (IR) + slot extraction
**Description:** As the engine, I want a structured IR so structure comes from the corpus, not hardcoded prose.
**Acceptance Criteria:**
- [ ] IR structure (subject, action, environment, style, lighting, color, mood, composition, text_elements, negative_concepts, aspect_ratio, references, output_intent, quality_tier) defined
- [ ] Slot extractor parses retrieved exemplars (zone names, element counts, section headers, template arguments) into IR
- [ ] Unit-checkable: `extract_ir(json_prompt)` and `extract_ir(prose_prompt)` both populate fields

### US-012: Two prose renderers
**Description:** As the engine, I want per-model prose output honoring each vendor's documented style.
**Acceptance Criteria:**
- [ ] `render_gpt_image_2(IR)`: cohesive paragraph (labeled sections optional), front-loaded subject, 7 facets, inline "without X" exclusions, quotes/CAPS text levers, size heuristics
- [ ] `render_nano_banana_pro(IR)`: narrative scene description, camera language welcome, semantic positive rewrites for negatives, ordinal reference addressing
- [ ] Neither renderer emits booster tokens, REFERENCE_N, or word-limit folklore

### US-013: generate_prompt consumes retrieval (the product commit)
**Description:** As a user, I want generated prompts that demonstrably use the corpus.
**Acceptance Criteria:**
- [ ] Pipeline: retrieve exemplar → extract IR → fill slots from goal + corrected layers → render per routed model
- [ ] Template outputs carry 2-4 arguments (corpus average 2.7), zone schemas with element counts where the exemplar had them
- [ ] Goal platform keywords checked BEFORE category map (LinkedIn goal never emits Instagram safe-zones)
- [ ] Removing retrieval (stub returns []) changes the output (goal-swap sanity in story notes)
- [ ] `source_prompt_ids` reflects exemplars actually consumed

### US-014: PQS quality scorer
**Description:** As an agent, I want a score that discriminates and detects duplication.
**Acceptance Criteria:**
- [ ] `_quality_score` replaced per research/prompt-quality-evaluation.md §8: 6-factor weighted geometric mean (Coverage slots, Specificity via corpus IDF/SCS, Atomic density with anti-padding, Non-redundancy, Goal-fidelity @ 0.30) minus contradiction/vagueness penalty
- [ ] Grades are percentiles against corpus distribution (no hardcoded cutoffs); calibration run stored
- [ ] Adversarial checks: padding decreases score; goal-swap drops ≥25 points; "x" ≠ "analytics dashboard" scores
- [ ] Pure stdlib (gzip/zlib/math/re/sqlite3); no torch

### US-015: Regression gate v2
**Description:** As a maintainer, I want the verifier to catch the duplication class of bugs.
**Acceptance Criteria:**
- [ ] verify-generation-diversity.py extended: pairwise 5-gram Jaccard across different goals (FAIL ≥0.70), batch distinct-3, source-ID entropy
- [ ] Cross-goal discrimination Δ = mean G(pᵢ,gᵢ) − mean G(pᵢ,gⱼ≠ᵢ) computed; target Δ ≥ 0.30
- [ ] Goal-swap hard-fail: outputs ≥0.70 similar while goals <0.20 similar → exit 1
- [ ] Exit codes honored (0 pass / 1 fail) for CI use

### US-016: Docs truth pass
**Description:** As a new user, I want README/SKILL.md to match reality.
**Acceptance Criteria:**
- [ ] README rewritten to real API (HiggsfieldPromptMaster.generate_prompt), phantom HiggsfieldPromptGenerator + torch/transformers/requirements.txt fiction removed
- [ ] SKILL.md: FTS schema section matches reality (3 cols, unicode61, external content); stats table generated from `hpm.stats()`; ID-range fixed
- [ ] Version single-sourced; `__init__.py` fixed or removed (hyphenated-dir note)
- [ ] SKILL.md:421 mandate rewritten post-US-013 (generate_prompt now the strong path); ~/.hermes paths → repo-relative

### Phase P2 — structure & hygiene (US-017 … US-026)

### US-017: Dead code deletion
**Description:** As a maintainer, I want the codebase free of unreachable code.
**Acceptance Criteria:**
- [ ] V1 generators `_generate_json/_generate_template/_generate_flat` deleted (higgsfield_prompt.py:959-1044) incl. bare except
- [ ] Unused `count`/`platform` params removed or implemented
- [ ] `non_photo_categories` one module constant (was triplicated 770/848/915)
- [ ] Stop-word sets deduplicated (fts_search vs _extract_keywords drift, "this" twice)

### US-018: search() relevance + LIKE escaping
**Description:** As an agent, I want relevance ordering and correct wildcard handling.
**Acceptance Criteria:**
- [ ] `search()` no longer orders by `length_chars DESC` (line 248); relevance-ranked
- [ ] `%`/`_` escaped with `ESCAPE '\'` clause (lines 218-229); `search(query='%')` no longer matches everything

### US-019: Structure reclassification (copy-safe)
**Description:** As a data owner, I want `structure_type='JSON'` to mean parseable JSON.
**Acceptance Criteria:**
- [ ] Classifier checks Template (`{argument`) before JSON; JSON label requires `json.loads` success (hybrid bucket for template-JSON)
- [ ] Re-run on copy; report: ≤352 true-JSON (was 636), remainder Template/hybrid
- [ ] Copy-safe default + `--apply`

### US-020: Schema hygiene (copy-safe)
**Description:** As a data owner, I want indexes, integrity, and versioned migrations.
**Acceptance Criteria:**
- [ ] Indexes on (status/has_prompt, structure_type), (model); PRAGMA foreign_keys=ON; prompt_techniques FK with ON DELETE CASCADE
- [ ] 6 orphan technique rows cleaned; 4 `model=''` rows quarantined/fixed; enriched-coverage marker added
- [ ] `PRAGMA user_version` migrations invoked by explicit migrate command, not constructor
- [ ] Legacy columns (structure, techniques, inferred_category, complexity — 9/7613 populated) dropped

### US-021: Externalize intelligence data
**Description:** As a curator, I want model knowledge editable as data.
**Acceptance Criteria:**
- [ ] PHOTOGRAPHY, MARKETING, ART_DIRECTION, GPT_IMAGE_2, NANO_BANANA_PRO → data/*.json with same accessor signatures
- [ ] Loader validates `_source/_date/_confidence` present per top-level claim group
- [ ] Code no longer contains the dicts inline

### US-022: curated_prompts table from references/*.md
**Description:** As the engine, I want the category-guide master prompts inside retrieval.
**Acceptance Criteria:**
- [ ] Importer parses ~16 references/*.md master prompts (e.g. portraits.md P1-P6 with model/ratio metadata) into curated_prompts(source, category, model, ratio, text)
- [ ] Retrieval (fts/templates) includes curated rows; count reported
- [ ] Idempotent re-run

### US-023: Module split + CLI
**Description:** As a library user, I want coherent modules and a real CLI.
**Acceptance Criteria:**
- [ ] higgsfield_prompt.py split: db.py, retrieval.py, generate.py, analytics.py, cli.py (back-compat re-exports preserved for SKILL.md imports)
- [ ] argparse CLI: search / generate / guide / stats / random / enrich / verify subcommands; `--json` output; `generate` prints result['prompt']
- [ ] SKILL.md usage examples updated to CLI where beneficial

### US-024: pytest suite + CI
**Description:** As a maintainer, I want regression protection in CI.
**Acceptance Criteria:**
- [ ] tests/conftest.py builds ~50-row fixture DB via HIGGSFIELD_DB (correct external-content FTS)
- [ ] Unit tests: FTS sanitization, _extract_keywords, CATEGORY_NORMALIZE round-trips, structure detection, _recommend_model, scorer determinism, DB-path resolution
- [ ] verify-generation-diversity ported to parameterized pytest
- [ ] GitHub Actions workflow: pytest + diversity gate on push/PR

### US-025: Loud intelligence import
**Description:** As a developer, I want import failures visible, not silent degradation.
**Acceptance Criteria:**
- [ ] Import tries absolute then relative; on failure emits warning into result dict + stderr (higgsfield_prompt.py:499-506)
- [ ] Packaged import (via __init__) no longer silently drops layers

### US-026: Scraper hardening
**Description:** As a data engineer, I want the extractor safe and consistent.
**Acceptance Criteria:**
- [ ] URL scheme restricted to http(s) (no file://, no leading-dash flags) in scripts/rsc-prompt-extractor.py
- [ ] `--start 0` works (is not None guards); output as JSONL; bare excepts removed
- [ ] Language filter extended (Cyrillic/Thai/Hebrew/Devanagari); single shared is_english implementation

### Phase P3 — pipeline & growth (US-027 … US-033)

### US-027: Reproducible build script
**Description:** As a data owner, I want the DB rebuildable from committed code.
**Acceptance Criteria:**
- [ ] scripts/build-db.py: create schema → ingest JSONL → enrich → FTS rebuild → VACUUM → checksum report
- [ ] Rebuild from a scraped JSONL export produces a DB with matching stats (counts by category/model/structure)
- [ ] Documented in README (Releases remain the distribution channel)

### US-028: Release fetch + verify
**Description:** As an installer, I want the DB pinned and checksum-verified.
**Acceptance Criteria:**
- [ ] scripts/fetch-db.py downloads tagged release asset, verifies SHA-256 against committed checksums file, refuses mismatch
- [ ] Default tag pin; `--tag` override

### US-029: Refresh pipeline
**Description:** As a data owner, I want new prompts ingestible without heroics.
**Acceptance Criteria:**
- [ ] scripts/refresh.py: re-probe id range past prompt-id-map.json watermark → scrape new ids (JSONL) → idempotent upsert → FTS rebuild → diff summary (new/updated/excluded)
- [ ] scrape_log written; boilerplate + language + model guards applied at ingest
- [ ] Dry-run default; `--apply` to write

### US-030: Versioned capability profiles
**Description:** As a curator, I want model claims versioned, evidenced, review-dated.
**Acceptance Criteria:**
- [ ] profiles/gpt-image-2@<date>.yaml + profiles/nano-banana-pro@<date>.yaml (claims with evidence URL, confidence, review_after)
- [ ] data/*.json (US-021) generated from or validated against profiles
- [ ] Loader rejects claims missing evidence fields

### US-031: Outcome feedback logging
**Description:** As a curator, I want acceptance signal per injected spec.
**Acceptance Criteria:**
- [ ] generation_log table (timestamp, goal, model, prompt, source_ids, layers_injected, outcome: accepted/edited/regenerated)
- [ ] Analytics: per-layer acceptance rates surfaced via stats/CLI
- [ ] Opt-in; no PII

### US-032: Category registry
**Description:** As a maintainer, I want one place to define categories.
**Acceptance Criteria:**
- [ ] data/categories.json (canonical name, aliases, photo/marketing/model mappings, non-photo flag)
- [ ] CATEGORY_NORMALIZE + maps generated from it at load; six-edit problem gone
- [ ] Docs tables regenerate from registry

### US-033: Non-English goal bridge
**Description:** As an Arabic-speaking user, I want non-Latin goals handled, not silently degraded.
**Acceptance Criteria:**
- [ ] Non-Latin goal detection → explicit warning in result + translate-then-retrieve path (translation hook injectable, offline stub documented)
- [ ] `generate_prompt(goal='مشرقي', ...)` returns relevant results or a clear warning, never silent generic output

## Functional Requirements

- FR-1: The engine routes to exactly two models: gpt_image_2, nano_banana_pro
- FR-2: Every model claim in code/data carries source URL + date + confidence
- FR-3: All read paths open the DB read-only; mutation requires explicit apply
- FR-4: Retrieval output demonstrably affects generated text (goal-swap test enforces)
- FR-5: All 7,613 corpus rows searchable after repair; 0 boilerplate rows remain
- FR-6: Quality grades are corpus-percentile-calibrated and goal-conditioned
- FR-7: No crash on any documented entry point for any input
- FR-8: The DB is rebuildable via committed scripts from JSONL exports

## Non-Goals (Out of Scope)

- Any model beyond GPT Image 2 + Nano Banana Pro (adapters descoped by owner directive)
- Embedding/vector retrieval (P3-2 deferred — revisit post-US-013 with evidence)
- GUI/web interface
- Non-English corpus ingestion (English-only policy holds)
- Auto-pushing releases (human tags releases)

## Technical Considerations

- Pure-Python stdlib only (sqlite3, gzip, zlib, math, re); no torch — keep it that way (US-014, US-024)
- External-content FTS: every future insert path must maintain/rebuild the index (US-027, US-029)
- DB lives at references/gpt-image2-prompts-full.db, gitignored, Releases-distributed; HIGGSFIELD_DB overrides
- The live skill is a junction target for 5 agent installs — every merged commit ships instantly; keep main green
- Windows-first environment (Git Bash, cp1252 default stdout — US-001 pattern)

## Success Metrics

- verify-generation-diversity v2 (US-015) passes with Δ ≥ 0.30 and zero goal-swap failures
- Corpus: 7,613 searchable, 0 boilerplate, 100% enriched
- Every intelligence claim: source+date+confidence coverage = 100%
- CI green on push/PR

## Open Questions

- Exact GLM-5.3 max-thinking behavior on very long stories — watch first ralph iterations
- Whether `ar-EG` text rendering quality on NB Pro justifies an Arabic text-in-image recipe story later

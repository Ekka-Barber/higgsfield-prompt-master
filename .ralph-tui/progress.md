# Ralph Progress Log

This file tracks progress across iterations. Agents update this file
after each iteration and it's included in prompts for context.

## Codebase Patterns (Study These First)

* **Windows cp1252 fix**: any script printing emoji must call `sys.stdout.reconfigure(encoding='utf-8')` immediately after `import sys` — Windows default encoding crashes UnicodeEncodeError on 📊/✅/❌.
* **`HiggsfieldPromptMaster.generate_prompt()` returns a dict**, not a string — always use `result['prompt']`, `result['quality_score']['total']`, `result['length']`.
* Scripts must add repo root to `sys.path` (`sys.path.insert(0, str(Path(__file__).parent.parent))`) since `higgsfield_prompt` lives at repo root, not in a package.
* **Retrieval donors must be goal-relevant (FTS)** — merging category-template exemplars into generation leaks off-domain fragments into every same-category goal (the June 2026 "Y2K Scream" contamination class, corpus id 23501). Category templates are last-resort primary only, never donors.
* **Prove regression gates can fail** — seed `sys.modules["higgsfield_prompt"]` with a stub before `runpy.run_path(script, run_name="__main__")` to drive a verify script's failure path (catch SystemExit for the code); a gate that has never failed red is unverified.
* **Docs truth = query the source, never the old docs** — real schema via `SELECT sql FROM sqlite_master WHERE name='prompts_fts'` (no `tokenize=` option = default unicode61, NOT porter), real stats via `hpm.stats()` (searchable rows only, 6,337 denominator), real category counts via pipe-split Counter over `categories`.
* **SQLite positional `?` params follow SQL placeholder order, not loop order** — when WHERE and ORDER BY both reference per-term patterns, append ALL WHERE params first, then ALL rank params (two loops); one interleaved loop permutes patterns silently.
* **Re-run reports must scope to the baseline's population** — "was 636" counted only labeled rows; sweeping the 1,276 previously-NULL rows into the same re-run made true-JSON 353 and tripped a 352 AC cap. Scope migration UPDATE + report to the population the baseline measured.
* **PRAGMA foreign_keys is per-connection and defaults OFF** — a raw `sqlite3.connect` in a test harness silently skips FK enforcement/cascade; only `get_conn()` enables it. Any script asserting cascade must set the pragma on ITS OWN connection, and FK can't be toggled inside a transaction (table rebuilds: PRAGMA off → BEGIN → rebuild → COMMIT → PRAGMA on).
* **Copy-mode migration scripts always re-copy from live** — a second copy run "passing" proves nothing about step idempotency; prove version-gated skipping by calling the migrate function directly on the already-migrated copy.
* **Externalize-to-JSON migrations dump programmatically from the live module** — never hand-transcribe dicts (content parity + f-string provenance resolves to final strings); validate provenance PRESENCE in the loader, value truthfulness stays the curator's job.
* **`dict(X)` shallow copies share nested dicts** — intelligence model accessors (US-005 parity) protect only the top level; tests proving copy-protection must mutate top-level keys.
* **Numbered-guide discrimination** — `^## [A-Z]\d+:` + fenced code block cleanly separates the 13 category-guide master-prompt files (62 prompts) from analysis/report .md docs; per-prompt `**Model:** X · **Ratio:** Y` metadata (42 rows) falls back to file-level `Model: \`x\``. Import metadata VERBATIM (nano_banana_2/soul_cinematic are historical doc names, not current engine ids).
* **Small-table OR-search needs matched-term-count ranking** — with ~62 rows, OR'd term matching returns any single-term coincidence ("Professional illustration quality" in abstract.md for "professional headshot"); a per-term CASE rank (text hit=2, category hit=1, summed DESC) puts multi-term matches first.
* **conftest must set HIGGSFIELD_DB at module import, not inside a fixture** — test modules do top-level `from higgsfield_prompt import ...` at collection time, which runs db.py's import-time `DB_PATH = _resolve_db_path()`; a fixture-function env set is too late. Build the fixture DB first, then set env, then import db for enrichment helpers.
* **Fixture diversity goals need one dedicated FTS row each, embedding the goal phrase verbatim** — FTS MATCH is AND over `_extract_keywords` terms, so a row containing the full phrase is the only hit for that goal; filler rows must avoid goal-keyword combos (AND semantics tolerate single shared words like "poster").
* **`str.splitlines()` splits on \u2028/\u2029/\x85 too** — corpus text contains these; JSONL harnesses must iterate the file object (splits only on \r/\n), never `splitlines()` (`json.dumps` leaves \u2028 raw under `ensure_ascii=False`).
* **A raised assert before `conn.close()` leaks the connection** — Windows keeps the DB file locked (next `unlink()` = WinError 32); fetch everything, close, THEN assert.
* **Docs can describe scripts that don't exist yet, with invented details** — before implementing a "missing" script, grep the DB schema (`sqlite_master`) and existing tables for the real mechanism (US-029: SKILL.md promised a `scrape_log.jsonl` file; the DB already had a `scrape_log` table with a status vocabulary to reuse).
* **Corpus-wide writers must scope enrichment to touched rows** — `enrich_all()` sweeps every NULL-enrichment row (live DB has 1,276 deliberately unenriched); an ingest/refresh step enriches only the ids it wrote.

---

## 2026-08-17 - US-001
- Fixed two demo.py crashes: cp1252 UnicodeEncodeError on emoji prints; TypeError from slicing `generate_prompt()`'s dict return. Removed duplicate `from pathlib import Path`.
- Also added the same one-line `sys.stdout.reconfigure(encoding='utf-8')` to `scripts/verify-generation-diversity.py` — it crashed on ✅ before its `sys.exit(0)`, failing the "exits 0" AC.
- Files changed: `demo.py`, `scripts/verify-generation-diversity.py`
- **Learnings:**
  - `generate_prompt()` returns a dict with `prompt`, `quality_score` (dict with `total`/`grade`), `source_prompt_ids`, `length` keys (higgsfield_prompt.py:558)
  - Windows Python defaults to cp1252 stdout; any emoji-printing entry script needs the reconfigure line
  - The verify script calls `sys.exit(0)` only after printing ✅, so encoding crashes turn a passing run into exit 1
---

## 2026-08-17 - US-002
- Fixed FTS5 quote crash in `fts_search`: doubled embedded `"` per FTS5 escaping rules and wrapped the `_do_search` execute in try/except `sqlite3.OperationalError` returning `[]`, so all three strategies degrade to the next instead of raising. Added regression script `scripts/test_fts_quotes.py`.
- Files changed: `higgsfield_prompt.py` (`_do_search`), `scripts/test_fts_quotes.py` (new)
- **Learnings:**
  - FTS5 phrase escaping: literal `"` inside a quoted term is written doubled — `"glass` becomes `"""glass"`; wrapping raw terms raw makes any user quote an OperationalError (fts query syntax error).
  - One try/except inside `_do_search` covers all 3 call strategies — no need to duplicate handlers per strategy.
  - `fts_search` pre-filters terms (`len > 1`, stop words), so empty/stop-word-only queries already return `[]`; only quote-bearing tokens could crash.
## 2026-08-17 - US-003
- Made DB opening safe: `_resolve_db_path` now raises `FileNotFoundError` (listing every candidate path) instead of returning a nonexistent path; env-var override fails immediately if its target is missing (no silent fallback). `get_conn(readonly=True)` opens via `file:...?mode=ro` URI (default); `__init__` no longer runs enrichment DDL — `enrich_all()` reopens read-write (`mode=rw`) and runs `_ensure_enrichment_columns()` itself.
- Files changed: `higgsfield_prompt.py` (`_resolve_db_path`, `get_conn`, `__init__`, `enrich_all`)
- **Learnings:**
  - `Path.as_uri()` needs an absolute path — env-var DB paths must be `.resolve()`d before use or `as_uri()` raises ValueError.
  - SQLite URI `?mode=ro` on Windows works fine with `file:///C:/...` URIs from `as_uri()`; `mode=rw` (unlike default connect) never creates a missing file.
  - Readers query `prompt_techniques`/`structure_type` unconditionally, so the shipped DB must already be enriched — DDL-in-enrich-path assumes that (holds for the repo DB).
  - All 8 ACs verified: py_compile, import+stats (6337 prompts), HIGGSFIELD_DB=/nonexistent raises FileNotFoundError with no file created, verify-diversity exit 0, demo.py exit 0, enrich path reopens rw cleanly.
---

## 2026-08-17 - US-004
- Verified pre-existing `scripts/purge_boilerplate.py` meets all ACs (no code changes needed): copy-safe default (temp copy, live untouched, `--apply` for live), purges 291 boilerplate rows (253 curated: 6337→6080 minus 4 dups) + 4 exact-dup pairs, prints before/after counts. Ingestion-guard note already in SKILL.md maintenance section (SKILL.md:371).
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0.
- **Learnings:**
  - Curated-drop math: 6337−6080=257 = 253 curated boilerplate + 4 dup extras — matches AC numbers exactly.
  - Script imports `_resolve_db_path` from repo root (sys.path insert pattern), so it follows the live DB even if HIGGSFIELD_DB is set.
  - FTS cleanup: `INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')` after row deletes keeps full-text index consistent.
---

## 2026-08-17 - US-005
- Rebuilt `GPT_IMAGE_2` in intelligence.py from research/SOURCE_TRUTH.md §3 / research/gpt-image-2-official.md. Deleted: JSON-supremacy, negative_prompt_library, REFERENCE_N syntax, word limits, lens incantations, quality_modifiers, token_budget_guidance, per-category accessor mapping. Added: names/snapshots, paragraph-primary structures, quotes/CAPS/letter-spelling text levers, inline-exclusion rules, ordinal+role references (16 inputs, batch edits, blending, world knowledge), size heuristics + hard constraints (÷16, 1:3–3:1, 262,144–5,529,600 px, 512–3840, experimental >2560×1440, 32k char cap), params incl. quality=high and input_fidelity, ui_mockups, localization, official mistakes list, generic-camera guidance. Every one of the 11 sections carries `_source`/`_date`/`_confidence`. Accessor `get_gpt_image_2_intelligence` now returns a shallow copy of the dict (signature kept for parity).
- Files changed: `intelligence.py`
- Gates: provenance self-check OK (11 sections), py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0.
- **Learnings:**
  - `GPT_IMAGE_2` was never wired into `generate_prompt()` (higgsfield_prompt.py imports only photo/marketing accessors) — the dict could be reshaped freely without touching generation.
  - SOURCE_TRUTH §3 "1536x1536→1536x1024 banners/hero" is a typo; official table says 1536x1024 (1536x1536 isn't even a preset) — encoded 1536x1024.
  - Cookbook vs API-reference conflict on sizes (512–4096 vs 512–3840): API numbers win; noted in research file's Gaps section.
  - Provenance pattern: module-level `_GPT_I2_*` URL constants + `_source`/`_date`/`_confidence` keys per section — self-checkable via `all('_source' in v ...)` one-liner.
---

## 2026-08-17 - US-006
- Rebuilt `NANO_BANANA` as `NANO_BANANA_PRO` in intelligence.py from research/SOURCE_TRUTH.md §4 / research/nano-banana-official.md: retargeted to `gemini-3-pro-image` (GA 2026-05-28, `-preview` dead, 2.5/Lite/3.1-Flash ids forbidden). Deleted: green-screen workflow, "100% accuracy" face-lock, flat "14 refs" (deletion history kept in the layer header comment, NOT in dict values). Added 12 sections: names, prompting (narrative prose, both formulas, camera-language-encouraged), references (6 objects + 5 characters + 3 style refs, ordinal syntax), face_lock ("completely unchanged", up-to-five-character cap), editing (semantic-mask, conversational removal, First/Then/Finally, previous_interaction_id), semantic_negatives ("no signs of traffic" example), text (per-line fonts, text-first, Pro-only interleaved, ar-EG), ratios (10 Pro ratios, 1:4/8:1 marked Flash-only, 1K/2K/4K), pro_only_strengths, not_pro (thinking_level, video_to_image, image_search_grounding, 512px), cost, limits. Accessor renamed `get_nano_banana_pro_intelligence` returning a shallow copy (US-005 parity).
- Files changed: `intelligence.py`
- Gates: provenance self-check OK (12/12 sections), deleted-claims scan OK (no green screen/chroma/100% accuracy anywhere in dict), AC spot-checks OK, py_compile OK, import+stats exit 0, verify-generation-diversity exit 0, demo.py exit 0.
- **Learnings:**
  - `NANO_BANANA` was also never wired into `generate_prompt()` — same freedom as GPT_IMAGE_2; nothing else imported it, so the rename broke nothing.
  - Keep deletion notes in comments, not dict values: a `green_screen_deleted` note inside the dict made my own "no green screen in dict" assertion fail and would leak folklore into any renderer that dumps values.
  - Self-check substring scans catch self-inflicted hits: "chroma" matched my own "not chroma" contrast phrasing in semantic_mask — rewritten to plain official phrasing.
  - Google research file has no canonical blog URLs (only post titles) — cite `ai.google.dev/gemini-api/docs/*` + `deepmind.google/models/gemini-image/pro` as URLs and name blog posts by title rather than inventing URLs.
---

## 2026-08-17 - US-007
- Rebuilt `_recommend_model` per SOURCE_TRUTH §6: returns a dict (id/model_id/snapshot/display_name/signal) with exactly `gpt_image_2` (gpt-image-2, gpt-image-2-2026-04-21, "GPT Image 2") or `nano_banana_pro` (gemini-3-pro-image, "Nano Banana Pro"). Signals: layout/UI/text-dense keywords + App/Web, Infographic, Thumbnail, Poster categories → gpt_image_2; reference compositing, consistency, localization, brand, photo keywords + Profile/Portrait/E-commerce categories → nano_banana_pro. "Higgsfield model" framing removed (docstrings + SKILL.md:121, SKILL.md:269 now document the dict shape); aggregator note moved into the MODELS comment. Added `scripts/test_recommend_model.py`.
- Files changed: `higgsfield_prompt.py`, `SKILL.md`, `scripts/test_recommend_model.py` (new)
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, routing self-check OK.
- **Learnings:**
  - `model_recommendation` had no code consumers (only SKILL.md docs) — return type could change from str to dict freely.
  - `stats()` returns a dict and prints nothing; a silent `python -c` run is success, not a swallowed crash.
  - Old router had a duplicated "dashboard" keyword (copy-paste bug) — gone in the rewrite.
  - `nano_banana_2` id appears nowhere else in code; the rename is complete repo-wide (remaining grep hits are story text in .ralph-tui only).
---

## 2026-08-17 - US-008
- Added `scripts/migrate_status.py` (purge-script pattern: temp copy by default, `--apply` for live, idempotent): adds `status`+`excluded_reason` columns, maps has_prompt 1→curated (6,337) / 0→harvested (1,276, all text-bearing), strips JSON-array category wrappers (1,276 rows, all single-cat) to canonical pipe form via `normalize_category`, prints before/after report (searchable 6,337→7,613). `has_prompt` column kept (enrich_all/purge script still depend on it). Engine made dual-schema: `__init__` detects `status` column → `self._searchable = "status IN ('curated','harvested')"`, else legacy `"has_prompt = 1"`; all 15 read-path query sites (search/fts/category_guide/_get_category_prompts/_quality_score/stats/compare_models) use it. enrich_all left on has_prompt (US-009 relaxes it).
- Files changed: `higgsfield_prompt.py`, `scripts/migrate_status.py` (new)
- Gates: py_compile OK, import+stats OK (live 6,337), verify-diversity exit 0, demo.py exit 0, fts/router regression scripts OK; migrated copy: stats=7,613, harvested row searchable, category_guide includes harvested (Profile / Avatar 840).
- **Learnings:**
  - 'excluded' status is reserved for future purge-driven exclusions (excluded_reason: boilerplate/exact_duplicate); populating it now would break the "1,276 harvested searchable" AC since 38 of the 291 boilerplate rows are has_prompt=0.
  - Embedding `{self._searchable}` into an existing non-f triple-quoted SQL string silently breaks at runtime, not compile — exercised every touched method on both schemas to catch the 5 missed f-prefixes (Select-String context checks missed nested ones).
  - Harvested rows have NULL length_chars until re-enriched (US-009), so `ORDER BY length_chars DESC` sinks them below any small LIMIT — search visibility tests need limit≥total or a title-term query.
  - DB_PATH resolves at import time; switching HIGGSFIELD_DB mid-process requires `importlib.reload(higgsfield_prompt)` (or a fresh subprocess).
---

## 2026-08-17 - US-009
- Relaxed `enrich_all()` filter (higgsfield_prompt.py:192): dropped `has_prompt=1 AND` — now enriches any row with NULL structure_type/technique_tags. Added `scripts/rebuild_corpus.py` (purge-script pattern): temp copy by default / `--apply` for live, points HIGGSFIELD_DB at the target + `importlib.reload(hp)` (DB_PATH is import-time), runs enrich_all → `INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')` → VACUUM, prints before/after stats + size, asserts 0 unenriched rows remain. Verified run on copy: 1,276 harvested rows enriched (7,613/7,613 total, all got length_chars), FTS rebuilt, DB 57,782,272 → 28,319,744 bytes (51.0% reduction — FTS rebuild + first-ever VACUUM after US-004 deletes); live DB untouched (still 1,276 unenriched).
- Files changed: `higgsfield_prompt.py` (enrich_all one-line filter), `scripts/rebuild_corpus.py` (new)
- Gates: py_compile OK, import+stats OK (live 6,337), verify-generation-diversity exit 0, demo.py exit 0, copy fully enriched.
- **Learnings:**
  - `global x` must be declared BEFORE first use in the function body, else SyntaxError even if assignment comes later — put it at the top of main() when rebinding a module-level import.
  - Python sqlite3's implicit transactions only open before DML statements, so `conn.execute("VACUUM")` runs fine right after a commit — no autocommit dance needed.
  - The 51% size drop comes mostly from the FTS rebuild compacting the external-content index + VACUUM reclaiming US-004's never-vacuumed deleted pages, not from enrichment itself.
  - total_prompts stays 6,337 on the unmigrated live schema (searchable gate = has_prompt) while all 7,613 rows are enriched — the consistency AC is about the printed report matching actual row counts, not forcing schema migration.
---

## 2026-08-17 - US-010
- Verified US-010 was already fully implemented (sentinel landed in a prior story, never logged): `get_photo_intelligence` returns None for all 6 explicit non-photo categories before goal inference (intelligence.py:258-260); all 4 generator sites guarded (higgsfield_prompt.py:815/860/895/962); `intelligence.photography` = `photo is not None` (line 585). Added `scripts/test_photo_truthfulness.py` regression check: sweeps 6 non-photo categories x 4 structures for camera tokens (Phase One/Canon/Sony/Shot on/Camera:) + asserts photography flag False, and asserts photo categories still keep camera specs.
- Files changed: `scripts/test_photo_truthfulness.py` (new)
- Gates: photo-truthfulness script OK, py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0.
- **Learnings:**
  - IMPROVEMENT_PLAN.md P2-1 was stale relative to code — always run the AC check before implementing; the sentinel + guards already existed.
  - Goal-keyword inference (e.g. "food" in goal) can no longer smuggle cameras into App/Web for a restaurant app — the mapped-category check short-circuits before goal inference.
  - The per-generator `non_photo_categories` lists (858, 895, 962) are now redundant belt-and-suspenders since photo=None for those categories — left in place, harmless.
---

## 2026-08-17 - US-012
- Added `renderers.py` (new module; US-013 does the generate_prompt wiring): `render_gpt_image_2(ir)` — cohesive paragraph, front-loaded subject sentence, 7 facets (subject/action lead; environment+composition; style+lighting+color; mood+text levers), inline "without any X" exclusions (leading articles stripped from neg fragments to avoid "any any"), double-quote/ALL-CAPS text levers (plain text_elements get wrapped in quotes), size heuristics (numeric w:h or word-forms → 1024x1024 social / 1024x1536 posters+stories / 1536x1024 banners+hero; ratios outside 1:3–3:1 emit nothing). `render_nano_banana_pro(ir)` — narrative opener "The scene centers on …", official t2i formula order, camera fragments woven into composition (pass-through welcome), semantic positive rewrites (small official-example dict + "no signs of X" fallback, matching Google's own 'no signs of traffic' phrasing), ordinal+role reference addressing ("Use the second image…"), Pro-ratio allowlist gate on the "Presented in a N:N frame" tail (1:4/8:1 never emitted). Shared `_clean`: zone-prefix strip via ir._match_slot (only alias-named prefixes), `{argument name=... default=X}` unwrap → default, REFERENCE_N → "the Nth image" ordinal rewrite, booster scrub. Internal asserts guarantee no booster/REFERENCE_N/word-limit output. Added `scripts/test_renderers.py`: synthetic IR exercising every AC lever + degenerate inputs (empty IR, bad ratios) + full 6,337-exemplar corpus sweep × both renderers with leak scan.
- Files changed: `renderers.py` (new), `scripts/test_renderers.py` (new)
- Gates: test_renderers OK (6337×2 swept, 0 leaks), py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, all prior regression scripts (fts/recommend_model/photo_truthfulness/extract_ir) OK.
- **Learnings:**
  - Booster self-hit again (US-006 repeat): my positive-rewrite dict value "tack-sharp focus" matched the booster regex `\bsharp focus\b` (hyphen = word boundary) — leaked on 17 corpus rows until the sweep caught it. Phrasing values must be scanned against the ban regex, not just corpus fragments.
  - Fragment-level scrubbing is insufficient as a guarantee — keep the per-render assert on the FINAL body; debug leaks with `python -O` (asserts disabled) so the renderer returns the body instead of crashing on its own invariant check.
  - _NEG_RE captures the article ("any human presence"), so renderers adding "without any" must strip leading any/an/the or you get "without any any human presence".
  - Corpus template syntax ({argument name=... default="female"}) survives into IR subject fragments — _clean unwraps the tag to its default value, a big readability win for US-013 slot-filling.
  - _paragraph capitalizes sentence starts, so tests asserting mid-sentence phrasings ("the second image") need case-insensitive matching.
  - Non-strict-JSON rows rendered through prose parsing embed JSON keys as quoted text_elements — tolerated as evidence pass-through; no AC violation.
---

## 2026-08-17 - US-011
- Added `ir.py` (new module, no existing files touched — US-013 does the wiring): `IR_FIELDS` tuple of the 14 canonical fields, `PromptIR` dataclass (11 list slots for evidence fragments + `aspect_ratio`/`output_intent`/`quality_tier` str slots, `add()` dedupe+cap, `filled()`, `to_dict()`), and `extract_ir(source)` accepting a Prompt row / raw text / JSON dict. Parses: JSON exemplars via `json.loads` with prose fallback (284/636 corpus JSON rows are non-strict), Template exemplars via `{argument name=...}` regex (handles backslash-escaped `\"` variants) + `Header:` section routing, prose via clause keyword buckets. Universal scan: element counts ("three-tier", "exactly 8 numbered badges"), negatives ("without X"), references ("inspired by X"), quoted/CAPS text elements (skipped on JSON — quotes are syntax), aspect ratios, output_intent, quality_tier. Zone/section/key names kept in fragments (`"Header: content"`) so zone-name evidence survives alias routing. Added `scripts/test_extract_ir.py`: IR_FIELDS exact-match, 3 synthetic fixtures, full 6,337-exemplar sweep (zero exceptions, all non-empty), per-structure real-exemplar spot checks, garbage tolerance.
- Files changed: `ir.py` (new), `scripts/test_extract_ir.py` (new)
- Gates: test_extract_ir OK (6337 swept), py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0.
- **Learnings:**
  - `_LIST_SLOTS = IR_FIELDS[:11]` was an off-by-one landmine: `references` is index 11 and `aspect_ratio` (a str) got treated as a list — derive list slots by excluding the 3 str fields instead of slicing.
  - 284/636 "JSON" corpus rows fail strict `json.loads` (trailing commas / escaped-quote garbage) — extract_ir MUST fall back to the prose parser; some rows also store args as `{argument name=\"x\" default=\"y\"}` with literal backslashes, so the arg regex accepts `\\?` before quotes.
  - Keeping zone names inside routed fragments (`"Canvas: 4:5 aspect ratio..."`) preserves the "zone names into IR" evidence while still slot-routing content — provenance lives in the fragment.
  - Corpus structure mix (curated): Template 4,846 / Other 606 / JSON 636 / Flat prose 249 — "Other" rows flow through the same prose parser fine.
---

## 2026-08-17 - US-013
- Rewired `generate_prompt` (higgsfield_prompt.py) to the product pipeline: retrieve goal-relevant FTS exemplars → `extract_ir` (primary + top-3 donor merge) → fill slots from goal (subject lead, style, mood, aspect ratio) + corrected layers (photo fragments only when photo is not None; camera-bearing corpus fragments dropped for non-photo categories via renderers._CAMERA_RE) → render per routed model (`render_gpt_image_2` / `render_nano_banana_pro` by `_recommend_model`). `structure` now only biases exemplar selection (Template prefers 2-4 {argument} exemplars, corpus avg 2.7), not output format. Deleted 387 lines of dead generators (v1+v2 `_generate_*`, `_synthesize_template`, `_build_from_intelligence`, `_extract_sections`). `intelligence.get_marketing_intelligence` reordered: goal platform keywords (`_goal_platform_key`) checked BEFORE the category map. Updated `test_photo_truthfulness.py` camera-substance assertion (label "Camera:" no longer exists in prose rendering). Added `scripts/test_generation_pipeline.py`.
- Files changed: `higgsfield_prompt.py`, `intelligence.py`, `scripts/test_photo_truthfulness.py`, `scripts/test_generation_pipeline.py` (new)
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, all prior regression scripts (fts/recommend_model/photo_truthfulness/extract_ir/renderers) + new pipeline script OK.
- **Learnings:**
  - Donor-merging category templates into the IR re-triggered the June 2026 contamination class (the "Y2K Futurist Scream" App/Web template, id 23501, leaked Munch/vaporwave into every same-category goal) — corpus evidence donors MUST be goal-relevant FTS hits; category templates are last-resort primary only (single exemplar).
  - `_quality_score` still gates on the old specificity word-list, so prose-rendered outputs score lower than the old boilerplate-stuffed ones (C/D grades on web goals) — acceptable; US-014 replaces the scorer.
  - `aspect_ratio` result now falls back to the exemplar's own ratio (ir.aspect_ratio) before "1:1"; linkedin_post's "1.91:1" matches neither renderer's ratio gate and renders no size/ratio tail (harmless — no AC on it).
  - Stable-sort key `not (2 <= argc <= 4)` preserves FTS relevance order within groups — boolean False sorts before True, in-range exemplars first without re-ranking.
  - US-010's photo test asserted the literal "Camera:" label; prose rendering carries camera substance (photo layer strings verbatim) instead — updated the test, semantics unchanged.
  - SKILL.md still names the deleted `_generate_*_v2` methods (lines ~446-456) — left for US-016 docs truth pass.
---

## 2026-08-17 - US-014
- Verified US-014 was already fully implemented but unlogged (US-010 pattern): `pqs.py` implements the §8.1 6-factor weighted geometric mean — Coverage 0.20 (typed slot schema, per-category REQUIRED masks, modified-noun-phrase fills), Specificity 0.20 (corpus AvIDF + SCS, QPP predictors; Brysbaert arm omitted → weights rescaled 4/7 + 3/7), Atomic density 0.20 (regex atom patterns; anti-padding = atoms/word vs corpus p25 rho), Non-redundancy 0.10 (distinct-3 0.6 + compression-ratio 0.4), Goal fidelity 0.30 (IDF-weighted goal-term recall) — times (1 − X), X capped 0.5 (MUTEX conflicts, AR dupes, vague fraction). Grades are percentiles vs the per-category corpus distribution in `pqs_calibration.json` (bisect, no hardcoded cutoffs); `scripts/calibrate_pqs.py` rebuilds it; `PQSScorer` falls back to an in-memory build when the file is missing. `higgsfield_prompt._quality_score` now takes `(prompt_text, category, goal)` and delegates to a lazily built `PQSScorer`.
- Adversarial checks (`scripts/test_pqs.py`): padding 88→61, goal-swap drop 39 (≥25), goal 'x'=22 vs 'analytics dashboard'=88. All gates green: py_compile, import+stats (6,337), verify-generation-diversity exit 0, demo.py exit 0, calibration n=6,337 matches live searchable count.
- Files: `pqs.py`, `scripts/test_pqs.py`, `scripts/calibrate_pqs.py`, `pqs_calibration.json`, `higgsfield_prompt.py` (`_quality_score`, lazy `self._pqs`) — no changes needed this iteration, verification only.
- **Learnings:**
  - `PQSScorer` caches calibration in module-global `_CACHED` — a second HiggsfieldPromptMaster in the same process reuses the first load; mid-process HIGGSFIELD_DB switches would need a pqs reload too (same class of import-time binding as US-008's DB_PATH).
  - Calibration's goal proxy is the row `title` (the only per-row goal-ish signal); generated prompts scored against a real user goal get genuinely comparable percentiles.
  - `_slot_subject` scores filled by ≥2 non-stop content words in the first 14 tokens — the one slot that doesn't need a modified head; all other slots reject bare head tokens (the §8.0 "mm matches commercial" substring disease is gone).
  - Geometric mean floors every factor at 0.01, so goal-swap collapse (G→0) alone drags an A+ to a C/D without NaN — exactly the duplication-bug detector the research demanded.
---

## 2026-08-17 - US-015
- Extended `scripts/verify-generation-diversity.py` with duplication-class gates: pairwise 5-gram Jaccard across all 15 cross-goal pairs (FAIL >=0.70, worst pair reported), goal-swap hard-fail (outputs >=0.70 while goals <0.20 -> error + exit 1), batch distinct-3 (reported: 0.944), source-ID Shannon entropy (reported: 4.000 bits/16 IDs), cross-goal discrimination delta = mean G(pi,gi) - mean G(pi,gj!=i) with G = goal content-word recall (FAIL <0.30). Baseline run: max pair Jaccard 0.000, delta 0.877, exit 0. Failure path proven via sys.modules stub + runpy (constant duplicate outputs -> 30 errors incl. DUPLICATION/GOAL-SWAP/DISCRIMINATION, exit 1).
- Files changed: `scripts/verify-generation-diversity.py` (helpers `_words`/`_ngrams`/`_jaccard`/`_goal_recall` + 5 checks; no library code touched)
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0 (and stubbed-fail exit 1), demo.py exit 0.
- **Learnings:**
  - The US-013 pipeline renders outputs so goal-specific that cross-goal 5-gram overlap is literally 0.000 — the 0.70 threshold has enormous headroom, exactly what a regression gate wants.
  - Discrimination delta with plain content-word recall: own-goal G=1.000 (subject lead echoes every goal word), cross-goal G=0.123 — no IDF weighting needed for the 0.30 target.
  - Pairwise Jaccard gate subsumes goal-swap, but AC lists both — implemented as one loop appending both error labels; ~0 extra code.
  - Entropy/distinct-3 have no AC thresholds → report-only (YAGNI); the pre-existing unique-set check stays as the retrieval-diversity gate.
---

## 2026-08-17 - US-016 to the real API (HiggsfieldPromptMaster, dict-returning generate_prompt, Prompt dataclass results, CLI, stdlib-only deps); removed phantom HiggsfieldPromptGenerator, torch/transformers/requirements.txt fiction, Hermes/NousResearch/Ekka-Barber repo fiction, Releases download table. SKILL.md: stats table regenerated from `hpm.stats()` (6,337 searchable of 7,613; 5,008/1,329 model split; avg 1,457 chars; ID range fixed to 13,440–28,686 — was "51–28,686"); FTS schema fixed to reality (3 cols prompt_text/title/model, external content, default unicode61 — was 5 cols + `tokenize='porter unicode61'` fiction); structure/technique/category tables regenerated from live queries; pipeline section + line-421 mandate rewritten post-US-013 (IR+renderers, PQS percentile grades); pitfalls de-fictionsized (_synthesize_template/_generate_*_v2 references replaced with current mechanisms, "Old V1 Generators" section deleted); all ~/.hermes command paths → repo-relative; maintenance section now lists the real copy-safe script set. Deleted `__init__.py` (dead: hyphenated repo dir is not an importable package; nothing imported it — module import via repo root on sys.path); version single-sourced in SKILL.md frontmatter (2.2.0) with hyphenated-dir note in README + SKILL.md Quick Start. higgsfield_prompt.py docstring 8,596→7,613.
- Files changed: `README.md` (rewrite), `SKILL.md`, `__init__.py` (deleted), `higgsfield_prompt.py` (docstring only)
- Gates: py_compile OK, import+stats OK (with __init__.py deleted — proves module import is unaffected), verify-generation-diversity exit 0, demo.py exit 0, README "~55 MB" claim verified (55.1 MB actual).
- **Learnings:**
  - Real FTS DDL via `SELECT sql FROM sqlite_master WHERE name='prompts_fts'` — no `tokenize=` option means default unicode61, NOT porter; docs had invented both the 5-column schema and the porter tokenizer.
  - stats() is searchable-rows-only (6,337 on legacy schema), so model/structure percentages must use 6,337 as denominator; category counts need a separate pipe-split Counter over the categories column (26 real categories, top = Social Media Post 1,978).
  - SKILL.md frontmatter YAML tolerates trailing comments — `version: 2.2.0  # single source of truth` works as the version single-sourcing note.
  - Deleting the root `__init__.py` is safe even though it imported `.higgsfield_prompt`: `import higgsfield_prompt` always resolved to the module (hyphenated dir can't be a package), so the file was provably dead.
  - references/*.md keep their historical ~/.hermes paths and 8,596 numbers deliberately — they are dated reports, and the AC scope is README + SKILL.md; rewriting history documents is not docs truth.
---

## 2026-08-17 - US-017
- Verified US-017 was already fully implemented but unlogged (US-010 pattern): V1 generators (old lines 959-1044) went out with US-013's 387-line deletion — file is now 798 lines, only `except sqlite3.OperationalError:` remains (no bare `except:` in any library module); `generate_prompt` signature carries no count/platform params; the triplicated `non_photo_categories` lists were deleted outright — the single source of truth is `CATEGORY_PHOTO_MAP` with explicit None values (intelligence.py:248-249) feeding the `get_photo_intelligence` sentinel; stop words deduplicated into one module-level `_STOP_WORDS` frozenset (higgsfield_prompt.py:110, 'this' listed once) shared by `fts_search` (line 317) and `_extract_keywords` (line 349, union with `_DOMAIN_STOP_WORDS` which only ever applied to goal-keyword extraction).
- Files changed: none this iteration (verification only — code landed in US-013/earlier).
- Gates: py_compile all 5 modules OK, import+stats OK, verify-generation-diversity exit 0 (delta 0.877), demo.py exit 0, test_photo_truthfulness OK.
- **Learnings:**
  - US-013's generator deletion quietly satisfied most of US-017 — always re-run AC checks before implementing cleanup stories; the IMPROVEMENT_PLAN.md line numbers (959-1044, 770/848/915) refer to the pre-US-013 file and are stale.
  - Deduplicating the stop words as `_STOP_WORDS | _DOMAIN_STOP_WORDS` preserved the original semantics: domain filler ("website", "arabic", "brand"...) was only ever stripped from goal-keyword extraction, never from raw FTS user queries — merging them into one set would have changed search behavior.
## 2026-08-17 - US-018
- Rewrote `search()` LIKE layer (higgsfield_prompt.py): new module-level `_like(term)` escapes `\` first, then `%`/`_`, every LIKE param (query terms, category, model) now carries `ESCAPE '\'`; relevance ordering replaces `ORDER BY length_chars DESC` — per-term `CASE` rank (title hit=3, description=2, body=1) summed DESC, tiebreak `id`; no-query searches order by `id`. Relaxed term filter `len(t) > 1` → `if t` so wildcard-only queries become escaped literal searches instead of being silently dropped (dropped = no WHERE = matches everything — the exact AC failure mode). Added `scripts/test_search_like.py`: `_like` escaping asserts, `%`/`_` queries return 197/640 literal hits vs 6,337 total, per-term OR hit validation, title-match outranks body-only assertion, not-length-ordering assertion.
- Files changed: `higgsfield_prompt.py` (search + _like), `scripts/test_search_like.py` (new)
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0 (search example now leads with title match 15648), all prior regression scripts OK, gate proven red-capable (old unescaped `%%%` pattern = 6,337/6,337 rows → assert fails).
- **Learnings:**
  - The old `len(t) > 1` filter made `search(query='%')` return everything via the no-filter path, not via LIKE — wildcard handling and term filtering interact; escaping alone wouldn't have fixed the AC example.
  - Positional `?` params must follow SQL placeholder order: WHERE patterns for ALL terms first, then ORDER BY rank patterns for all terms — two separate loops, not one interleaved loop (interleaving permutes params and silently mismatches patterns).
  - Multi-term queries are OR'd, so a regression assert like `"100% satisfaction" in blob` is wrong — each hit only needs ONE literal term; assert `any(term in blob)`.
  - Relevance rank uses the same escaped patterns duplicated as extra params (SQLite has no named-param reuse in f-strings); ~6 extra params per term, negligible.
  - `_get_category_prompts` (last-resort primary path) calls `search()` with no query → its ordering changed from length DESC to id; pipeline gates (diversity, generation, renderers) all still green.
---
## 2026-08-17 - US-019
- Reclassified structure_type so 'JSON' means parseable JSON: added `_parses_as_json` + reordered `STRUCTURE_TYPES` (higgsfield_prompt.py:74) — Template (`{argument`, json-fail) checked BEFORE JSON; JSON requires `startswith('{')` AND strict `json.loads`; new `Template-JSON` hybrid bucket for rows that parse AND carry `{argument` tags. Added `scripts/reclassify_structure.py` (purge-script pattern: temp copy default / `--apply` live; updates only rows that already carry a label — NULL rows stay enrich_all's job, which now uses the fixed classifier; asserts true-JSON <= 352). Copy run: 536/6,337 reclassified, JSON 636 -> {JSON 100, Template-JSON 252, Template +269, Other +15}, true-JSON = 352 exactly. Live DB untouched (still 636 JSON; run `python scripts/reclassify_structure.py --apply` to apply).
- Files changed: `higgsfield_prompt.py` (`_parses_as_json`, `STRUCTURE_TYPES`), `scripts/reclassify_structure.py` (new), `scripts/test_structure_classify.py` (new)
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, all prior regression scripts (fts/recommend_model/photo_truthfulness/extract_ir/renderers/generation_pipeline/search_like/pqs) OK, generation verified on the reclassified copy (score 75, donors retrieved), assert proven red (first sweep included NULL rows -> 353 > 352 -> AssertionError).
- **Learnings:**
  - 252/636 old-JSON rows strict-parse AND contain `{argument` (tags live inside escaped JSON string values) — that's the hybrid class; 269 fail json.loads (pure templates mislabeled), 15 fail with no tags (go to Other), only 100 are true JSON-only. 100+252=352 = the AC number exactly.
  - Sweeping previously-NULL rows into the re-run broke the AC cap (353) — the "was 636" baseline only covered labeled rows; scope migration reports to the baseline population (added to top patterns).
  - `shutil.get_tempdir()` doesn't exist — it's `tempfile.gettempdir()` (rebuild_corpus.py had it right).
  - `UPDATE ... WHERE id=? AND structure_type IS NOT ?` + `cur.rowcount` counts only actually-changed rows (SQLite `IS NOT` = null-safe value compare) — free changed-row counter.
  - SKILL.md:223 schema comment still lists "Template | JSON | Flat prose | Other" and structure tables show live-DB (unmigrated) numbers — left as-is; live counts stay correct until an `--apply` run, at which point docs need a refresh.
---

## 2026-08-17 - US-020
- Schema hygiene via `scripts/migrate_schema.py` (new): versioned `PRAGMA user_version` migrations (v1 status mapping, v2 orphan cleanup + model='' quarantine + db_meta enrichment-coverage marker, v3 prompt_techniques rebuild with `REFERENCES prompts(id) ON DELETE CASCADE`, v4 DROP COLUMN of structure/techniques/inferred_category/complexity, v5 indexes on (status, structure_type) and (model)); copy-safe temp-copy default / `--apply` live / `--status` read-only report; per-step BEGIN/COMMIT with user_version bump inside the txn; post-migration verify asserts (user_version, foreign_key_check empty, 0 orphans, 0 searchable model='', no legacy cols, both indexes, CASCADE in DDL, marker present). Library: `get_conn()` now runs `PRAGMA foreign_keys = ON` per connection; `_ensure_enrichment_columns` CREATE TABLE carries the FK cascade so fresh DBs can't recreate the orphan-prone table. Copy run: orphans=6, quarantined=4 (claude-fable-5 SVG rows, excluded_reason='missing_model'), marker 6337/7613, statuses curated 6,337 / harvested 1,272 / excluded 4 (searchable 7,609). Live DB untouched (user_version=0, legacy cols present).
- Files changed: `higgsfield_prompt.py` (get_conn pragma, FK in CREATE TABLE), `scripts/migrate_schema.py` (new)
- Gates: py_compile OK, import+stats OK (live 6,337), verify-generation-diversity exit 0 on live AND on migrated copy (delta 0.882), demo.py exit 0, search_like + fts_quotes regressions OK; proven on migrated copy: step-skip idempotency (direct call → "already at version 5"), CASCADE (DELETE prompt → technique rows gone, rolled back), FK enforcement (bogus prompt_id insert → IntegrityError), stats 7,609 with clean model split, generate score 80, writer path (INSERT into prompt_techniques with FK ON, rolled back).
- **Learnings:**
  - `PRAGMA foreign_keys` is per-connection, defaults OFF — my first cascade test failed because the raw `sqlite3.connect` in the test harness didn't set it; the pragma also can't be toggled inside a transaction, so the v3 table rebuild sequences PRAGMA off → BEGIN → rebuild → COMMIT → PRAGMA on (added to top patterns).
  - SQLite 3.51 `ALTER TABLE DROP COLUMN` coexists fine with the external-content FTS table as long as the dropped columns aren't FTS content columns (prompt_text/title/model untouched).
  - Copy-mode scripts re-copy from live every run, so back-to-back copy runs prove determinism, not idempotency — version-gate skipping needs a direct call on the already-migrated copy.
  - Quarantining the 4 model='' rows moves searchable from 7,613 → 7,609 on migrated DBs; `SELECT *` + `Prompt.from_row` named-key access is unaffected by dropped columns since from_row never read the legacy four.
## 2026-08-17 - US-021
- Externalized all intelligence data to `data/*.json`: photography.json / marketing.json / art_direction.json (each claim group stamped with honest provenance stub — "original curated layer, no external doc", confidence medium), gpt_image_2.json / nano_banana_pro.json (provenance already per-section from US-005/006; f-string URL constants resolved to final strings), category_maps.json (CATEGORY_PHOTO_MAP + CATEGORY_MARKETING_MAP — routing config, loaded with provenance=False). intelligence.py rewritten as loader: `_validate(data, filename)` requires _source/_date/_confidence on every top-level claim group (raises ValueError listing every miss), `_load(filename, provenance=True)`; all accessor functions verbatim (signatures unchanged). Added `scripts/test_intelligence_data.py` (42 claim groups provenance-checked, accessor parity incl. JSON-null sentinel, tampered-dict failure path, `= {` absent from intelligence.py source). README file tree + SKILL.md:137/420 updated to point at data/*.json ("Edit the JSON, not the module").
- Files changed: `intelligence.py` (rewrite), `data/*.json` (6 new), `scripts/test_intelligence_data.py` (new), `README.md`, `SKILL.md`
- Gates: py_compile OK, import+stats OK, test_intelligence_data OK, verify-generation-diversity exit 0, demo.py exit 0, all prior regressions (photo_truthfulness/generation_pipeline/renderers/recommend_model/extract_ir) OK.
- **Learnings:**
  - "No dicts remain inline" read literally — the AC names five dicts but a `= {` grep also hits CATEGORY_PHOTO_MAP/CATEGORY_MARKETING_MAP; moved them too (US-022's categories.json can evolve from category_maps.json).
  - Model accessors return SHALLOW copies (`dict(GPT_IMAGE_2)`) — nested section dicts are shared by design (US-005 parity); tests proving copy-protection must mutate top-level keys, not nested ones.
  - Externalize migrations: dump programmatically from the live module (temp script importing intelligence), never hand-transcribe — guarantees content parity and resolves f-string provenance (`f"{_A} + {_B}"`) to final URLs for free.
  - Curated layers (photography/marketing/art_direction) never had provenance — record the absence honestly ("no external doc", date "unknown") instead of inventing sources; the validator checks PRESENCE of keys, truthfulness of values stays the curator's job.
  - `except ValueError as e:` deletes `e` at block exit — capture `msg = str(e)` inside the block or the success print NameErrors after proving the failure path.
---

## 2026-08-17 - US-022
- Added `scripts/import_curated.py` (purge-script pattern: temp copy default / `--apply` live / idempotent): parses the 13 numbered-guide references/*.md files (62 master prompts — PRD said "~16", the `## X1:` + fenced-block pattern found 13 files/62 prompts; portraits.md P1-P6, infographics I1-I6, etc.) into `curated_prompts(source, category, model, ratio, text)`. Per-prompt `**Model:** · **Ratio:**` metadata (42/62 rows incl. "same as original" verbatim and I6's `· **Resolution:** 2K` tail stripped), file-level `Model:` fallback for the rest (ratio NULL), category = H1 guide name before the model suffix, source = "file.md#P1". Engine: `_has_curated` table detection in `__init__`, new `search_curated(query, category, limit)` returning Prompt objects with negative synthetic ids (-rowid) + matched-term-count relevance rank, `generate_prompt` last-resort now tries curated (goal-keyword-gated) BEFORE stale corpus category templates, `stats()` reports `curated_prompts` count (0 when table absent). Importer verifies: count reported, direct-call idempotency (62==62==parsed), stats parity, search_curated hits, and stubs `fts_search=[]` to prove the generation fallback consumes a curated row (negative source_prompt_ids).
- Files changed: `higgsfield_prompt.py`, `scripts/import_curated.py` (new)
- Gates: py_compile OK, import+stats OK (live 6,337 / curated 0 — table guarded), verify-generation-diversity exit 0 on live AND on the imported copy, demo.py exit 0, all 8 prior regression scripts exit 0, live DB untouched (no curated_prompts table).
- **Learnings:**
  - Curated master prompts are the category-template class — retrieval includes them as last-resort primary (keyword-gated), never as generation donors (June 2026 contamination lesson applies to them too).
  - Curated fallback fires only when FTS returns nothing, so all 15 diversity goals' outputs are byte-identical on the imported copy — gates green with zero generation drift.
  - Synthetic negative ids (-rowid) make curated provenance visible in `source_prompt_ids` without touching the corpus id space; the stub-fts test drives the otherwise-unreachable fallback deterministically.
  - PRD "~16" was a file-count estimate; honest parse = 13 files / 62 prompts, reported as parsed (count AC is "reported", not a magic number).
---


## 2026-08-17 - US-023
- Verified US-023 was already fully implemented but unlogged (US-010/US-014/US-017 pattern): higgsfield_prompt.py is now a 51-line back-compat facade re-assembling `HiggsfieldPromptMaster(DbMixin, RetrievalMixin, GenerationMixin, AnalyticsMixin)` and re-exporting every public name (DB_PATH, Prompt, _resolve_db_path, normalize_category, detect_structure/techniques, _like, MODELS, plus the 5 convenience functions demo.py/SKILL.md import). Implementation lives in db.py (243 lines: path resolution, connections, Prompt, detection constants, enrichment), retrieval.py (304: LIKE+FTS+curated search, keywords, templates, random), generate.py (196: pipeline, routing, PQS), analytics.py (150: guides, patterns, stats, compare), cli.py (124: argparse).
- All ACs verified, no code changes needed this iteration:
  - py_compile OK on all 6 .py files
  - `from higgsfield_prompt import HiggsfieldPromptMaster; HiggsfieldPromptMaster().stats()` OK from repo root (6,337)
  - scripts/verify-generation-diversity.py exit 0
  - demo.py exit 0 (exercises search_prompts/get_templates/analyze_patterns/generate_prompt/random_prompt via the facade)
  - CLI: all 7 subcommands green - search (relevance-ranked), generate (text mode prints result['prompt'], --json prints full dict), guide, stats, random (returns 1 with "No matching prompt found." on empty filters), enrich (proven on temp copy via HIGGSFIELD_DB: 1,276 rows enriched, live DB untouched), verify (exit 0); --json accepted both before and after the subcommand
  - All 10 prior regression scripts exit 0 through the facade (test_search_like/test_structure_classify prove the _like/detect_structure re-exports)
- Files changed: none this iteration (verification only - split landed in a prior unlogged session)
- **Learnings:**
  - argparse `--json` in both positions: give the shared flag-parser `default=argparse.SUPPRESS` and parent it into each subparser - a plain `default=False` on the subparser would clobber a main-parser `--json` set before the subcommand.
  - "random" with a filter needs a REAL category ("Logo" is not a corpus category; "Poster / Flyer" works) - empty-result CLI paths deserve a smoke test too, they returned exit 1 cleanly.
  - Mixin-split facade keeps `import higgsfield_prompt as hp` scripts working only if the facade re-exports what they touch attribute-style (DB_PATH, _resolve_db_path were the risky ones - both re-exported).
  - `enrich` CLI writes to the DB - smoke-test it against HIGGSFIELD_DB pointing at a temp copy, never live (same discipline as the migration scripts).

### US-023 re-verification (2026-08-17, second pass)
- Stop-condition check: work already complete, re-ran every AC gate fresh. py_compile 6/6 OK; facade import + stats (6,337) OK; verify-generation-diversity exit 0 (delta 0.877); demo.py exit 0; CLI search/generate/guide/stats/random/verify all exit 0; --json proven BOTH before and after the subcommand; enrich exit 0 on a temp-copy DB (1,276 rows, live DB untouched, copy deleted).
- Files changed: none.
- **Learnings:**
  - Live DB lives at `references/gpt-image2-prompts-full.db` (57,782,272 B) — `prompts.db` does not exist; temp-copy smoke tests must copy the real path.
  - PowerShell `Select-Object -First N` force-terminates a native pipeline early and `$LASTEXITCODE` stays unset (prints empty) — redirect to `$null` instead when only the exit code matters.
  - `--%` stop-parsing mangles quoted args (kept a literal trailing quote -> argparse "unrecognized arguments"); plain quoted args work fine.

## 2026-08-17 - US-024
- Added pytest suite + CI. `tests/conftest.py` builds a 50-row fixture DB (6 goal-matched rows embedding each diversity goal phrase verbatim + 44 fillers cycling 18 real categories x 5 structure archetypes incl. one Template-JSON hybrid) with the live legacy schema: external-content FTS5 (prompt_text/title/model, content_rowid='id') + `INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')`, enrichment via db.py's own detect_structure/detect_techniques. Sets HIGGSFIELD_DB at module import (before any higgsfield_prompt import). `tests/test_units.py` (22 tests): FTS quote sanitization/stopword-empty/external-content parity (fts count == prompts count == 50), _extract_keywords domain-stop stripping + design-term priority + stop-only→"", CATEGORY_NORMALIZE parametrized round-trips (raw→canonical, idempotent, lower→canonical), detect_structure all 5 buckets, _recommend_model parametrized routing + MODELS identity + shape, generate/score determinism, _resolve_db_path env-missing→FileNotFoundError / env-existing→resolved. `tests/test_generation_diversity.py` (26 tests): full port of the verify script — per-goal parameterized shape/contamination/photo-specs + batch unique-source-sets (>=50%), source-ID entropy >0, pairwise 5-gram Jaccard <0.70 + goal-swap, discrimination delta >=0.30. `pytest.ini` (pythonpath=., testpaths=tests). `.github/workflows/ci.yml`: py_compile all 10 modules → pytest → diversity gate + demo smoke on live corpus, conditioned on `hashFiles('references/gpt-image2-prompts-full.db') != ''` (DB is gitignored so fresh CI checkouts run the fixture-backed pytest; the script gates run wherever the 55 MB DB exists).
- Files changed: `tests/conftest.py`, `tests/test_units.py`, `tests/test_generation_diversity.py`, `pytest.ini`, `.github/workflows/ci.yml` (all new)
- Gates: pytest 66 passed / 4 skipped (expected non-App/Web skip branches) in 0.12s; py_compile OK; import+stats OK; verify-generation-diversity exit 0; demo.py exit 0; RED-PROOF: collapsing CASES to one duplicated goal made test_unique_source_id_sets + test_pairwise_jaccard fail (exit 1), file restored (git diff clean).
- **Learnings:**
  - conftest env-set must be at module import, not fixture scope — collection-time top-level imports in test modules trigger db.py's import-time DB_PATH resolution before any fixture runs.
  - FTS AND semantics make fixture-goal isolation nearly free: one row per goal embedding the phrase verbatim is that goal's only hit; uniqueness/jaccard/delta gates all pass deterministically on 50 rows.
  - PQS percentile grading works fine on the fixture (calibration file is repo-rooted via `Path(__file__).parent` and loaded once per process; scorer takes the fixture conn for corpus stats) — scores deterministic, no min-corpus threshold.
## 2026-08-17 - US-025
- Loud intelligence import (the IMPROVEMENT_PLAN P2-10 site, pre-split higgsfield_prompt.py:499-506 = now generate.py's function-level imports): every sibling import across the 6 mixin/facade modules is now absolute-first then package-relative (higgsfield_prompt, db in generate/retrieval/analytics, ir in renderers, ir/renderers/pqs in generate, cli + higgsfield_prompt in cli/facade __main__). The intelligence import in `generate_prompt` soft-degrades LOUDLY: on both-path failure it stubs the accessors (None / empty-mood lambda), appends a message to a new always-present `result['warnings']` list, and prints `WARNING: ...` to stderr — generation still returns a dict instead of silently dropping photo/marketing/mood layers. ir/renderers/pqs/db stay hard deps (dual-mode import, crash loudly if truly missing). Added `scripts/test_packaged_import.py`: builds a temp package (10 .py + data/ + pqs_calibration.json + `__init__.py` with `from .higgsfield_prompt import ...`), runs subprocesses with cwd OUTSIDE the repo (absolute imports can't accidentally succeed), HIGGSFIELD_DB → live DB. Proves: packaged import keeps layers (photography=True, warnings=[]) AND intelligence.py-deleted package returns a dict with WARNING on stderr + non-empty result['warnings'] + still-rendered prompt.
- Files changed: `generate.py`, `higgsfield_prompt.py`, `retrieval.py`, `analytics.py`, `renderers.py`, `cli.py`, `scripts/test_packaged_import.py` (new)
- Gates: py_compile 11 files OK, facade import+stats OK, verify-generation-diversity exit 0 (delta 0.877), demo.py exit 0, pytest 66 passed / 4 skipped, all 10 prior regression scripts exit 0, packaged-import script both paths OK.
- **Learnings:**
  - A shared `import_sibling()` helper can't bootstrap itself: every module's FIRST sibling import still needs an inline try/except, so uniform inline dual-mode try/except at all sites is the minimal uniform pattern.
  - `python -c` puts cwd on sys.path — packaged-import tests must run subprocesses with cwd = the dir CONTAINING the package (not inside it, not the repo), or absolute imports succeed by accident and the relative path is never exercised.
  - The degrade stub needs `infer_mood = lambda style, goal: ""` (empty mood is skipped downstream) and None-guards at the photo/marketing call sites — the US-010 sentinel path already handles photo=None, so degraded generation flows through the camera-scrub branch cleanly.
  - Pre-split line refs in ACs (499-506) map to the mixin files post-US-023 — locate the semantic site (the guarded intelligence import) before assuming it still exists verbatim; here it had become a plain unguarded absolute import (silently "loud" only by crashing).
---


## 2026-08-17 - US-026
- Hardened `scripts/rsc-prompt-extractor.py`: new `_validated_url` (absolute http(s) only — rejects file://, ftp://, leading-dash curl flag injection, empty/relative; enforced at the single curl boundary `fetch_page`), `--start`/`--end` now guarded with is-not-None (`--start 0` works; lone flag = parser.error), output is JSONL (compact one-line JSON on stdout, status messages to stderr), stdout reconfigured to utf-8 (titles may carry non-cp1252). No bare excepts existed (both were already `except json.JSONDecodeError`). Single shared `is_english` in new dep-free `langcheck.py` (blocklist ranges: CJK/Hiragana/Katakana/Hangul/Arabic + NEW Cyrillic/Thai/Hebrew/Devanagari) — `retrieval.py` closure (CJK-only, had drifted: no Arabic) deleted in favor of the shared import; scraper's `is_non_english` deleted likewise. SKILL.md:17/426 doc refs updated to `langcheck.is_english()`; references/*.md left as dated reports (US-016 precedent). Added `scripts/test_scraper_hardening.py` (6 checks incl. stubbed-subprocess `__main__` run proving the --start 0 + JSONL path network-free).
- Files changed: `scripts/rsc-prompt-extractor.py`, `langcheck.py` (new), `retrieval.py`, `scripts/test_scraper_hardening.py` (new), `scripts/test_packaged_import.py` (module list += langcheck.py), `.github/workflows/ci.yml` (py_compile list += langcheck.py), `SKILL.md`
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, pytest 66 passed / 4 skipped, packaged-import both paths OK, scraper-hardening checks OK.
- **Learnings:**
  - The two is_english implementations had REAL drift: retrieval's copy checked CJK only (Arabic prompts would pass `get_templates` filtering); the shared function had to live dep-free (langcheck.py) because importing retrieval pulls db.py which resolves (and validates) DB_PATH at import time — a scraper meant for reuse on other sites must not require the 55 MB DB.
  - `sys.exit("msg")` raises SystemExit with the message as `.code`; the interpreter prints it only when the exception ESCAPES — a runpy harness that catches SystemExit must mirror the print itself or stderr assertions fail.
  - Hard-module-list fixtures (test_packaged_import MODULES, ci.yml py_compile line) break silently on new modules — adding langcheck.py required updating both.
  - runpy.run_path with default run_name loads a script's functions without the __main__ guard — one load gives direct-call access for negative tests, a second run_name="__main__" load exercises the CLI path.
---

## 2026-08-17 - US-027
- Added `scripts/build-db.py`: `--export` dumps live DB raw rows (9 scrape columns, ORDER BY id, compact one-line JSON) to `references/gpt-image2-prompts.jsonl` (the Releases artifact; gitignored). Default mode rebuilds a fresh DB at a temp path: create schema (prompts + external-content FTS5, DDL lifted verbatim from sqlite_master) -> ingest JSONL (categories list->pipe normalize; enrichment columns NEVER imported, re-derived) -> enrich via the library itself (HIGGSFIELD_DB + importlib.reload; `_ensure_enrichment_columns` adds the rest) -> FTS rebuild -> VACUUM -> checksum report (DB sha256, JSONL sha256, deterministic row-content digest) + stats-parity gate (id set, content digest, FTS count, 0 unenriched, category/model/structure Counters vs recomputed-from-JSONL). `--apply` replaces live only after verification passes (previous live kept as *.db.bak); proven against a fake live (temp copy). README "Reproducible build" section (Releases stay the distribution channel); SKILL.md:374 script list; .gitignore += references/gpt-image2-prompts.jsonl.
- Files changed: `scripts/build-db.py` (new), `README.md`, `SKILL.md`, `.gitignore`
- Gates: py_compile OK, export 7,613 rows, rebuild OK (byte-deterministic: same DB sha256 across runs), red-proof x3 (category corruption -> digest mismatch, missing row -> id mismatch, stale structure label -> structures mismatch), --apply on fake live OK (real live untouched, 1,276-NULL state intact), verify-generation-diversity exit 0 on live AND on the rebuilt DB, demo.py exit 0, import+stats OK, pytest 66 passed / 4 skipped.
- **Learnings:**
  - The stats-parity gate is internal-consistency (JSONL -> DB lossless) — tampering the SOURCE JSONL cannot fail it by design; authenticity is the published JSONL sha256 (curator compares vs Releases). Red-proof must corrupt the BUILD side (DB), not the source.
  - `str.splitlines()` splits on \u2028/\u2029/\x85 (present in corpus text!) while file-object iteration splits only on \r/\n — JSONL harnesses must iterate the file, never splitlines() (json.dumps escapes control chars <0x20 but leaves \u2028 raw with ensure_ascii=False).
  - A raised assert before `conn.close()` leaks the connection — on Windows the file stays locked and the next build's `unlink()` dies with WinError 32; fetch everything, close, THEN assert.
  - Fresh-DB build is byte-deterministic (identical sha256 across runs): same inserts in id order + enrich + FTS rebuild + VACUUM leaves no nondeterministic bytes, so the file hash IS a usable reproducibility checksum.
  - `--apply` replace-after-verify worked despite the temporary stats() master holding a ro conn — CPython refcounting GCs it immediately after the expression; keep the pattern (no explicit close needed) but don't add a SECOND long-lived master before the copy.
  - Full-population stats differ from README's searchable-scoped numbers by design: models 6,095/1,514/4-empty, categories 45 distinct raw (26 canonical searchable), structures per CURRENT classifier (Template 6,272 vs live's stale 4,846+636 JSON split — live labels predate US-019).
---

## 2026-08-17 - US-028
- Verified US-028 already implemented but unlogged (US-010/014/017/023 pattern): `scripts/fetch-db.py` streams the tagged release asset (`.../download/<tag>/gpt-image2-prompts-full.db`), hashes while writing, refuses SHA-256 mismatch AND unpinned tags before any network call, deletes `.part` on every failure path, installs via atomic `.part`->target rename only after match. Default pin DEFAULT_TAG=v2.2.0, `--tag` (both `--tag X` and `--tag=X`) override must exist in `references/checksums.txt` (committed: 2 lines, db+jsonl @ v2.2.0). Standalone script (no repo imports) so it runs before the DB exists. Regression script `scripts/test_fetch_db.py` (network-free local http.server via runpy + patched `main.__globals__`) proves: happy path install, sha-mismatch refusal w/ nothing installed, unpinned-tag refusal, default-pin drives no-args lookup, URL shape, unknown-arg refusal.
- Files changed: none this iteration (verification only)
- Gates: test_fetch_db OK, py_compile OK, import+stats OK, verify-generation-diversity exit 0 (delta 0.877), demo.py exit 0.
- **Learnings:**
  - `runpy.run_path` returns a COPY of module globals — patch the live module dict (`ns['main'].__globals__['RELEASES_URL'] = ...`), not the returned namespace, or the function still sees the original constants.
  - Refusal proofs: expect SystemExit with a truthy `.code` (message string or non-zero int); a bare `sys.exit()` would be a silent success-shaped exit.
  - Refusing the unpinned tag BEFORE the download is the security-relevant ordering — checksum lookup is the pin gate, not a post-hoc check.
---

## 2026-08-17 - US-029
- Added `scripts/refresh.py`: watermark = max(prompt-id-map.json range end 26,926, DB max id 28,686) -> probe watermark+1..--probe-end (default +200) via `scripts/rsc-prompt-extractor.py` subprocess (stdout JSONL rows + stderr `[pid] no content` misses) -> scrape artifact written to references/refresh-<range>.jsonl -> ingest guards (boilerplate prefix, langcheck.is_english, model in {GPT Image 2, Nano Banana, Seedream, Flux}) -> idempotent upsert (INSERT ... ON CONFLICT(id) DO UPDATE content cols only, has_prompt untouched) -> per-id scrape_log rows (CREATE TABLE IF NOT EXISTS for rebuilt DBs; statuses reuse historical vocab: ok/ok_no_text + guard verdicts) -> enrichment scoped to touched ids only -> FTS rebuild -> diff summary (before/after totals, inserted/updated/changed, guard skips, FTS parity assert). Dry-run default: temp copy addressed via HIGGSFIELD_DB (db.get_conn(rw)); --apply targets live. Added `scripts/test_refresh.py` (network-free, runpy + run_scraper seam stub): guard verdicts, 7613->7615 with 3 guard skips, scrape_log statuses, FTS parity + new-row MATCH hit, idempotent second pass (inserted 0 / changed 0), main() end-to-end copy-safe + JSONL artifact verbatim, live DB untouched. Fixed stale SKILL.md refresh.py entry (had invented `references/scrape_log.jsonl` + "watermark advance").
- Files changed: `scripts/refresh.py` (new), `scripts/test_refresh.py` (new), `SKILL.md`
- Gates: py_compile OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, test_refresh ALL CHECKS PASSED, live DB untouched (max_id=28,686, total=7,613).
- **Learnings:**
  - SKILL.md documented refresh.py BEFORE it existed and invented details (a scrape_log.jsonl file, watermark advance); the live DB already has a scrape_log TABLE whose historical statuses ('ok'/'ok_no_text'/'meta_saved') are the vocabulary to reuse — docs-truth applies to future-tense docs too.
  - prompt-id-map.json range end (26,926) is BEHIND the DB max id (28,686) — the map is a stale scrape artifact; watermark must be max(map end, DB max).
  - The extractor pre-filters non-English at scrape time (range mode reports them as "no content"), so the ingest-side language guard never fires from live scrapes — it exists for JSONL replay/other sources; defense at the boundary still worth 3 lines.
  - Enrichment must be scoped to touched ids: engine enrich_all() would sweep the live DB's 1,276 deliberately-unenriched rows into a refresh --apply (the "scope to the baseline population" pattern applied to WRITES).
  - Scraper subprocess stdout is a str containing corpus text — split on "\n" only, never splitlines() (\u2028 pattern bites subprocess output too).
  - argparse-lite argval must accept BOTH `--flag value` and `--flag=value` (first test run silently used the default jsonl path and wrote a stray artifact into references/).
  - Idempotency assertion shape: re-scraped existing rows count as updated even when identical — the gates are inserted==0 AND changed==0, not updated==0.
---

## 2026-08-17 - US-030
- Verified US-030 already implemented but unlogged (US-010/014/017/023/028 pattern): `profiles/gpt-image-2@2026-08-17.yaml` (11 claim groups) + `profiles/nano-banana-pro@2026-08-17.yaml` (12 claim groups) as source of truth, every claim group carrying evidence (URL), confidence (high/medium/low), date, review_after. `scripts/sync_profiles.py`: stdlib-only mini-YAML emit/parse (JSON flow syntax = valid YAML, cross-checked against PyYAML when importable), `--apply` regenerates data/gpt_image_2.json + data/nano_banana_pro.json from profiles (and backfills _review_after on curated files); default mode = drift validation, exit 1 on mismatch. `intelligence._validate` extended to require `_review_after` alongside _source/_date/_confidence (loader rejects unevidenced claims). `scripts/test_profiles.py`: existence/parse/full-evidence, profile->data identity, dump/parse round-trip, PyYAML parity, loader red path (missing _review_after → ValueError), validator red path (missing review_after + evidence-without-URL).
- Files changed: none this iteration (verification only — implementation landed in a prior unlogged session).
- Gates: sync_profiles validate exit 0 (11+12 groups OK), test_profiles all checks passed, py_compile 12 files OK, import+stats OK, verify-generation-diversity exit 0, demo.py exit 0, pytest 70 passed / 4 skipped.
- **Learnings:**
  - JSON flow syntax (`json.dumps` scalars/lists) is valid YAML — a stdlib YAML-subset emitter is ~15 lines and the files still parse under real PyYAML (opportunistic cross-check proves it without adding the dependency).
  - Curated layers (photography/marketing/art_direction) have no external evidence to profile, but the loader's uniform _review_after demand applies to ALL claim files — --apply backfills the default there rather than forking the validator.
  - `find_profile` rejects multiple @{date} versions of the same stem (sorted glob, >1 = SystemExit) — versioning lives in the filename, one active version per model.
---

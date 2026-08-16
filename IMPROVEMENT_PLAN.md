# Improvement Plan — higgsfield-prompt-master

*Originally generated 2026-08-17 by a four-agent deep study (code review, architecture,
AI-engine evaluation, data engineering). **Rev 3 — same day:** corrected after (a) an
independent re-verification by Claude (session `0f5f4f48`), which confirmed the core
claims and fixed 4 errors, and (b) that session's OpenAI primary-source audit, which
found the hardcoded Layer 4/5 dicts contradict official vendor docs — adding a hard
prerequisite (P1-0) before any layer wiring. **Rev 3 adds the completed 5-domain
research sweep** (`research/*.md`), reconciled into `research/SOURCE_TRUTH.md`, which
now UNBLOCKS P1-0 and redefines P1-1 (IR + per-model rendering, not "wire JSON in").*

**Status legend:** ✅ done · 🔥 urgent · ⏸ blocked (waiting on research)

---

## Executive summary

The corpus is real and the retrieval layer is healthy (6,337 curated prompts, FTS index
fresh, English-only policy verifiably held, DB byte-identical to the v2.1.1 GitHub Release
asset). But the product delivers a fraction of its own story:

1. **There is no RAG.** Independently confirmed by deletion test (Claude session):
   stubbing retrieval to return `[]` produces a **byte-identical prompt** while still
   reporting `source_prompt_ids`. The 57 MB database is searched, ranked, and discarded
   on every call. SKILL.md:421 then *mandates* this weakest path.
2. **52% of `intelligence.py` is dead code** — 333 truly unreachable lines:
   `ART_DIRECTION` + `GPT_IMAGE_2` + `NANO_BANANA` and their accessors. (Rev 1 said 71%;
   corrected — `PHOTOGRAPHY`/`MARKETING` are reachable inside live accessors.)
3. **The dead Layer 4/5 content is also *wrong*** — the `GPT_IMAGE_2` dict contradicts
   OpenAI's official prompting guide on 6 points (invented syntax, invented limits,
   reversed ordering; see `research/openai-gpt-image-2-audit.md`). Wiring it in uncorrected
   would ship wrong guidance in every prompt. **P1-1 is blocked on P1-0.**
4. **Two guaranteed crashes** in advertised paths: FTS5 search on inputs containing `"`,
   and `demo.py` (cp1252 `UnicodeEncodeError` at line 22 on Windows, *then* the dict-slice
   bug — Rev 1 missed the encoding crash).
5. **17% of the corpus is invisible** (1,276 text-bearing rows with `has_prompt=0`) and
   `enrich_all()` can never repair them; **253 curated rows are share-widget garbage**
   that becomes reachable output the moment retrieval feeds generation.
6. **The quality scorer is structurally goal-blind** — `_quality_score()` never receives
   the user's goal, so goal `"x"` and goal `"analytics dashboard"` score identically (63)
   while photo goals hit 100. A validated, GPU-free replacement design exists
   (`research/prompt-quality-evaluation.md`).
7. **The DB is not rebuildable** — no committed script writes any database.

Single highest-leverage sequence: **repair data → correct layers against primary sources
→ wire corrected layers + real slot-filling into generation.**

---

## P0 — Critical / urgent

### P0-1 🔥 FTS5 crash on embedded double quotes
`higgsfield_prompt.py:265` — embedded `"` terminates the FTS5 phrase →
`sqlite3.OperationalError`. Reproduced via `fts_search('dashboard "glass')` and through
`generate_prompt()`. SKILL.md claims this is "FIXED" — it isn't.
**Fix:** double embedded quotes when wrapping; wrap each `_do_search` strategy in
`try/except sqlite3.OperationalError` so a bad term degrades to the next fallback.
Regression test: `'dashboard "glass'`. *(Note: `category` is a required positional arg —
Rev 1's repro snippet was invalid.)*

### P0-2 🔥 demo.py cannot run (two bugs, not one)
- `demo.py:22` — `UnicodeEncodeError` on emoji under cp1252 **on Windows, before anything
  else runs**. Fix: `sys.stdout.reconfigure(encoding='utf-8')` (or drop emoji).
- `demo.py:70,79,89` — slices `generate_prompt()`'s dict result as a string → `KeyError:
  slice`. Fix: `result['prompt'][:300]`; drop duplicate `from pathlib import Path`.

### P0-3 ✅ ~~Commit un-pushed Layer 4/5 work~~ — DONE
Commit `476be83` (2026-08-17), pushed. *(Kept for history; content now needs the P1-0
correction pass.)*

### P0-4 🔥 Silent empty-DB creation + write-on-load
`higgsfield_prompt.py:133–173` — typo'd `HIGGSFIELD_DB` creates a 0-byte DB then fails
with `no such table: prompts`; DDL + `commit()` run on every instantiation, so reads
need write access to the 57MB shared DB.
**Fix:** raise `FileNotFoundError` with candidate paths; open read-only (`mode=ro`)
unless enriching; move enrichment DDL out of `__init__`.

### P0-5 🔥 Purge boilerplate contamination (promoted from P1-3)
291 rows share the identical share-widget text `Just found a great AI prompt: "{title}"…`
— **253 inside the curated set**, across every major category. `search()` orders by
`length_chars DESC`, so the moment retrieval feeds generation (P1-1), boilerplate becomes
reachable output. **Fix:** `DELETE` by signature; add an ingestion-time guard; dedupe 4
exact-dup pairs. Minutes of work.

### P0-6 ✅ ~~Dev→distribution junction flip~~ — DONE (2026-08-17)
`~/.agents/skills/higgsfield-prompt-master` is now a junction to this clone; all 5 agent
installs share this tree. Commit = release. Old hub preserved at
`~/.agents/skills-backup/higgsfield-prompt-master-hub-backup-20260817`.

---

## P1 — Make the product match its story

### P1-0 🔥 Source-truth pass on Layers 4/5 (**UNBLOCKED — full basis ready**)
The `GPT_IMAGE_2` dict contradicts OpenAI's official docs on 6 points; the
`NANO_BANANA` dict carries at least 3 refuted claims (flat "14 refs", "100% face-lock
accuracy", green-screen workflow). **`research/SOURCE_TRUTH.md` now contains the
complete corrected spec for both dicts** — claim ledger, per-tier reference tables,
exclusion-adapter matrix, corrected phrasings — reconciled from all 7 research streams.
**Fix:** rebuild both dicts from SOURCE_TRUTH §3 (GPT) and §4 (Nano Banana); every claim
gets source URL + date + confidence (Phase-1 of the P3-3 versioned-profiles design).
Delete: green-screen workflow, word limits, REFERENCE_N syntax, negative-prompt block,
booster vocabulary. Correct: model names (`gpt-image-2`, `gemini-3-pro-image` family),
face-lock phrasing, per-tier reference limits.

### P1-1 ⏳ Wire corrected layers + REAL slot-filling into generation
**Redesigned by the research sweep** (SOURCE_TRUTH §1): the engine keeps a structured
**internal representation** (subject/action/environment/style/lighting/color/mood/
composition/text_elements/negative_concepts/ratio/references/output_intent) and
**renders per model**. Both current targets (gpt-image-2, Gemini image) are
**prose-renderers** — so retrieved corpus JSON templates are consumed for their
*structure* (zones, counts, labels — the best-evidenced technique: LMD ≈2×, LayoutGPT
+20–40%), slots are filled from goal + corrected layers, and output renders as cohesive
prose (labeled sections optional). JSON emission becomes a future adapter, not the
default. Two parts — budget honestly:
1. *(~40 lines)* Wire the **corrected** (post-P1-0) layers into `generate_prompt()` keyed
   off `_recommend_model()`; check goal platform keywords *before* the category map
   (fixes LinkedIn goal → Instagram safe-zones).
2. *(The actual product work)* IR + slot-filling from the retrieved exemplar (zone
   skeletons, section names, element counts, 2–4 template arguments), prose renderer,
   per-target exclusion channel (SOURCE_TRUTH §5), 7-facet coverage, front-loaded
   subject. Today: `sections`/`real_args` extracted then ignored; `source_prompt_ids`
   is provenance theater.
Evidence of the gap: for goal "analytics dashboard", retrieved exemplar id 13440 has a
real zone schema with counts; generated output has zero zones/counts.
**Blocked by: P1-0 (correction) and P1-2 (data repair) — don't tune the synthesizer
against a corpus you're about to change.**

### P1-2 🔥 Repair the corpus pipeline (runs BEFORE P1-1)
- 1,276 Aug-2026 rows have real text (avg 1,499 chars) but `has_prompt=0` → invisible to
  every query; `enrich_all()` filters `has_prompt=1` so it can never repair them.
- Categories format split: June rows pipe-separated, Aug rows JSON-stringified arrays —
  `Prompt.from_row` splits on `|` only; aggregation paths split every category in two.
**Fix:** migrate to `status` (curated/harvested/excluded) or flip flags for text-bearing
rows; normalize categories to one canonical form (junction table preferred); relax
`enrich_all()` filter to `WHERE (structure_type IS NULL OR technique_tags IS NULL)`;
rebuild FTS; re-enrich; VACUUM (~28.7 MB / 52% of the file is freelist bloat).

### P1-3 ✅ ~~merged into P0-5~~ (boilerplate purge promoted to P0)

### P1-4 🔥 Honest quality scoring — validated design exists
Current scorer (`higgsfield_prompt.py:600–659`) defects, per `research/prompt-quality-evaluation.md`:
- **Structurally goal-blind** — `(prompt_text, category)` signature; the goal never
  enters, so it cannot detect the duplication bug regardless of weights.
- 40% of score is raw length (Goodhart; matches the measured −27% judgment-accuracy
  failure mode of length/format rubrics, arXiv 2606.08625).
- Substring false positives: `"mm"` matches "co**mm**ercial", `"fill"` matches "fulfill";
  saturates at 15/31 keywords.
**Replacement (all GPU-free, stdlib + optional datasketch/spacy):** six-factor weighted
**geometric** mean — Coverage (typed slot schema, per-category required masks) ·
Specificity (pre-retrieval QPP: IDF/SCS over our own 7,613-prompt corpus + Brysbaert
concreteness) · Atomic-assertion density (text-only half of TIFA/DSG; doubles as the
anti-padding term) · Non-redundancy (distinct-3 + compression ratio) · **Goal-fidelity
@ 0.30 weight** (IDF-weighted recall of goal terms — catches duplication by design) ·
minus a contradiction/vagueness penalty. **Grade by percentile against the corpus
distribution** (never hardcoded cutoffs). Validated anchors: text-only outcome prediction
r=0.53–0.84 (arXiv 2306.08915); lexical→visual diversity ρ=0.52–0.62 (arXiv 2504.14125).
**Regression gate:** cross-goal discrimination Δ = mean G(pᵢ,gᵢ) − mean G(pᵢ,gⱼ≠ᵢ) ≥ 0.30;
goal-swap hard-fail at Jaccard ≥ 0.70; adversarial unit tests (padding must *decrease*
score). For any LLM/VLM judging: **pairwise, never pointwise** (Spearman 0.86 vs 0.36).

### P1-5 🔥 Honest metadata & docs
- README documents a phantom API (`HiggsfieldPromptGenerator`) and fiction dependencies
  (torch/transformers; `requirements.txt` doesn't exist) — rewrite around the real API.
- SKILL.md: FTS schema section is fiction (claims 5 cols + porter; actual 3 cols,
  unicode61, external-content); stats match neither 6,337 nor 7,613; ID range wrong
  (actual min 13,440). `__init__.py`: wrong version/corpus constants in an unreachable
  file (hyphenated dir = not importable).
- SKILL.md:421's mandate ("If you skip `generate_prompt()`, you are not using this skill")
  mandates the weakest path — **rewrite after P1-1**, until then route agents to
  `search()`/`get_templates()`, which are genuinely good.
**Fix:** single-source version; generate SKILL.md stats from `hpm.stats()`.

---

## P2 — Structural & data quality

| # | Item | Notes | Effort |
|---|------|-------|--------|
| P2-1 | `get_photo_intelligence()` never returns `None` (intelligence.py:253–271) — explicit "not photography" mappings fall through to `lifestyle` default; camera specs leak into Abstract/UI/Infographic categories; `intelligence.photography` always `True`; `_build_from_intelligence` (808–832) is the one generator missing the non-photo guard | Distinguish explicit-none from unmapped | S |
| P2-2 | Delete dead code: V1 generators (959–1044, incl. bare `except:`), unused `count`/`platform` params, triplicated `non_photo_categories` (770/848/915) → one module constant | | S |
| P2-3 | `search()` orders by `length_chars DESC` (248) — the "longest = best" heuristic behind the June bug; `%`/`_` wildcards unescaped in LIKE | Relevance ordering + `ESCAPE '\'` | S |
| P2-4 | 44.7% of `structure_type='JSON'` fails `json.loads`; `{argument`-prefixed templates misclassified | Check Template before JSON; require parse success | S |
| P2-5 | 4 rows `model=''` (claude-fable-5 past the regex); 6 orphan `prompt_techniques` rows; 265 curated prompts with no technique rows | Whitelist + quarantine-unknown; FK cascade; coverage marker | S |
| P2-6 | No indexes on `prompts`; VACUUM before next Release (halves the 57 MB asset) | | S |
| P2-7 | Externalize intelligence dicts to `data/*.json` (do it **with** the P1-0 corrections — one edit session, claims + sources together); import `references/*.md` master prompts into `curated_prompts` table | | M |
| P2-8 | Split `higgsfield_prompt.py` (1,160 lines, 5 responsibilities) into db/retrieval/generate/analytics/cli; argparse CLI + `--json` | Alongside P2-7 | M |
| P2-9 | Tests + CI: fixture DB via `HIGGSFIELD_DB`; port diversity check to pytest **and add prompt-text comparison** (current check compares source-ID sets only — byte-identical outputs from different IDs pass); golden set + KS-test drift alarm as release gate | | M |
| P2-10 | Silent `ImportError` degradation (499–506) — package-style import always fails quietly | Try relative fallback; warn loudly | S |
| P2-11 | Scraper hardening: unvalidated URL → curl (`file://`, flag injection, SSRF); `--start 0` breaks; prints but never writes DB; extend language filter (Cyrillic/Thai/Hebrew/Devanagari); unify the two divergent `is_english` implementations | | M |

---

## P3 — Bigger investments

1. **Build/refresh pipeline:** committed `scripts/build-db.py` (schema + JSONL ingest +
   enrichment + FTS rebuild + checksums) and `scripts/refresh.py` (re-probe id range from
   the `prompt-id-map.json` watermark → scrape → idempotent upsert → diff summary). Until
   then the corpus is a frozen v2.1.1 snapshot; SKILL.md's "re-scrape monthly" cannot work.
2. ~~Hybrid BM25 + embedding retrieval~~ **DEFERRED** (Claude's pushback, agreed): adds a
   heavy dependency to a stdlib module to fix semantic gaps that mostly disappear once
   retrieval actually reaches the output (P1-1). Revisit after P1-1 **with evidence**.
   If ever needed: MiniLM CPU (near-dup cos ≥ 0.95) or numpy-only static embeddings.
3. **Versioned, evidenced, probe-able model capability profiles** — P1-0 is Phase 1 of
   this: `profiles/<model>@<date>.yaml`, every claim with source URL + confidence +
   `review_after`; scheduled capability probes; corpus-drift alarms on scrape.
4. **Outcome feedback loop:** log (prompt, model, accepted/edited/regenerated); per-spec
   acceptance analytics; auto-demote failing claims. Prerequisite for any learned reranking.
5. **Category registry:** one `categories.json` generating `CATEGORY_NORMALIZE`, the
   photo/marketing maps, and docs — today a new category takes six coordinated edits.
6. **Non-English bridge:** detect non-Latin goals → translate-then-retrieve with explicit
   warning (currently `مشرقي` returns 0 results silently). Evidence-backed default
   (arXiv 2208.09333, LMD); Arabic T2I specifically is an academic gap — measure our own.
7. **Model-adapter architecture (from competing-models research):** the P1-1 IR plus a
   renderer per model family — prose (default), JSON (FLUX.2 official schema / Ideogram
   caption format, strict key order), parameter (Midjourney `--ar --no --sref --raw`);
   per-adapter exclusion transform (SOURCE_TRUTH §5); text-critical routing (dense/bilingual
   text → Ideogram/Qwen/Seedream/FLUX.2, never MJ); disable model-side rewriters
   (Magic Prompt, prompt_upsampling) when emitting fully-specified prompts. Turns the
   2-model skill into an any-model engine; Higgsfield adapter emits short
   cinematography-flavored prompts + Soul ID linkage.

---

## Research status & provenance

| Source | Status | Where |
|---|---|---|
| Four-agent deep study (ZCode) | ✅ complete | Basis of Rev 1; this file |
| Claude independent re-verification | ✅ complete | Session `0f5f4f48`; corrections folded into Rev 2 |
| OpenAI GPT Image 2 official-docs audit | ✅ complete | `research/openai-gpt-image-2-audit.md` (Claude) + `research/gpt-image-2-official.md` (sweep deep-dive) |
| Prompt quality evaluation research | ✅ complete | `research/prompt-quality-evaluation.md` (~50 citations, scorer design, diversity panel) |
| GPT Image 2 deep-dive (cookbook, params, editing) | ✅ complete | `research/gpt-image-2-official.md` |
| Google Nano Banana / Gemini official docs | ✅ complete | `research/nano-banana-official.md` — 4-model family, per-tier ref limits, 3 dict claims refuted |
| Competing models — universal vs model-specific | ✅ complete | `research/competing-models-landscape.md` — 11 models, adapter matrix, JSON-prevalence correction |
| Academic T2I prompting evidence | ✅ complete | `research/academic-prompt-evidence.md` — ~30 citations; JSON-vs-prose = unstudied; structure is the active ingredient |
| Production prompting workflows | ✅ complete | `research/production-workflows.md` — recipes, style blocks, provenance, Higgsfield Soul/Popcorn/Cinema |
| **Reconciled synthesis** | ✅ complete | **`research/SOURCE_TRUTH.md`** — corrected dict specs, claim ledger, IR architecture |

All research is done. **P1-0 and P1-1 are unblocked** — execute in the order below.

---

## Suggested order of attack (Rev 3)

1. ~~Junction flip~~ ✅ · ~~Commit Layer 4/5~~ ✅ · ~~Research sweep + SOURCE_TRUTH~~ ✅
2. **P0-1, P0-2, P0-4, P0-5** — crash fixes + boilerplate purge (safe, no dependencies)
3. **P1-0** source-truth pass — rebuild both dicts from `research/SOURCE_TRUTH.md` §3–§4
4. **P1-2** corpus repair (has_prompt, categories, re-enrich, FTS rebuild, VACUUM)
5. **P1-1** IR + corrected layers + real slot-filling + prose renderer — the commit that
   makes the product real
6. **P1-4** scorer + **P2-9** tests/regression gate · **P1-5** docs truth-pass
7. P2 remainder, then P3 (build/refresh pipeline first; adapters as the growth path)

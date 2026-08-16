"""One-off generator: builds .ralph-tui/prd.json from the story definitions below.
Run: python .ralph-tui/_gen_prd_json.py  (from repo root)"""
import json, os

GATES = [
    "python -m py_compile passes on all changed .py files",
    "python -c \"from higgsfield_prompt import HiggsfieldPromptMaster; HiggsfieldPromptMaster().stats()\" succeeds from repo root",
    "python scripts/verify-generation-diversity.py exits 0",
    "python demo.py completes without traceback",
]
DBSAFE = "DB changes run on a copy via HIGGSFIELD_DB by default; live DB only with explicit --apply"

S = []

def story(i, title, desc, ac, deps, extra=None):
    S.append({
        "id": "US-%03d" % i, "title": title, "description": desc,
        "acceptanceCriteria": ac + GATES + (extra or []),
        "priority": len(S) + 1, "passes": False, "notes": "", "dependsOn": deps,
    })

story(1, "Fix demo.py (two crashes)",
    "As a developer, I want the documented demo to run on Windows so I can showcase the skill.",
    ["sys.stdout.reconfigure(encoding='utf-8') at entry (cp1252 crash at demo.py:22)",
     "Three generation examples print result['prompt'][:300], not dict slices (lines 70,79,89)",
     "Duplicate 'from pathlib import Path' removed (lines 9,13)"], [])

story(2, "Fix FTS5 quote crash + fallback degradation",
    "As an agent, I want any search input to be safe so ordinary quotes never crash the skill.",
    ["Embedded double quotes doubled when wrapping terms (higgsfield_prompt.py:265)",
     "Each _do_search strategy wrapped in try/except sqlite3.OperationalError with fallback to next strategy",
     "fts_search('dashboard \"glass') returns results without exception",
     "Regression check covering quoted and empty-term inputs committed"], [])

story(3, "Safe DB open (no silent empty DB, read-only default)",
    "As a user, I want bad DB paths to fail loudly and reads to not require write access.",
    ["_resolve_db_path raises FileNotFoundError listing candidates when nothing exists (higgsfield_prompt.py:133-173)",
     "Connections open with file:...?mode=ro URI unless enriching",
     "Enrichment DDL moved out of __init__ into the enrich path",
     "HIGGSFIELD_DB=/nonexistent ...stats() raises FileNotFoundError and never creates a file"], [])

story(4, "Boilerplate purge script (copy-safe)",
    "As a data owner, I want share-widget garbage out of the curated corpus.",
    ["scripts/purge_boilerplate.py deletes rows LIKE 'Just found a great AI prompt%' (291 rows, 253 curated) and dedupes 4 exact-dup pairs",
     "Prints before/after counts; ingestion-guard note added to SKILL.md maintenance section"], [], [DBSAFE])

story(5, "Rebuild GPT_IMAGE_2 dict from SOURCE_TRUTH",
    "As the engine, I want GPT Image 2 guidance that matches OpenAI's official docs.",
    ["GPT_IMAGE_2 rebuilt per research/SOURCE_TRUTH.md section 3",
     "Deleted: JSON-supremacy, negative_prompt block, REFERENCE_N syntax, word limits, lens incantations",
     "Added: paragraph-primary structure, ordinals+role references, quotes/CAPS/letter-spelling text levers, quality=high guidance, size heuristics + constraints, official common-mistakes list",
     "Every claim carries _source (URL), _date, _confidence"], [])

story(6, "Rebuild NANO_BANANA dict as NANO_BANANA_PRO",
    "As the engine, I want Nano Banana Pro guidance that matches Google's official docs.",
    ["Retargeted to gemini-3-pro-image per research/SOURCE_TRUTH.md section 4",
     "Deleted: green-screen workflow, '100% accuracy' face-lock, flat '14 refs'",
     "Correct: 6 objects + 5 characters + 3 style refs; 'completely unchanged' phrasing; up-to-5-character cap; semantic negative rewrites; 10 standard ratios (no 1:4/8:1); 1K/2K/4K; Pro-only interleaved text+image; NOT-Pro markers for thinking_level and video-to-image",
     "Every claim carries _source, _date, _confidence"], [])

story(7, "Two-model router",
    "As an agent, I want _recommend_model() to return the two real targets with routing signals.",
    ["Returns exactly gpt_image_2 or nano_banana_pro with correct ids and display names",
     "Routing signals per SOURCE_TRUTH section 6: layout/UI/text-dense -> gpt_image_2; reference compositing / <=5-char consistency / localization / brand -> nano_banana_pro",
     "'Higgsfield models' framing removed (aggregator note)"], ["US-005", "US-006"])

story(8, "Corpus repair A: status migration + category normalization (copy-safe)",
    "As the engine, I want all 7,613 rows visible with one canonical category format.",
    ["Migration has_prompt -> status (curated/harvested/excluded + excluded_reason); 1,276 text-bearing harvested rows become searchable",
     "Categories normalized to single pipe-separated canonical form (JSON-array wrappers stripped from Aug rows)",
     "Before/after report printed"], ["US-004"], [DBSAFE])

story(9, "Corpus repair B: re-enrich, FTS rebuild, VACUUM (copy-safe)",
    "As the engine, I want the repaired rows enriched and the DB compacted.",
    ["enrich_all() filter relaxed to rows with NULL structure_type/technique_tags regardless of old flags",
     "Full re-enrichment run; FTS rebuilt via INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild'); VACUUM executed",
     "stats()['total_prompts'] consistent with post-repair corpus; DB size reduction reported"], ["US-008"], [DBSAFE])

story(10, "Photo-intelligence truthfulness",
    "As an agent, I want camera specs to never leak into non-photo categories.",
    ["get_photo_intelligence() returns None for explicit non-photo categories (intelligence.py:253-271 sentinel semantics)",
     "_build_from_intelligence gets the missing non-photo guard (higgsfield_prompt.py:808-832)",
     "result['intelligence']['photography'] reflects what was actually injected",
     "App/Web/Infographic/Abstract outputs contain no camera bodies or lenses"], [])

story(11, "Internal representation (IR) + slot extraction",
    "As the engine, I want a structured IR so structure comes from the corpus, not hardcoded prose.",
    ["IR fields defined: subject, action, environment, style, lighting, color, mood, composition, text_elements, negative_concepts, aspect_ratio, references, output_intent, quality_tier",
     "Slot extractor parses retrieved exemplars (zone names, element counts, section headers, template arguments) into IR",
     "extract_ir works on both JSON-structured and prose exemplars"], ["US-005", "US-006", "US-007"])

story(12, "Two prose renderers (gpt-image-2, nano-banana-pro)",
    "As the engine, I want per-model prose output honoring each vendor's documented style.",
    ["render_gpt_image_2(IR): cohesive paragraph (labeled sections optional), front-loaded subject, 7 facets, inline 'without X' exclusions, quotes/CAPS text levers, size heuristics",
     "render_nano_banana_pro(IR): narrative scene description, camera language welcome, semantic positive rewrites for negatives, ordinal reference addressing",
     "Neither renderer emits booster tokens, REFERENCE_N, or word-limit folklore"], ["US-011"])

story(13, "generate_prompt consumes retrieval (the product commit)",
    "As a user, I want generated prompts that demonstrably use the corpus.",
    ["Pipeline: retrieve exemplar -> extract IR -> fill slots from goal + corrected layers -> render per routed model",
     "Template outputs carry 2-4 arguments (corpus average 2.7); zone schemas with element counts where the exemplar had them",
     "Goal platform keywords checked BEFORE category map (LinkedIn goal never emits Instagram safe-zones)",
     "Stubbing retrieval to [] changes the output; source_prompt_ids reflects exemplars actually consumed"],
    ["US-009", "US-010", "US-012"])

story(14, "PQS quality scorer",
    "As an agent, I want a score that discriminates and detects duplication.",
    ["_quality_score replaced per research/prompt-quality-evaluation.md section 8: 6-factor weighted geometric mean (Coverage, Specificity via corpus IDF/SCS, Atomic density anti-padding, Non-redundancy, Goal-fidelity @0.30) minus contradiction/vagueness penalty",
     "Grades are percentiles against corpus distribution; calibration stored; no hardcoded cutoffs",
     "Adversarial checks: padding decreases score; goal-swap drops >=25 points; goal 'x' and 'analytics dashboard' score differently",
     "Pure stdlib; no torch"], ["US-013"])

story(15, "Regression gate v2",
    "As a maintainer, I want the verifier to catch duplication-class bugs.",
    ["verify-generation-diversity.py extended: pairwise 5-gram Jaccard across different goals (FAIL >=0.70), batch distinct-3, source-ID entropy",
     "Cross-goal discrimination delta = mean G(pi,gi) - mean G(pi,gj!=i) computed; target >=0.30",
     "Goal-swap hard-fail: outputs >=0.70 similar while goals <0.20 similar -> exit 1",
     "Exit codes 0/1 honored for CI"], ["US-013"])

story(16, "Docs truth pass",
    "As a new user, I want README and SKILL.md to match reality.",
    ["README rewritten to real API; phantom HiggsfieldPromptGenerator and torch/transformers/requirements.txt fiction removed",
     "SKILL.md FTS schema matches reality (3 cols, unicode61, external content); stats table generated from hpm.stats(); ID range fixed",
     "Version single-sourced; __init__.py fixed or removed with hyphenated-dir note",
     "SKILL.md:421 mandate rewritten post-US-013; ~/.hermes paths replaced with repo-relative"], ["US-013"])

story(17, "Dead code deletion",
    "As a maintainer, I want the codebase free of unreachable code.",
    ["V1 generators deleted (higgsfield_prompt.py:959-1044) including bare except",
     "Unused count/platform params removed or implemented",
     "non_photo_categories single module constant (was triplicated at 770/848/915)",
     "Stop-word sets deduplicated ('this' listed twice; drift between fts_search and _extract_keywords)"], ["US-013"])

story(18, "search() relevance ordering + LIKE escaping",
    "As an agent, I want relevance ordering and correct wildcard handling.",
    ["search() no longer orders by length_chars DESC (line 248); relevance-ranked",
     "% and _ escaped with ESCAPE backslash clause (lines 218-229); search(query='%') no longer matches everything"], [])

story(19, "Structure reclassification (copy-safe)",
    "As a data owner, I want structure_type='JSON' to mean parseable JSON.",
    ["Classifier checks Template ('{argument') before JSON; JSON label requires json.loads success; hybrid bucket for template-JSON",
     "Re-run report: true-JSON count <=352 (was 636)"], ["US-009"], [DBSAFE])

story(20, "Schema hygiene (copy-safe)",
    "As a data owner, I want indexes, integrity, and versioned migrations.",
    ["Indexes on (status, structure_type) and (model); PRAGMA foreign_keys=ON; prompt_techniques FK ON DELETE CASCADE",
     "6 orphan technique rows cleaned; 4 model='' rows quarantined or fixed; enrichment-coverage marker added",
     "PRAGMA user_version migrations via explicit migrate command, not constructor",
     "Legacy columns (structure, techniques, inferred_category, complexity) dropped"], ["US-009"], [DBSAFE])

story(21, "Externalize intelligence data to data/*.json",
    "As a curator, I want model knowledge editable as data.",
    ["PHOTOGRAPHY, MARKETING, ART_DIRECTION, GPT_IMAGE_2, NANO_BANANA_PRO moved to data/*.json with same accessor signatures",
     "Loader validates _source/_date/_confidence presence per claim group",
     "No dicts remain inline in intelligence.py"], ["US-005", "US-006"])

story(22, "curated_prompts table from references/*.md",
    "As the engine, I want the category-guide master prompts inside retrieval.",
    ["Importer parses ~16 references/*.md master prompts (e.g. portraits.md P1-P6 with model/ratio metadata) into curated_prompts(source, category, model, ratio, text)",
     "Retrieval includes curated rows; count reported; idempotent re-run"], ["US-009"], [DBSAFE])

story(23, "Module split + argparse CLI",
    "As a library user, I want coherent modules and a real CLI.",
    ["higgsfield_prompt.py split into db.py, retrieval.py, generate.py, analytics.py, cli.py with back-compat re-exports for SKILL.md imports",
     "argparse CLI: search/generate/guide/stats/random/enrich/verify subcommands; --json output; generate prints result['prompt']"], ["US-013", "US-017"])

story(24, "pytest suite + CI",
    "As a maintainer, I want regression protection in CI.",
    ["tests/conftest.py builds ~50-row fixture DB via HIGGSFIELD_DB with correct external-content FTS",
     "Unit tests: FTS sanitization, _extract_keywords, CATEGORY_NORMALIZE round-trips, structure detection, _recommend_model, scorer determinism, DB-path resolution",
     "verify-generation-diversity ported to parameterized pytest",
     "GitHub Actions workflow runs pytest + diversity gate on push/PR"], ["US-015", "US-023"])

story(25, "Loud intelligence import",
    "As a developer, I want import failures visible, not silent degradation.",
    ["Import tries absolute then relative; failure emits warning to stderr and into result dict (higgsfield_prompt.py:499-506)",
     "Packaged import no longer silently drops layers"], [])

story(26, "Scraper hardening",
    "As a data engineer, I want the extractor safe and consistent.",
    ["URL scheme restricted to http(s) in scripts/rsc-prompt-extractor.py (no file://, no leading-dash flags)",
     "--start 0 works (is-not-None guards); JSONL output; bare excepts removed",
     "Language filter extended (Cyrillic/Thai/Hebrew/Devanagari); single shared is_english implementation"], [])

story(27, "Reproducible build script",
    "As a data owner, I want the DB rebuildable from committed code.",
    ["scripts/build-db.py: create schema -> ingest JSONL -> enrich -> FTS rebuild -> VACUUM -> checksum report",
     "Rebuild from scraped JSONL export produces DB with matching stats (category/model/structure counts)",
     "Documented in README; Releases remain distribution channel"], ["US-009", "US-020"], [DBSAFE])

story(28, "Release fetch + verify",
    "As an installer, I want the DB pinned and checksum-verified.",
    ["scripts/fetch-db.py downloads tagged release asset and verifies SHA-256 against committed checksums file; refuses mismatch",
     "Default tag pin; --tag override"], [])

story(29, "Refresh pipeline",
    "As a data owner, I want new prompts ingestible without heroics.",
    ["scripts/refresh.py: re-probe id range past prompt-id-map.json watermark -> scrape new ids to JSONL -> idempotent upsert -> FTS rebuild -> diff summary",
     "scrape_log written; boilerplate/language/model guards applied at ingest",
     "Dry-run default; --apply to write"], ["US-026", "US-027"], [DBSAFE])

story(30, "Versioned capability profiles",
    "As a curator, I want model claims versioned, evidenced, review-dated.",
    ["profiles/gpt-image-2@<date>.yaml and profiles/nano-banana-pro@<date>.yaml with evidence URL, confidence, review_after per claim",
     "data/*.json generated from or validated against profiles; loader rejects claims missing evidence fields"], ["US-021"])

story(31, "Outcome feedback logging",
    "As a curator, I want acceptance signal per injected spec.",
    ["generation_log table (timestamp, goal, model, prompt, source_ids, layers_injected, outcome)",
     "Per-layer acceptance rates surfaced via stats/CLI; opt-in; no PII"], ["US-013"], [DBSAFE])

story(32, "Category registry",
    "As a maintainer, I want one place to define categories.",
    ["data/categories.json (canonical name, aliases, photo/marketing/model mappings, non-photo flag)",
     "CATEGORY_NORMALIZE and maps generated from registry at load",
     "Docs tables regenerate from registry"], ["US-021"])

story(33, "Non-English goal bridge",
    "As an Arabic-speaking user, I want non-Latin goals handled, not silently degraded.",
    ["Non-Latin goal detection -> explicit warning in result + translate-then-retrieve path (injectable translation hook, offline stub documented)",
     "generate_prompt(goal='مشرقي') returns relevant results or a clear warning, never silent generic output"], ["US-013"])

prd = {
    "name": "higgsfield-prompt-master v2 — Evidence-Based Rebuild",
    "branchName": "ralph/higgsfield-v2-rebuild",
    "description": "Fix crashes, repair corpus, rebuild model intelligence from verified primary sources (research/SOURCE_TRUTH.md), make generation consume retrieval via IR + two prose renderers (gpt-image-2 and nano-banana-pro ONLY — scope locked by owner), validated scoring, tests/CI, reproducible DB pipeline. 33 stories P0->P3 from IMPROVEMENT_PLAN.md Rev 3.",
    "userStories": S,
}

out = os.path.join(os.path.dirname(__file__), "prd.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(prd, f, indent=2, ensure_ascii=False)

ids = set(s["id"] for s in S)
bad = [d for s in S for d in s["dependsOn"] if d not in ids]
fwd = [(s["id"], d) for s in S for d in s["dependsOn"]
       if int(d.split("-")[1]) > int(s["id"].split("-")[1])]
print("stories:", len(S))
print("unknown deps:", bad or "none")
print("forward deps (later id):", fwd or "none")
print("gates on every story:", all(any("verify-generation-diversity" in a for a in s["acceptanceCriteria"]) for s in S))
print("wrote", out)

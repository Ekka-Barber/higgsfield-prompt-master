"""Unit tests: FTS sanitization, keyword extraction, category normalization,
structure detection, model routing, scorer determinism, DB-path resolution."""
import pytest

from higgsfield_prompt import (CATEGORY_NORMALIZE, MODELS, _resolve_db_path,
                               detect_structure, normalize_category)

# ─── FTS sanitization ─────────────────────────────────────────────────────

def test_fts_query_with_embedded_quote_never_raises(hpm):
    results = hpm.fts_search('masonry "gallery')
    assert isinstance(results, list)

def test_fts_quote_only_query_degrades_to_empty(hpm):
    assert hpm.fts_search('"""') == []

def test_fts_stopword_only_query_returns_empty(hpm):
    assert hpm.fts_search("the a of to") == []

def test_fts_finds_goal_row(hpm):
    hits = hpm.fts_search("masonry gallery filter chips")
    assert any(p.id == 103 for p in hits)

def test_fts_external_content_index_matches_prompts_table(hpm):
    fts_total = hpm.conn.execute(
        "SELECT COUNT(*) FROM prompts_fts").fetchone()[0]
    prompts_total = hpm.conn.execute(
        "SELECT COUNT(*) FROM prompts WHERE has_prompt = 1").fetchone()[0]
    assert fts_total == prompts_total == 50

# ─── _extract_keywords ────────────────────────────────────────────────────

def test_extract_keywords_strips_domain_filler(hpm):
    kw = hpm._extract_keywords("Premium skincare serum product shot on marble")
    assert set(kw.split()) == {"product", "skincare", "marble", "serum", "shot"}

def test_extract_keywords_prioritizes_design_terms(hpm):
    kw = hpm._extract_keywords(
        "redesign my personal brand landing page with hero area")
    words = kw.split()
    assert len(words) <= 6
    assert "landing" in words and "hero" in words
    assert "personal" not in words and "brand" not in words
    assert words[0] in ("landing", "hero")  # design terms sort first

def test_extract_keywords_stopword_only_goal_is_empty(hpm):
    assert hpm._extract_keywords("create a page for the website") == ""

# ─── CATEGORY_NORMALIZE round-trips ───────────────────────────────────────

@pytest.mark.parametrize("raw,canonical", sorted(CATEGORY_NORMALIZE.items()))
def test_category_normalize_roundtrip(raw, canonical):
    assert normalize_category(raw) == canonical
    assert normalize_category(canonical) == canonical  # idempotent
    assert normalize_category(canonical.lower()) == canonical

def test_category_normalize_unknown_passthrough():
    assert normalize_category(" Weird Cat ") == "Weird Cat"

# ─── Structure detection ──────────────────────────────────────────────────

@pytest.mark.parametrize("text,expected", [
    ('{argument name="x" default="y"} poster', "Template"),
    ('{"style": "grid"}', "JSON"),
    ('{"a": "{argument x}"}', "Template-JSON"),
    ("A moody portrait of a chef", "Flat prose"),
    ("random text 123", "Other"),
])
def test_detect_structure(text, expected):
    assert detect_structure(text) == expected

# ─── _recommend_model ─────────────────────────────────────────────────────

@pytest.mark.parametrize("category,goal,expected_id", [
    ("App / Web Design", "dark analytics dashboard", "gpt_image_2"),
    ("Poster / Flyer", "music festival poster", "gpt_image_2"),
    ("Portrait / Selfie", "reference photo of the same person", "nano_banana_pro"),
    ("Profile / Avatar", "stylized avatar", "nano_banana_pro"),  # category default
    ("Landscape / Nature", "misty forest valley", "gpt_image_2"),  # global default
])
def test_recommend_model(hpm, category, goal, expected_id):
    rec = hpm._recommend_model(category, goal, "Template")
    assert rec["id"] == expected_id
    assert rec == MODELS[expected_id]
    assert {"id", "model_id", "display_name", "signal"} <= set(rec)

# ─── Scorer determinism ───────────────────────────────────────────────────

def test_generate_prompt_and_score_are_deterministic(hpm):
    kwargs = dict(goal="Masonry photo gallery with filter chips",
                  category="App / Web Design", structure="Template")
    r1 = hpm.generate_prompt(**kwargs)
    r2 = hpm.generate_prompt(**kwargs)
    assert r1["prompt"] == r2["prompt"]
    assert r1["source_prompt_ids"] == r2["source_prompt_ids"]
    assert r1["quality_score"] == r2["quality_score"]
    assert 0 <= r1["quality_score"]["total"] <= 100
    assert r1["length"] == len(r1["prompt"])

# ─── DB-path resolution ───────────────────────────────────────────────────

def test_resolve_db_path_env_missing_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("HIGGSFIELD_DB", str(tmp_path / "nope.db"))
    with pytest.raises(FileNotFoundError):
        _resolve_db_path()

def test_resolve_db_path_env_existing_wins(monkeypatch, tmp_path):
    db = tmp_path / "real.db"
    db.write_bytes(b"")
    monkeypatch.setenv("HIGGSFIELD_DB", str(db))
    assert _resolve_db_path() == db.resolve()

def test_resolve_db_path_fixture_env(hpm):
    # conftest pointed HIGGSFIELD_DB at the fixture — the session engine
    # must be reading exactly that DB.
    from db import _resolve_db_path
    assert hpm.conn.execute(
        "SELECT COUNT(*) FROM prompts WHERE has_prompt = 1").fetchone()[0] == 50

# ─── fixture sanity ───────────────────────────────────────────────────────

def test_fixture_stats(hpm):
    stats = hpm.stats()
    assert stats["total_prompts"] == 50
    assert stats["curated_prompts"] == 0
    assert set(stats["models"]) == {"GPT Image 2", "Nano Banana Pro"}

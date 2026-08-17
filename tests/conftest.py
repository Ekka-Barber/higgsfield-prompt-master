"""Pytest fixtures for the Higgsfield Prompt Master suite.

Builds a ~50-row fixture corpus DB with the same external-content FTS5
schema as the live DB and points HIGGSFIELD_DB at it at conftest import
time — BEFORE any test module imports higgsfield_prompt/db (db.py
resolves DB_PATH at import time; get_conn re-resolves per call).
"""
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

FIXTURE_DB = Path(tempfile.mkdtemp(prefix="hpm_test_")) / "fixture_prompts.db"

# Mirrors the live legacy schema (SELECT sql FROM sqlite_master): prompts
# with enrichment columns, external-content FTS5 over (prompt_text, title,
# model) keyed on id, and the pre-FK prompt_techniques table.
_DDL = """
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    prompt_text TEXT,
    categories TEXT,
    model TEXT,
    slug TEXT,
    scraped_at TEXT,
    has_prompt INTEGER DEFAULT 0,
    structure_type TEXT,
    length_chars INTEGER,
    technique_tags TEXT
);
CREATE VIRTUAL TABLE prompts_fts USING fts5(
    prompt_text, title, model,
    content='prompts', content_rowid='id'
);
CREATE TABLE prompt_techniques (
    prompt_id INTEGER,
    technique TEXT,
    PRIMARY KEY (prompt_id, technique)
);
"""

# Goal rows for the diversity gate port: each row embeds its goal phrase
# verbatim so FTS MATCH (AND over _extract_keywords terms) hits exactly
# this row — the 6 diversity goals retrieve 6 distinct donor sets.
GOAL_ROWS = [
    (101, "Personal brand hero landing page",
     "Personal brand hero landing page with portrait",
     'Personal brand hero landing page with portrait area, {argument name="tagline" default="Build your brand"} headline block and a warm neutral palette.',
     "App / Web Design"),
    (102, "Dark mode book reading section",
     "Dark mode reading UI",
     'Dark mode book reading section with amber light glow, {argument name="title" default="Chapter One"} card layout and soft contrast.',
     "App / Web Design"),
    (103, "Masonry photo gallery",
     "Masonry gallery UI",
     'Masonry photo gallery with filter chips, {argument name="chip" default="All"} pinned toolbar and lazy-load cells.',
     "App / Web Design"),
    (104, "Contact form footer",
     "Contact form footer",
     'Contact form with footer and social links, {argument name="email" default="hello@studio.com"} label fields on a cream background.',
     "App / Web Design"),
    (105, "Skincare serum on marble",
     "Product marketing shot",
     'Premium skincare serum product shot on marble pedestal, {argument name="bottle" default="amber glass"} droplets and morning window light.',
     "Product Marketing"),
    (106, "Cyberpunk portrait in neon alleyway",
     "Cyberpunk character portrait",
     'Cyberpunk character portrait in neon alleyway, {argument name="hair" default="silver undercut"} rim glow and rain-slick reflections.',
     "Portrait / Selfie"),
]

# Fillers: strict JSON / {argument} Template / "A ..." prose / Other /
# one Template-JSON hybrid. Neutral vocabulary only — no goal-keyword
# combos (FTS MATCH is AND), no contamination terms, no camera words.
_FILLER_CATEGORIES = [
    "App / Web Design", "Product Marketing", "Social Media Post", "Poster / Flyer",
    "Comic / Storyboard", "Profile / Avatar", "Game Asset", "Infographic / Edu Visual",
    "YouTube Thumbnail", "E-commerce Main Image", "Portrait / Selfie",
    "Landscape / Nature", "Architecture / Interior", "Cinematic / Film Still",
    "Abstract / Background", "Animal / Creature", "Group / Couple", "Sketch / Line Art",
]
_FILLER_TEXTS = [
    '{"canvas": "editorial magazine cover", "grid": "3-column card layout", "palette": ["ivory", "charcoal", "sage"]}',
    'A {argument name="subject" default="feature banner"} layout with {argument name="accent" default="duotone gradient"} accents and generous whitespace.',
    'A wide editorial spread with balanced whitespace, serif typography and a calm neutral palette.',
    'Bold typographic experiment: oversized numerals, high-contrast ink, torn paper edges.',
    '{"frame": "{argument name=\\"ratio\\" default=\\"4:5\\"}", "mood": "quiet luxury"}',
]


def _build_fixture() -> None:
    conn = sqlite3.connect(FIXTURE_DB)
    conn.executescript(_DDL)

    rows = []
    for pid, title, desc, text, cat in GOAL_ROWS:
        rows.append((pid, title, desc, text, cat, f"goal-{pid}"))
    for i in range(44):
        cat = _FILLER_CATEGORIES[i % len(_FILLER_CATEGORIES)]
        text = _FILLER_TEXTS[i % len(_FILLER_TEXTS)]
        rows.append((200 + i, f"Filler {i} {cat}", f"Fixture filler row {i}", text,
                     cat, f"filler-{i}"))

    for pid, title, desc, text, cat, slug in rows:
        conn.execute(
            "INSERT INTO prompts (id, title, description, prompt_text, categories,"
            " model, slug, scraped_at, has_prompt) VALUES (?,?,?,?,?,?,?,?,1)",
            (pid, title, desc, text, cat,
             "GPT Image 2" if pid % 2 else "Nano Banana Pro", slug, "2026-01-01 00:00:00"))
    conn.commit()
    conn.close()

    # HIGGSFIELD_DB must be set before importing db (import-time DB_PATH).
    os.environ["HIGGSFIELD_DB"] = str(FIXTURE_DB)
    from db import detect_structure, detect_techniques

    conn = sqlite3.connect(FIXTURE_DB)
    conn.row_factory = sqlite3.Row
    for row in conn.execute("SELECT id, prompt_text FROM prompts").fetchall():
        conn.execute(
            "UPDATE prompts SET structure_type=?, length_chars=?, technique_tags=? WHERE id=?",
            (detect_structure(row["prompt_text"]), len(row["prompt_text"]),
             json.dumps(detect_techniques(row["prompt_text"])), row["id"]))
        for tech in detect_techniques(row["prompt_text"]):
            conn.execute("INSERT OR IGNORE INTO prompt_techniques VALUES (?,?)",
                         (row["id"], tech))
    conn.execute("INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()


_build_fixture()


@pytest.fixture(scope="session")
def hpm():
    from higgsfield_prompt import HiggsfieldPromptMaster
    return HiggsfieldPromptMaster()

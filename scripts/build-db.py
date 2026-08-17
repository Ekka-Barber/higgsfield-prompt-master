#!/usr/bin/env python3
"""Reproducible build: rebuild the corpus DB from the scraped JSONL export.

Pipeline: create schema -> ingest JSONL -> enrich -> FTS rebuild -> VACUUM
-> checksum report (DB sha256 + deterministic content digest) with a
stats-parity gate (row ids, category/model/structure counts vs the JSONL).

Modes:
  --export            dump the live DB to the JSONL export (the Releases
                      artifact; gitignored — Releases stay the distribution
                      channel for the 55 MB DB and the JSONL)
  (default)           build a fresh DB from the JSONL into a temp path
                      (live DB untouched) and verify it
  --apply             after verification passes, replace the live DB with the
                      rebuild (previous live copy kept as *.db.bak)
  --jsonl PATH        export destination / build source (default
                      references/gpt-image2-prompts.jsonl)
"""
import hashlib
import importlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 crashes on report symbols

import higgsfield_prompt as hp
from db import detect_structure, normalize_category

REPO = Path(__file__).parent.parent
DEFAULT_JSONL = REPO / "references" / "gpt-image2-prompts.jsonl"

# Raw scrape columns only — enrichment (structure_type, length_chars,
# technique_tags) is re-derived by the enrich step, never imported.
RAW_COLS = ("id", "title", "description", "prompt_text", "categories",
            "model", "slug", "scraped_at", "has_prompt")

SCHEMA = """
CREATE TABLE prompts (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    prompt_text TEXT,
    categories TEXT,
    model TEXT,
    slug TEXT,
    scraped_at TEXT,
    has_prompt INTEGER DEFAULT 0
);
CREATE VIRTUAL TABLE prompts_fts USING fts5(
    prompt_text, title, model,
    content='prompts', content_rowid='id'
);
"""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def export(live, out_path):
    conn = sqlite3.connect(live)
    n = 0
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for row in conn.execute(
                f"SELECT {','.join(RAW_COLS)} FROM prompts ORDER BY id"):
            f.write(json.dumps(dict(zip(RAW_COLS, row)),
                               ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
    conn.close()
    print(f"exported {n} rows -> {out_path}")
    print(f"jsonl sha256: {sha256_file(out_path)}")


def load_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            cats = r.get("categories") or ""
            if isinstance(cats, list):  # scraper emits a list; DB stores pipes
                cats = "|".join(str(c).strip() for c in cats if str(c).strip())
            rows.append({"id": r["id"], "title": r.get("title") or "",
                         "description": r.get("description") or "",
                         "prompt_text": r.get("prompt_text") or "",
                         "categories": cats, "model": r.get("model") or "",
                         "slug": r.get("slug") or "",
                         "scraped_at": r.get("scraped_at") or "",
                         "has_prompt": int(r.get("has_prompt") or 0)})
    return rows


def row_stats(rows):
    """Category / model / structure counters over raw rows (the rebuild gate)."""
    cat, model, structure = Counter(), Counter(), Counter()
    for r in rows:
        model[r["model"]] += 1
        structure[detect_structure(r["prompt_text"])] += 1
        for c in r["categories"].split("|"):
            if c.strip():
                cat[normalize_category(c)] += 1
    return cat, model, structure


def db_row_stats(conn):
    cat, model, structure = Counter(), Counter(), Counter()
    for title, text, cats, m, st in conn.execute(
            "SELECT title, prompt_text, categories, model, structure_type FROM prompts"):
        model[m] += 1
        structure[st] += 1
        for c in (cats or "").split("|"):
            if c.strip():
                cat[normalize_category(c)] += 1
    return cat, model, structure


def content_digest(rows):
    """Deterministic digest over the raw corpus (stable across rebuilds even
    though SQLite file bytes are not)."""
    h = hashlib.sha256()
    for r in sorted(rows, key=lambda r: r["id"]):
        h.update(json.dumps([r[c] for c in RAW_COLS],
                            ensure_ascii=False).encode("utf-8"))
    return h.hexdigest()


def fmt(counter, top=5):
    items = ", ".join(f"{k}: {v:,}" for k, v in counter.most_common(top))
    extra = f" (+{len(counter) - top} more)" if len(counter) > top else ""
    return f"{len(counter)} distinct [{items}{extra}]"


def build(rows, out):
    if out.exists():
        out.unlink()
    conn = sqlite3.connect(out)
    conn.executescript(SCHEMA)
    conn.executemany(
        f"INSERT INTO prompts ({','.join(RAW_COLS)}) VALUES ({','.join('?' * len(RAW_COLS))})",
        [tuple(r[c] for c in RAW_COLS) for r in rows])
    conn.commit()

    # Enrich via the library itself (adds structure/length/technique columns
    # + prompt_techniques). get_conn re-resolves HIGGSFIELD_DB per call, so a
    # module reload repoints the engine at the fresh DB.
    os.environ["HIGGSFIELD_DB"] = str(out.resolve())
    eng = importlib.reload(hp).HiggsfieldPromptMaster()
    eng.enrich_all()
    eng.conn.close()

    conn.execute("INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')")
    conn.commit()
    conn.execute("VACUUM")
    conn.close()


def verify(rows, out, jsonl):
    # Fetch everything, close, THEN assert — a raised assert must not leak the
    # connection (Windows keeps the file locked while any handle is open).
    conn = sqlite3.connect(out)
    ids_db = [r[0] for r in conn.execute("SELECT id FROM prompts ORDER BY id")]
    db_rows = [dict(zip(RAW_COLS, r)) for r in conn.execute(
        f"SELECT {','.join(RAW_COLS)} FROM prompts")]
    fts_n = conn.execute("SELECT COUNT(*) FROM prompts_fts").fetchone()[0]
    unenriched = conn.execute(
        "SELECT COUNT(*) FROM prompts WHERE structure_type IS NULL").fetchone()[0]
    db_counts = db_row_stats(conn)
    conn.close()

    ids_jsonl = sorted(r["id"] for r in rows)
    assert ids_db == ids_jsonl, (
        f"id mismatch: {len(ids_db)} DB ids vs {len(ids_jsonl)} JSONL ids "
        f"(missing {sorted(set(ids_jsonl) - set(ids_db))[:5]})")

    # Raw-column round-trip: DB content digest must equal the JSONL digest.
    assert content_digest(db_rows) == content_digest(rows), "content digest mismatch"

    assert fts_n == len(rows), f"FTS rows {fts_n} != {len(rows)} prompts"
    assert unenriched == 0, f"{unenriched} rows left unenriched"

    for name, got, want in zip(("categories", "models", "structures"),
                               db_counts, row_stats(rows)):
        assert got == want, f"{name} mismatch: {got} != {want}"

    print(f"rows: {len(rows):,}  (ids match, content digest match, FTS parity, 0 unenriched)")
    print(f"categories: {fmt(row_stats(rows)[0])}")
    print(f"models:     {fmt(row_stats(rows)[1])}")
    print(f"structures: {fmt(row_stats(rows)[2])}")
    print(f"db sha256:    {sha256_file(out)}")
    print(f"jsonl sha256: {sha256_file(jsonl)}")
    print(f"content digest (rows, deterministic): {content_digest(rows)}")


def main():
    global hp
    args = sys.argv[1:]
    jsonl = Path(next((a.split("=", 1)[1] for a in args if a.startswith("--jsonl=")), DEFAULT_JSONL))
    live = hp._resolve_db_path()

    if "--export" in args:
        export(live, jsonl)
        return

    if not jsonl.exists():
        sys.exit(f"error: {jsonl} not found — run 'python scripts/build-db.py --export' "
                 f"first, or download the JSONL from Releases")
    rows = load_jsonl(jsonl)
    print(f"building from {jsonl} ({len(rows):,} rows)")

    out = Path(tempfile.gettempdir()) / "higgsfield-built.db"
    build(rows, out)
    verify(rows, out, jsonl)

    # The rebuilt DB must load through the engine like the shipped one.
    stats = hp.HiggsfieldPromptMaster().stats()
    print(f"engine stats() on rebuild: total_prompts={stats['total_prompts']:,}")

    if "--apply" in args:
        bak = live.with_suffix(".db.bak")
        shutil.copy2(live, bak)
        shutil.copy2(out, live)
        print(f"--apply: live DB replaced ({live}); previous copy kept at {bak}")
    else:
        print(f"copy-safe mode: rebuild at {out} (live DB {live} untouched)")
        print(f"use it via HIGGSFIELD_DB={out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Refresh pipeline: ingest newly published prompts without heroics.

Pipeline: re-probe the id range past the watermark -> scrape new ids to JSONL
(via scripts/rsc-prompt-extractor.py) -> ingest guards (boilerplate /
non-English / unknown model) -> idempotent upsert into prompts -> scrape_log
written -> scoped enrichment + FTS rebuild -> diff summary.

Watermark = max(prompt-id-map.json range end, DB max id) — the DB is the live
truth, the map is the historical scrape artifact (its range end, 26,926, is
already behind the corpus max id, 28,686).

Default (dry-run): every DB change runs on a temp copy addressed via
HIGGSFIELD_DB; the live DB is untouched. --apply writes to the live DB. The
scraped-JSONL artifact is always written (it is the scrape record, not a DB
change).

Usage:
  python scripts/refresh.py                     # probe watermark+1 .. +200 on a copy
  python scripts/refresh.py --probe-end 30000   # widen the probe window
  python scripts/refresh.py --apply             # write to the LIVE DB
  python scripts/refresh.py --jsonl PATH        # artifact location
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 crashes on report symbols

import db  # get_conn, detect_structure, detect_techniques
from langcheck import is_english

REPO = Path(__file__).parent.parent
ID_MAP = REPO / "references" / "prompt-id-map.json"
EXTRACTOR = REPO / "scripts" / "rsc-prompt-extractor.py"
DEFAULT_WINDOW = 200

RAW_COLS = ("id", "title", "description", "prompt_text", "categories",
            "model", "slug", "scraped_at", "has_prompt")

# Guards applied at ingest, in order. Share-widget boilerplate pattern matches
# scripts/purge_boilerplate.py; language guard is the shared langcheck filter;
# model guard rejects pages the extractor could not attribute (US-020
# quarantined the 4 historical model='' rows as missing_model).
BOILERPLATE_PREFIX = "Just found a great AI prompt"
KNOWN_MODELS = {"GPT Image 2", "Nano Banana", "Seedream", "Flux"}

_MISS_RE = re.compile(r"^\[(\d+)\] no content", re.M)


def run_scraper(start, end):
    """Probe/scrape [start, end] via the RSC extractor subprocess.
    Returns (jsonl_lines, miss_ids) — stdout JSONL rows plus the ids the
    extractor reported as no-content on stderr. Split on '\n' only: corpus
    text contains \u2028 which str.splitlines() would treat as a break."""
    r = subprocess.run(
        [sys.executable, str(EXTRACTOR), "--start", str(start), "--end", str(end)],
        capture_output=True, text=True, timeout=(end - start + 1) * 20 + 120,
    )
    lines = [l for l in r.stdout.split("\n") if l.strip()]
    misses = [int(m) for m in _MISS_RE.findall(r.stderr)]
    return lines, misses


def normalize(raw):
    """Scraper JSON dict -> raw-column dict (categories list -> pipe form)."""
    cats = raw.get("categories") or ""
    if isinstance(cats, list):
        cats = "|".join(str(c).strip() for c in cats if str(c).strip())
    return {"id": int(raw["id"]), "title": raw.get("title") or "",
            "description": raw.get("description") or "",
            "prompt_text": raw.get("prompt_text") or "",
            "categories": cats, "model": raw.get("model") or "",
            "slug": raw.get("slug") or "",
            "scraped_at": raw.get("scraped_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "has_prompt": 1}


def guard(row):
    """Ingest guard: return None if the row passes, else the scrape_log status."""
    if row["prompt_text"].startswith(BOILERPLATE_PREFIX):
        return "boilerplate"
    if not row["prompt_text"] or not is_english(row["prompt_text"]):
        return "non_english"
    if row["model"] not in KNOWN_MODELS:
        return "bad_model"
    return None


def searchable_where(conn):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(prompts)")]
    return "status IN ('curated','harvested')" if "status" in cols else "has_prompt = 1"


def _log(conn, pid, status, error=""):
    conn.execute(
        "INSERT INTO scrape_log (id, status, error, timestamp) VALUES (?,?,?,?)"
        " ON CONFLICT(id) DO UPDATE SET status=excluded.status,"
        " error=excluded.error, timestamp=excluded.timestamp",
        (pid, status, error, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def refresh_db(target, raw_rows, misses):
    """Guards -> idempotent upsert -> scoped enrichment -> FTS rebuild on the
    DB at `target` (via HIGGSFIELD_DB + db.get_conn). Returns the diff summary.
    Idempotent: same input on an already-refreshed DB changes nothing."""
    os.environ["HIGGSFIELD_DB"] = str(Path(target).resolve())
    conn = db.get_conn(readonly=False)
    # Fresh rebuilds (scripts/build-db.py) don't carry the original scrape_log.
    conn.execute("CREATE TABLE IF NOT EXISTS scrape_log ("
                 "id INTEGER PRIMARY KEY, status TEXT, error TEXT, timestamp TEXT)")
    where = searchable_where(conn)
    has_status = "status" in [r[1] for r in conn.execute("PRAGMA table_info(prompts)")]

    total_before, searchable_before = conn.execute(
        f"SELECT COUNT(*), (SELECT COUNT(*) FROM prompts WHERE {where})"
        " FROM prompts").fetchone()
    max_id_before = conn.execute("SELECT MAX(id) FROM prompts").fetchone()[0] or 0

    summary = {"total_before": total_before, "searchable_before": searchable_before,
               "max_id_before": max_id_before, "scraped": len(raw_rows),
               "no_content": len(misses), "inserted": 0, "updated": 0, "changed": 0,
               "skipped": {"boilerplate": 0, "non_english": 0, "bad_model": 0}}

    existing = {}
    if raw_rows:
        existing = {r[0]: tuple(r) for r in conn.execute(
            "SELECT id, title, description, prompt_text, categories, model FROM prompts"
            " WHERE id IN (%s)" % ",".join("?" * len(raw_rows)),
            [r["id"] for r in raw_rows])}

    for raw in raw_rows:
        row = normalize(raw)
        verdict = guard(row)
        if verdict:
            summary["skipped"][verdict] += 1
            _log(conn, row["id"], verdict, "ingest guard")
            continue
        if row["id"] in existing:
            summary["updated"] += 1
            if any(existing[row["id"]][i + 1] != row[c] for i, c in enumerate(
                    ("title", "description", "prompt_text", "categories", "model"))):
                summary["changed"] += 1
        else:
            summary["inserted"] += 1
        # Post-migration, visibility is driven by `status`, not has_prompt (see
        # _searchable_clause). Inserting without it would leave every newly
        # scraped prompt NULL-status and therefore invisible to search -- the
        # same class of bug as the 1,276 rows the status migration just fixed.
        if has_status:
            conn.execute(
                "INSERT INTO prompts (id,title,description,prompt_text,categories,"
                "model,slug,scraped_at,has_prompt,status)"
                " VALUES (?,?,?,?,?,?,?,?,?,'curated')"
                " ON CONFLICT(id) DO UPDATE SET title=excluded.title,"
                " description=excluded.description, prompt_text=excluded.prompt_text,"
                " categories=excluded.categories, model=excluded.model,"
                " scraped_at=excluded.scraped_at,"
                " status=COALESCE(prompts.status, 'curated')",
                tuple(row[c] for c in RAW_COLS))
        else:
            conn.execute(
                "INSERT INTO prompts (id,title,description,prompt_text,categories,model,"
                "slug,scraped_at,has_prompt) VALUES (?,?,?,?,?,?,?,?,?)"
                " ON CONFLICT(id) DO UPDATE SET title=excluded.title,"
                " description=excluded.description, prompt_text=excluded.prompt_text,"
                " categories=excluded.categories, model=excluded.model,"
                " scraped_at=excluded.scraped_at",
                tuple(row[c] for c in RAW_COLS))
        # Scoped enrichment: only the touched id (never a corpus-wide sweep —
        # the live DB still carries 1,276 deliberately-unenriched rows).
        conn.execute("UPDATE prompts SET structure_type=?, length_chars=?, technique_tags=?"
                     " WHERE id=?",
                     (db.detect_structure(row["prompt_text"]), len(row["prompt_text"]),
                      json.dumps(db.detect_techniques(row["prompt_text"])), row["id"]))
        for tech in db.detect_techniques(row["prompt_text"]):
            conn.execute("INSERT OR IGNORE INTO prompt_techniques (prompt_id, technique)"
                         " VALUES (?,?)", (row["id"], tech))
        _log(conn, row["id"], "ok")

    for pid in misses:
        _log(conn, pid, "ok_no_text")

    conn.execute("INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')")
    conn.commit()

    total_after, searchable_after = conn.execute(
        f"SELECT COUNT(*), (SELECT COUNT(*) FROM prompts WHERE {where})"
        " FROM prompts").fetchone()
    fts_n = conn.execute("SELECT COUNT(*) FROM prompts_fts").fetchone()[0]
    conn.close()

    assert fts_n == total_after, f"FTS rows {fts_n} != {total_after} prompts"
    summary.update({"total_after": total_after, "searchable_after": searchable_after})
    summary["max_id_after"] = max(max_id_before,
                                  max((r["id"] for r in raw_rows), default=0))
    return summary


def report(s):
    print(f"before: total={s['total_before']:,} searchable={s['searchable_before']:,}"
          f" max_id={s['max_id_before']:,}")
    print(f"scraped: {s['scraped']} rows ({s['no_content']} no-content ids)")
    print(f"upsert:  {s['inserted']} inserted, {s['updated']} re-scraped"
          f" ({s['changed']} with changed content)")
    sk = s["skipped"]
    print(f"guards:  skipped {sum(sk.values())}"
          f" (boilerplate={sk['boilerplate']}, non_english={sk['non_english']},"
          f" bad_model={sk['bad_model']})")
    print(f"after:  total={s['total_after']:,} searchable={s['searchable_after']:,}"
          f" max_id={s['max_id_after']:,}  (FTS parity OK)")


def main():
    args = sys.argv[1:]
    apply_mode = "--apply" in args

    def argval(flag, default=None, cast=int):
        for i, a in enumerate(args):
            if a == flag and i + 1 < len(args):
                return cast(args[i + 1])
            if a.startswith(flag + "="):
                return cast(a.split("=", 1)[1])
        return default

    live = db._resolve_db_path()
    map_end = json.loads(ID_MAP.read_text(encoding="utf-8"))["range"][1]
    ro = db.get_conn()
    db_max = ro.execute("SELECT MAX(id) FROM prompts").fetchone()[0]
    ro.close()
    watermark = max(map_end, db_max)
    probe_end = argval("--probe-end", watermark + DEFAULT_WINDOW)
    jsonl = Path(argval("--jsonl", str(
        REPO / "references" / f"refresh-{watermark + 1}-{probe_end}.jsonl"), str))

    print(f"watermark: prompt-id-map.json range end={map_end:,}, DB max id={db_max:,}"
          f" -> probing {watermark + 1:,}..{probe_end:,}")
    if probe_end <= watermark:
        print("nothing to probe (probe end <= watermark)")
        return

    lines, misses = run_scraper(watermark + 1, probe_end)
    jsonl.parent.mkdir(parents=True, exist_ok=True)
    jsonl.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    raw_rows = [json.loads(l) for l in lines]
    print(f"scraped {len(raw_rows)} rows, {len(misses)} no-content ids -> {jsonl}")

    if apply_mode:
        target = live
        print(f"--apply: refreshing LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-refresh-copy.db"
        shutil.copy2(live, target)
        print(f"copy-safe mode: refreshing temp copy {target}")
        print(f"(live DB {live} untouched; inspect copy with HIGGSFIELD_DB={target})")

    summary = refresh_db(target, raw_rows, misses)
    report(summary)
    print("OK")


if __name__ == "__main__":
    main()

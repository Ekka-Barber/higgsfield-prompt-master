#!/usr/bin/env python3
"""Migrate has_prompt -> status (curated/harvested/excluded + excluded_reason)
and normalize categories to canonical pipe-separated form.

Mapping: has_prompt=1 -> 'curated', has_prompt=0 (all text-bearing) -> 'harvested'.
'excluded' is reserved for rows dropped by scripts/purge_boilerplate.py
(excluded_reason: 'boilerplate' / 'exact_duplicate'); none exist in this DB yet.
has_prompt column is kept for backwards compatibility (enrich_all, purge script).

Default: copy-safe — operates on a temp copy of the DB (point HIGGSFIELD_DB at
the printed copy path to use it). Use --apply to modify the live DB.
Idempotent: re-running is a no-op.
"""
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import _resolve_db_path, normalize_category


def canonical_categories(raw):
    """'["A", "B"]' or 'A|B' or 'A' -> 'Canonical A|Canonical B'."""
    if raw is None:
        return ""
    s = raw.strip()
    if not s:
        return ""
    if s.startswith("["):
        try:
            parts = json.loads(s)
        except ValueError:
            parts = [p.strip().strip('"') for p in s.strip("[]").split(",")]
    else:
        parts = s.split("|")
    return "|".join(normalize_category(p) for p in parts if p and p.strip())


def report(conn, label):
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    hp = dict(cur.execute("SELECT has_prompt, COUNT(*) FROM prompts GROUP BY has_prompt").fetchall())
    searchable = cur.execute("SELECT COUNT(*) FROM prompts WHERE has_prompt = 1").fetchone()[0]
    line = (f"{label}: total={total} has_prompt(1/0)={hp.get(1, 0)}/{hp.get(0, 0)} "
            f"searchable(has_prompt=1)={searchable}")
    cols = [r[1] for r in cur.execute("PRAGMA table_info(prompts)").fetchall()]
    if "status" in cols:
        st = dict(cur.execute("SELECT status, COUNT(*) FROM prompts GROUP BY status").fetchall())
        searchable2 = cur.execute(
            "SELECT COUNT(*) FROM prompts WHERE status IN ('curated','harvested')").fetchone()[0]
        line += (f" status(curated/harvested/excluded)={st.get('curated', 0)}/{st.get('harvested', 0)}"
                 f"/{st.get('excluded', 0)} searchable(status)={searchable2}")
    json_wrapped = cur.execute("SELECT COUNT(*) FROM prompts WHERE categories LIKE '[%'").fetchone()[0]
    print(line)
    print(f"{' ' * len(label)}  categories: json-wrapped={json_wrapped}")
    return {"json_wrapped": json_wrapped}


def migrate(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    report(conn, "before")

    cols = [r[1] for r in cur.execute("PRAGMA table_info(prompts)").fetchall()]
    if "status" not in cols:
        cur.execute("ALTER TABLE prompts ADD COLUMN status TEXT")
    if "excluded_reason" not in cols:
        cur.execute("ALTER TABLE prompts ADD COLUMN excluded_reason TEXT")

    cur.execute("UPDATE prompts SET status='harvested' WHERE has_prompt=0")
    n_harvested = cur.rowcount
    cur.execute("UPDATE prompts SET status='curated' WHERE has_prompt=1")
    n_curated = cur.rowcount

    n_json = n_norm = 0
    samples = []
    for pid, raw in cur.execute("SELECT id, categories FROM prompts").fetchall():
        new = canonical_categories(raw)
        if new != (raw or ""):
            if (raw or "").strip().startswith("["):
                n_json += 1
            else:
                n_norm += 1
            if len(samples) < 3:
                samples.append((pid, raw, new))
            cur.execute("UPDATE prompts SET categories=? WHERE id=?", (new, pid))
    conn.commit()

    after = report(conn, "after ")
    st = dict(cur.execute("SELECT status, COUNT(*) FROM prompts GROUP BY status").fetchall())
    harvested_text = cur.execute(
        "SELECT COUNT(*) FROM prompts WHERE status='harvested'"
        " AND prompt_text IS NOT NULL AND TRIM(prompt_text) != ''").fetchone()[0]

    print(f"migrated: curated={n_curated} harvested={n_harvested}; "
          f"categories: json-stripped={n_json} normalized={n_norm}")
    for pid, old, new in samples:
        print(f"  sample: {pid} {old!r} -> {new!r}")

    assert after["json_wrapped"] == 0, "JSON-array categories remain"
    assert st.get("harvested", 0) == 1276 and harvested_text == 1276, \
        f"expected 1,276 text-bearing harvested rows, got {harvested_text}"
    assert st.get("curated", 0) + st.get("harvested", 0) + st.get("excluded", 0) == \
        cur.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    conn.close()


def main():
    live = _resolve_db_path()
    if "--apply" in sys.argv:
        target = live
        print(f"--apply: migrating LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-migrated-copy.db"
        shutil.copy2(live, target)
        print(f"Copy-safe mode: migrating temp copy {target}")
        print(f"(live DB {live} untouched; use the copy via HIGGSFIELD_DB={target})")
    migrate(target)
    print("OK")


if __name__ == "__main__":
    main()

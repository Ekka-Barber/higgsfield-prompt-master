#!/usr/bin/env python3
"""Purge share-widget boilerplate + exact-dup pairs from the prompt corpus.

Default: copy-safe — operates on a temp copy of the DB (inspect it afterwards
by setting HIGGSFIELD_DB=<printed copy path>).
Use --apply to modify the live DB. Idempotent: re-running is a no-op.
"""
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import _resolve_db_path

BOILERPLATE_LIKE = "Just found a great AI prompt%"


def counts(conn):
    cur = conn.execute(
        "SELECT (SELECT COUNT(*) FROM prompts),"
        " (SELECT COUNT(*) FROM prompts WHERE has_prompt=1),"
        " (SELECT COUNT(*) FROM prompts WHERE prompt_text LIKE ?)", (BOILERPLATE_LIKE,))
    total, curated, boiler = cur.fetchone()
    cur = conn.execute(
        "SELECT COALESCE(SUM(c - 1), 0) FROM"
        " (SELECT COUNT(*) c FROM prompts WHERE has_prompt=1"
        "  AND prompt_text NOT LIKE ? GROUP BY prompt_text HAVING c > 1)",
        (BOILERPLATE_LIKE,))
    return {"total": total, "curated": curated, "boilerplate": boiler,
            "dup_extras": cur.fetchone()[0]}


def purge(db_path):
    conn = sqlite3.connect(db_path)
    before = counts(conn)
    cur = conn.cursor()
    cur.execute("SELECT id FROM prompts WHERE prompt_text LIKE ?", (BOILERPLATE_LIKE,))
    purged_ids = [r[0] for r in cur.fetchall()]
    # exact dups among curated, excluding boilerplate: keep MIN(id) per text
    cur.execute(
        "SELECT p.id FROM prompts p JOIN"
        " (SELECT prompt_text, MIN(id) keep_id FROM prompts WHERE has_prompt=1"
        "  AND prompt_text NOT LIKE ? GROUP BY prompt_text HAVING COUNT(*) > 1) d"
        " ON p.prompt_text = d.prompt_text AND p.id != d.keep_id"
        " WHERE p.has_prompt=1", (BOILERPLATE_LIKE,))
    dup_ids = [r[0] for r in cur.fetchall()]
    gone = purged_ids + dup_ids
    if gone:
        cur.executemany("DELETE FROM prompts WHERE id = ?", [(i,) for i in gone])
        cur.executemany("DELETE FROM prompt_techniques WHERE prompt_id = ?",
                        [(i,) for i in gone])
        cur.execute("INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')")
        conn.commit()
    after = counts(conn)
    conn.close()
    return before, after, len(purged_ids), len(dup_ids)


def main():
    live = _resolve_db_path()
    if "--apply" in sys.argv:
        target = live
        print(f"--apply: purging LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-purge-copy.db"
        shutil.copy2(live, target)
        print(f"Copy-safe mode: purging temp copy {target}")
        print(f"(live DB {live} untouched; inspect copy with HIGGSFIELD_DB={target})")
    before, after, n_purged, n_dups = purge(target)
    print(f"before: total={before['total']} curated={before['curated']} "
          f"boilerplate={before['boilerplate']} dup-extras={before['dup_extras']}")
    print(f"deleted {n_purged} boilerplate rows, {n_dups} exact-dup rows")
    print(f"after:  total={after['total']} curated={after['curated']} "
          f"boilerplate={after['boilerplate']} dup-extras={after['dup_extras']}")
    assert after["boilerplate"] == 0 and after["dup_extras"] == 0
    print("OK")


if __name__ == "__main__":
    main()

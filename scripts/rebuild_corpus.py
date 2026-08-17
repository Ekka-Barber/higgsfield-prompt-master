#!/usr/bin/env python3
"""Corpus repair B: re-enrich all rows (NULL structure_type/technique_tags,
regardless of status/has_prompt), rebuild FTS, VACUUM.

Default: copy-safe — operates on a temp copy of the DB (point HIGGSFIELD_DB at
the printed copy path to use it). Use --apply to modify the live DB.
"""
import importlib
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import higgsfield_prompt as hp


def main():
    global hp
    live = hp._resolve_db_path()
    if "--apply" in sys.argv:
        target = live
        print(f"--apply: rebuilding LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-rebuilt-copy.db"
        shutil.copy2(live, target)
        print(f"Copy-safe mode: rebuilding temp copy {target}")
        print(f"(live DB {live} untouched; use the copy via HIGGSFIELD_DB={target})")

    # DB_PATH resolves at import time -> reload with env var pointing at target
    os.environ["HIGGSFIELD_DB"] = str(target.resolve())
    hp = importlib.reload(hp)

    m = hp.HiggsfieldPromptMaster()
    before = m.stats()
    size_before = target.stat().st_size

    m.enrich_all()
    m.conn.close()

    conn = sqlite3.connect(target)
    rows = conn.execute(
        "SELECT COUNT(*) FROM prompts WHERE structure_type IS NOT NULL AND technique_tags IS NOT NULL"
    ).fetchone()[0]
    conn.execute("INSERT INTO prompts_fts(prompts_fts) VALUES('rebuild')")
    conn.commit()
    conn.execute("VACUUM")
    conn.close()

    after = hp.HiggsfieldPromptMaster().stats()
    size_after = target.stat().st_size
    total_rows = hp.HiggsfieldPromptMaster().conn.execute(
        "SELECT COUNT(*) FROM prompts").fetchone()[0]

    print(f"total_prompts (searchable): {before['total_prompts']} -> {after['total_prompts']}")
    print(f"enriched rows (structure+tags set): {rows}/{total_rows}")
    print(f"DB size: {size_before:,} -> {size_after:,} bytes "
          f"({size_before - size_after:,} bytes freed, "
          f"{100 * (size_before - size_after) / max(size_before, 1):.1f}% reduction)")

    assert rows == total_rows, f"{total_rows - rows} rows left unenriched"
    print("OK")


if __name__ == "__main__":
    main()

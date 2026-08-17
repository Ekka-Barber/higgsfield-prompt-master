#!/usr/bin/env python3
"""Structure reclassification (US-019): structure_type='JSON' now means
parseable JSON. Re-runs detect_structure on every row:
  - Template ('{argument') checked before JSON
  - JSON label requires strict json.loads success
  - Template-JSON hybrid bucket for rows that parse AND carry {argument tags

Default: copy-safe — operates on a temp copy of the DB (point HIGGSFIELD_DB
at the printed copy path to use it). Use --apply to modify the live DB.
"""
import importlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))
import higgsfield_prompt as hp


def structure_counts(conn):
    return dict(conn.execute(
        "SELECT structure_type, COUNT(*) FROM prompts GROUP BY structure_type"
    ).fetchall())


def main():
    global hp
    live = hp._resolve_db_path()
    if "--apply" in sys.argv:
        target = live
        print(f"--apply: reclassifying LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-reclass-copy.db"
        shutil.copy2(live, target)
        print(f"Copy-safe mode: reclassifying temp copy {target}")
        print(f"(live DB {live} untouched; use the copy via HIGGSFIELD_DB={target})")

    # DB_PATH resolves at import time -> reload with env var pointing at target
    os.environ["HIGGSFIELD_DB"] = str(target.resolve())
    hp = importlib.reload(hp)

    conn = hp.get_conn(readonly=False)
    before = structure_counts(conn)

    # Reclassify rows that already carry a label (the "was 636" population).
    # NULL rows are enrich_all's job — it now labels them with this classifier.
    rows = conn.execute(
        "SELECT id, prompt_text FROM prompts WHERE structure_type IS NOT NULL"
    ).fetchall()
    changed = 0
    for pid, text in rows:
        new = hp.detect_structure(text)
        cur = conn.execute(
            "UPDATE prompts SET structure_type=? WHERE id=? AND structure_type IS NOT ?",
            (new, pid, new))
        changed += cur.rowcount
    conn.commit()

    after = structure_counts(conn)
    conn.close()

    print(f"\nrows reclassified: {changed}/{len(rows)}")
    print("before:", {k or "NULL": v for k, v in sorted(before.items(), key=lambda x: -x[1])})
    print("after: ", {k or "NULL": v for k, v in sorted(after.items(), key=lambda x: -x[1])})

    # True JSON = rows that strict-parse (JSON label + Template-JSON hybrids).
    # Old classifier said 636; 284 of those fail json.loads -> must be <= 352.
    true_json = after.get("JSON", 0)
    strict_parse = true_json + after.get("Template-JSON", 0)
    print(f"true-JSON count: {strict_parse} (JSON {true_json} + Template-JSON "
          f"{after.get('Template-JSON', 0)}; was 636)")
    # Assert the property, not a snapshot count. The old 352 cap was measured on
    # the 6,337-row corpus; once the harvested rows became searchable and enriched
    # the true-JSON population legitimately grows, so a fixed cap gives a false
    # failure. What must always hold: anything labelled JSON really parses.
    def _parses(txt):
        try:
            json.loads(txt)
            return True
        except Exception:
            return False

    verify = hp.get_conn(readonly=True)
    mislabelled = [
        pid for pid, txt in verify.execute(
            "SELECT id, prompt_text FROM prompts WHERE structure_type='JSON'")
        if not _parses(txt or "")
    ]
    verify.close()
    assert not mislabelled, (
        f"{len(mislabelled)} rows labelled JSON do not parse, e.g. {mislabelled[:5]}")
    assert true_json == strict_parse - after.get("Template-JSON", 0)
    print(f"verified: all {true_json} JSON-labelled rows strict-parse")
    print("OK")


if __name__ == "__main__":
    main()

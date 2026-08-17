#!/usr/bin/env python3
"""Versioned schema migrations (PRAGMA user_version) for the prompt corpus DB.

Default: copy-safe — operates on a temp copy of the DB (point HIGGSFIELD_DB at
the printed copy path to use it). Use --apply to modify the live DB.
Idempotent: steps below the DB's current user_version are skipped.

Migration steps (each atomic, each bumps user_version):
  1  status migration: add status/excluded_reason, has_prompt -> curated/harvested
  2  hygiene: delete orphan prompt_techniques rows, quarantine model='' rows
     (status='excluded', excluded_reason='missing_model'), add db_meta table
     with the enrichment-coverage marker
  3  rebuild prompt_techniques with FK -> prompts(id) ON DELETE CASCADE
  4  drop legacy columns: structure, techniques, inferred_category, complexity
  5  indexes: (status, structure_type) and (model)

Run `python scripts/migrate_schema.py --status` to only print the current
version and what would run.
"""
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import _resolve_db_path

SCHEMA_VERSION = 5
LEGACY_COLUMNS = ("structure", "techniques", "inferred_category", "complexity")


def _cols(cur):
    return [r[1] for r in cur.execute("PRAGMA table_info(prompts)").fetchall()]


def _table(cur, name):
    return cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _v1_status(cur):
    cols = _cols(cur)
    if "status" not in cols:
        cur.execute("ALTER TABLE prompts ADD COLUMN status TEXT")
    if "excluded_reason" not in cols:
        cur.execute("ALTER TABLE prompts ADD COLUMN excluded_reason TEXT")
    cur.execute("UPDATE prompts SET status='harvested' WHERE has_prompt=0 AND status IS NULL")
    cur.execute("UPDATE prompts SET status='curated' WHERE has_prompt=1 AND status IS NULL")


def _v2_hygiene(cur):
    # Orphan technique rows (prompt_id with no parent prompt)
    cur.execute("DELETE FROM prompt_techniques WHERE prompt_id NOT IN (SELECT id FROM prompts)")
    orphans = cur.rowcount
    # model='' rows -> quarantined, kept for audit (excluded_reason='missing_model')
    cur.execute(
        "UPDATE prompts SET status='excluded', excluded_reason='missing_model'"
        " WHERE model = ''"
    )
    bad_model = cur.rowcount
    # Enrichment-coverage marker: what fraction of rows carry enrichment today
    cur.execute(
        "CREATE TABLE IF NOT EXISTS db_meta (key TEXT PRIMARY KEY, value TEXT)"
    )
    enriched = cur.execute(
        "SELECT COUNT(*) FROM prompts WHERE structure_type IS NOT NULL"
    ).fetchone()[0]
    total = cur.execute("SELECT COUNT(*) FROM prompts").fetchone()[0]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    cur.execute("INSERT OR REPLACE INTO db_meta VALUES ('enrichment_coverage', ?)",
                (f"{enriched}/{total}",))
    cur.execute("INSERT OR REPLACE INTO db_meta VALUES ('enrichment_coverage_date', ?)",
                (stamp,))
    print(f"  v2: orphans deleted={orphans}, model='' quarantined={bad_model}, "
          f"enrichment coverage={enriched}/{total} @ {stamp}")


def _v3_fk_cascade(cur):
    # Table rebuild: FK must be toggleable outside a transaction, so this step
    # manages its own PRAGMA + BEGIN/COMMIT (see _run_migration_steps).
    cur.execute("PRAGMA foreign_keys = OFF")
    cur.execute("BEGIN")
    cur.execute("""
        CREATE TABLE prompt_techniques_new (
            prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
            technique TEXT,
            PRIMARY KEY (prompt_id, technique)
        )
    """)
    cur.execute("INSERT INTO prompt_techniques_new SELECT prompt_id, technique FROM prompt_techniques")
    cur.execute("DROP TABLE prompt_techniques")
    cur.execute("ALTER TABLE prompt_techniques_new RENAME TO prompt_techniques")
    cur.execute("COMMIT")
    cur.execute("PRAGMA foreign_keys = ON")


def _v4_drop_legacy(cur):
    cols = _cols(cur)
    dropped = [c for c in LEGACY_COLUMNS if c in cols]
    for col in dropped:
        cur.execute(f"ALTER TABLE prompts DROP COLUMN {col}")
    print(f"  v4: dropped legacy columns {dropped}")


def _v5_indexes(cur):
    cur.execute("CREATE INDEX IF NOT EXISTS idx_prompts_status_structure"
                " ON prompts(status, structure_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_prompts_model ON prompts(model)")


STEPS = {1: _v1_status, 2: _v2_hygiene, 3: _v3_fk_cascade, 4: _v4_drop_legacy, 5: _v5_indexes}


def _run_migration_steps(conn):
    """Run pending steps; v3 controls its own PRAGMA/txn, so others run in
    autocommit-wrapped explicit transactions."""
    cur = conn.cursor()
    v = cur.execute("PRAGMA user_version").fetchone()[0]
    if v >= SCHEMA_VERSION:
        print(f"schema already at version {v} — nothing to do")
        return
    for version in range(v + 1, SCHEMA_VERSION + 1):
        if version == 3:
            STEPS[version](cur)  # own BEGIN/COMMIT + PRAGMA toggling
        else:
            cur.execute("BEGIN")
            STEPS[version](cur)
            cur.execute("COMMIT")
        cur.execute(f"PRAGMA user_version = {version}")
        if version != 3:
            print(f"  v{version} applied")
    print(f"user_version -> {SCHEMA_VERSION}")


def verify(conn):
    cur = conn.cursor()
    v = cur.execute("PRAGMA user_version").fetchone()[0]
    assert v == SCHEMA_VERSION, f"user_version {v} != {SCHEMA_VERSION}"
    assert cur.execute("PRAGMA foreign_key_check").fetchall() == [], "FK violations remain"
    orphans = cur.execute(
        "SELECT COUNT(*) FROM prompt_techniques"
        " WHERE prompt_id NOT IN (SELECT id FROM prompts)").fetchone()[0]
    assert orphans == 0, f"{orphans} orphan technique rows remain"
    bad = cur.execute(
        "SELECT COUNT(*) FROM prompts WHERE model='' AND status IN ('curated','harvested')"
    ).fetchone()[0]
    assert bad == 0, f"{bad} model='' rows still searchable"
    cols = _cols(cur)
    assert not (set(LEGACY_COLUMNS) & set(cols)), f"legacy columns remain: {cols}"
    idx = {r[0] for r in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
    assert "idx_prompts_status_structure" in idx and "idx_prompts_model" in idx
    fk_sql = cur.execute(
        "SELECT sql FROM sqlite_master WHERE name='prompt_techniques'").fetchone()[0]
    assert "ON DELETE CASCADE" in fk_sql, "prompt_techniques missing FK cascade"
    meta = dict(cur.execute("SELECT key, value FROM db_meta").fetchall())
    assert "enrichment_coverage" in meta, "enrichment-coverage marker missing"
    st = dict(cur.execute("SELECT status, COUNT(*) FROM prompts GROUP BY status").fetchall())
    print(f"verify OK: user_version={v}, statuses={st}, marker={meta['enrichment_coverage']}"
          f" @ {meta['enrichment_coverage_date']}")


def main():
    live = _resolve_db_path()
    if "--status" in sys.argv:
        conn = sqlite3.connect(live)
        v = conn.execute("PRAGMA user_version").fetchone()[0]
        print(f"{live}: user_version={v} (target {SCHEMA_VERSION})")
        pending = [s for s in range(v + 1, SCHEMA_VERSION + 1)] or "none"
        print(f"pending steps: {pending}")
        return
    if "--apply" in sys.argv:
        target = live
        print(f"--apply: migrating LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-schema-copy.db"
        shutil.copy2(live, target)
        print(f"Copy-safe mode: migrating temp copy {target}")
        print(f"(live DB {live} untouched; use the copy via HIGGSFIELD_DB={target})")
    # isolation_level=None: explicit BEGIN/COMMIT so v3 can toggle PRAGMA
    # foreign_keys around its table rebuild.
    conn = sqlite3.connect(target, isolation_level=None)
    _run_migration_steps(conn)
    conn.execute("PRAGMA foreign_keys = ON")
    verify(conn)
    conn.close()
    print("OK")


if __name__ == "__main__":
    main()

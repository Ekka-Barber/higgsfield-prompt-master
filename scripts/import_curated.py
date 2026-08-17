#!/usr/bin/env python3
"""US-022: import references/*.md category-guide master prompts into
curated_prompts(source, category, model, ratio, text).

Parses the numbered guide pattern — `## X1: Title` headings followed by a
fenced code block — with per-prompt `**Model:** ... **Ratio:** ...` metadata
where present (portraits.md P1-P6 style) and file-level `Model: `x`` fallback
(food.md / abstract.md style). Analysis/report .md files without numbered
master prompts are ignored by construction.

Default: copy-safe — operates on a temp copy of the DB (point HIGGSFIELD_DB
at the printed copy path to use it). Use --apply to modify the live DB.
Idempotent: INSERT OR REPLACE on the source primary key.
"""
import importlib
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))
import higgsfield_prompt as hp

REFS = Path(__file__).parent.parent / "references"
HEADING_RE = re.compile(r"^## ([A-Z]\d+):\s*(.+?)\s*$", re.M)
FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
FILE_MODEL_RE = re.compile(r"Model:\s*`(\w+)`")


def parse_guide(path: Path) -> list:
    """Return curated rows for one numbered-guide .md file."""
    text = path.read_text(encoding="utf-8")
    h1 = re.search(r"^# (.+)$", text, re.M)
    # Guide name = H1 before the " — <model>" suffix ("Portraits & Headshots")
    category = re.split(r"\s+[—–-]\s+", h1.group(1))[0] if h1 else path.stem
    fm = FILE_MODEL_RE.search(text)
    file_model = fm.group(1) if fm else None

    rows = []
    matches = list(HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        pid = m.group(1)
        seg_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        segment = text[m.start():seg_end]
        model, ratio = file_model, None
        meta = re.search(r"^\*\*Model:\*\*(.*)$", segment, re.M)
        if meta:
            line = meta.group(1)
            if "**Ratio:**" in line:
                left, right = line.split("**Ratio:**", 1)
                model = re.split(r"[·•]", left)[0].strip().strip("`").strip() or file_model
                ratio = re.split(r"[·•]", right)[0].strip() or None
            else:
                model = line.strip().strip("`") or file_model
        fence = FENCE_RE.search(segment)
        if not fence:
            print(f"  WARNING: {path.name}#{pid} has no fenced prompt block — skipped")
            continue
        rows.append({
            "source": f"{path.name}#{pid}",
            "category": category,
            "model": model or "",
            "ratio": ratio,
            "text": fence.group(1).strip(),
        })
    return rows


def import_curated(conn, rows) -> int:
    """Create table if needed and upsert rows; returns total table count."""
    conn.execute("""CREATE TABLE IF NOT EXISTS curated_prompts (
        source TEXT PRIMARY KEY,
        category TEXT,
        model TEXT,
        ratio TEXT,
        text TEXT
    )""")
    for r in rows:
        conn.execute(
            "INSERT OR REPLACE INTO curated_prompts (source, category, model, ratio, text) "
            "VALUES (?,?,?,?,?)",
            (r["source"], r["category"], r["model"], r["ratio"], r["text"]))
    conn.commit()
    return conn.execute("SELECT COUNT(*) FROM curated_prompts").fetchone()[0]


def main():
    global hp
    # ── Parse ──
    all_rows, per_file = [], {}
    for path in sorted(REFS.glob("*.md")):
        rows = parse_guide(path)
        if rows:
            all_rows.extend(rows)
            per_file[path.name] = len(rows)
    assert all_rows, "no master prompts parsed from references/*.md"
    sources = [r["source"] for r in all_rows]
    assert len(set(sources)) == len(sources), "duplicate source ids"
    with_ratio = sum(1 for r in all_rows if r["ratio"])
    print(f"parsed {len(all_rows)} master prompts from {len(per_file)} guide files")
    for name, n in per_file.items():
        print(f"  {name}: {n}")
    print(f"  ratio metadata: {with_ratio}/{len(all_rows)}")

    # ── Target: copy-safe default, --apply for live ──
    live = hp._resolve_db_path()
    if "--apply" in sys.argv:
        target = live
        print(f"\n--apply: importing into LIVE DB {live}")
    else:
        target = Path(tempfile.gettempdir()) / "higgsfield-curated-copy.db"
        shutil.copy2(live, target)
        print(f"\nCopy-safe mode: importing into temp copy {target}")
        print(f"(live DB {live} untouched; use the copy via HIGGSFIELD_DB={target})")

    # DB_PATH resolves at import time -> reload with env var pointing at target
    os.environ["HIGGSFIELD_DB"] = str(target.resolve())
    hp = importlib.reload(hp)

    conn = hp.get_conn(readonly=False)
    count1 = import_curated(conn, all_rows)
    # Idempotency proof: direct second call on the already-imported target
    # (a fresh script run would re-copy from live — proves nothing).
    count2 = import_curated(conn, all_rows)
    conn.close()
    assert count1 == count2 == len(all_rows), (count1, count2, len(all_rows))
    print(f"\nimported: {count1} curated rows (idempotent re-run: {count2})")

    # ── Verify through the engine ──
    hpm = hp.HiggsfieldPromptMaster()
    st = hpm.stats()
    assert st["curated_prompts"] == len(all_rows), st["curated_prompts"]
    hits = hpm.search_curated("professional headshot")
    assert hits and all(p.id < 0 for p in hits), "search_curated returned no curated rows"
    print(f"stats()['curated_prompts'] = {st['curated_prompts']}")
    print(f"search_curated('professional headshot') -> {[p.title for p in hits[:3]]}")

    # Drive generate_prompt's last-resort path: stub FTS empty -> curated
    # fallback must fire (negative synthetic id in source_prompt_ids).
    orig_fts = hpm.fts_search
    hpm.fts_search = lambda q, limit=10: []
    try:
        result = hpm.generate_prompt("professional headshot for LinkedIn", "Portrait / Selfie")
        assert any(i < 0 for i in result["source_prompt_ids"]), result["source_prompt_ids"]
    finally:
        hpm.fts_search = orig_fts
    print("generate_prompt last-resort fallback consumed a curated row:",
          [i for i in result["source_prompt_ids"] if i < 0])
    print("OK")


if __name__ == "__main__":
    main()

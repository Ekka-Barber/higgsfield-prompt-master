#!/usr/bin/env python3
"""US-029 regression checks: refresh pipeline (guards, idempotent upsert,
scrape_log, FTS rebuild, diff summary) — fully network-free."""
import json
import os
import runpy
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT = str(Path(__file__).parent / "refresh.py")
TMP = Path(tempfile.mkdtemp(prefix="refresh-test-"))
ENV_DB = os.environ.get("HIGGSFIELD_DB")

ns = runpy.run_path(SCRIPT)  # loads functions, __main__ guard skips CLI
refresh_db, normalize, guard = ns["refresh_db"], ns["normalize"], ns["guard"]

live = ns["db"]._resolve_db_path()
COPY = TMP / "refresh-copy.db"
COPY.write_bytes(live.read_bytes())


def conn():
    c = sqlite3.connect(COPY)
    c.execute("PRAGMA foreign_keys = ON")
    return c


# Snapshot the live DB before anything runs. Check 5 asserts it is untouched;
# comparing against this baseline tests that invariant at whatever size the
# corpus happens to be, rather than pinning a count that goes stale the first
# time a maintenance script legitimately changes the row total.
_lc = sqlite3.connect(f"file:{live}?mode=ro", uri=True)
LIVE_BASELINE = _lc.execute("SELECT MAX(id), COUNT(*) FROM prompts").fetchone()
_lc.close()

WM = LIVE_BASELINE[0]  # live max id (watermark = max(map end 26926, this))
ROWS = [
    {"id": WM + 1, "title": "Neon Poster AI Prompt for Minimalist | youmind",
     "model": "GPT Image 2", "categories": ["poster / flyer"],
     "prompt_text": "A minimalist neon poster with soft studio lighting and a pastel palette, " + "x" * 40},
    {"id": WM + 2, "title": "Avatar AI Prompt for Profile | youmind",
     "model": "Nano Banana", "categories": ["profile / avatar"],
     "prompt_text": "A stylized avatar portrait with rim lighting and grain, " + "y" * 40},
    {"id": WM + 3, "title": "Boilerplate | youmind", "model": "GPT Image 2",
     "categories": [], "prompt_text": 'Just found a great AI prompt: "x"! This site also has thousands more'},
    {"id": WM + 4, "title": "RU | youmind", "model": "GPT Image 2",
     "categories": [], "prompt_text": "Минималистичный постер продукта со студийным светом и мягкими тенями"},
    {"id": WM + 5, "title": "No model | youmind", "model": "",
     "categories": [], "prompt_text": "A clean studio product shot with soft shadows and a muted palette, " + "z" * 40},
    {"id": 13440, "title": "UPDATED TITLE for existing row", "model": "GPT Image 2",
     "categories": ["abstract / background"],
     "prompt_text": "An abstract flowing gradient background with volumetric light, " + "w" * 40},
]
MISSES = [WM + 6, WM + 7]

# 1. Guard verdicts
assert guard(normalize(ROWS[0])) is None
assert guard(normalize(ROWS[2])) == "boilerplate"
assert guard(normalize(ROWS[3])) == "non_english"
assert guard(normalize(ROWS[4])) == "bad_model"
print("[OK] guards: pass / boilerplate / non_english / bad_model verdicts correct")

# 2. refresh_db on the copy: inserts, guarded skips, update-with-change, log, FTS
os.environ["HIGGSFIELD_DB"] = str(COPY)
s1 = refresh_db(COPY, ROWS, MISSES)
assert s1["inserted"] == 2 and s1["updated"] == 1 and s1["changed"] == 1, s1
assert s1["skipped"] == {"boilerplate": 1, "non_english": 1, "bad_model": 1}, s1
assert s1["total_after"] == s1["total_before"] + 2
assert s1["searchable_after"] == s1["searchable_before"] + 2
print(f"[OK] refresh_db: inserted 2 (of 5 scraped), 1 re-scrape with changed content, "
      f"3 guard skips — {s1['total_before']} -> {s1['total_after']} rows")

c = conn()
for pid, st in [(WM + 1, "ok"), (WM + 2, "ok"), (WM + 3, "boilerplate"),
                (WM + 4, "non_english"), (WM + 5, "bad_model"),
                (WM + 6, "ok_no_text"), (WM + 7, "ok_no_text"), (13440, "ok")]:
    got = c.execute("SELECT status FROM scrape_log WHERE id=?", (pid,)).fetchone()
    assert got and got[0] == st, (pid, st, got)
print("[OK] scrape_log: all 8 probed ids written with correct statuses")

new = c.execute("SELECT prompt_text, has_prompt, structure_type, length_chars, technique_tags"
                " FROM prompts WHERE id=?", (WM + 1,)).fetchone()
assert new and new[1] == 1 and new[2] and new[3] == len(new[0]) and new[4], new
assert c.execute("SELECT COUNT(*) FROM prompts WHERE id IN (?,?,?)",
                 (WM + 3, WM + 4, WM + 5)).fetchone()[0] == 0
old = c.execute("SELECT title, has_prompt, prompt_text FROM prompts WHERE id=13440").fetchone()
assert old[0] == "UPDATED TITLE for existing row" and old[1] == 1, old
fts_n, prompt_n = c.execute(
    "SELECT (SELECT COUNT(*) FROM prompts_fts), (SELECT COUNT(*) FROM prompts)").fetchone()
hit = c.execute("SELECT COUNT(*) FROM prompts_fts WHERE prompts_fts MATCH 'neon minimalist'").fetchone()[0]
c.close()
assert fts_n == prompt_n and hit >= 1, (fts_n, prompt_n, hit)
print(f"[OK] upsert: guarded ids absent, new rows enriched+searchable (has_prompt=1), "
      f"existing row refreshed without touching has_prompt, FTS parity {fts_n}=={prompt_n}, FTS finds new row")

# 3. Idempotency: same input on the already-refreshed copy changes nothing
#    (WM+1/WM+2 now exist -> counted as re-scraped, but zero content changes)
s2 = refresh_db(COPY, ROWS, MISSES)
assert s2["inserted"] == 0 and s2["updated"] == 3 and s2["changed"] == 0, s2
assert s2["total_after"] == s2["total_before"] and s2["searchable_after"] == s2["searchable_before"]
print("[OK] idempotent: second pass inserts 0, changes 0, totals unchanged")

# 4. main() end-to-end in copy-safe mode (network stubbed at the scraper seam)
lines = [json.dumps(r, ensure_ascii=False) for r in ROWS]
ns["main"].__globals__["run_scraper"] = lambda start, end: (
    lines if start <= WM + 1 else [], MISSES if start <= WM + 1 else [])
if ENV_DB is None:
    os.environ.pop("HIGGSFIELD_DB", None)  # main resolves live itself; no leftover bias
else:
    os.environ["HIGGSFIELD_DB"] = ENV_DB
old_argv = sys.argv[:]
sys.argv = ["refresh.py", "--jsonl", str(TMP / "artifact.jsonl")]
import contextlib, io
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        ns["main"]()
finally:
    sys.argv = old_argv
out = buf.getvalue()
assert "--apply" not in out and "copy-safe mode" in out and "OK" in out, out
target = Path(tempfile.gettempdir()) / "higgsfield-refresh-copy.db"
assert target.exists(), "copy-safe mode never created the temp copy"
artifact = (TMP / "artifact.jsonl").read_text(encoding="utf-8").strip().split("\n")
assert len(artifact) == len(ROWS) and json.loads(artifact[0])["id"] == WM + 1
lc = sqlite3.connect(target)
n = lc.execute("SELECT COUNT(*) FROM prompts WHERE id>?", (WM,)).fetchone()[0]
lc.close()
assert n == 2, n
print("[OK] main() dry-run: live untouched, scrape JSONL artifact written verbatim, "
      "temp copy refreshed via HIGGSFIELD_DB")

# 5. Live DB untouched throughout
lc = sqlite3.connect(live)
live_max, live_total = lc.execute("SELECT MAX(id), COUNT(*) FROM prompts").fetchone()
lc.close()
assert (live_max, live_total) == LIVE_BASELINE, (live_max, live_total, LIVE_BASELINE)
print(f"[OK] live DB untouched: max_id={live_max}, total={live_total}")

if ENV_DB is None:
    os.environ.pop("HIGGSFIELD_DB", None)
else:
    os.environ["HIGGSFIELD_DB"] = ENV_DB
print("ALL CHECKS PASSED")

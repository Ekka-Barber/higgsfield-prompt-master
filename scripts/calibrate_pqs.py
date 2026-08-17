#!/usr/bin/env python3
"""Build pqs_calibration.json (US-014) from the corpus DB.

Scores every searchable corpus prompt once (goal proxy = row title) and
stores the per-category PQS distribution, the lemma DF table and the
normalization percentiles used by pqs.PQSScorer. Re-run after purges,
enrichment or schema migrations so grades track whatever DB is live.
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import HiggsfieldPromptMaster
from pqs import build_calibration, CALIBRATION_PATH

master = HiggsfieldPromptMaster()
calib = build_calibration(master.conn, master._searchable)
CALIBRATION_PATH.write_text(json.dumps(calib), encoding="utf-8")

# ── Second pass: distribution over the GENERATOR's own output ──
# The corpus pass scores each row against its title as a stand-in goal, so its
# goal-fidelity is near zero. A generated prompt carries its goal verbatim and
# scores ~1.0, which put every generated prompt above the 99th percentile of the
# corpus distribution -- grades stopped discriminating. Grading needs a
# reference set produced the same way the graded item is, so generate a
# stratified sample using real corpus titles as goals and score those.
SAMPLE_PER_CAT = 12
gen_dist = {"_all": []}
cats = [c for c in sorted(calib["dist"]) if c != "_all"]
for cat in cats:
    rows = master.conn.execute(
        f"SELECT title FROM prompts WHERE {master._searchable} AND categories LIKE ?"
        " AND title IS NOT NULL AND length(title) > 12 LIMIT ?",
        (f"%{cat}%", SAMPLE_PER_CAT)).fetchall()
    for (title,) in rows:
        goal = " ".join(str(title).split()[:10])
        try:
            total = master.generate_prompt(goal, cat)["quality_score"]["total"]
        except Exception:
            continue
        gen_dist.setdefault(cat, []).append(total)
        gen_dist["_all"].append(total)
gen_dist = {c: sorted(v) for c, v in gen_dist.items() if v}

calib["gen_dist"] = gen_dist
CALIBRATION_PATH.write_text(json.dumps(calib), encoding="utf-8")
print(f"Generated-output distribution: {len(gen_dist['_all'])} prompts "
      f"across {len(gen_dist) - 1} categories")

dist = calib["dist"]
print(f"Calibrated {calib['n_prompts']} prompts -> {CALIBRATION_PATH.name} "
      f"({CALIBRATION_PATH.stat().st_size:,} bytes)")
for cat in sorted(dist):
    v = dist[cat]
    print(f"  {cat[:32]:<34} n={len(v):>5}  p25={v[len(v)//4]:>5}  "
          f"p50={v[len(v)//2]:>5}  p90={v[int(0.9*len(v))]:>5}")

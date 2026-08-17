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

dist = calib["dist"]
print(f"Calibrated {calib['n_prompts']} prompts -> {CALIBRATION_PATH.name} "
      f"({CALIBRATION_PATH.stat().st_size:,} bytes)")
for cat in sorted(dist):
    v = dist[cat]
    print(f"  {cat[:32]:<34} n={len(v):>5}  p25={v[len(v)//4]:>5}  "
          f"p50={v[len(v)//2]:>5}  p90={v[int(0.9*len(v))]:>5}")

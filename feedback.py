#!/usr/bin/env python3
"""US-031: opt-in outcome logging, so injected guidance can be judged by results.

Every generated prompt injects specs from the intelligence layers. Without an
outcome signal there is no way to tell which of those specs help and which are
inherited folklore -- exactly how the pre-v2 layers accumulated claims that the
2026-08 research later refuted.

Two deliberate design choices:

* **Separate database.** US-003 made the corpus read-only on purpose: it is a
  30 MB shared asset and reads must not need write access. Logging therefore
  goes to its own file (``HIGGSFIELD_LOG_DB``, else ``generation_log.db``
  beside this module), never into the corpus.
* **Opt-in.** Nothing is written until :func:`enable` is called or
  ``HIGGSFIELD_LOG=1`` is set. A prompt-engineering library should not start
  recording what its user is designing because it was imported.

No PII is stored: the goal text the caller supplied, the routed model, the
generated prompt, and which layers fired. No user, host, or environment data.
"""
import json
import os
import sqlite3
from pathlib import Path
from time import strftime

_DEFAULT = Path(__file__).resolve().parent / "generation_log.db"
_enabled = os.environ.get("HIGGSFIELD_LOG") == "1"
_path = Path(os.environ.get("HIGGSFIELD_LOG_DB") or _DEFAULT)

SCHEMA = """
CREATE TABLE IF NOT EXISTS generation_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp       TEXT    NOT NULL,
    goal            TEXT    NOT NULL,
    category        TEXT,
    model           TEXT,
    prompt          TEXT    NOT NULL,
    source_ids      TEXT,              -- JSON array of corpus exemplar ids
    layers_injected TEXT,              -- JSON array of layer names
    quality_total   INTEGER,
    outcome         TEXT               -- accepted | edited | regenerated | NULL
);
CREATE INDEX IF NOT EXISTS idx_log_outcome ON generation_log(outcome);
"""


def enable(path=None):
    """Turn logging on for this process (optionally at a specific path)."""
    global _enabled, _path
    _enabled = True
    if path:
        _path = Path(path)
    _connect().close()          # create the file/schema eagerly so failures
    return _path                # surface at enable() rather than mid-generation


def disable():
    global _enabled
    _enabled = False


def is_enabled() -> bool:
    return _enabled


def _connect():
    conn = sqlite3.connect(str(_path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def log_generation(goal: str, category: str, result: dict) -> "int | None":
    """Record one generation. Returns the row id, or None when disabled.

    Never raises: a logging failure must not take down generation.
    """
    if not _enabled:
        return None
    try:
        model = result.get("model_recommendation") or {}
        intel = result.get("intelligence") or {}
        layers = sorted(k for k, v in intel.items() if v)
        score = result.get("quality_score") or {}
        conn = _connect()
        cur = conn.execute(
            "INSERT INTO generation_log (timestamp, goal, category, model,"
            " prompt, source_ids, layers_injected, quality_total, outcome)"
            " VALUES (?,?,?,?,?,?,?,?,NULL)",
            (strftime("%Y-%m-%dT%H:%M:%S"), goal, category,
             model.get("id") if isinstance(model, dict) else str(model),
             result.get("prompt", ""),
             json.dumps(result.get("source_prompt_ids", [])),
             json.dumps(layers),
             score.get("total") if isinstance(score, dict) else None))
        conn.commit()
        rid = cur.lastrowid
        conn.close()
        return rid
    except Exception:
        return None


def record_outcome(log_id: int, outcome: str) -> bool:
    """Attach the human verdict: accepted | edited | regenerated."""
    if outcome not in {"accepted", "edited", "regenerated"}:
        raise ValueError(f"unknown outcome {outcome!r}")
    try:
        conn = _connect()
        conn.execute("UPDATE generation_log SET outcome=? WHERE id=?",
                     (outcome, log_id))
        conn.commit()
        changed = conn.total_changes
        conn.close()
        return bool(changed)
    except Exception:
        return False


def acceptance_rates() -> dict:
    """Acceptance rate per injected layer and per routed model.

    A layer whose prompts are consistently regenerated is a demotion candidate;
    that is the whole point of collecting this.
    """
    if not _path.exists():
        return {"logged": 0, "with_outcome": 0, "by_layer": {}, "by_model": {}}
    conn = _connect()
    rows = conn.execute(
        "SELECT layers_injected, model, outcome FROM generation_log").fetchall()
    conn.close()

    def _bump(bucket, key, outcome):
        d = bucket.setdefault(key, {"accepted": 0, "edited": 0,
                                    "regenerated": 0, "total": 0})
        d["total"] += 1
        if outcome:
            d[outcome] += 1

    by_layer, by_model = {}, {}
    with_outcome = 0
    for layers, model, outcome in rows:
        if outcome:
            with_outcome += 1
        for layer in json.loads(layers or "[]"):
            _bump(by_layer, layer, outcome)
        _bump(by_model, model or "unknown", outcome)

    for bucket in (by_layer, by_model):
        for stats in bucket.values():
            judged = stats["accepted"] + stats["edited"] + stats["regenerated"]
            stats["acceptance"] = (round(stats["accepted"] / judged, 3)
                                   if judged else None)
    return {"logged": len(rows), "with_outcome": with_outcome,
            "by_layer": by_layer, "by_model": by_model, "path": str(_path)}

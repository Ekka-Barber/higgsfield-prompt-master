#!/usr/bin/env python3
"""Higgsfield Prompt Master — database layer.

Path resolution, connections, the Prompt row model, and the structure /
technique / category detection constants shared by every other module.
"""

import sqlite3, json, os
from pathlib import Path
from dataclasses import dataclass

# ─── DATABASE PATH RESOLUTION ─────────────────────────────────────────────
# The corpus database can live in different places depending on how this skill
# was installed. Resolution order (first existing file wins):
#   1. HIGGSFIELD_DB environment variable  — explicit override (any path)
#   2. Auto-detect via this file's location — <skill_dir>/references/gpt-image2-prompts-full.db
#      Works regardless of where the skill was dropped (~/.agents/, ~/.hermes/, venv, etc.)
#   3. Legacy Hermes default — ~/.hermes/skills/higgsfield-prompt-master/references/...
#   4. Legacy .agents default — ~/.agents/skills/higgsfield-prompt-master/references/...
# Set HIGGSFIELD_DB to point at a non-standard location, e.g. for tests or CI.

_DB_FILENAME = "gpt-image2-prompts-full.db"
_SKILL_NAME = "higgsfield-prompt-master"

def _resolve_db_path() -> Path:
    # 1. Explicit env var override — if set, it must exist (no silent fallback)
    env = os.environ.get("HIGGSFIELD_DB")
    if env:
        p = Path(env).expanduser().resolve()
        if p.exists():
            return p
        raise FileNotFoundError(f"HIGGSFIELD_DB={env} does not exist (resolved: {p})")

    # 2. Auto-detect: this module sits at <skill_dir>/db.py
    here = Path(__file__).resolve().parent
    candidates = [here / "references" / _DB_FILENAME]

    # 3-4. Legacy conventional locations
    for base in (Path.home() / ".hermes", Path.home() / ".agents"):
        candidates.append(base / "skills" / _SKILL_NAME / "references" / _DB_FILENAME)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Higgsfield prompt DB not found. Tried:\n  "
        + "\n  ".join(str(c) for c in candidates)
        + "\nSet HIGGSFIELD_DB to the database path."
    )

# Import-time validation + back-compat constant. get_conn re-resolves on every
# call so HIGGSFIELD_DB switches take effect at the next connection without a
# module reload (scripts/rebuild_corpus.py et al. relied on reload for this).
DB_PATH = _resolve_db_path()

# ─── TECHNIQUE DETECTORS ───
TECHNIQUE_DETECTORS = {
    "JSON structure": lambda t: t.strip().startswith("{"),
    "Arguments/Templates": lambda t: "{argument" in t,
    "Negative prompts": lambda t: "negative" in t.lower() or "avoid" in t.lower(),
    "Aspect ratio specs": lambda t: "--ar " in t or "aspect ratio" in t.lower() or any(r in t for r in ["16:9", "9:16", "1:1", "4:3", "21:9", "2:3", "3:2"]),
    "Lighting details": lambda t: any(w in t.lower() for w in ["lighting", "golden hour", "studio light", "soft light", "natural light", "volumetric", "rim light", "caustics"]),
    "Camera specs": lambda t: any(w in t.lower() for w in ["lens", "camera", "shot", "f/", "mm ", "aperture", "depth of field", "bokeh", "35mm", "50mm", "85mm", "24mm"]),
    "Color palette": lambda t: any(w in t.lower() for w in ["color palette", "colour palette", "colors:", "palette:", "gradient", "monochrome", "complementary", "brand colors"]),
    "Material/Texture": lambda t: any(w in t.lower() for w in ["material", "texture", "surface", "finish", "glass", "metal", "matte", "glossy", "fabric", "organic", "translucent", "opacity"]),
    "Typography": lambda t: any(w in t.lower() for w in ["typography", "font", "text style", "lettering", "typeface", "font-weight", "kerning", "heading", "body text"]),
    "Layout/Composition": lambda t: any(w in t.lower() for w in ["layout", "composition", "grid", "alignment", "center", "balanced", "rule of thirds", "hierarchy", "whitespace", "spacing"]),
    "UI/UX terms": lambda t: any(w in t.lower() for w in ["ui/", "ux", "interface", "button", "navbar", "sidebar", "dashboard", "component", "responsive", "breakpoint", "design system"]),
    "Mood/Atmosphere": lambda t: any(w in t.lower() for w in ["mood", "atmosphere", "vibe", "feel", "aesthetic", "cinematic", "moody", "vibrant", "ethereal", "gritty", "dreamy"]),
    "Reference images": lambda t: "reference" in t.lower() or "inspired by" in t.lower() or "style of" in t.lower(),
    "Step-by-step": lambda t: "step" in t.lower() and any(w in t.lower() for w in ["first", "then", "next", "step 1", "step 2"]),
}

def _parses_as_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except (ValueError, TypeError):
        return False

STRUCTURE_TYPES = {
    # Template is checked BEFORE JSON (US-019): an "{argument"-bearing text
    # that fails json.loads is a Template, never JSON. The JSON label
    # requires strict json.loads success; rows that both parse as JSON and
    # carry {argument tags get the Template-JSON hybrid bucket.
    "Template": lambda t: "{argument" in t and not _parses_as_json(t),
    "Template-JSON": lambda t: "{argument" in t and _parses_as_json(t),
    "JSON": lambda t: t.strip().startswith("{") and _parses_as_json(t),
    "Flat prose": lambda t: t.strip().startswith(("A ", "The ", "An ")),
    "Other": lambda t: True,
}

def _load_category_registry():
    """Derive the alias->canonical map from data/categories.json (US-032).

    One registry generates CATEGORY_NORMALIZE here and the photo/marketing maps
    in intelligence.py, so adding a category is a single edit instead of six
    coordinated ones. Falls back to canonical-only normalisation if the file is
    missing, which keeps a partial install working rather than crashing import.
    """
    path = Path(__file__).resolve().parent / "data" / "categories.json"
    mapping = {}
    try:
        reg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return mapping
    for entry in reg.get("categories", []):
        name = entry["name"]
        mapping[name.lower()] = name
        for alias in entry.get("aliases", []):
            mapping[alias.lower()] = name
    return mapping


CATEGORY_NORMALIZE = _load_category_registry()

@dataclass
class Prompt:
    id: int
    title: str
    description: str
    prompt_text: str
    categories: list
    model: str
    slug: str
    structure_type: str
    length_chars: int
    techniques: list

    @classmethod
    def from_row(cls, row):
        cats = [c.strip() for c in (row["categories"] or "").split("|") if c.strip()]
        techs = json.loads(row["technique_tags"]) if row["technique_tags"] else []
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            prompt_text=row["prompt_text"],
            categories=cats,
            model=row["model"],
            slug=row["slug"],
            structure_type=row["structure_type"] or detect_structure(row["prompt_text"]),
            length_chars=row["length_chars"] or len(row["prompt_text"] or ""),
            techniques=techs
        )

def get_conn(readonly: bool = True):
    # URI mode so reads never require (or take) write access.
    mode = "ro" if readonly else "rw"
    conn = sqlite3.connect(f"{_resolve_db_path().as_uri()}?mode={mode}", uri=True)
    # FK enforcement is per-connection in SQLite (US-020); prompt_techniques
    # carries ON DELETE CASCADE, so purge scripts' prompt deletes stay clean.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def detect_structure(text: str) -> str:
    for name, checker in STRUCTURE_TYPES.items():
        if checker(text):
            return name
    return "Other"

def detect_techniques(text: str) -> list:
    return [name for name, checker in TECHNIQUE_DETECTORS.items() if checker(text)]

def normalize_category(cat: str) -> str:
    return CATEGORY_NORMALIZE.get(cat.lower().strip(), cat.strip())

# ─── DB MIXIN ───
class DbMixin:
    """Connection management and enrichment writing (composed into
    HiggsfieldPromptMaster by higgsfield_prompt.py)."""

    def __init__(self):
        self.conn = get_conn()
        self.conn.row_factory = sqlite3.Row
        # Migrated DBs (scripts/migrate_status.py) gate reads on status; legacy DBs on has_prompt
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(prompts)")]
        self._searchable = "status IN ('curated','harvested')" if "status" in cols else "has_prompt = 1"
        self._pqs = None  # lazy PQSScorer (US-014), built on first score
        # US-022: curated master prompts imported from references/*.md guides.
        # Optional table — absent until scripts/import_curated.py --apply runs.
        self._has_curated = bool(self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='curated_prompts'"
        ).fetchone())

    def _ensure_enrichment_columns(self):
        """Add structure_type, length_chars, technique_tags columns if missing."""
        c = self.conn.cursor()
        cols = [r[1] for r in c.execute("PRAGMA table_info(prompts)").fetchall()]
        if "structure_type" not in cols:
            c.execute("ALTER TABLE prompts ADD COLUMN structure_type TEXT")
        if "length_chars" not in cols:
            c.execute("ALTER TABLE prompts ADD COLUMN length_chars INTEGER")
        if "technique_tags" not in cols:
            c.execute("ALTER TABLE prompts ADD COLUMN technique_tags TEXT")
        if "prompt_techniques" not in [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            c.execute("""
                CREATE TABLE prompt_techniques (
                    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
                    technique TEXT,
                    PRIMARY KEY (prompt_id, technique)
                )
            """)
        self.conn.commit()

    def enrich_all(self, batch_size=500):
        """Enrich all prompts with structure type, length, and techniques."""
        # Enrichment is the only writer: reopen read-write, then ensure schema.
        self.conn.close()
        self.conn = get_conn(readonly=False)
        self.conn.row_factory = sqlite3.Row
        self._ensure_enrichment_columns()
        c = self.conn.cursor()
        c.execute("SELECT id, prompt_text FROM prompts WHERE structure_type IS NULL OR technique_tags IS NULL")
        rows = c.fetchall()
        print(f"Enriching {len(rows)} prompts...")

        for i, row in enumerate(rows):
            pid, text = row
            structure = detect_structure(text)
            techniques = detect_techniques(text)
            length = len(text)

            c.execute("""
                UPDATE prompts SET structure_type=?, length_chars=?, technique_tags=?
                WHERE id=?
            """, (structure, length, json.dumps(techniques), pid))

            for tech in techniques:
                c.execute("INSERT OR IGNORE INTO prompt_techniques (prompt_id, technique) VALUES (?,?)",
                          (pid, tech))

            if (i + 1) % batch_size == 0:
                self.conn.commit()
                print(f"  {i+1}/{len(rows)}...")

        self.conn.commit()
        print("Enrichment complete!")

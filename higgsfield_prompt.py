#!/usr/bin/env python3
"""
Higgsfield Prompt Master — back-compat facade
==============================================
Search, analyze, and generate GPT Image 2 prompts from the 7,613-prompt corpus.

US-023 split: the implementation lives in db.py (connections, detection,
enrichment), retrieval.py (search/FTS/curated), generate.py (pipeline,
routing, scoring), analytics.py (guides, stats), and cli.py (argparse CLI).
This module re-assembles HiggsfieldPromptMaster and re-exports every public
name so existing `from higgsfield_prompt import ...` calls keep working.
"""

# US-025: every sibling import tries absolute (repo root on sys.path)
# first, then package-relative (packaged via __init__) — import failures
# are loud, never silent layer drops.
try:
    from db import (DB_PATH, CATEGORY_NORMALIZE, STRUCTURE_TYPES, TECHNIQUE_DETECTORS,
                    Prompt, DbMixin, _resolve_db_path, detect_structure,
                    detect_techniques, get_conn, normalize_category)
    from retrieval import RetrievalMixin, _like
    from generate import GenerationMixin, MODELS
    from analytics import AnalyticsMixin
except ImportError:
    from .db import (DB_PATH, CATEGORY_NORMALIZE, STRUCTURE_TYPES, TECHNIQUE_DETECTORS,
                     Prompt, DbMixin, _resolve_db_path, detect_structure,
                     detect_techniques, get_conn, normalize_category)
    from .retrieval import RetrievalMixin, _like
    from .generate import GenerationMixin, MODELS
    from .analytics import AnalyticsMixin


class HiggsfieldPromptMaster(DbMixin, RetrievalMixin, GenerationMixin, AnalyticsMixin):
    """Facade over the db/retrieval/generate/analytics mixins (US-023)."""


# ─── CONVENIENCE FUNCTIONS ───
def search_prompts(query="", category="", model="", structure="", techniques=None, limit=10):
    hpm = HiggsfieldPromptMaster()
    return hpm.search(query, category, model, structure, techniques, limit)

def get_templates(category, structure="", limit=10):
    hpm = HiggsfieldPromptMaster()
    return hpm.get_templates(category, structure, limit)

def analyze_patterns(category):
    hpm = HiggsfieldPromptMaster()
    return hpm.analyze_patterns(category)

def generate_prompt(goal, category, structure="Template", techniques=None, style="", aspect_ratio=""):
    hpm = HiggsfieldPromptMaster()
    return hpm.generate_prompt(goal, category, structure, techniques, style, aspect_ratio)

def random_prompt(category="", model="", structure=""):
    hpm = HiggsfieldPromptMaster()
    return hpm.random_prompt(category, model, structure)


# ─── CLI ───
if __name__ == "__main__":
    try:
        from cli import main
    except ImportError:  # US-025: packaged layout
        from .cli import main
    raise SystemExit(main())

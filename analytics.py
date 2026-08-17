#!/usr/bin/env python3
"""Higgsfield Prompt Master — analytics layer.

Category guides, pattern analysis, corpus-wide stats, and model comparison.
"""

import re
from collections import Counter

try:
    from db import Prompt, normalize_category
except ImportError:  # US-025: packaged layout
    from .db import Prompt, normalize_category

# ─── ANALYTICS MIXIN ───
class AnalyticsMixin:
    """Corpus analytics (composed into HiggsfieldPromptMaster by
    higgsfield_prompt.py)."""

    def category_guide(self, category: str) -> dict:
        """Get comprehensive guide for a category."""
        norm_cat = normalize_category(category)
        c = self.conn.cursor()

        # Structure breakdown
        c.execute(f"""
            SELECT structure_type, COUNT(*) as cnt, AVG(length_chars) as avg_len
            FROM prompts
            WHERE {self._searchable} AND categories LIKE ?
            GROUP BY structure_type ORDER BY cnt DESC
        """, (f"%{norm_cat}%",))
        structures = [dict(r) for r in c.fetchall()]

        # Technique frequency
        c.execute(f"""
            SELECT technique, COUNT(*) as cnt
            FROM prompt_techniques pt
            JOIN prompts p ON pt.prompt_id = p.id
            WHERE p.{self._searchable} AND p.categories LIKE ?
            GROUP BY technique ORDER BY cnt DESC
        """, (f"%{norm_cat}%",))
        techniques = [dict(r) for r in c.fetchall()]

        # Example prompts (one per structure)
        examples = {}
        for struct in ["JSON", "Template", "Flat prose"]:
            c.execute(f"""
                SELECT * FROM prompts
                WHERE {self._searchable} AND categories LIKE ? AND structure_type = ?
                ORDER BY length_chars DESC LIMIT 1
            """, (f"%{norm_cat}%", struct))
            row = c.fetchone()
            if row:
                examples[struct] = Prompt.from_row(row)

        # Length stats
        c.execute(f"""
            SELECT MIN(length_chars), MAX(length_chars), AVG(length_chars), COUNT(*)
            FROM prompts WHERE {self._searchable} AND categories LIKE ?
        """, (f"%{norm_cat}%",))
        stats = c.fetchone()

        return {
            "category": norm_cat,
            "total_prompts": stats[3] if stats else 0,
            "length_stats": {"min": stats[0], "max": stats[1], "avg": int(stats[2]) if stats[2] else 0} if stats else {},
            "structure_breakdown": structures,
            "technique_frequency": techniques,
            "examples": examples,
        }

    def analyze_patterns(self, category: str) -> dict:
        """Deep pattern analysis for a category."""
        guide = self.category_guide(category)

        # Get top prompts for manual review
        prompts = self.search(category=category, limit=20)

        # Extract common phrases/patterns
        all_text = " ".join(p.prompt_text for p in prompts)

        return {
            "category": category,
            "guide": guide,
            "top_prompts": prompts[:5],
            "common_phrases": self._extract_common_phrases(all_text),
        }

    def _extract_common_phrases(self, text: str, min_len: int = 3, top_n: int = 20) -> list:
        """Extract common n-grams from prompt text."""
        # Simple word frequency
        words = re.findall(r'\b[a-z]{4,}\b', text.lower())
        return [w for w, _ in Counter(words).most_common(top_n)]

    def stats(self) -> dict:
        """Corpus-wide statistics."""
        c = self.conn.cursor()
        c.execute(f"SELECT COUNT(*) FROM prompts WHERE {self._searchable}")
        total = c.fetchone()[0]

        c.execute(f"SELECT model, COUNT(*) FROM prompts WHERE {self._searchable} GROUP BY model")
        models = dict(c.fetchall())

        c.execute(f"SELECT structure_type, COUNT(*) FROM prompts WHERE {self._searchable} GROUP BY structure_type")
        structures = dict(c.fetchall())

        c.execute("SELECT technique, COUNT(*) FROM prompt_techniques GROUP BY technique ORDER BY COUNT(*) DESC")
        techniques = dict(c.fetchall())

        # US-022: curated count when the table exists (0 on un-imported DBs)
        curated = 0
        if self._has_curated:
            curated = c.execute("SELECT COUNT(*) FROM curated_prompts").fetchone()[0]

        return {
            "total_prompts": total,
            "curated_prompts": curated,
            "models": models,
            "structures": structures,
            "techniques": techniques,
        }

    def compare_models(self, model1: str, model2: str) -> dict:
        """Compare two models' prompt patterns."""
        c = self.conn.cursor()
        result = {}

        for model in [model1, model2]:
            c.execute(f"""
                SELECT structure_type, COUNT(*) as cnt
                FROM prompts WHERE {self._searchable} AND model LIKE ?
                GROUP BY structure_type ORDER BY cnt DESC
            """, (f"%{model}%",))
            result[model] = {"structures": dict(c.fetchall())}

            c.execute(f"""
                SELECT technique, COUNT(*) as cnt
                FROM prompt_techniques pt
                JOIN prompts p ON pt.prompt_id = p.id
                WHERE p.{self._searchable} AND p.model LIKE ?
                GROUP BY technique ORDER BY cnt DESC LIMIT 10
            """, (f"%{model}%",))
            result[model]["top_techniques"] = dict(c.fetchall())

            c.execute(f"""
                SELECT categories, COUNT(*) as cnt
                FROM prompts WHERE {self._searchable} AND model LIKE ?
                GROUP BY categories ORDER BY cnt DESC LIMIT 10
            """, (f"%{model}%",))
            result[model]["top_categories"] = dict(c.fetchall())

        return result

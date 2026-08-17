#!/usr/bin/env python3
"""Higgsfield Prompt Master — retrieval layer.

LIKE search (relevance-ranked), FTS5 search with progressive fallback,
curated-prompt search, goal-keyword extraction, category templates, and
random draws.
"""

import random
import sqlite3
from typing import Optional

try:
    from db import Prompt, detect_structure, detect_techniques, normalize_category
    from langcheck import is_english
except ImportError:  # US-025: packaged layout
    from .db import Prompt, detect_structure, detect_techniques, normalize_category
    from .langcheck import is_english

# Shared FTS stop words (US-017: single source — was duplicated with drift
# between fts_search and _extract_keywords, 'this' listed twice).
_STOP_WORDS = frozenset({
    "the", "a", "an", "for", "of", "in", "on", "at", "to", "and", "or", "is", "are",
    "with", "from", "by", "this", "that", "showing", "shows", "display", "displaying",
    "create", "called", "page", "section", "website", "webapp", "large", "full",
    "these", "those", "their", "there", "where", "which", "what", "when",
})

# Extra domain filler filtered only when extracting goal keywords (never
# stripped from raw user searches).
_DOMAIN_STOP_WORDS = frozenset({
    "has", "have", "each", "every", "some", "all", "into", "onto", "over", "under", "about",
    # Arabic/common web terms that hurt FTS (too common)
    "arabic", "warm", "minimal", "premium", "personal", "brand", "entrepreneur",
    "saudi", "company", "project", "mockup", "image", "photo", "design",
})

def _like(term: str) -> str:
    """LIKE pattern matching term as a literal substring.

    % and _ are escaped (ESCAPE '\\' must be added to the LIKE clause) so
    user wildcards can't broaden the match.
    """
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"

# ─── RETRIEVAL MIXIN ───
class RetrievalMixin:
    """Search and exemplar retrieval (composed into HiggsfieldPromptMaster
    by higgsfield_prompt.py)."""

    def search(self, query: str = "", category: str = "", model: str = "",
               structure: str = "", techniques: list = None, limit: int = 10) -> list:
        """Search prompts with multiple filters. Query terms are OR'd together;
        results ranked by relevance (title match > description > body, summed
        over matched terms), never by length."""
        if techniques is None:
            techniques = []

        c = self.conn.cursor()

        # Build query
        conditions = [self._searchable]
        params = []
        order_by = "id"

        if query:
            # Split query into terms, each term matches ANY field (OR)
            terms = [t for t in query.split() if t]
            if terms:
                term_conditions = []
                for term in terms:
                    pat = _like(term)
                    term_conditions.append(
                        "(title LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\' "
                        "OR prompt_text LIKE ? ESCAPE '\\')")
                    params.extend([pat] * 3)
                # Relevance rank: per term, title hit=3, description hit=2, body hit=1
                rank_expr = []
                for term in terms:
                    pat = _like(term)
                    rank_expr.append(
                        "(CASE WHEN title LIKE ? ESCAPE '\\' THEN 3 ELSE 0 END"
                        " + CASE WHEN description LIKE ? ESCAPE '\\' THEN 2 ELSE 0 END"
                        " + CASE WHEN prompt_text LIKE ? ESCAPE '\\' THEN 1 ELSE 0 END)")
                    params.extend([pat] * 3)
                conditions.append(f"({' OR '.join(term_conditions)})")
                order_by = f"({' + '.join(rank_expr)}) DESC, id"

        if category:
            norm_cat = normalize_category(category)
            conditions.append("categories LIKE ? ESCAPE '\\'")
            params.append(_like(norm_cat))

        if model:
            conditions.append("model LIKE ? ESCAPE '\\'")
            params.append(_like(model))

        if structure:
            conditions.append("structure_type = ?")
            params.append(structure)

        if techniques:
            placeholders = ",".join("?" * len(techniques))
            conditions.append(f"id IN (SELECT prompt_id FROM prompt_techniques WHERE technique IN ({placeholders}))")
            params.extend(techniques)

        where = " AND ".join(conditions)
        sql = f"""
            SELECT * FROM prompts
            WHERE {where}
            ORDER BY {order_by}
            LIMIT ?
        """
        params.append(limit)

        rows = c.execute(sql, params).fetchall()
        return [Prompt.from_row(r) for r in rows]

    def fts_search(self, query: str, limit: int = 10) -> list:
        """Full-text search using FTS5 index. Sanitizes query to prevent syntax errors.
        Uses progressive fallback: tries full query, then key terms, then single terms."""
        c = self.conn.cursor()

        def _do_search(safe_q, lim):
            terms = [t for t in safe_q.split() if len(t) > 1]
            if not terms:
                return []
            # Double embedded quotes per FTS5 escaping rules so input
            # like 'dashboard "glass' can never break the MATCH string.
            safe_query = " ".join('"' + t.replace('"', '""') + '"' for t in terms)
            try:
                rows = c.execute(f"""
                    SELECT p.id, p.title, p.description, p.prompt_text, p.categories,
                           p.model, p.slug, p.structure_type, p.length_chars, p.technique_tags
                    FROM prompts_fts f
                    JOIN prompts p ON p.id = f.rowid
                    WHERE prompts_fts MATCH ? AND p.{self._searchable}
                    ORDER BY rank
                    LIMIT ?
                """, (safe_query, lim)).fetchall()
            except sqlite3.OperationalError:
                # Malformed MATCH despite escaping: caller falls back to next strategy
                return []
            return [Prompt.from_row(r) for r in rows]

        # Extract content words (remove stop words, prefer nouns/adjectives)
        words = [w for w in query.lower().split() if len(w) > 2 and w not in _STOP_WORDS]

        # Strategy 1: Try all content words
        if words:
            results = _do_search(" ".join(words), limit)
            if results:
                return results

        # Strategy 2: Try top 3 most specific (longest) words
        if len(words) > 3:
            top3 = sorted(words, key=len, reverse=True)[:3]
            results = _do_search(" ".join(top3), limit)
            if results:
                return results

        # Strategy 3: Try each word individually (OR semantics)
        all_results = []
        seen_ids = set()
        for w in words[:5]:
            r = _do_search(w, limit)
            for p in r:
                if p.id not in seen_ids:
                    all_results.append(p)
                    seen_ids.add(p.id)
            if len(all_results) >= limit:
                break

        return all_results[:limit]

    def search_curated(self, query: str = "", category: str = "", limit: int = 10) -> list:
        """Search curated_prompts (US-022): hand-tested master prompts from
        the references/*.md category guides, imported by scripts/import_curated.py.
        Rows come back as Prompt objects with negative synthetic ids (-rowid)
        so curated provenance is distinguishable from corpus ids in
        source_prompt_ids. Terms are OR'd (mirrors search()); query terms and
        category are escaped LIKE matches. Curated rows are the
        category-template class — last-resort primaries in generate_prompt,
        never generation donors (the June 2026 contamination lesson)."""
        if not self._has_curated:
            return []
        conditions, params = [], []
        order_by = "rowid"
        terms = [t for t in query.split() if t]
        if terms:
            term_conditions = []
            for term in terms:
                pat = _like(term)
                term_conditions.append("(category LIKE ? ESCAPE '\\' OR text LIKE ? ESCAPE '\\')")
                params.extend([pat, pat])
            conditions.append(f"({' OR '.join(term_conditions)})")
            # Relevance rank: per term, text hit=2, category hit=1 — rows
            # matching MORE terms outrank single-term coincidences (P1 for
            # "professional headshot", not a dreamscape matching "professional").
            rank_expr = []
            for term in terms:
                pat = _like(term)
                rank_expr.append(
                    "(CASE WHEN text LIKE ? ESCAPE '\\' THEN 2 ELSE 0 END"
                    " + CASE WHEN category LIKE ? ESCAPE '\\' THEN 1 ELSE 0 END)")
                params.extend([pat, pat])
            order_by = f"({' + '.join(rank_expr)}) DESC, rowid"
        if category:
            conditions.append("category LIKE ? ESCAPE '\\'")
            params.append(_like(category))
        where = " AND ".join(conditions) if conditions else "1=1"
        rows = self.conn.execute(
            f"SELECT rowid, * FROM curated_prompts WHERE {where} ORDER BY {order_by} LIMIT ?",
            (*params, limit)).fetchall()
        return [Prompt(id=-r["rowid"], title=r["source"], description=r["category"] or "",
                       prompt_text=r["text"] or "", categories=[r["category"]] if r["category"] else [],
                       model=r["model"] or "", slug=r["source"],
                       structure_type=detect_structure(r["text"] or ""),
                       length_chars=len(r["text"] or ""),
                       techniques=detect_techniques(r["text"] or ""))
                for r in rows]

    def _extract_keywords(self, text: str) -> str:
        """Extract the most important keywords from a goal description for FTS search.
        Removes stop words and domain filler, keeps nouns/adjectives/design terms."""
        stop_words = _STOP_WORDS | _DOMAIN_STOP_WORDS
        # Design-relevant terms that should be prioritized
        design_terms = {
            "hero", "landing", "dashboard", "gallery", "grid", "card", "masonry", "timeline",
            "dark", "light", "cream", "contact", "form", "footer", "header", "navbar",
            "sidebar", "book", "reading", "product", "checkout", "mobile", "desktop",
            "responsive", "login", "profile", "menu", "table", "chart", "map", "search",
            "filter", "list", "detail", "wireframe", "sketch", "infographic", "poster",
            "social", "media", "button", "input", "modal", "dialog", "toast", "badge",
            "avatar", "icon", "logo", "illustration", "3d", "gradient", "shadow", "blur",
            "glassmorphism", "neumorphism", "brutalism", "editorial", "magazine", "newspaper",
        }

        words = text.lower().split()
        # Keep only meaningful words (remove stop words, keep 3+ chars)
        meaningful = [w.strip(".,;:!?\"'()[]{}") for w in words
                      if len(w) > 2 and w.lower().strip(".,;:!?\"'()[]{}") not in stop_words]

        # Prioritize: design terms first, then by length
        prioritized = sorted(meaningful, key=lambda w: (w in design_terms, len(w)), reverse=True)

        # Take top 6 keywords
        return " ".join(prioritized[:6])

    def random_prompt(self, category: str = "", model: str = "", structure: str = "") -> Optional[Prompt]:
        """Get a random prompt matching filters."""
        prompts = self.search(category=category, model=model, structure=structure, limit=100)
        return random.choice(prompts) if prompts else None

    def get_templates(self, category: str, structure: str = "", limit: int = 10) -> list:
        """Get best template prompts for a category - prioritized by relevance."""
        norm_cat = normalize_category(category)
        c = self.conn.cursor()

        # Get prompts for this category, ordered by relevance (length + technique count)
        # Fetch extra to allow filtering
        fetch_limit = limit * 3
        if structure:
            c.execute(f"""
                SELECT p.*,
                       (p.length_chars + COALESCE(t.tech_count, 0) * 100) as score
                FROM prompts p
                LEFT JOIN (
                    SELECT prompt_id, COUNT(*) as tech_count
                    FROM prompt_techniques
                    GROUP BY prompt_id
                ) t ON p.id = t.prompt_id
                WHERE p.{self._searchable} AND p.categories LIKE ? AND p.structure_type = ?
                ORDER BY score DESC
                LIMIT ?
            """, (f"%{norm_cat}%", structure, fetch_limit))
        else:
            c.execute(f"""
                SELECT p.*,
                       (p.length_chars + COALESCE(t.tech_count, 0) * 100) as score
                FROM prompts p
                LEFT JOIN (
                    SELECT prompt_id, COUNT(*) as tech_count
                    FROM prompt_techniques
                    GROUP BY prompt_id
                ) t ON p.id = t.prompt_id
                WHERE p.{self._searchable} AND p.categories LIKE ?
                ORDER BY score DESC
                LIMIT ?
            """, (f"%{norm_cat}%", fetch_limit))

        rows = c.fetchall()
        prompts = [Prompt.from_row(r) for r in rows]

        # Filter: prefer English prompts (shared langcheck.is_english)
        english_prompts = [p for p in prompts if is_english(p.prompt_text)]
        return (english_prompts or prompts)[:limit]

#!/usr/bin/env python3
"""
Higgsfield Prompt Master — Core Module
=======================================
Search, analyze, and generate GPT Image 2 prompts from the 8,596-prompt corpus.
"""

import sqlite3, json, re, random
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from collections import Counter

DB_PATH = Path.home() / ".hermes" / "skills" / "higgsfield-prompt-master" / "references" / "gpt-image2-prompts-full.db"

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

STRUCTURE_TYPES = {
    "JSON": lambda t: t.strip().startswith("{"),
    "Template": lambda t: "{argument" in t,
    "Flat prose": lambda t: t.strip().startswith(("A ", "The ", "An ")),
    "Other": lambda t: True,
}

CATEGORY_NORMALIZE = {
    "app / web design": "App / Web Design",
    "app/web design": "App / Web Design",
    "product marketing": "Product Marketing",
    "social media post": "Social Media Post",
    "poster / flyer": "Poster / Flyer",
    "poster/flyer": "Poster / Flyer",
    "comic / storyboard": "Comic / Storyboard",
    "comic/storyboard": "Comic / Storyboard",
    "profile / avatar": "Profile / Avatar",
    "profile/avatar": "Profile / Avatar",
    "game asset": "Game Asset",
    "infographic / edu visual": "Infographic / Edu Visual",
    "infographic/edu visual": "Infographic / Edu Visual",
    "youtube thumbnail": "YouTube Thumbnail",
    "e-commerce main image": "E-commerce Main Image",
    "ecommerce main image": "E-commerce Main Image",
    "portrait / selfie": "Portrait / Selfie",
    "landscape / nature": "Landscape / Nature",
    "architecture / interior": "Architecture / Interior",
    "cinematic / film still": "Cinematic / Film Still",
    "abstract / background": "Abstract / Background",
    "animal / creature": "Animal / Creature",
    "group / couple": "Group / Couple",
    "sketch / line art": "Sketch / Line Art",
}

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

def get_conn():
    return sqlite3.connect(str(DB_PATH))

def detect_structure(text: str) -> str:
    for name, checker in STRUCTURE_TYPES.items():
        if checker(text):
            return name
    return "Other"

def detect_techniques(text: str) -> list:
    return [name for name, checker in TECHNIQUE_DETECTORS.items() if checker(text)]

def normalize_category(cat: str) -> str:
    return CATEGORY_NORMALIZE.get(cat.lower().strip(), cat.strip())

# ─── CORE CLASS ───
class HiggsfieldPromptMaster:
    def __init__(self):
        self.conn = get_conn()
        self.conn.row_factory = sqlite3.Row
        self._ensure_enrichment_columns()

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
                    prompt_id INTEGER,
                    technique TEXT,
                    PRIMARY KEY (prompt_id, technique)
                )
            """)
        self.conn.commit()

    def enrich_all(self, batch_size=500):
        """Enrich all prompts with structure type, length, and techniques."""
        c = self.conn.cursor()
        c.execute("SELECT id, prompt_text FROM prompts WHERE has_prompt=1 AND (structure_type IS NULL OR technique_tags IS NULL)")
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

    def search(self, query: str = "", category: str = "", model: str = "", 
               structure: str = "", techniques: list = None, limit: int = 10) -> list:
        """Search prompts with multiple filters. Query terms are OR'd together."""
        if techniques is None:
            techniques = []
        
        c = self.conn.cursor()
        
        # Build query
        conditions = ["has_prompt = 1"]
        params = []
        
        if query:
            # Split query into terms, each term matches ANY field (OR)
            terms = [t for t in query.split() if len(t) > 1]
            if terms:
                term_conditions = []
                for term in terms:
                    term_conditions.append("(title LIKE ? OR description LIKE ? OR prompt_text LIKE ?)")
                    params.extend([f"%{term}%"] * 3)
                conditions.append(f"({' OR '.join(term_conditions)})")
        
        if category:
            norm_cat = normalize_category(category)
            conditions.append("categories LIKE ?")
            params.append(f"%{norm_cat}%")
        
        if model:
            conditions.append("model LIKE ?")
            params.append(f"%{model}%")
        
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
            ORDER BY length_chars DESC
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
            safe_query = " ".join(f'"{t}"' for t in terms)
            rows = c.execute("""
                SELECT p.id, p.title, p.description, p.prompt_text, p.categories,
                       p.model, p.slug, p.structure_type, p.length_chars, p.technique_tags
                FROM prompts_fts f
                JOIN prompts p ON CAST(f.id AS INTEGER) = p.id
                WHERE prompts_fts MATCH ? AND p.has_prompt = 1
                ORDER BY rank
                LIMIT ?
            """, (safe_query, lim)).fetchall()
            return [Prompt.from_row(r) for r in rows]

        # Stop words to filter out
        stop_words = {"the", "a", "an", "for", "of", "in", "on", "at", "to", "and", "or", "is", "are",
                       "with", "from", "by", "this", "that", "showing", "shows", "display", "displaying",
                       "create", "called", "page", "section", "website", "webapp", "large", "full",
                       "this", "these", "those", "their", "there", "where", "which", "what", "when"}
        
        # Extract content words (remove stop words, prefer nouns/adjectives)
        words = [w for w in query.lower().split() if len(w) > 2 and w not in stop_words]
        
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
    
    def _extract_keywords(self, text: str) -> str:
        """Extract the most important keywords from a goal description for FTS search.
        Removes stop words and domain filler, keeps nouns/adjectives/design terms."""
        stop_words = {
            "the", "a", "an", "for", "of", "in", "on", "at", "to", "and", "or", "is", "are",
            "with", "from", "by", "this", "that", "showing", "shows", "display", "displaying",
            "create", "called", "page", "section", "website", "webapp", "large", "full",
            "these", "those", "their", "there", "where", "which", "what", "when", "has", "have",
            "each", "every", "some", "all", "into", "onto", "over", "under", "about",
            # Arabic/common web terms that hurt FTS (too common)
            "arabic", "warm", "minimal", "premium", "personal", "brand", "entrepreneur",
            "saudi", "company", "project", "mockup", "image", "photo", "design",
        }
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
            c.execute("""
                SELECT p.*, 
                       (p.length_chars + COALESCE(t.tech_count, 0) * 100) as score
                FROM prompts p
                LEFT JOIN (
                    SELECT prompt_id, COUNT(*) as tech_count
                    FROM prompt_techniques
                    GROUP BY prompt_id
                ) t ON p.id = t.prompt_id
                WHERE p.has_prompt=1 AND p.categories LIKE ? AND p.structure_type = ?
                ORDER BY score DESC
                LIMIT ?
            """, (f"%{norm_cat}%", structure, fetch_limit))
        else:
            c.execute("""
                SELECT p.*, 
                       (p.length_chars + COALESCE(t.tech_count, 0) * 100) as score
                FROM prompts p
                LEFT JOIN (
                    SELECT prompt_id, COUNT(*) as tech_count
                    FROM prompt_techniques
                    GROUP BY prompt_id
                ) t ON p.id = t.prompt_id
                WHERE p.has_prompt=1 AND p.categories LIKE ?
                ORDER BY score DESC
                LIMIT ?
            """, (f"%{norm_cat}%", fetch_limit))
        
        rows = c.fetchall()
        prompts = [Prompt.from_row(r) for r in rows]
        
        # Filter: prefer English prompts (no Japanese/Korean/Chinese chars in prompt_text)
        def is_english(prompt):
            text = prompt.prompt_text
            for ch in text:
                if ('\u3040' <= ch <= '\u309f' or  # Hiragana
                    '\u30a0' <= ch <= '\u30ff' or  # Katakana
                    '\u4e00' <= ch <= '\u9fff' or  # CJK Unified
                    '\uac00' <= ch <= '\ud7af'):   # Hangul
                    return False
            return True
        
        english_prompts = [p for p in prompts if is_english(p)]
        return (english_prompts or prompts)[:limit]

    def category_guide(self, category: str) -> dict:
        """Get comprehensive guide for a category."""
        norm_cat = normalize_category(category)
        c = self.conn.cursor()
        
        # Structure breakdown
        c.execute("""
            SELECT structure_type, COUNT(*) as cnt, AVG(length_chars) as avg_len
            FROM prompts 
            WHERE has_prompt=1 AND categories LIKE ?
            GROUP BY structure_type ORDER BY cnt DESC
        """, (f"%{norm_cat}%",))
        structures = [dict(r) for r in c.fetchall()]
        
        # Technique frequency
        c.execute("""
            SELECT technique, COUNT(*) as cnt
            FROM prompt_techniques pt
            JOIN prompts p ON pt.prompt_id = p.id
            WHERE p.has_prompt=1 AND p.categories LIKE ?
            GROUP BY technique ORDER BY cnt DESC
        """, (f"%{norm_cat}%",))
        techniques = [dict(r) for r in c.fetchall()]
        
        # Example prompts (one per structure)
        examples = {}
        for struct in ["JSON", "Template", "Flat prose"]:
            c.execute("""
                SELECT * FROM prompts 
                WHERE has_prompt=1 AND categories LIKE ? AND structure_type = ?
                ORDER BY length_chars DESC LIMIT 1
            """, (f"%{norm_cat}%", struct))
            row = c.fetchone()
            if row:
                examples[struct] = Prompt.from_row(row)
        
        # Length stats
        c.execute("""
            SELECT MIN(length_chars), MAX(length_chars), AVG(length_chars), COUNT(*)
            FROM prompts WHERE has_prompt=1 AND categories LIKE ?
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

    def generate_prompt(self, goal: str, category: str, structure: str = "Template",
                        techniques: list = None, style: str = "", aspect_ratio: str = "",
                        count: int = 1, platform: str = "") -> dict:
        """
        Generate an optimized prompt using RAG from the corpus + intelligence layers.
        
        Returns a dict with:
          - 'prompt': the full crafted prompt text
          - 'model_recommendation': suggested Higgsfield model
          - 'aspect_ratio': recommended ratio
          - 'count': number of images to generate
          - 'quality_score': 0-100 score vs corpus
          - 'intelligence': photo/marketing/art metadata used
          - 'source_prompt_ids': corpus prompt IDs used as reference
        """
        # Ensure intelligence module is loaded
        try:
            from intelligence import (
                get_photo_intelligence, get_marketing_intelligence, 
                infer_mood, CATEGORY_PHOTO_MAP, CATEGORY_MARKETING_MAP
            )
            has_intelligence = True
        except ImportError:
            has_intelligence = False

        norm_cat = normalize_category(category)
        
        if techniques is None:
            guide = self.category_guide(norm_cat)
            techniques = [t["technique"] for t in guide["technique_frequency"][:7]]
        
        # ── RAG: Retrieve real corpus prompts ──
        # 1. Extract key concepts from goal for better FTS matching
        goal_keywords = self._extract_keywords(goal)
        
        # 2. FTS search using keywords (more likely to hit relevant prompts)
        similar = self.fts_search(goal_keywords, limit=5) if goal_keywords else []
        
        # 3. If FTS found nothing, try with the raw goal
        if not similar and goal:
            similar = self.fts_search(goal[:100], limit=5)
        
        # 4. Get best templates for this category
        templates = self.get_templates(norm_cat, structure, limit=5)
        
        # 5. Prefer FTS results as the template source (goal-relevant)
        # Only fall back to category templates if FTS returned nothing useful
        source_ids = list({p.id for p in similar + templates})
        
        # ── Intelligence layers ──
        photo = get_photo_intelligence(norm_cat, goal) if has_intelligence else None
        marketing = get_marketing_intelligence(norm_cat, goal) if has_intelligence else None
        mood = infer_mood(style, goal) if has_intelligence else ""
        
        # ── Auto-detect aspect ratio from marketing ──
        if not aspect_ratio and marketing and "ratio" in marketing:
            aspect_ratio = marketing["ratio"].split(" or ")[0]
        
        # ── Model recommendation ──
        model_rec = self._recommend_model(norm_cat, goal, structure)
        
        # ── Build the prompt by structure ──
        if structure == "JSON":
            prompt_text = self._generate_json_v2(goal, norm_cat, templates, similar, 
                                                  techniques, style, aspect_ratio, photo, marketing, mood)
        elif structure == "Template":
            prompt_text = self._generate_template_v2(goal, norm_cat, templates, similar,
                                                      techniques, style, aspect_ratio, photo, marketing, mood)
        else:
            prompt_text = self._generate_flat_v2(goal, norm_cat, templates, similar,
                                                  techniques, style, aspect_ratio, photo, marketing, mood)
        
        # ── Quality score against corpus ──
        score = self._quality_score(prompt_text, norm_cat)
        
        return {
            "prompt": prompt_text,
            "model_recommendation": model_rec,
            "aspect_ratio": aspect_ratio or "1:1",
            "count": count,
            "quality_score": score,
            "intelligence": {
                "photography": photo is not None,
                "marketing": marketing is not None,
                "mood": mood[:80] + "..." if len(mood) > 80 else mood,
            },
            "source_prompt_ids": source_ids[:5],
            "length": len(prompt_text),
        }
    
    def _recommend_model(self, category: str, goal: str, structure: str) -> str:
        """Recommend the best Higgsfield model for the task."""
        goal_lower = goal.lower()
        
        # Photography-heavy → nano_banana_2
        if any(w in goal_lower for w in ["photo", "portrait", "selfie", "product shot", 
                                          "headshot", "profile pic", "real person"]):
            return "nano_banana_2"
        
        # Text/graphics-heavy → gpt_image_2
        if any(w in goal_lower for w in ["poster", "infographic", "thumbnail", "logo",
                                          "banner", "flyer", "ui", "dashboard", "dashboard",
                                          "diagram", "chart"]):
            return "gpt_image_2"
        
        # Category-based defaults
        cat_map = {
            "Profile / Avatar": "nano_banana_2",
            "Portrait / Selfie": "nano_banana_2",
            "E-commerce Main Image": "nano_banana_2",
            "App / Web Design": "gpt_image_2",
            "Infographic / Edu Visual": "gpt_image_2",
            "YouTube Thumbnail": "gpt_image_2",
            "Poster / Flyer": "gpt_image_2",
        }
        return cat_map.get(category, "gpt_image_2")
    
    def _quality_score(self, prompt_text: str, category: str) -> dict:
        """Score the generated prompt against corpus benchmarks."""
        # Get corpus benchmarks for this category
        c = self.conn.cursor()
        c.execute("""
            SELECT AVG(length_chars) as avg_len, 
                   AVG(tech_count) as avg_tech
            FROM (
                SELECT p.length_chars, COUNT(pt.technique) as tech_count
                FROM prompts p
                LEFT JOIN prompt_techniques pt ON p.id = pt.prompt_id
                WHERE p.has_prompt=1 AND p.categories LIKE ?
                GROUP BY p.id
            )
        """, (f"%{category}%",))
        bench = c.fetchone()
        
        avg_len = bench[0] if bench and bench[0] else 1500
        avg_tech = bench[1] if bench and bench[1] else 5.5
        
        # Score the generated prompt
        gen_len = len(prompt_text)
        gen_techs = detect_techniques(prompt_text)
        gen_tech_count = len(gen_techs)
        
        # Length score (0-40): ratio to corpus average, capped at 1.5x
        len_ratio = min(gen_len / avg_len, 1.5)
        len_score = int(len_ratio / 1.5 * 40)
        
        # Technique score (0-30): ratio to corpus average
        tech_ratio = min(gen_tech_count / max(avg_tech, 1), 1.5)
        tech_score = int(tech_ratio / 1.5 * 30)
        
        # Specificity score (0-30): based on domain vocabulary density
        specificity_words = [
            "camera", "lens", "f/", "mm", "lighting", "softbox", "beauty dish",
            "golden hour", "depth of field", "bokeh", "color", "palette",
            "texture", "material", "matte", "glossy", "composition",
            "negative space", "rule of thirds", "golden ratio",
            "mood", "atmosphere", "cinematic", "vibrant",
            "studio", "rim light", "key light", "fill",
            "background", "gradient", "shadow",
        ]
        prompt_lower = prompt_text.lower()
        spec_count = sum(1 for w in specificity_words if w in prompt_lower)
        spec_score = min(int(spec_count / 15 * 30), 30)
        
        total = len_score + tech_score + spec_score
        
        return {
            "total": total,
            "grade": "A+" if total >= 85 else "A" if total >= 75 else "B" if total >= 60 else "C" if total >= 40 else "D",
            "length_score": len_score,
            "technique_score": tech_score,
            "specificity_score": spec_score,
            "generated_length": gen_len,
            "corpus_avg_length": int(avg_len),
            "generated_techniques": gen_tech_count,
            "corpus_avg_techniques": round(avg_tech, 1),
        }
    
    # ═══════════════════════════════════════════════════════════════
    # V2 GENERATORS — Corpus-grounded + Intelligence-enhanced
    # ═══════════════════════════════════════════════════════════════
    
    def _generate_template_v2(self, goal, category, templates, similar,
                               techniques, style, aspect_ratio, photo, marketing, mood):
        """
        RAG-based template generation.
        Retrieves the best matching REAL corpus prompt, then adapts it
        with the user's goal, style, and intelligence layer specifics.
        """
        # ── Step 1: Find the best real template to adapt ──
        best_template = None
        
        # Prefer templates from FTS search (semantically matched to goal)
        if similar:
            for p in similar:
                if p.structure_type == "Template" and p.length_chars > 800:
                    best_template = p
                    break
        
        # Fall back to category templates
        if not best_template and templates:
            for p in templates:
                if p.structure_type == "Template" and p.length_chars > 800:
                    best_template = p
                    break
        
        # ── Step 2: Extract the STRUCTURE from the real prompt ──
        if best_template:
            # Get the structure pattern (section headers, argument layout, canvas specs)
            real_text = best_template.prompt_text
            
            # Extract section structure (Goal:, Canvas:, Layout:, etc.)
            sections = self._extract_sections(real_text)
            
            # Extract argument names used in the real prompt
            real_args = re.findall(r'\{argument\s+name="([^"]+)"\s+default="([^"]*)"\}', real_text)
            
            # ── Step 3: Synthesize new prompt using real structure + intelligence ──
            return self._synthesize_template(goal, style, aspect_ratio, sections, 
                                              real_args, photo, marketing, mood, category)
        
        # ── Fallback: Build from intelligence if no good template found ──
        return self._build_from_intelligence(goal, style, aspect_ratio, 
                                              photo, marketing, mood, category)
    
    def _extract_sections(self, text: str) -> list:
        """Extract section headers and their content from a corpus prompt."""
        sections = []
        # Common section headers in corpus: Goal:, Canvas:, Layout:, Main subject:, etc.
        pattern = r'^([A-Z][A-Za-z\s]+):\s*(.+?)(?=\n[A-Z][A-Za-z\s]+:|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        for header, content in matches:
            sections.append((header.strip(), content.strip()[:300]))
        return sections
    
    def _synthesize_template(self, goal, style, aspect_ratio, sections, real_args,
                              photo, marketing, mood, category):
        """Synthesize a new template prompt from real structure + intelligence.
        Generates GOAL-SPECIFIC arguments instead of copying source template's args."""
        lines = []
        
        # ── Arguments block (goal-specific, NOT copied from source) ──
        # Only include arguments that are universally useful for this goal
        # Generate from the goal itself, not from the source template
        goal_lower = goal.lower()
        
        # Determine which argument types are relevant based on goal content
        relevant_args = []
        
        # Always include style/aesthetic argument
        relevant_args.append(("aesthetic", style or "modern, clean, professional"))
        
        # Color palette if mentioned or inferred
        if any(w in goal_lower for w in ["cream", "dark", "color", "palette", "theme", "warm", "amber", "sepia"]):
            relevant_args.append(("color_palette", style or "warm earth tones"))
        
        # Layout type if mentioned
        if any(w in goal_lower for w in ["grid", "card", "masonry", "timeline", "hero", "gallery", "layout"]):
            relevant_args.append(("layout", "responsive grid with consistent spacing"))
        
        # Typography if mentioned
        if any(w in goal_lower for w in ["arabic", "text", "typography", "heading", "font", "naskh"]):
            relevant_args.append(("typography", "classical naskh for Arabic, clean sans-serif for Latin text"))
        
        # Device/view if mentioned
        if any(w in goal_lower for w in ["mobile", "phone", "desktop", "tablet", "responsive"]):
            relevant_args.append(("viewport", "desktop 1440px or mobile 390px"))
        
        for arg_name, default in relevant_args:
            lines.append(f'{{argument name="{arg_name}" default="{default}"}}')
        
        # ── Goal directive ──
        lines.append(f"\nGoal: Create {goal}")
        if style:
            lines.append(f"Style: {style}")
        
        # ── Canvas spec (from marketing intelligence) ──
        if marketing and "ratio" in marketing:
            lines.append(f"\nCanvas: {aspect_ratio or marketing['ratio'].split(' or ')[0]} aspect ratio")
            if "safe_zones" in marketing:
                lines.append(f"Safe zones: {marketing['safe_zones']}")
        elif aspect_ratio:
            lines.append(f"\nCanvas: {aspect_ratio} aspect ratio")
        else:
            lines.append(f"\nCanvas: 16:9 aspect ratio (web desktop)")
        
        # ── Design specs (for UI/web categories) vs Photography (for photo categories) ──
        non_photo_categories = ["App / Web Design", "Infographic / Edu Visual", 
                                 "YouTube Thumbnail", "Comic / Storyboard", "Game Asset"]
        if category in non_photo_categories:
            lines.append("\nDesign system: clean component-based UI, 8px spacing grid, "
                         "consistent border-radius (8-12px), soft layered shadows for depth, "
                         "generous whitespace, clear visual hierarchy with 3 weight levels")
            lines.append("Typography: well-defined type scale, proper line-height, "
                         "readable contrast ratios (WCAG AA), harmonious letter-spacing")
            lines.append("Materials: subtle frosted-glass panels where appropriate, "
                         "micro-gradients for depth, fine noise texture overlay for warmth")
        elif photo:
            lines.append(f"\nCamera: {photo['camera']}, {photo['lens']}")
            lines.append(f"Lighting: {photo['lighting']}")
            lines.append(f"Color science: {photo['color_science']}")
            lines.append(f"Background: {photo['background']}")
            lines.append(f"Post-processing: {photo['post']}")
        
        # ── Mood ──
        if mood:
            lines.append(f"\nMood: {mood}")
        
        # ── Marketing framework ──
        if marketing:
            lines.append(f"\nMarketing framework: {marketing['framework']}")
            if "attention" in marketing:
                lines.append(f"Attention layer: {marketing['attention']}")
            if "desire" in marketing:
                lines.append(f"Desire layer: {marketing['desire']}")
        
        # ── Composition & quality ──
        lines.append(f"\nComposition: rule of thirds with negative space for content. "
                      f"Visual hierarchy guides eye from hero element through supporting details. "
                      f"Consistent alignment, intentional spacing, balanced negative space.")
        lines.append("Quality: 8K resolution, commercial-grade, color-calibrated, "
                      "pixel-perfect rendering. No watermark, no artifacts, no text errors.")
        
        return "\n".join(lines)
    
    def _build_from_intelligence(self, goal, style, aspect_ratio,
                                  photo, marketing, mood, category):
        """Build a prompt from scratch using intelligence layers when no template matches."""
        lines = [f"\nGoal: Create {goal}"]
        if style:
            lines.append(f"Style: {style}")
        
        if photo:
            lines.append(f"\nCamera: {photo['camera']}, {photo['lens']}")
            lines.append(f"Lighting: {photo['lighting']}")
            lines.append(f"Color science: {photo['color_science']}")
            lines.append(f"Background: {photo['background']}")
            lines.append(f"Post-processing: {photo['post']}")
        
        if mood:
            lines.append(f"\nMood: {mood}")
        
        if marketing:
            lines.append(f"\nFormat: {marketing['framework']} framework, {marketing['ratio']}")
            lines.append(f"Attention: {marketing['attention']}")
        
        lines.append(f"\nAspect ratio: {aspect_ratio or '1:1'}")
        lines.append("Quality: 8K, professional, commercial-grade. No watermark.")
        
        return "\n".join(lines)
    
    def _generate_flat_v2(self, goal, category, templates, similar,
                           techniques, style, aspect_ratio, photo, marketing, mood):
        """
        Dense flat prose with full photography/marketing/art intelligence.
        Produces 800-2000 char paragraphs matching corpus quality.
        """
        parts = []
        
        # ── Opening: Subject + style ──
        parts.append(goal)
        if style:
            parts.append(style)
        
        # ── Photography details (skip for non-photo categories) ──
        non_photo_categories = ["App / Web Design", "Infographic / Edu Visual", 
                                 "YouTube Thumbnail", "Comic / Storyboard", "Game Asset"]
        if photo and category not in non_photo_categories:
            parts.append(f"Shot on {photo['camera']} with {photo['lens']}")
            parts.append(photo['lighting'])
            parts.append(f"Color science: {photo['color_science']}")
            parts.append(f"{photo['background']}")
        
        # ── Mood ──
        if mood:
            parts.append(f"Mood: {mood}")
        
        # ── Composition ──
        parts.append("Rule of thirds composition with deliberate negative space for text overlay. "
                      "Visual hierarchy leads the eye from hero subject through supporting elements. "
                      "Strong diagonal or converging lines create depth and guide attention.")
        
        # ── Material/texture detail ──
        parts.append("Detailed material specification — surface textures rendered with micro-detail, "
                      "accurate light interaction on matte and glossy surfaces, realistic reflections and caustics. "
                      "Color-calibrated for accurate reproduction across print and digital.")
        
        # ── Marketing layer ──
        if marketing:
            parts.append(f"Optimized for {marketing['framework']} marketing framework. "
                          f"{marketing['attention']} {marketing.get('desire', '')}")
        
        # ── Quality directives ──
        parts.append("8K resolution, hyper-detailed, professional commercial quality. "
                      "No watermark, no artifacts, no text errors. Color-accurate and print-ready.")
        
        # ── Aspect ratio ──
        if aspect_ratio:
            parts.append(f"--ar {aspect_ratio}")
        
        # ── Negative prompt ──
        parts.append("Avoid: blurry, low quality, distorted proportions, oversaturated colors, "
                      "artificial-looking lighting, text rendering errors, watermarks, noise, grain (unless intentional)")
        
        return ". ".join(parts) + "."
    
    def _generate_json_v2(self, goal, category, templates, similar,
                           techniques, style, aspect_ratio, photo, marketing, mood):
        """
        Build a JSON prompt from scratch using the canonical schema from corpus analysis
        + intelligence layer content. NOT blind injection into a random template.
        """
        # Build canonical JSON structure (derived from corpus analysis):
        # type(92%) → layout(74%) → style(62%) → subject(30%) → composition(20%)
        result = {
            "type": goal,
            "format": f"professional {category.lower()} image",
            "style": style or "modern, clean, professional",
        }
        
        # ── Aspect ratio ──
        if aspect_ratio or (marketing and "ratio" in marketing):
            result["aspect_ratio"] = aspect_ratio or marketing["ratio"].split(" or ")[0]
        
        # ── Layout (from corpus: 74% of JSON prompts have this) ──
        result["layout"] = {
            "composition": "rule of thirds with negative space for text overlay",
            "visual_hierarchy": "hero element in upper third, supporting details in middle, CTA zone in bottom 15%",
            "focal_point": goal,
        }
        
        # ── Photography (skip for non-photography categories) ──
        non_photo_categories = ["App / Web Design", "Infographic / Edu Visual", 
                                 "YouTube Thumbnail", "Comic / Storyboard", "Game Asset"]
        if photo and category not in non_photo_categories:
            result["camera"] = {
                "body": photo["camera"],
                "lens": photo["lens"],
                "lighting": photo["lighting"],
                "color_science": photo["color_science"],
            }
            result["background"] = photo["background"]
            result["post_processing"] = photo["post"]
        elif category in non_photo_categories:
            # UI/Graphics categories get design specs instead of photography
            result["design"] = {
                "rendering": "high-fidelity, pixel-perfect, production-ready",
                "lighting": "soft ambient gradient with subtle vignette, directional highlight on hero element",
                "materials": "glassmorphism surfaces with backdrop blur, subtle frosted glass panels, soft drop shadows with 10% opacity",
                "typography": "clean sans-serif system font, clear hierarchy with 3 weight levels (400/600/800), consistent line-height",
                "spacing": "8px grid system, consistent padding, generous whitespace between sections",
            }
            result["background"] = "dark mode canvas (#0A0A0F) with subtle radial gradient glow behind hero element, fine noise texture for depth"
        
        # ── Mood ──
        if mood:
            result["mood"] = mood
        
        # ── Marketing ──
        if marketing:
            result["marketing"] = {
                "framework": marketing["framework"],
                "attention": marketing["attention"],
                "desire": marketing.get("desire", ""),
                "safe_zones": marketing.get("safe_zones", ""),
            }
        
        # ── Quality ──
        result["quality"] = {
            "resolution": "8K",
            "standard": "commercial-grade, color-calibrated",
            "constraints": "no watermark, no artifacts, no text rendering errors",
        }
        
        return json.dumps(result, indent=2)

    def _generate_json(self, goal, category, templates, techniques, style) -> str:
        # Pick the best template (longest JSON = most complete)
        json_templates = [t for t in templates if t.structure_type == "JSON"]
        if not json_templates:
            json_templates = [t for t in templates if t.prompt_text.strip().startswith("{")]
        if not json_templates and templates:
            json_templates = templates
        
        if json_templates:
            # Sort by length descending (most detailed first)
            json_templates.sort(key=lambda t: t.length_chars, reverse=True)
            template = json_templates[0].prompt_text
            try:
                parsed = json.loads(template)
                if "type" in parsed:
                    parsed["type"] = goal
                if style and "style" in parsed:
                    parsed["style"] = style
                return json.dumps(parsed, indent=2)
            except:
                pass
        
        return json.dumps({
            "type": goal,
            "style": style or "Modern, clean, professional",
            "layout": {"grid": "responsive", "spacing": "consistent"},
            "components": []
        }, indent=2)

    def _generate_template(self, goal, category, templates, techniques, style, aspect_ratio) -> str:
        # Build template with arguments
        args = {
            "subject": goal,
            "style": style or "Modern, professional",
            "composition": "Centered, balanced, rule of thirds",
            "lighting": "Soft studio lighting",
            "color_palette": "Professional brand colors",
        }
        
        # Add category-specific args
        if "Product" in category:
            args.update({"product": goal, "hero_shot": "Product hero on clean background", "accent_color": "Brand accent"})
        elif "App" in category or "Web" in category:
            args.update({"screen": f"{goal} interface", "theme": "Light/dark mode", "components": "Dashboard, sidebar, cards"})
        elif "Poster" in category:
            args.update({"headline": goal.upper(), "subheadline": "Supporting tagline", "details": "Date, venue, info"})
        elif "Social" in category:
            args.update({"hook": goal, "vibe": "Engaging, shareable", "cta": "Link in bio"})
        
        # Build template
        lines = []
        for name, default in args.items():
            lines.append(f'{{argument name="{name}" default="{default}"}}')
        
        # Core prompt
        core = f"{goal}, {style}, professional quality"
        if aspect_ratio:
            core += f" --ar {aspect_ratio}"
        
        return "\n".join(lines) + "\n\n" + core

    def _generate_flat(self, goal, category, templates, techniques, style, aspect_ratio) -> str:
        # Build flat prose prompt
        parts = [goal]
        if style:
            parts.append(style)
        
        # Add technique-based directives
        technique_phrases = {
            "Lighting details": "professional lighting setup",
            "Camera specs": "85mm f/1.4, shallow depth of field",
            "Color palette": "harmonious color palette",
            "Material/Texture": "detailed textures and materials",
            "Typography": "clean typography hierarchy",
            "Layout/Composition": "balanced composition, rule of thirds",
            "Mood/Atmosphere": "cinematic atmosphere",
        }
        
        for tech in techniques:
            if tech in technique_phrases:
                parts.append(technique_phrases[tech])
        
        if aspect_ratio:
            parts.append(f"--ar {aspect_ratio}")
        
        return ", ".join(parts) + "."

    def stats(self) -> dict:
        """Corpus-wide statistics."""
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM prompts WHERE has_prompt=1")
        total = c.fetchone()[0]
        
        c.execute("SELECT model, COUNT(*) FROM prompts WHERE has_prompt=1 GROUP BY model")
        models = dict(c.fetchall())
        
        c.execute("SELECT structure_type, COUNT(*) FROM prompts WHERE has_prompt=1 GROUP BY structure_type")
        structures = dict(c.fetchall())
        
        c.execute("SELECT technique, COUNT(*) FROM prompt_techniques GROUP BY technique ORDER BY COUNT(*) DESC")
        techniques = dict(c.fetchall())
        
        return {
            "total_prompts": total,
            "models": models,
            "structures": structures,
            "techniques": techniques,
        }

    def compare_models(self, model1: str, model2: str) -> dict:
        """Compare two models' prompt patterns."""
        c = self.conn.cursor()
        result = {}
        
        for model in [model1, model2]:
            c.execute("""
                SELECT structure_type, COUNT(*) as cnt 
                FROM prompts WHERE has_prompt=1 AND model LIKE ?
                GROUP BY structure_type ORDER BY cnt DESC
            """, (f"%{model}%",))
            result[model] = {"structures": dict(c.fetchall())}
            
            c.execute("""
                SELECT technique, COUNT(*) as cnt
                FROM prompt_techniques pt
                JOIN prompts p ON pt.prompt_id = p.id
                WHERE p.has_prompt=1 AND p.model LIKE ?
                GROUP BY technique ORDER BY cnt DESC LIMIT 10
            """, (f"%{model}%",))
            result[model]["top_techniques"] = dict(c.fetchall())
            
            c.execute("""
                SELECT categories, COUNT(*) as cnt
                FROM prompts WHERE has_prompt=1 AND model LIKE ?
                GROUP BY categories ORDER BY cnt DESC LIMIT 10
            """, (f"%{model}%",))
            result[model]["top_categories"] = dict(c.fetchall())
        
        return result

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

# ─── MAIN / CLI ───
if __name__ == "__main__":
    import sys
    hpm = HiggsfieldPromptMaster()
    
    if len(sys.argv) < 2:
        print("Usage: python3 -m higgsfield_prompt <command> [args]")
        print("Commands: search, guide, generate, stats, enrich, random")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "search":
        q = sys.argv[2] if len(sys.argv) > 2 else ""
        results = hpm.search(query=q, limit=5)
        for p in results:
            print(f"[{p.id}] {p.title[:60]} ({p.structure_type}, {p.length_chars} chars)")
            print(f"    {p.prompt_text[:120]}...\n")
    
    elif cmd == "guide":
        cat = sys.argv[2] if len(sys.argv) > 2 else "App / Web Design"
        guide = hpm.category_guide(cat)
        print(json.dumps(guide, indent=2, default=str))
    
    elif cmd == "generate":
        goal = sys.argv[2] if len(sys.argv) > 2 else "SaaS dashboard"
        cat = sys.argv[3] if len(sys.argv) > 3 else "App / Web Design"
        struct = sys.argv[4] if len(sys.argv) > 4 else "Template"
        print(hpm.generate_prompt(goal, cat, struct))
    
    elif cmd == "stats":
        print(json.dumps(hpm.stats(), indent=2))
    
    elif cmd == "enrich":
        hpm.enrich_all()
    
    elif cmd == "random":
        cat = sys.argv[2] if len(sys.argv) > 2 else ""
        p = hpm.random_prompt(category=cat)
        if p:
            print(f"[{p.id}] {p.title}")
            print(p.prompt_text[:500])
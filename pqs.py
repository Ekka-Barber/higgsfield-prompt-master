#!/usr/bin/env python3
"""
PQS — Prompt Quality Score (US-014)
====================================
Text-only prompt scorer implemented per research/prompt-quality-evaluation.md §8.1.

    PQS = 100 * (C^0.20 * S^0.20 * A^0.20 * R^0.10 * G^0.30) * (1 - X)

  C  slot coverage       — typed slot schema, per-category required masks,
                           modified-noun phrases (never bare tokens)
  S  specificity         — corpus IDF (AvIDF) + Simplified Clarity Score,
                           pre-retrieval QPP predictors over the prompt corpus
  A  atomic density      — distinct (modifier, noun) / (noun, prep, noun)
                           assertions per word; the second factor is the
                           anti-padding term (length without atoms hurts)
  R  non-redundancy      — distinct-3 trigrams + gzip compression ratio
  G  goal fidelity       — IDF-weighted recall of the user's goal in the
                           prompt (the duplication-bug detector, weight 0.30)
  X  contradiction/vagueness penalty (multiplicative, cap 0.5)

Grades are percentiles against the corpus PQS distribution (A+ >= p90,
A >= p75, B >= p50, C >= p25, D < p25) — no hardcoded score cutoffs.
The distribution, DF table and normalization percentiles live in
pqs_calibration.json, built by scripts/calibrate_pqs.py.

Pure stdlib (gzip, math, re, json, bisect, collections). The research's
optional Brysbaert-concreteness arm is omitted (external CSV); S keeps the
research's IDF:SCS 0.4:0.3 ratio, rescaled to 4/7 and 3/7.
"""
import bisect
import gzip
import json
import math
import re
from collections import Counter
from pathlib import Path

CALIBRATION_PATH = Path(__file__).resolve().parent / "pqs_calibration.json"

WEIGHTS = {"coverage": 0.20, "specificity": 0.20, "atomic_density": 0.20,
           "non_redundancy": 0.10, "goal_fidelity": 0.30}
_S_W_IDF, _S_W_SCS = 0.4 / 0.7, 0.3 / 0.7  # research 0.4/0.3 minus concreteness arm

TOKEN_RE = re.compile(r"[a-z0-9']+")

STOP = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "while",
    "of", "at", "by", "for", "with", "about", "against", "between", "into",
    "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "once", "here", "there", "all", "any", "both", "each", "every", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "can", "will", "just", "should", "now",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "having", "do", "does", "did", "doing", "would", "could", "i", "you", "he",
    "she", "it", "we", "they", "them", "his", "her", "its", "our", "their",
    "this", "that", "these", "those", "what", "which", "who", "whom", "as",
    "until", "because", "s", "t", "don", "ve", "ll", "re", "m", "also",
    "without", "onto", "upon", "within", "across", "toward", "towards", "like",
    "atop", "via", "per", "using", "use", "used", "include", "includes",
    "including", "create", "creating", "created", "make", "makes", "made",
}

VAGUE_WORDS = {"beautiful", "nice", "detailed", "4k", "8k", "masterpiece",
               "stunning", "amazing", "various", "some", "professional"}
VAGUE_PHRASES = ("high quality", "highly detailed", "top quality", "best quality",
                 "ultra detailed", "extremely detailed", "ultra realistic")

MUTEX = [
    {"golden hour", "studio softbox", "moonlight", "overcast"},
    {"daytime", "night", "dusk"},
    {"photograph", "3d render", "watercolor", "vector illustration", "oil painting"},
    {"no text", "headline reads", "caption reads"},
]

# ─── tokenization / lemmatization ──────────────────────────────────────────

def _lem(w: str) -> str:
    if w.endswith("'s"):
        w = w[:-2]
    for suf, rep in (("ies", "y"), ("sses", "ss"), ("xes", "x"),
                     ("ches", "ch"), ("shes", "sh")):
        if w.endswith(suf) and len(w) > len(suf):
            return w[:-len(suf)] + rep
    if w.endswith("s") and not w.endswith(("ss", "us", "is")) and len(w) > 3:
        return w[:-1]
    return w


def tokenize(text: str) -> list:
    return TOKEN_RE.findall(text.lower())


def _content_lemmas(tokens) -> list:
    return [_lem(t) for t in tokens if t.isalpha() and t not in STOP]


def _goal_terms(goal: str) -> set:
    return {t for t in _content_lemmas(tokenize(goal))}


# ─── slot coverage (C) ─────────────────────────────────────────────────────

REQUIRED = {
    "Portrait / Selfie": {"subject", "subject_attrs", "lighting", "composition",
                          "style_medium", "technical"},
    "App / Web Design": {"subject", "setting", "composition", "color",
                         "style_medium", "text_in_image", "constraints_negative"},
    "Product Marketing": {"subject", "subject_attrs", "lighting", "setting",
                          "composition", "color", "technical"},
    "Infographic / Edu Visual": {"subject", "composition", "color",
                                 "style_medium", "text_in_image"},
}
DEFAULT_REQUIRED = {"subject", "subject_attrs", "composition", "lighting",
                    "style_medium", "technical"}

_MOD_BAD = STOP


def _mod_head(low: str, heads: str) -> bool:
    # a slot is filled by a MODIFIED noun phrase, never a bare head token
    for m in re.finditer(rf"\b([a-z][a-z-]+)\s+(?:{heads})\b", low):
        if m.group(1) not in _MOD_BAD:
            return True
    return False


def _phrase(low: str, alts: str) -> bool:
    return re.search(rf"\b(?:{alts})\b", low) is not None


_SETTING_HEADS = (
    r"background|backdrop|foreground|scene|setting|environment|studio|street|"
    r"city|cityscape|forest|woods|beach|desert|ocean|sea|sky|skyline|office|"
    r"room|interior|cafe|stage|garden|library|laboratory|marketplace|alley|"
    r"rooftop|terrace|balcony|kitchen|bedroom|workshop|factory|stadium|valley|"
    r"canyon|field|meadow|river|lake|waterfall|cliff|coast|harbor|port|airport|"
    r"station|museum|gallery|temple|church|castle|village|town|landscape|"
    r"terrain|mountains?|countryside|seaside|boardwalk|courtyard|plaza|mall|"
    r"restaurant|bar|cafe|bistro|bakery|gym|spa|salon|clinic|classroom|campus"
)
_ATTR_HEADS = (
    r"skin|hair|hairs|eyes|eye|beard|mustache|outfit|attire|clothing|fabric|"
    r"textures?|expression|face|features|wardrobe|costume|jewelry|jewellery|"
    r"accessor(?:y|ies)|tattoos?|freckles|makeup|complexion|wrinkles|nails|"
    r"footwear|gloves|scarf|hat|cap|helmet|armor|armour|dress|suit|jacket|"
    r"coat|uniform|gown|thobe|ghutra|shemagh|heels|sneakers|boots|eyewear|"
    r"glasses|sunglasses|haircut|hairstyle|piercings?"
)
_LIGHT_HEADS = (
    r"lights?|lighting|lit|glow|backlight|backlit|illuminated|sunlight|"
    r"moonlight|skylight|streetlight|spotlight|highlights?|shadows?|sheen|luster"
)
_LIGHT_PHRASES = (
    r"golden hour|blue hour|softbox|soft box|beauty dish|rim light|rim lighting|"
    r"key light|fill light|practical light|volumetric|caustics|overcast|dawn|"
    r"dusk|twilight|sunrise|sunset|noon|candlelight|firelight|window light|"
    r"natural light|three-point|chiaroscuro|low-key|high-key|neon glow|"
    r"diffused light|ambient light|direct sunlight|shafts of light"
)
_COMP_HEADS = r"composition|framing|perspective|angle|shot|crop|vantage"
_COMP_PHRASES = (
    r"close-up|closeup|wide shot|medium shot|full shot|cowboy shot|overhead|"
    r"top-down|top down|bird'?s-eye|worm'?s-eye|low angle|high angle|dutch "
    r"angle|eye level|macro|symmetr\w+|centered|off-center|rule of thirds|"
    r"leading lines|focal point|negative space|headroom|center frame|"
    r"off center|centered frame|portrait orientation|landscape orientation"
)
_COLOR_HEADS = r"tones|hues|palette|colors?|colours?|shades|tints"
_COLOR_PHRASES = (
    r"color palette|colour palette|color scheme|colour scheme|color grading|"
    r"colour grading|monochrome|monochromatic|grayscale|greyscale|pastel|"
    r"muted colou?rs|vibrant colou?rs|accent colou?r|shades of|tones of|"
    r"splashes? of colou?r|pops? of colou?r|gradient|ombr|earth tones|"
    r"jewel tones|neon colou?rs|duotone|tritone|sepia|washed out|color-blocked"
)
_STYLE_HEADS = r"style|aesthetic|vibe|look|treatment|finish"
_STYLE_PHRASES = (
    r"photographs?|photography|photographic|photo|illustrations?|illustrated|"
    r"drawing|sketch(?:es)?|paintings?|painted|watercolou?r|gouache|acrylic|"
    r"markers?|pencils?|charcoal|ink(?:ed)?|vector|flat design|3d render|"
    r"renders?|rendering|cgi|voxel|claymation|papercraft|collage|mixed media|"
    r"minimalist|brutalist|art deco|art nouveau|bauhaus|memphis|y2k|"
    r"cyberpunk|solarpunk|steampunk|retrofuturism|mid-century|baroque|"
    r"renaissance|impressionist|expressionist|surrealist|in the style of|"
    r"photorealistic|cartoon|anime|manga|comic|pixel art|isometric|wireframe|"
    r"blueprint|technical drawing|editorial|collage"
)
_TECH_PHRASES = (
    r"aspect ratio|--ar \S+|f/\d+(?:\.\d+)?|\d{1,3}mm|mm lens|aperture|"
    r"f-stop|f stop|depth of field|shallow depth|bokeh|resolution|4k|8k|16k|"
    r"ultra hd|uhd|octane|unreal engine|blender|redshift|v-ray|ray trac\w+|"
    r"subsurface scattering|pbr|hdr|iso \d+|shutter|focal length|telephoto|"
    r"wide-angle|macro lens|medium format|large format|film grain|grain|"
    r"megapixels?|\b\d{1,2}:\d{1,2}\b|portrait mode|long exposure|double "
    r"exposure|tilt-shift|anamorphic"
)
_NEG_PHRASES = (
    r"\bwithout\b|\bavoids?\b|\bavoiding\b|\bexcludes?\b|\bexcluding\b|"
    r"\blacking\b|\bdevoid\b|must not|do not|don't|free of|\bno\s+[a-z]+|"
    r"\bnone of\b|\bnot include"
)
_TEXT_PHRASES = (
    r"headline|caption|subtitle|tagline|lettering|wordmark|reads|inscribed|"
    r"engraved|title text|logo text|text reading|typography|quotable"
)


def _slot_subject(low: str, orig: str) -> bool:
    head = [w for w in tokenize(" ".join(low.split()[:14])) if len(w) > 2]
    return sum(1 for w in head if w not in STOP) >= 2


SLOT_CHECKS = {
    "subject": _slot_subject,
    "subject_attrs": lambda low, orig: _mod_head(low, _ATTR_HEADS)
                                     or _phrase(low, r"freckled|wrinkled|bare-?faced"),
    "action_pose": lambda low, orig: _phrase(
        low, r"standing|sitting|seated|walking|running|holding|carrying|looking|"
             r"gazing|leaning|posing|smiling|laughing|reaching|stretching|"
             r"wearing|reading|cooking|typing|dancing|jumping|lying|kneeling|"
             r"crouching|pointing|waving|sipping|browsing|skating|cycling|"
             r"swimming|climbing|painting|writing|presenting|gesturing|"
             r"arms crossed|hands clasped|over the shoulder|hand on"),
    "setting": lambda low, orig: _mod_head(low, _SETTING_HEADS),
    "composition": lambda low, orig: _mod_head(low, _COMP_HEADS)
                                    or _phrase(low, _COMP_PHRASES),
    "lighting": lambda low, orig: _mod_head(low, _LIGHT_HEADS)
                                  or _phrase(low, _LIGHT_PHRASES),
    "color": lambda low, orig: _mod_head(low, _COLOR_HEADS)
                               or _phrase(low, _COLOR_PHRASES),
    "style_medium": lambda low, orig: _mod_head(low, _STYLE_HEADS)
                                      or _phrase(low, _STYLE_PHRASES),
    "technical": lambda low, orig: _phrase(low, _TECH_PHRASES),
    "constraints_negative": lambda low, orig: _phrase(low, _NEG_PHRASES),
    "text_in_image": lambda low, orig: bool(
        re.search(r'"[^"\n]{1,80}"', orig)
        or re.search(r"\b[A-Z]{3,}\b", orig)
        or re.search(rf"\b(?:{_TEXT_PHRASES})\b", low)
    ),
}


def _coverage(low: str, orig: str, category: str) -> float:
    req = REQUIRED.get(category, DEFAULT_REQUIRED)
    return sum(1 for s in req if SLOT_CHECKS[s](low, orig)) / len(req)


# ─── atomic assertion density (A) — regex fallback, TIFA/DSG text half ─────

_MODIFIERS = (
    "soft", "warm", "cool", "dark", "bright", "matte", "glossy", "sleek",
    "bold", "subtle", "muted", "vibrant", "rich", "deep", "pale", "stark",
    "crisp", "smooth", "rough", "layered", "minimal", "ornate", "dense",
    "sparse", "sharp", "blurred", "clean", "rustic", "modern", "vintage",
    "retro", "futuristic", "classic", "elegant", "polished", "dramatic",
    "moody", "cheerful", "serene", "dynamic", "geometric", "organic",
    "angular", "rounded", "symmetrical", "translucent", "opaque", "iridescent",
    "holographic", "metallic", "wooden", "golden", "silver", "copper", "pastel",
    "earthy", "frosted", "etched", "embossed", "miniature", "giant", "tiny",
    "huge", "massive", "slim", "wide", "narrow", "tall", "short", "young",
    "elderly", "ancient", "intricate", "elaborate", "simplified", "stylized",
    "realistic", "hyperrealistic", "delicate", "luminous", "glowing",
    "reflective", "transparent", "solid", "hollow", "fluffy", "plush",
)
_COLORS = (
    "red", "orange", "yellow", "green", "blue", "purple", "violet", "indigo",
    "pink", "magenta", "cyan", "teal", "turquoise", "navy", "lavender",
    "beige", "cream", "ivory", "charcoal", "black", "white", "gray", "grey",
    "brown", "tan", "maroon", "olive", "khaki", "coral", "salmon", "amber",
    "jade", "ruby", "sapphire", "azure", "emerald",
)
_MOD_ALT = "|".join(re.escape(w) for w in _MODIFIERS + _COLORS)

_ATOM_PATTERNS = [
    # participle + noun ("weathered fisherman", "flowing hair")
    re.compile(r"\b[a-z]+(?:ed|ing)\s+([a-z]{3,})\b"),
    # adjective-suffix + noun ("vibrant" misses, "photographic style" hits)
    re.compile(r"\b[a-z]+(?:ful|ous|ive|ical|ic|ish|able|ible|less|esque)\s+([a-z]{3,})\b"),
    # modifier/color lexicon + noun
    re.compile(rf"\b(?:{_MOD_ALT})\s+([a-z]{{3,}})\b"),
    # counted noun ("three women", "8 badges")
    re.compile(r"\b(?:\d+(?:\.\d+)?|one|two|three|four|five|six|seven|eight|"
               r"nine|ten|eleven|twelve|dozens?)\s+([a-z]{3,})\b"),
    # preposition-linked noun pair ("fisherman on the dock")
    re.compile(r"\b([a-z]{3,})\s+(?:on|in|at|of|with|against|beside|near|under|"
               r"behind|along|across|above|below|beneath|upon|within|inside|"
               r"outside|amid|among)\s+(?:an?|the)?\s*([a-z]{3,})\b"),
]


def _count_atoms(low: str) -> int:
    atoms = set()
    for pat in _ATOM_PATTERNS:
        for m in pat.finditer(low):
            if any(g is not None and g in STOP for g in m.groups()):
                continue
            atoms.add(m.group(0))
    return len(atoms)


# ─── penalty (X) ───────────────────────────────────────────────────────────

_AR_RE = re.compile(r"\b\d{1,2}:\d{1,2}\b")


def _penalty(low: str, tokens) -> float:
    conflicts = sum(
        1 for grp in MUTEX
        if sum(1 for p in grp if re.search(rf"\b{re.escape(p)}\b", low)) > 1
    )
    ar_dupes = max(0, len(_AR_RE.findall(low)) - 1)
    vague = sum(1 for t in tokens if t in VAGUE_WORDS)
    vague += sum(len(re.findall(rf"\b{re.escape(p)}\b", low)) for p in VAGUE_PHRASES)
    return min(0.5, 0.12 * conflicts + 0.10 * ar_dupes
               + 2.0 * vague / max(len(tokens), 1))


# ─── idf-dependent statistics (S, G) ───────────────────────────────────────

def _clip01(v: float) -> float:
    return 0.0 if v < 0.0 else (1.0 if v > 1.0 else v)


def _avg_idf(content_set, idf) -> float:
    if not content_set:
        return 0.0
    return sum(idf(t) for t in content_set) / len(content_set)


def _scs(counts: Counter, N: int, df: dict) -> float:
    L = sum(counts.values())
    if not L:
        return 0.0
    total = 0.0
    for t, c in counts.items():
        p_ml = c / L
        p_coll = df.get(t, 0) / N
        total += p_ml * math.log2(p_ml / max(p_coll, 1e-9))
    return total


def _goal_fidelity(goal_set: set, prompt_set: set, idf) -> float:
    if not goal_set:
        return 1.0  # no goal signal -> neutral, not zero
    num = sum(idf(t) for t in goal_set if t in prompt_set)
    den = sum(idf(t) for t in goal_set)
    return num / max(den, 1e-9)


# ─── raw component extraction (shared by scorer + calibration) ─────────────

def _raw(text: str, category: str) -> dict:
    low = text.lower()
    tokens = TOKEN_RE.findall(low)
    content = _content_lemmas(tokens)
    tris = list(zip(tokens, tokens[1:], tokens[2:]))
    raw_bytes = text.encode("utf-8", "ignore")
    return {
        "category": category,
        "words": len(tokens) or 1,
        "counts": Counter(content),
        "content_set": set(content),
        "atoms": _count_atoms(low),
        "d3": len(set(tris)) / max(len(tris), 1),
        "cr": len(raw_bytes) / max(len(gzip.compress(raw_bytes)), 1),
        "cov": _coverage(low, text, category),
        "x": _penalty(low, tokens),
    }


def _factors(raw: dict, goal_set: set, idf, gl: dict):
    avidf = _avg_idf(raw["content_set"], idf)
    scs = _scs(raw["counts"], gl["N"], gl["df"])
    s = (_S_W_IDF * _clip01(avidf / gl["avidf_p90"])
         + _S_W_SCS * _clip01(scs / gl["scs_p90"]))
    t_cat = gl["T"].get(raw["category"], gl["T_all"])
    a = (min(1.0, raw["atoms"] / max(t_cat, 1.0))
         * min(1.0, (raw["atoms"] / raw["words"]) / gl["rho"]))
    span = gl["cr_p90"] - gl["cr_p10"]
    cr_term = 0.5 if span < 1e-9 else _clip01((gl["cr_p90"] - raw["cr"]) / span)
    r = 0.6 * raw["d3"] + 0.4 * cr_term
    g = _goal_fidelity(goal_set, raw["content_set"], idf)
    return {"coverage": raw["cov"], "specificity": s, "atomic_density": a,
            "non_redundancy": r, "goal_fidelity": g}, raw["x"]


def _pqs_total(factors: dict, x: float) -> float:
    prod = 1.0
    for name, w in WEIGHTS.items():
        prod *= max(factors[name], 0.01) ** w
    return 100.0 * prod * (1.0 - min(x, 0.5))


# ─── calibration ───────────────────────────────────────────────────────────

def _pct(sorted_vals, p: float) -> float:
    if not sorted_vals:
        return 0.0
    return sorted_vals[min(len(sorted_vals) - 1, int(p * len(sorted_vals)))]


def build_calibration(conn, searchable: str) -> dict:
    """Score the whole corpus once (goal proxy = row title) and store the
    per-category PQS distribution plus the DF table and normalization
    percentiles. Pure reads; caller persists the result."""
    from time import strftime
    rows = conn.execute(
        f"SELECT title, prompt_text, categories FROM prompts WHERE {searchable}"
    ).fetchall()

    raws, cats = [], []
    df = Counter()
    for r in rows:
        cat = (r["categories"] or "").split("|")[0].strip() or "Uncategorized"
        raw = _raw(r["prompt_text"] or "", cat)
        raws.append(raw)
        cats.append(cat)
        for t in raw["content_set"]:
            df[t] += 1

    N = len(raws) or 1
    df = dict(df)

    def idf(t):
        return math.log(N / (1 + df.get(t, 0)))

    avidfs = sorted(_avg_idf(r["content_set"], idf) for r in raws)
    scss = sorted(_scs(r["counts"], N, df) for r in raws)
    crs = sorted(r["cr"] for r in raws)
    densities = sorted(r["atoms"] / r["words"] for r in raws)
    atoms_by_cat = {}
    for r in raws:
        atoms_by_cat.setdefault(r["category"], []).append(r["atoms"])
    T = {c: sorted(v)[len(v) // 2] for c, v in atoms_by_cat.items()}
    all_atoms = sorted(a for v in atoms_by_cat.values() for a in v)

    gl = {
        "N": N,
        "df": df,
        "avidf_p90": _pct(avidfs, 0.90) or 1.0,
        "scs_p90": _pct(scss, 0.90) or 1.0,
        "cr_p10": _pct(crs, 0.10),
        "cr_p90": _pct(crs, 0.90),
        "rho": _pct(densities, 0.25) or 0.01,
        "T": T,
        "T_all": all_atoms[len(all_atoms) // 2] if all_atoms else 10,
    }

    dist = {"_all": []}
    for r, cat, row in zip(raws, cats, rows):
        factors, x = _factors(r, _goal_terms(row["title"] or ""), idf, gl)
        total = round(_pqs_total(factors, x), 1)
        dist.setdefault(cat, []).append(total)
        dist["_all"].append(total)
    dist = {c: sorted(v) for c, v in dist.items()}

    return {
        "pqs": "US-014",
        "built": strftime("%Y-%m-%d"),
        "n_prompts": N,
        "global": {k: v for k, v in gl.items() if k != "df"},
        "df": df,
        "dist": dist,
    }


# ─── scorer ────────────────────────────────────────────────────────────────

_CACHED = None


class PQSScorer:
    """Loads pqs_calibration.json once per process; falls back to an
    in-memory build from the live DB when the file is absent."""

    def __init__(self, conn=None, searchable: str = "has_prompt = 1"):
        global _CACHED
        if _CACHED is None:
            if CALIBRATION_PATH.exists():
                with CALIBRATION_PATH.open(encoding="utf-8") as f:
                    _CACHED = json.load(f)
            elif conn is not None:
                import sys
                print("pqs: calibration file missing — building in memory "
                      "(run scripts/calibrate_pqs.py to persist)", file=sys.stderr)
                _CACHED = build_calibration(conn, searchable)
            else:
                raise FileNotFoundError(
                    f"{CALIBRATION_PATH} not found and no connection given")
        calib = _CACHED
        gl = dict(calib["global"])
        gl["df"] = calib["df"]
        self._gl = gl
        self._dist = calib["dist"]

    def _idf(self, t: str) -> float:
        g = self._gl
        return math.log(g["N"] / (1 + g["df"].get(t, 0)))

    def score(self, prompt_text: str, category: str, goal: str = "") -> dict:
        raw = _raw(prompt_text, category)
        factors, x = _factors(raw, _goal_terms(goal), self._idf, self._gl)
        total = _pqs_total(factors, x)

        arr = self._dist.get(category) or self._dist["_all"]
        pct = bisect.bisect_left(arr, total) / max(len(arr), 1) * 100.0
        grade = ("A+" if pct >= 90 else "A" if pct >= 75 else "B" if pct >= 50
                 else "C" if pct >= 25 else "D")
        return {
            "total": int(round(total)),
            "grade": grade,
            "percentile": round(pct, 1),
            "factors": {k: round(v, 3) for k, v in factors.items()},
            "penalty": round(x, 3),
            "atoms": raw["atoms"],
            "words": raw["words"],
            "pqs_version": "US-014",
        }

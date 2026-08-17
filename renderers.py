#!/usr/bin/env python3
"""
Per-model prose renderers — US-012.

Both target models are prose-renderers (SOURCE_TRUTH §1): the engine keeps a
structured IR (ir.PromptIR) and renders it to cohesive prose per vendor style.
Vendor guidance comes from intelligence.GPT_IMAGE_2 / NANO_BANANA_PRO
(rebuilt from official docs, US-005/US-006):

- render_gpt_image_2: cohesive paragraph, front-loaded subject, 7 facets
  (Subject/Medium/Environment/Lighting/Color/Mood/Composition), inline
  "without X" exclusions (no negative_prompt param exists), double-quotes +
  ALL CAPS text levers, size heuristics (1024x1024 social / 1024x1536
  posters+stories / 1536x1024 banners+hero).
- render_nano_banana_pro: narrative scene description (keyword lists won't
  cut it), camera language welcome, semantic positive rewrites for negatives
  (never bare "no X"), ordinal + role reference addressing.

Neither renderer emits booster tokens (no efficacy evidence, SOURCE_TRUTH §8),
REFERENCE_N syntax, or word-limit folklore (no numeric word limits exist).
"""

import re

try:
    from ir import PromptIR, _match_slot
except ImportError:  # US-025: packaged layout
    from .ir import PromptIR, _match_slot

# ─── SHARED CLEANUP ─────────────────────────────────────────────────────────

_ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh",
             "eighth", "ninth", "tenth", "eleventh", "twelfth", "thirteenth",
             "fourteenth", "fifteenth", "sixteenth")

# ponytail: fixed booster list from SOURCE_TRUTH §8 examples — extend only
# when a new corpus booster shows up in renderer output
_BOOSTER_RE = re.compile(
    r"\b(?:masterpieces?|best quality|award.?winning|trending on artstation|"
    r"[48]k|u?hd|ultra.?detailed|ultra.?realistic|hyper.?detailed|"
    r"extremely detailed|highly detailed|intricate details?|sharp focus)\b",
    re.I)
_REFN_RE = re.compile(r"\bREFERENCE_?(\d+)\b", re.I)
_PREFIX_RE = re.compile(r"^([A-Za-z][A-Za-z0-9 /&-]{0,38}):\s+(.+)$", re.S)
_EQ_RE = re.compile(r"^([a-z][a-z0-9 _]{1,30})\s*=\s*(.+)$", re.S)
_WORD_LIMIT_RE = re.compile(
    r"\b(?:under|less than|max(?:imum)?|no more than|up to|limit(?:ed)? to)\s+"
    r"\d+\s+(?:words|tokens)\b|\bword (?:count|limit)s?\b|\btoken limits?\b",
    re.I)


def _ordinal(n: int) -> str:
    return _ORDINALS[n - 1] if 1 <= n <= len(_ORDINALS) else f"image {n}"


_ARG_TAG_RE = re.compile(
    r'\{argument[^}]*?default=\\?"([^"\\]*)\\?"[^}]*\}', re.S)


def _clean(fragment: str) -> str:
    """Zone-prefix strip + {argument} unwrap + REFERENCE_N rewrite +
    booster scrub."""
    frag = re.sub(r"\s+", " ", str(fragment)).strip()
    frag = _ARG_TAG_RE.sub(lambda m: m.group(1), frag)
    m = _PREFIX_RE.match(frag)
    if m and _match_slot(m.group(1)) and len(m.group(2).strip()) >= 3:
        frag = m.group(2).strip()
    m = _EQ_RE.match(frag)
    if m and _match_slot(m.group(1)) and len(m.group(2).strip()) >= 3:
        frag = m.group(2).strip()
    frag = _REFN_RE.sub(lambda mm: f"the {_ordinal(int(mm.group(1)))} image",
                        frag)
    frag = _BOOSTER_RE.sub("", frag)
    frag = re.sub(r"\s{2,}", " ", frag)
    frag = re.sub(r"\s*,(\s*,)+", ",", frag).strip(" ,.;-")
    return frag


def _join(frags, seen=None) -> str:
    """Clean + dedupe fragments into one comma-joined phrase ('' if none)."""
    seen = seen if seen is not None else set()
    out = []
    for f in frags:
        c = _clean(f)
        low = c.lower()
        if len(c) >= 3 and low not in seen:
            seen.add(low)
            out.append(c)
    return ", ".join(out)


def _style_only(frags) -> list:
    """Reference fragments that are style attributions, not image slots."""
    return [f for f in frags
            if re.match(r"(?i)^(inspired by|in the style of|style of)\b", f)]


def _text_levers(frags, seen) -> list:
    """Literal text as vendor levers: keep quotes/ALL-CAPS, double-quote the rest."""
    out = []
    for f in frags:
        c = _clean(f)
        low = c.lower()
        if len(c) < 3 or low in seen:
            continue
        seen.add(low)
        if c.startswith('"') or (c.isupper() and len(c) >= 3):
            out.append(c)
        else:
            out.append(f'"{c}"')
    return out


def _paragraph(sentences) -> str:
    """Join kept sentences, capitalizing each start, period-terminating."""
    parts = [s.rstrip(" ,") for s in sentences if s and s.strip(" ,")]
    return " ".join(p[0].upper() + p[1:] + "." for p in parts)


# ─── GPT IMAGE 2 ────────────────────────────────────────────────────────────

_SIZE_TALL = ("1024x1536", "portrait - posters and stories")
_SIZE_WIDE = ("1536x1024", "landscape - banners and hero sections")
_SIZE_SQUARE = ("1024x1024", "square - social posts and avatars")


def _size_hint(ar: str):
    """aspect_ratio -> suggested size via official heuristics (or None)."""
    a = (ar or "").strip().lower()
    if not a:
        return None
    m = re.match(r"^(\d{1,2}):(\d{1,2})$", a)
    if m:
        w, h = int(m.group(1)), int(m.group(2))
        if not w or not h or not (1 / 3 <= w / h <= 3):
            return None  # outside gpt-image-2's supported 1:3-3:1
        if w == h:
            return _SIZE_SQUARE
        return _SIZE_TALL if h > w else _SIZE_WIDE
    if "square" in a:
        return _SIZE_SQUARE
    if "vertical" in a or "portrait" in a:
        return _SIZE_TALL
    if "widescreen" in a or "landscape" in a:
        return _SIZE_WIDE
    return None


def render_gpt_image_2(ir: PromptIR) -> str:
    """Render a PromptIR as a cohesive gpt-image-2 prompt paragraph.

    Front-loads the subject, covers the 7 facets when the IR carries them,
    excludes inline ('without any X' — no negative_prompt param exists),
    keeps quoted/ALL-CAPS text levers, and appends the official size
    heuristic for the aspect ratio.
    """
    seen = set()
    lead = _join(list(ir.subject)[:2] + list(ir.action)[:1], seen)
    sentences = []
    if lead:
        sentences.append(lead[0].upper() + lead[1:])
    sentences.append(_join(list(ir.environment)[:2] + list(ir.composition)[:3], seen))
    sentences.append(_join(list(ir.style)[:2] + list(ir.lighting)[:2]
                          + list(ir.color)[:2], seen))
    text_levers = _text_levers(ir.text_elements, seen)
    tail = _join(list(ir.mood)[:1], seen)
    if text_levers:
        tail = (tail + ", " if tail else "") + ", ".join(text_levers)
    if tail:
        sentences.append(tail)
    negs = ", ".join(
        re.sub(r"^(?:any|an?|the)\s+", "", c, flags=re.I)
        for c in (_clean(f) for f in ir.negative_concepts)
        if len(c) >= 3)
    if negs:
        sentences.append(f"Keep the result clean, without any {negs}")
    style_refs = _style_only(ir.references)
    if style_refs:
        sentences.append(_join(style_refs, seen))
    image_refs = [f for f in ir.references if f not in style_refs]
    for i, frag in enumerate(image_refs):
        c = _clean(frag)
        if not c:
            continue
        if re.search(r"\bimage\b", c, re.I):  # already ordinal-addressed
            sentences.append("Use " + c)
        else:
            sentences.append(f"Use the {_ordinal(i + 1)} image as {c}")
    body = _paragraph(sentences)
    if not body:
        return "A single clean subject on a simple background."
    hint = _size_hint(ir.aspect_ratio)
    if hint:
        body += f" Suggested size: {hint[0]} ({hint[1]})."
    assert not _BOOSTER_RE.search(body) and not _REFN_RE.search(body)
    assert not _WORD_LIMIT_RE.search(body)
    return body


# ─── NANO BANANA PRO ────────────────────────────────────────────────────────

# ponytail: small official-example-based rewrite table + 'no signs of' fallback
_POSITIVE_REWRITES = {
    "watermark": "a clean, unmarked finish",
    "watermarks": "a clean, unmarked finish",
    "text": "purely visual, lettering-free imagery",
    "words": "purely visual, lettering-free imagery",
    "blur": "crisp, precise focus",
    "blurriness": "crisp, precise focus",
    "clutter": "a calm, uncluttered arrangement",
    "distortion": "clean, natural proportions",
    "noise": "smooth, clean surfaces",
    "grain": "smooth, clean surfaces",
}
_PRO_RATIOS = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16",
               "16:9", "21:9"}
_CAMERA_RE = re.compile(
    r"\b(?:\d+\s*mm|f/[\d.]+|lens|aperture|depth of field|shallow depth|"
    r"shot on|close-up|wide-angle|macro|bokeh)\b", re.I)


def render_nano_banana_pro(ir: PromptIR) -> str:
    """Render a PromptIR as a narrative scene description for
    gemini-3-pro-image.

    Follows the official formula [Subject]+[Action]+[Location]+[Composition]+
    [Style]; camera language is welcome and woven in when present; negatives
    are restated as semantic positives (never bare negations); references are
    addressed by ordinal + role.
    """
    seen = set()
    lead = _join(list(ir.subject)[:2] + list(ir.action)[:1], seen)
    sentences = []
    if lead:
        sentences.append("The scene centers on " + lead)
    sentences.append(_join(list(ir.environment)[:2], seen))
    camera = [f for f in list(ir.composition) + list(ir.lighting) + list(ir.style)
              if _CAMERA_RE.search(f)]
    comp = _join(list(ir.composition)[:3] + camera[:2], seen)
    if comp:
        sentences.append(comp)
    rest = _join(list(ir.style)[:2] + list(ir.lighting)[:2]
                 + list(ir.color)[:2] + list(ir.mood)[:1], seen)
    if rest:
        sentences.append(rest)
    texts = _text_levers(ir.text_elements, seen)
    if texts:
        sentences.append("Text reads " + ", ".join(texts))
    if ir.negative_concepts:
        rewrites = [_POSITIVE_REWRITES.get(_clean(f).lower(),
                                           f"no signs of {_clean(f)}")
                    for f in ir.negative_concepts if _clean(f)]
        if rewrites:
            sentences.append("The scene keeps " + " and ".join(rewrites))
    style_refs = _style_only(ir.references)
    image_refs = [f for f in ir.references if f not in style_refs]
    for i, frag in enumerate(image_refs):
        c = _clean(frag)
        if not c:
            continue
        if re.search(r"\bimage\b", c, re.I):  # already ordinal-addressed
            sentences.append(c[0].upper() + c[1:])
        else:
            sentences.append(f"Draw from the {_ordinal(i + 1)} image: {c}, "
                             "woven into this new scenario")
    if style_refs:
        sentences.append(_join(style_refs, seen))
    body = _paragraph(sentences)
    if not body:
        return "A single clear subject telling one quiet, hyper-specific story."
    ar = (ir.aspect_ratio or "").strip().lower()
    if ar in _PRO_RATIOS:
        body += f" Presented in a {ar} frame."
    assert not _BOOSTER_RE.search(body) and not _REFN_RE.search(body)
    assert not _WORD_LIMIT_RE.search(body)
    return body

#!/usr/bin/env python3
"""
Prompt IR (internal representation) + slot extraction — US-011.

extract_ir() parses a retrieved corpus exemplar — JSON-structured, Template
({argument} tags + section headers), or flat prose — into a PromptIR.
Every field holds evidence fragments lifted from the exemplar text, so
structure comes from the corpus, not hardcoded prose. Downstream stories
(US-012 renderers, US-013 pipeline) consume PromptIR, never raw text.
"""

import json
import re
from dataclasses import dataclass, field

# ─── IR SCHEMA ──────────────────────────────────────────────────────────────

IR_FIELDS = (
    "subject", "action", "environment", "style", "lighting", "color", "mood",
    "composition", "text_elements", "negative_concepts", "aspect_ratio",
    "references", "output_intent", "quality_tier",
)

_LIST_SLOTS = tuple(f for f in IR_FIELDS if f not in
                    ("aspect_ratio", "output_intent", "quality_tier"))


@dataclass
class PromptIR:
    """Structured representation of an image prompt. List fields hold
    evidence fragments extracted from an exemplar; str fields hold a single
    derived value ("" / "general_image" / "standard" when unknown)."""
    subject: list = field(default_factory=list)
    action: list = field(default_factory=list)
    environment: list = field(default_factory=list)
    style: list = field(default_factory=list)
    lighting: list = field(default_factory=list)
    color: list = field(default_factory=list)
    mood: list = field(default_factory=list)
    composition: list = field(default_factory=list)
    text_elements: list = field(default_factory=list)
    negative_concepts: list = field(default_factory=list)
    references: list = field(default_factory=list)
    # Names of the exemplar's template arguments (structure borrowed from the
    # corpus). Filled from the user's goal at render time, never from the
    # exemplar's own defaults.
    template_slots: list = field(default_factory=list)
    # The donor exemplar's own subject terms (its template-argument defaults),
    # collected so scrub_exemplar_identity can delete them from borrowed prose.
    donor_terms: list = field(default_factory=list)
    aspect_ratio: str = ""
    output_intent: str = "general_image"
    quality_tier: str = "standard"

    def add(self, slot: str, fragment: str):
        """Append an evidence fragment to a list slot (dedup + cap)."""
        frag = re.sub(r"\s+", " ", str(fragment)).strip()
        if not frag or slot not in _LIST_SLOTS:
            return
        bucket = getattr(self, slot)
        low = frag.lower()
        if any(low in b.lower() or b.lower() in low for b in bucket):
            return
        if len(bucket) < 6:
            bucket.append(frag[:300])

    def scrub_exemplar_identity(self, goal: str):
        """Strip the donor exemplar's own subject matter from borrowed fragments.

        An exemplar contributes STRUCTURE (which sections exist, how many
        elements, what aspect ratio) -- never its subject. Without this, a
        'analytics dashboard' goal that retrieves a fitness-app template renders
        'PulseFit' and 'calories burned, workout streak' into the user's prompt.

        Two rules, both conservative:
          1. Drop brand-like coinages -- interior-capital words such as
             'PulseFit'. Deliberately narrow: ordinary capitalised words
             ('Instagram', 'Design') are left alone.
          2. Drop enumeration clauses -- three or more comma-separated items of
             which none appear in the goal. Those enumerate the donor's content,
             whereas aesthetic phrasing ('soft shadows', 'dark mode') transfers.
        """
        goal_words = {w for w in re.findall(r"[a-z]+", goal.lower()) if len(w) > 3}
        for slot in _LIST_SLOTS:
            kept = []
            for frag in getattr(self, slot):
                frag = _BRANDISH_RE.sub("", frag)
                for term in self.donor_terms:
                    if term not in goal.lower():  # keep it if the user asked for it
                        frag = re.sub(re.escape(term), "", frag, flags=re.I)
                # Deleting words leaves orphaned punctuation ("- , sharp text",
                # "Crisp typography,"). Repair before the fragment is rendered.
                frag = re.sub(r"\s{2,}", " ", frag)
                frag = re.sub(r"[-–]\s*,", ",", frag)
                frag = re.sub(r"\s+([,.;:])", r"\1", frag)
                frag = re.sub(r"(,\s*){2,}", ", ", frag)
                frag = frag.strip(" ,;:-")
                if len(frag) < 3:
                    continue
                items = [i.strip() for i in frag.split(",") if i.strip()]
                if len(items) >= 3:
                    # Filter per item, not per fragment: one on-topic item must
                    # not rescue a whole list of the donor's content. An item
                    # survives if it echoes the goal or is transferable design
                    # vocabulary ("soft shadows"); donor specifics
                    # ("calories burned") drop out.
                    items = [
                        i for i in items
                        if _AESTHETIC_RE.search(i)
                        or any(w in goal_words
                               for w in re.findall(r"[a-z]+", i.lower()))
                    ]
                    if not items:
                        continue
                    frag = ", ".join(items)
                kept.append(frag)
            setattr(self, slot, kept)

    def filled(self) -> list:
        """Names of slots carrying at least one fragment/value."""
        return [f for f in IR_FIELDS
                if (getattr(self, f) if f in _LIST_SLOTS
                    else [getattr(self, f)])]

    def to_dict(self) -> dict:
        return {f: getattr(self, f) for f in IR_FIELDS}


# ─── SLOT ROUTING ───────────────────────────────────────────────────────────

# Zone names (section headers, JSON keys, argument names) -> IR slot.
_SLOT_ALIASES = {
    "subject": "subject", "main subject": "subject", "character": "subject",
    "hero": "subject", "focus": "subject",
    "action": "action", "pose": "action", "gesture": "action",
    "environment": "environment", "setting": "environment",
    "background": "environment", "scene": "environment", "location": "environment",
    "style": "style", "aesthetic": "style", "art direction": "style",
    "look": "style", "visual style": "style",
    "lighting": "lighting", "light": "lighting", "illumination": "lighting",
    "color": "color", "colors": "color", "colour": "color",
    "palette": "color", "color palette": "color", "colour palette": "color",
    "mood": "mood", "atmosphere": "mood", "vibe": "mood", "tone": "mood",
    "composition": "composition", "layout": "composition",
    "framing": "composition", "zones": "composition", "zone": "composition",
    "canvas": "composition", "grid": "composition", "format": "composition",
    "text": "text_elements", "typography": "text_elements",
    "headline": "text_elements", "title": "text_elements",
    "subtitle": "text_elements", "caption": "text_elements",
    "text elements": "text_elements", "lettering": "text_elements",
    "negative": "negative_concepts", "negatives": "negative_concepts",
    "negative prompt": "negative_concepts", "avoid": "negative_concepts",
    "exclusions": "negative_concepts",
    "aspect ratio": "aspect_ratio", "ratio": "aspect_ratio",
    "size": "aspect_ratio",
    "reference": "references", "references": "references",
    "inspiration": "references",
}
_ALIASES_BY_LENGTH = sorted(_SLOT_ALIASES.items(), key=lambda kv: -len(kv[0]))

# Clause keyword buckets: (slot, regex) — vocabulary from corpus technique detectors.
_KEYWORD_SLOTS = (
    ("lighting", re.compile(
        r"\b(lighting|golden hour|studio light\w*|soft light\w*|natural "
        r"light\w*|volumetric|rim light\w*|caustics|backlit|backlight\w*|"
        r"neon (?:glow|light\w*)|ambient light\w*|led (?:strips?|ceiling)|"
        r"moody ambient|flash lighting)\b", re.I)),
    ("color", re.compile(
        r"\b(color palette|colour palette|colors?\s*:|palette\s*:|monochrome|"
        r"gradient|pastel|sepia|navy|cyan|magenta|amber|teal|neon|chrome|"
        r"metallic accents|earth tones|warm (?:tones|palette)|cool (?:tones|"
        r"palette)|black and white)\b", re.I)),
    ("mood", re.compile(
        r"\b(mood|atmosphere|vibe|aesthetic|cinematic|moody|vibrant|ethereal|"
        r"gritty|dreamy|nostalgic|serene|dramatic|whimsical|luxury|futuristic)\b",
        re.I)),
)

# Element counts: "three-tier", "exactly 8 numbered badges", "two stacked panels".
_COUNT_RE = re.compile(
    r"\b(?:exactly\s+)?(?:one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|\d{1,3})(?:[-\s]+(?:numbered|stacked|horizontal|vertical|"
    r"glowing|small|large|thin|rounded|decorative|content|text|image|"
    r"floating))?\s*[-\s]+(?:tiers?|sections?|panels?|cards?|badges?|"
    r"columns?|rows?|icons?|elements?|objects?|figures?|steps?|charts?|"
    r"graphs?|zones?|blocks?|strips?|variations?|lanes?|tiles?)\b", re.I)

_NEG_RE = re.compile(
    r"\b(?:without|excluding|avoid(?:ing)?|no)\s+([A-Za-z][A-Za-z\s-]{2,50})")
_REF_RE = re.compile(
    r"\b(?:inspired by|in the style of|style of|reference image|"
    r"(?:first|second|third|fourth|fifth)\s+reference)\b[^.,;\n]{0,60}", re.I)
_AR_NUMERIC_RE = re.compile(r"(?:--ar\s*)?(\b\d{1,2}:\d{1,2}\b)")
_AR_WORD_RE = re.compile(r"\b(vertical|square|widescreen|landscape format|"
                         r"portrait orientation)\b", re.I)
_SECTION_RE = re.compile(
    r"^([A-Z][A-Za-z0-9 /&-]{1,38}):\s*(.+?)(?=\n[A-Z][A-Za-z0-9 /&-]{1,38}:|\Z)",
    re.M | re.S)
# Corpus stores args both raw and backslash-escaped: name=\"x\".
_ARG_RE = re.compile(
    r'\{argument\s+name=\\?"([^"\\]+)\\?"\s+default=\\?"([^"\\]*)\\?"\}')
_QUOTED_RE = re.compile(r'"([^"\n]{2,80})"')
_CAPS_RE = re.compile(r"\b[A-Z][A-Z0-9 &'-]{3,}\b")
# Brand-like coinages with an interior capital ("PulseFit", "FitTrack"). Used to
# strip a donor exemplar's brand out of borrowed fragments. Intentionally narrow
# so ordinary capitalised words survive.
_BRANDISH_RE = re.compile(r"\b[A-Z][a-z]+[A-Z][A-Za-z]*\b")
# Design vocabulary that transfers between subjects. An enumeration item matching
# this is kept even when it does not echo the goal, because it describes HOW the
# image should look rather than WHAT the donor exemplar depicted.
# Words that show up inside template defaults but carry no donor identity, so
# denying them would strip ordinary vocabulary from every generated prompt.
_GENERIC_DEFAULT_WORDS = {
    "brand", "product", "modern", "clean", "simple", "image", "photo", "design",
    "style", "colour", "color", "white", "black", "light", "background", "text",
    "title", "header", "layout", "screen", "page", "website", "green", "blue",
}
_AESTHETIC_RE = re.compile(
    r"\b(shadow|spacing|hierarchy|typograph|font|minimal|modern|clean|gradient|"
    r"rounded|corner|contrast|palette|colou?r|whitespace|grid|align|bold|subtle|"
    r"margin|padding|layout|composition|balance|symmetr|texture|matte|glossy|"
    r"lighting|light|depth|blur|bokeh|sharp|crisp|muted|vibrant|pastel|neutral|"
    r"dark mode|light mode|flat|glass|shade|tone|hue|saturation|border|radius)",
    re.I)

_HIGH_TIER_RE = re.compile(
    r"hyper.?realistic|photorealistic|ultra.?detailed|highly detailed|"
    r"extremely detailed|intricate detail|8k|4k|cinematic|award.?winning|"
    r"masterpiece|premium", re.I)
_INTENT_PATTERNS = (
    ("ui_mockup", r"\b(ui|ux|dashboard|interface|app screen|web design|landing page|navbar|sidebar|design system)\b"),
    ("infographic", r"\b(infographic|educational|explainer|diagram|data visualization)\b"),
    ("thumbnail", r"\b(thumbnail)\b"),
    ("poster", r"\b(poster|flyer|banner)\b"),
    ("logo", r"\b(logo|logotype|brand mark)\b"),
    ("product_image", r"\b(product shot|e-?commerce|packaging|product photo)\b"),
    ("portrait", r"\b(portrait|selfie|headshot)\b"),
    ("landscape", r"\b(landscape|nature scene|vista)\b"),
    ("storyboard", r"\b(comic|storyboard|manga panel)\b"),
)


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", str(name).lower().strip())


def _match_slot(name: str):
    """Route a zone/argument name to an IR slot via alias table (greedy
    longest match); None when the name names no known slot."""
    n = _norm(name)
    if n in _SLOT_ALIASES:
        return _SLOT_ALIASES[n]
    for alias, slot in _ALIASES_BY_LENGTH:
        if alias in n:
            return slot
    return None


def _trim(text: str, limit: int = 300) -> str:
    return re.sub(r"\s+", " ", text).strip()[:limit]


def _scalarize(val) -> str:
    if isinstance(val, str):
        return val
    if isinstance(val, (list, tuple)):
        return ", ".join(_scalarize(v) for v in val if _scalarize(v))
    if isinstance(val, dict):
        return json.dumps(val, ensure_ascii=False)[:300]
    return "" if val is None else str(val)


def _clauses(text: str) -> list:
    parts = re.split(r"(?<=[.,;!?\n])\s+", text)
    return [p for p in parts if len(p.strip()) >= 12]


# ─── EXEMPLAR PARSERS ───────────────────────────────────────────────────────

def _from_json(obj: dict, ir: PromptIR):
    """JSON exemplar: top-level keys are zone names — alias-mapped keys route
    to their slot, unmapped keys become composition zone fragments."""
    for key, val in obj.items():
        text_val = _trim(_scalarize(val))
        if not text_val:
            continue
        slot = _SLOT_ALIASES.get(_norm(key))
        if slot == "aspect_ratio":
            if not ir.aspect_ratio:
                ir.aspect_ratio = text_val[:40]
        elif slot:
            ir.add(slot, f"{key}: {text_val}")
        else:
            ir.add("composition", f"{key}: {text_val}")


def _from_prose(text: str, ir: PromptIR):
    """Template/prose exemplar: template arguments, section headers
    (zone names), then clause keyword buckets."""
    # Template arguments are STRUCTURE, not content. The name tells us what the
    # exemplar parameterises ("brand name", "app type"); the default is that
    # exemplar's own domain ("PulseFit", "fitness app"). Emitting the default
    # leaks another prompt's subject into ours -- e.g. an analytics-dashboard
    # goal rendering "app type = fitness app, brand name = PulseFit". Record the
    # names as slots for the generator to fill from the goal; drop the defaults.
    for name, default in _ARG_RE.findall(text):
        name = " ".join(name.split())
        if name and name.lower() not in {s.lower() for s in ir.template_slots}:
            ir.template_slots.append(name)
        # The defaults ARE this exemplar's subject matter ("fitness app",
        # "PulseFit"). Record them as an exact denylist so scrub can remove them
        # wherever they also appear in the donor's prose, not just in the tag.
        default = " ".join(default.split())
        if len(default) > 2 and default.lower() not in ir.donor_terms:
            ir.donor_terms.append(default.lower())
        # Also deny the distinctive single words inside a multi-word default, so
        # "fitness app" additionally suppresses a stray "premium fitness brand".
        for word in re.findall(r"[A-Za-z]{5,}", default):
            w = word.lower()
            if w not in _GENERIC_DEFAULT_WORDS and w not in ir.donor_terms:
                ir.donor_terms.append(w)
    for header, content in _SECTION_RE.findall(text):
        content = content.strip()
        slot = _match_slot(header)
        if slot and slot != "aspect_ratio":
            ir.add(slot, f"{header}: {_trim(content)}")
        elif slot == "aspect_ratio":
            m = _AR_NUMERIC_RE.search(content)
            if m and not ir.aspect_ratio:
                ir.aspect_ratio = m.group(1)
        else:
            ir.add("composition", f"{header}: {_trim(content, 200)}")
    for clause in _clauses(text):
        for slot, rx in _KEYWORD_SLOTS:
            if rx.search(clause):
                ir.add(slot, _trim(clause))


def _scan_universal(text: str, ir: PromptIR, is_json: bool):
    """Model-agnostic signals present in any exemplar format."""
    for m in _COUNT_RE.finditer(text):
        ir.add("composition", m.group(0))
    for m in _NEG_RE.finditer(text):
        ir.add("negative_concepts", " ".join(m.group(1).split()[:5]))
    for m in _REF_RE.finditer(text):
        ir.add("references", _trim(m.group(0), 120))
    if not is_json:  # JSON quotes are syntax, not text elements
        # Template tags are syntax too: {argument name="app type" default="x"}
        # would otherwise register "app type" as copy to render in the image.
        for q in _QUOTED_RE.findall(_ARG_RE.sub(" ", text)):
            ir.add("text_elements", f'"{q}"')
        for c in _CAPS_RE.findall(text):
            if sum(ch.isalpha() for ch in c) >= 4:
                ir.add("text_elements", c.strip())
    if not ir.aspect_ratio:
        m = _AR_NUMERIC_RE.search(text)
        if m:
            ir.aspect_ratio = m.group(1)
        else:
            w = _AR_WORD_RE.search(text)
            if w:
                ir.aspect_ratio = w.group(1).lower()
    low = text.lower()
    for intent, rx in _INTENT_PATTERNS:
        if re.search(rx, low):
            ir.output_intent = intent
            break
    if _HIGH_TIER_RE.search(text):
        ir.quality_tier = "high"
    if not ir.subject:
        clauses = _clauses(text)
        if clauses:
            ir.add("subject", _trim(clauses[0]))


# ─── PUBLIC API ─────────────────────────────────────────────────────────────

def extract_ir(source) -> PromptIR:
    """Extract a PromptIR from a retrieved exemplar. Accepts a Prompt row
    object (uses .prompt_text), raw prompt text, or a JSON dict. Works on
    JSON-structured and prose exemplars alike; empty/garbage input yields a
    default IR rather than raising."""
    if isinstance(source, dict):
        ir = PromptIR()
        _from_json(source, ir)
        return ir
    text = str(getattr(source, "prompt_text", source) or "").strip()
    ir = PromptIR()
    if not text:
        return ir
    if text.startswith("{"):
        try:
            obj = json.loads(text)
        except ValueError:
            obj = None  # corpus has non-strict JSON (trailing commas, escapes)
        if isinstance(obj, dict):
            _from_json(obj, ir)
            _scan_universal(text, ir, is_json=True)
            return ir
    _from_prose(text, ir)
    _scan_universal(text, ir, is_json=False)
    return ir


if __name__ == "__main__":
    demo = extract_ir(
        'A hyper-realistic portrait of a chef in a dim kitchen, golden hour '
        'lighting, warm amber palette, inspired by Wes Anderson, without '
        'watermarks. 4:5')
    for f in IR_FIELDS:
        print(f"{f:>18}: {demo.to_dict()[f]}")

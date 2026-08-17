#!/usr/bin/env python3
"""Single shared English-only filter (SKILL.md language policy).

One implementation used by both the retrieval layer and the scraper —
previously two divergent copies (scraper checked CJK+Arabic, retrieval
only CJK).
"""

# ponytail: script-range blocklist, not full Unicode script detection;
# add ranges as new non-English leaks appear.
_NON_ENGLISH_RANGES = (
    ('\u0400', '\u04ff'),  # Cyrillic
    ('\u0590', '\u05ff'),  # Hebrew
    ('\u0600', '\u06ff'),  # Arabic
    ('\u0900', '\u097f'),  # Devanagari
    ('\u0e00', '\u0e7f'),  # Thai
    ('\u3040', '\u309f'),  # Hiragana
    ('\u30a0', '\u30ff'),  # Katakana
    ('\u4e00', '\u9fff'),  # CJK Unified Ideographs
    ('\uac00', '\ud7af'),  # Hangul (Korean)
)


def is_english(text: str) -> bool:
    """True when text contains no non-English script characters."""
    return not any(lo <= ch <= hi for ch in text for lo, hi in _NON_ENGLISH_RANGES)

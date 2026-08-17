#!/usr/bin/env python3
"""Single shared English-only filter (SKILL.md language policy).

One implementation used by both the retrieval layer and the scraper —
previously two divergent copies (scraper checked CJK+Arabic, retrieval
only CJK).
"""

# NOTE: script-range blocklist, not full Unicode script detection;
# add ranges as new non-English leaks appear.
_NON_ENGLISH_RANGES = (
    ('\u0400', '\u04ff', 'Cyrillic'),
    ('\u0590', '\u05ff', 'Hebrew'),
    ('\u0600', '\u06ff', 'Arabic'),
    ('\u0900', '\u097f', 'Devanagari'),
    ('\u0e00', '\u0e7f', 'Thai'),
    ('\u3040', '\u309f', 'Hiragana'),
    ('\u30a0', '\u30ff', 'Katakana'),
    ('\u4e00', '\u9fff', 'CJK'),
    ('\uac00', '\ud7af', 'Hangul'),
)


def is_english(text: str) -> bool:
    """True when text contains no non-English script characters."""
    return not detect_scripts(text)


def detect_scripts(text: str) -> list:
    """Names of the non-English scripts present, in first-seen order.

    The corpus is English-only by policy, so a goal written in another script
    cannot match anything via FTS. Callers use this to warn and take a
    translation path rather than degrade silently to an unrelated exemplar.
    """
    found = []
    for ch in text:
        for lo, hi, name in _NON_ENGLISH_RANGES:
            if lo <= ch <= hi and name not in found:
                found.append(name)
                break
    return found

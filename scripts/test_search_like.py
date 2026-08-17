"""US-018 regression: LIKE escaping + relevance ordering in search().

Run: python scripts/test_search_like.py  (exit 0 = pass)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from higgsfield_prompt import HiggsfieldPromptMaster, _like

# _like escaping (backslash first, then % and _)
assert _like("50%") == "%50\\%%", _like("50%")
assert _like("a_b") == "%a\\_b%", _like("a_b")
assert _like("x\\y") == "%x\\\\y%", _like("x\\y")

hpm = HiggsfieldPromptMaster()
BIG = 10**6

# Wildcard-only queries no longer match everything (they match literal chars)
total = len(hpm.search(limit=BIG))
pct_hits = hpm.search(query="%", limit=BIG)
und_hits = hpm.search(query="_", limit=BIG)
assert len(pct_hits) < total, f"'%' matched {len(pct_hits)}/{total} rows"
assert len(und_hits) < total, f"'_' matched {len(und_hits)}/{total} rows"
for r in pct_hits:
    assert "%" in (r.title + r.description + r.prompt_text), f"false % hit id={r.id}"

# Wildcards inside a longer query are literal too (terms are OR'd)
mixed = hpm.search(query="100% satisfaction", limit=BIG)
terms = ["100% satisfaction", "100%", "satisfaction"]
for r in mixed:
    blob = (r.title + " " + r.description + " " + r.prompt_text).lower()
    assert any(t in blob for t in terms), f"false hit id={r.id}"

# Relevance: single term -> every title match outranks every body-only match
term = "glassmorphism"
ranked = hpm.search(query=term, limit=BIG)
title_hits = [r for r in ranked if term in r.title.lower()]
body_only = [r for r in ranked if term not in r.title.lower()]
assert title_hits and body_only, f"need both classes, got {len(title_hits)}/{len(body_only)}"
first_body = ranked.index(body_only[0])
assert all(i < first_body for i in [ranked.index(r) for r in title_hits]), \
    "title match ranked below body-only match"
# And ordering is not length_chars DESC (ties broken by id, rank leads)
lens = [r.length_chars for r in ranked[:20]]
assert lens != sorted(lens, reverse=True) or len(set(lens)) == 1, \
    "looks like plain length ordering"

print(f"OK: total={total}, '%'={len(pct_hits)}, '_'={len(und_hits)}, "
      f"ranked '{term}': {len(ranked)} hits, {len(title_hits)} title-first")

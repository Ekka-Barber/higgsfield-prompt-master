#!/usr/bin/env python3
"""Regression check: FTS5 quote crash + fallback (US-002)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from higgsfield_prompt import HiggsfieldPromptMaster

m = HiggsfieldPromptMaster()

# Embedded/unclosed double quotes must not raise (US-002 core bug)
for q in ['dashboard "glass', '"unclosed', 'a "" b', '""""']:
    r = m.fts_search(q)
    assert isinstance(r, list), q

# Quoted input still finds results
assert len(m.fts_search('dashboard "glass')) > 0

# Empty / stop-word-only inputs return [] without exception
for q in ["", "   ", "the a of", '"']:
    assert m.fts_search(q) == [], q

print("OK: fts quote + empty-term regression checks passed")

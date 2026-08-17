#!/usr/bin/env python3
"""US-019 regression: structure classification order and JSON strictness."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent.parent))
from higgsfield_prompt import detect_structure

# Template before JSON: {argument text starting with '{' that fails json.loads
assert detect_structure('{argument name="subject" default="a cat"} in snow') == "Template"
# JSON requires strict parse: trailing-comma { starting text is NOT JSON
assert detect_structure('{"style": "minimal",}') == "Other"
# Valid parse, no template tags -> JSON
assert detect_structure('  {"style": "minimal"}') == "JSON"
# Hybrid: parses AND carries {argument -> Template-JSON
assert detect_structure('{"prompt": "{argument name=\\"x\\" default=\\"y\\"}"}') == "Template-JSON"
# Non-{ strict parses don't get JSON (old prefix rule kept)
assert detect_structure('["a", "b"]') == "Other"
# Unchanged buckets
assert detect_structure("A cat on a sofa") == "Flat prose"
assert detect_structure("random words here") == "Other"

# Old classifier would say JSON for the first two; 636-label regression
# is gated by scripts/reclassify_structure.py's <=352 assert.
print("OK")

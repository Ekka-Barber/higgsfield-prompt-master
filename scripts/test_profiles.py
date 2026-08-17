"""US-030 regression: versioned capability profiles.

Checks:
1. Both profiles exist with @<date>. names, parse (mini YAML subset),
   and every claim group carries evidence (URL), confidence, date,
   review_after.
2. data/gpt_image_2.json + data/nano_banana_pro.json are exactly what
   the profiles generate (profile_to_data identity).
3. Emitter/parser coherence: parse(dump(profile)) == profile.
4. Mini-parser output equals PyYAML's when pyyaml is importable
   (proves the .yaml files are real YAML, not a private format).
5. Loader red path: intelligence._validate rejects a claim group
   missing _review_after.
6. Validator red path: stripping review_after from a profile fails
   validate_profile.
7. Curated data files carry _review_after too (loader demand).
"""
import copy
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import sync_profiles as sp
import intelligence

ROOT = Path(__file__).parent.parent

# 1. Profiles exist, parse, fully evidenced
profiles = {}
for stem in sp.MODELS:
    f = sp.find_profile(stem)
    assert f is not None, f"no profiles/{stem}@<date>.yaml"
    assert f.name == f"{stem}@2026-08-17.yaml", f.name
    profile = sp.parse_yaml(f.read_text(encoding="utf-8"))
    sp.validate_profile(profile)
    profiles[stem] = profile
    print(f"profile OK: {f.name} ({len(profile['claims'])} claim groups, "
          f"all evidenced)")

# 2. data/*.json == what the profiles generate
for stem, filename in sp.MODELS.items():
    data = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
    assert sp.profile_to_data(profiles[stem]) == data, \
        f"{filename} drifted from {stem} profile — run scripts/sync_profiles.py --apply"
print("profile->data identity OK (both model JSONs are profile-generated)")

# 3. Emitter/parser coherence
for stem, profile in profiles.items():
    assert sp.parse_yaml(sp.dump_yaml(profile)) == profile, stem
assert sp.parse_yaml(sp.dump_yaml(profiles["nano-banana-pro"]))["claims"]["not_pro"]["never_emit"] \
    == profiles["nano-banana-pro"]["claims"]["not_pro"]["never_emit"]
print("yaml dump/parse round-trip OK (incl. nested dict + flow list values)")

# 4. Real-YAML proof (opportunistic; pyyaml not a dependency)
try:
    import yaml
    for stem in sp.MODELS:
        text = sp.find_profile(stem).read_text(encoding="utf-8")
        assert sp.parse_yaml(text) == yaml.safe_load(text), stem
    print("mini-parser == PyYAML safe_load OK")
except ImportError:
    print("pyyaml absent — skipped cross-check (not a dependency)")

# 5. Loader red path: missing _review_after must be rejected
try:
    intelligence._validate(
        {"g": {"_source": "https://x", "_date": "2026-08-17",
               "_confidence": "high"}}, "t.json")
    raise AssertionError("loader accepted claim missing _review_after")
except ValueError as err:
    assert "t.json:g._review_after" in str(err)
print("loader red path OK: missing _review_after rejected")

# 6. Profile-validator red path
tampered = copy.deepcopy(profiles["gpt-image-2"])
del tampered["claims"]["sizes"]["review_after"]
try:
    sp.validate_profile(tampered)
    raise AssertionError("validate_profile accepted missing review_after")
except ValueError as err:
    assert "sizes.review_after" in str(err)
tampered["claims"]["names"]["evidence"] = "no url here"
try:
    sp.validate_profile(tampered)
    raise AssertionError("validate_profile accepted evidence without URL")
except ValueError as err:
    assert "names.evidence" in str(err)
print("profile-validator red path OK: review_after + evidence-URL enforced")

# 7. Curated files carry _review_after (loader demand covers all claim files)
for filename in sp.CURATED:
    data = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
    assert all("_review_after" in g for g in data.values()), filename
    intelligence._validate(data, filename)
print("curated files carry _review_after OK")

print("✅ test_profiles: all checks passed")

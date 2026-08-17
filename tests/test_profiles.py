"""US-030: versioned capability profiles (committed-artifact checks for CI).

profiles/<model>@<date>.yaml are the source of truth for the two model
claim files; data/*.json must stay in sync and every claim group must
carry evidence fields (the loader enforces _review_after too).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import sync_profiles as sp


def test_profiles_exist_and_evidenced():
    files = sorted((ROOT / "profiles").glob("*@*.yaml"))
    assert [f.name for f in files] == [
        "gpt-image-2@2026-08-17.yaml", "nano-banana-pro@2026-08-17.yaml"]
    for f in files:
        profile = sp.parse_yaml(f.read_text(encoding="utf-8"))
        sp.validate_profile(profile)  # evidence URL/confidence/date/review_after
        assert profile["claims"]


def test_data_generated_from_profiles():
    for stem, filename in sp.MODELS.items():
        profile = sp.load_profile(stem)
        data = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
        assert sp.profile_to_data(profile) == data


def test_loader_rejects_missing_evidence_fields():
    import intelligence
    complete = {"_source": "https://x", "_date": "2026-08-17",
                "_confidence": "high", "_review_after": "2027-08-17"}
    intelligence._validate({"g": dict(complete)}, "t.json")  # passes
    for key in intelligence._PROVENANCE_KEYS:
        bad = dict(complete)
        del bad[key]
        with pytest.raises(ValueError, match=rf"t\.json:g\.{key}"):
            intelligence._validate({"g": bad}, "t.json")


def test_curated_claims_carry_review_after():
    import intelligence
    for filename in sp.CURATED:
        intelligence._validate(
            json.loads((ROOT / "data" / filename).read_text(encoding="utf-8")),
            filename)

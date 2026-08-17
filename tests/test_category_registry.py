"""US-032: data/categories.json is the single source for category config.

Guards the property the registry exists to provide -- that adding a category is
one edit. If someone reintroduces a hardcoded alias table in db.py or a second
routing map in intelligence.py, these fail.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "categories.json"


@pytest.fixture(scope="module")
def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))["categories"]


def test_registry_exists_and_is_wellformed(registry):
    assert registry, "registry is empty"
    for entry in registry:
        assert entry["name"].strip() == entry["name"]
        assert isinstance(entry["aliases"], list)
        assert isinstance(entry["non_photo"], bool)


def test_canonical_names_are_unique(registry):
    names = [c["name"] for c in registry]
    assert len(names) == len(set(names))


def test_aliases_are_unambiguous(registry):
    """No alias may point at two different canonical categories."""
    owner = {}
    for entry in registry:
        for alias in entry["aliases"]:
            assert alias.lower() not in owner, (
                f"alias {alias!r} claimed by {owner.get(alias.lower())!r} "
                f"and {entry['name']!r}")
            owner[alias.lower()] = entry["name"]


def test_normalize_map_is_derived_from_registry(registry):
    from db import CATEGORY_NORMALIZE, normalize_category
    for entry in registry:
        assert normalize_category(entry["name"]) == entry["name"]
        for alias in entry["aliases"]:
            assert CATEGORY_NORMALIZE[alias.lower()] == entry["name"], alias


def test_intelligence_maps_are_derived_from_registry(registry):
    from intelligence import CATEGORY_PHOTO_MAP, CATEGORY_MARKETING_MAP
    for entry in registry:
        if entry["photo"] is not None or entry["non_photo"]:
            assert CATEGORY_PHOTO_MAP[entry["name"]] == entry["photo"]
        if entry["marketing"] is not None:
            assert CATEGORY_MARKETING_MAP[entry["name"]] == entry["marketing"]


def test_non_photo_categories_return_no_photo_intelligence(registry):
    """US-010 semantics ride on the registry: an explicit non-photo category
    must yield None, not fall through to the lifestyle default."""
    from intelligence import get_photo_intelligence
    for entry in registry:
        if entry["non_photo"]:
            assert get_photo_intelligence(entry["name"], "") is None, entry["name"]


def test_no_hardcoded_category_table_reintroduced():
    """db.py must derive its aliases, not carry a literal map again."""
    src = (ROOT / "db.py").read_text(encoding="utf-8")
    assert not re.search(r"CATEGORY_NORMALIZE\s*=\s*\{\s*[\"']", src), (
        "db.py has a literal CATEGORY_NORMALIZE again; derive it from "
        "data/categories.json instead")

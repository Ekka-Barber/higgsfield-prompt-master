#!/usr/bin/env python3
"""US-030: versioned capability profiles for model claims.

profiles/<model>@<date>.yaml are the source of truth for the two model
claim files. Every claim group carries evidence (URL), confidence,
date (last verified) and review_after. data/gpt_image_2.json and
data/nano_banana_pro.json are GENERATED from the profiles (--apply);
the default mode validates profile <-> data consistency and exits 1
on drift. Curated layers (photography/marketing/art_direction) have
no external evidence to profile; the loader still demands
_review_after on every claim group, so --apply backfills it there.

YAML subset (stdlib-only; pyyaml is NOT a dependency): block
mappings, '#' comment lines, scalars/lists/dicts emitted as JSON
(JSON string/flow syntax is valid YAML). The parser accepts quoted
scalars, JSON flow collections, and plain unquoted scalars (for
hand edits); nested values are block mappings only.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent.parent
PROFILES_DIR = ROOT / "profiles"
DATA_DIR = ROOT / "data"

MODELS = {
    "gpt-image-2": "gpt_image_2.json",
    "nano-banana-pro": "nano_banana_pro.json",
}
CURATED = ("photography.json", "marketing.json", "art_direction.json")
META = ("evidence", "confidence", "date", "review_after")
CONFIDENCES = ("high", "medium", "low")
DEFAULT_REVIEW_AFTER = "2027-08-17"
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_URL_RE = re.compile(r"https?://")
_KEY_RE = re.compile(r"^[A-Za-z0-9_]+$")
_DECODER = json.JSONDecoder()


# ── YAML subset emit/parse ─────────────────────────────────────────

def dump_yaml(obj) -> str:
    lines = []
    def mapping(m, indent):
        pad = "  " * indent
        for k, v in m.items():
            key = k if _KEY_RE.match(k) else json.dumps(k)
            if isinstance(v, dict):
                lines.append(f"{pad}{key}:")
                mapping(v, indent + 1)
            else:
                lines.append(f"{pad}{key}: {json.dumps(v, ensure_ascii=True)}")
    mapping(obj, 0)
    return "\n".join(lines) + "\n"


def _split_kv(s):
    if s.startswith('"'):
        key, idx = _DECODER.raw_decode(s)
        rest = s[idx:]
        if not rest.startswith(":"):
            raise ValueError(f"bad line: {s!r}")
        return key, rest[1:].strip()
    key, sep, rest = s.partition(":")
    if not sep:
        raise ValueError(f"bad line: {s!r}")
    return key, rest.strip()


def _scalar(val):
    if val[:1] in ('"', "[", "{"):
        return json.loads(val)
    return val


def _next_content_indent(lines, i):
    while i < len(lines):
        s = lines[i].strip()
        if s and not s.startswith("#"):
            return len(lines[i]) - len(lines[i].lstrip(" "))
        i += 1
    return -1


def _parse_block(lines, i, indent):
    out = {}
    while i < len(lines):
        raw = lines[i]
        s = raw.strip()
        if not s or s.startswith("#"):
            i += 1
            continue
        cur = len(raw) - len(raw.lstrip(" "))
        if cur < indent:
            return out, i
        if cur > indent:
            raise ValueError(f"unexpected indent: {raw!r}")
        key, val = _split_kv(s)
        if val == "":
            child = _next_content_indent(lines, i + 1)
            if child <= indent:
                raise ValueError(f"empty value with no nested block: {raw!r}")
            out[key], i = _parse_block(lines, i + 1, child)
        else:
            out[key] = _scalar(val)
            i += 1
    return out, i


def parse_yaml(text) -> dict:
    obj, i = _parse_block(text.splitlines(), 0, 0)
    if i != len(text.splitlines()):
        raise ValueError("trailing content after top-level mapping")
    return obj


# ── profile <-> data mapping ───────────────────────────────────────

def profile_to_data(profile: dict) -> dict:
    data = {}
    for group, claims in profile["claims"].items():
        missing = set(META) - set(claims)
        if missing:
            raise ValueError(f"{profile['profile']}:{group} missing {sorted(missing)}")
        g = {"_source": claims["evidence"], "_date": claims["date"],
             "_confidence": claims["confidence"], "_review_after": claims["review_after"]}
        g.update({k: v for k, v in claims.items() if k not in META})
        data[group] = g
    return data


def data_to_profile(name: str, data: dict) -> dict:
    claims = {}
    for group, c in data.items():
        pg = {"evidence": c["_source"], "confidence": c["_confidence"],
              "date": c["_date"],
              "review_after": c.get("_review_after", DEFAULT_REVIEW_AFTER)}
        pg.update({k: v for k, v in c.items() if not k.startswith("_")})
        collision = [k for k in c if not k.startswith("_") and k in META]
        if collision:
            raise ValueError(f"{name}:{group} claim key collides with meta field: {collision}")
        claims[group] = pg
    version = max(c["date"] for c in claims.values() if _DATE_RE.match(c["date"]))
    return {"profile": name, "date": version, "claims": claims}


def validate_profile(profile: dict) -> None:
    errs = []
    for group, c in profile.get("claims", {}).items():
        if not _URL_RE.search(c.get("evidence", "")):
            errs.append(f"{group}.evidence has no URL")
        if c.get("confidence") not in CONFIDENCES:
            errs.append(f"{group}.confidence not in {CONFIDENCES}")
        for f in ("date", "review_after"):
            if not _DATE_RE.match(c.get(f, "")):
                errs.append(f"{group}.{f} not YYYY-MM-DD")
    if errs:
        raise ValueError(f"profile {profile.get('profile', '?')}: " + "; ".join(errs))


def check_drift(profile: dict, data: dict, data_name: str) -> list:
    pd = profile_to_data(profile)
    errs = []
    for g in sorted(set(pd) | set(data)):
        if g not in data:
            errs.append(f"{data_name}:{g} in profile but missing from data")
        elif g not in pd:
            errs.append(f"{data_name}:{g} in data but missing from profile")
        else:
            for k in sorted(set(pd[g]) | set(data[g])):
                if pd[g].get(k) != data[g].get(k):
                    errs.append(f"{data_name}:{g}.{k} drift "
                                f"(profile={pd[g].get(k)!r} data={data[g].get(k)!r})")
    return errs


# ── file IO ────────────────────────────────────────────────────────

def find_profile(stem: str):
    matches = sorted(PROFILES_DIR.glob(f"{stem}@*.yaml"))
    if len(matches) > 1:
        raise SystemExit(f"ERROR: multiple profiles for {stem}: "
                         f"{[m.name for m in matches]} — keep exactly one")
    return matches[0] if matches else None


def load_profile(stem: str):
    f = find_profile(stem)
    if f is None:
        return None
    profile = parse_yaml(f.read_text(encoding="utf-8"))
    validate_profile(profile)
    if profile["profile"] != stem:
        raise SystemExit(f"ERROR: {f.name} declares profile {profile['profile']!r}, expected {stem!r}")
    return profile


def write_profile(profile: dict) -> Path:
    PROFILES_DIR.mkdir(exist_ok=True)
    f = PROFILES_DIR / f"{profile['profile']}@{profile['date']}.yaml"
    header = (f"# Capability profile: {profile['profile']} (version {profile['date']})\n"
              f"# Source of truth for model claims — edit here, then run:\n"
              f"#   python scripts/sync_profiles.py --apply\n"
              f"# Per claim group: evidence (URL), confidence, date (last\n"
              f"# verified), review_after (re-review deadline).\n")
    f.write_text(header + dump_yaml(profile), encoding="utf-8")
    return f


def write_data(data: dict, filename: str) -> None:
    path = DATA_DIR / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


# ── main ───────────────────────────────────────────────────────────

def validate_mode() -> list:
    errs = []
    for stem, filename in MODELS.items():
        profile = load_profile(stem)
        if profile is None:
            errs.append(f"profiles/{stem}@<date>.yaml missing (run with --apply to bootstrap)")
            continue
        data = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
        errs += check_drift(profile, data, filename)
        print(f"  {stem}: {len(profile['claims'])} claim groups OK "
              f"(version {profile['date']})")
    return errs


def apply_mode() -> None:
    for stem, filename in MODELS.items():
        profile = load_profile(stem)
        if profile is None:
            data = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
            profile = data_to_profile(stem, data)
            validate_profile(profile)
            f = write_profile(profile)
            print(f"  bootstrapped {f.name} from data/{filename}")
        write_data(profile_to_data(profile), filename)
        print(f"  regenerated data/{filename} from profiles/{stem}@{profile['date']}.yaml")
    for filename in CURATED:
        path = DATA_DIR / filename
        data = json.loads(path.read_text(encoding="utf-8"))
        stamped = 0
        for group, c in data.items():
            if "_review_after" not in c:
                c["_review_after"] = DEFAULT_REVIEW_AFTER
                stamped += 1
        if stamped:
            write_data(data, filename)
        note = f"backfilled _review_after on {stamped} groups" if stamped else "already carries _review_after"
        print(f"  {filename}: {note}")


def main() -> None:
    apply = "--apply" in sys.argv[1:]
    if apply:
        print("apply: regenerating data/*.json from profiles")
        apply_mode()
    errs = validate_mode()
    if errs:
        print("FAIL:")
        for e in errs:
            print("  " + e)
        sys.exit(1)
    print("OK: profiles validated, data/*.json in sync")


if __name__ == "__main__":
    main()

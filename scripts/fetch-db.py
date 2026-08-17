#!/usr/bin/env python3
"""Installer: download the corpus DB from a pinned GitHub Release and verify
its SHA-256 against the committed checksums file (references/checksums.txt).

Refuses on any mismatch or unpinned tag — a tampered/truncated download is
deleted, never installed. Standalone (no repo imports), so it works before
the DB exists.

  python scripts/fetch-db.py                # DEFAULT_TAG pin
  python scripts/fetch-db.py --tag v9.9.9   # override (must be pinned in checksums)
"""
import hashlib
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 crashes on report symbols

REPO = Path(__file__).parent.parent
TARGET_DIR = REPO / "references"
ASSET = "gpt-image2-prompts-full.db"
DEFAULT_TAG = "v2.2.0"  # pin — follows the SKILL.md version; bump per release
RELEASES_URL = "https://github.com/Ekka-Barber/higgsfield-prompt-master/releases"


def url_for(tag):
    return f"{RELEASES_URL}/download/{tag}/{ASSET}"


def expected_sha(tag, checksums_path):
    """Committed checksum line: `<sha256>  <asset>  <tag>`."""
    if not checksums_path.exists():
        sys.exit(f"error: {checksums_path} not found — nothing to verify against")
    for line in checksums_path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == ASSET and parts[2] == tag:
            return parts[0]
    sys.exit(f"error: no checksum pinned for {ASSET} @ {tag} in {checksums_path} "
             f"— refusing to download an unpinned tag")


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    tag = DEFAULT_TAG
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--tag":
            tag = args[i + 1] if i + 1 < len(args) else ""
            i += 2
        elif a.startswith("--tag="):
            tag = a.split("=", 1)[1]
            i += 1
        else:
            sys.exit(f"error: unknown argument {a}")
    if not tag:
        sys.exit("error: --tag requires a value")

    target = TARGET_DIR / ASSET
    part = target.with_name(target.name + ".part")
    expected = expected_sha(tag, TARGET_DIR / "checksums.txt")
    url = url_for(tag)

    print(f"fetching {url}")
    print(f"expected sha256 ({tag}): {expected}")
    h = hashlib.sha256()
    try:
        with urllib.request.urlopen(url) as resp, open(part, "wb") as f:
            for chunk in iter(lambda: resp.read(1 << 20), b""):
                h.update(chunk)
                f.write(chunk)
    except OSError as e:  # URLError/HTTPError are OSError subclasses
        part.unlink(missing_ok=True)
        sys.exit(f"error: download failed: {e}")

    got = h.hexdigest()
    if got != expected:
        part.unlink(missing_ok=True)
        sys.exit(f"error: SHA-256 mismatch for {ASSET} @ {tag}\n"
                 f"  expected {expected}\n  got      {got}\n"
                 f"refusing to install — download deleted")
    part.replace(target)
    print(f"OK: {target} ({target.stat().st_size:,} bytes) verified @ {tag}")


if __name__ == "__main__":
    main()

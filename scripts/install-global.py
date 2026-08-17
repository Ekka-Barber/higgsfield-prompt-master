#!/usr/bin/env python3
"""Install this skill and its /hf-* commands into every AI agent on the machine.

Each agent reads skills from its own directory. Rather than copying the tree
into each one -- which guarantees they drift, and a missed copy means an agent
silently runs yesterday's rules -- this links every install back to this repo.
A commit is then a release to all agents at once.

Windows uses directory junctions (no admin needed, unlike symlinks); POSIX uses
symlinks. Existing real directories are never overwritten: the script reports
them and moves on, so a hand-installed copy is your call to remove.

    python scripts/install-global.py            # link everywhere found
    python scripts/install-global.py --dry-run  # show what would happen
    python scripts/install-global.py --list     # just show discovered agents
"""
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMANDS = REPO / "commands"

#: Skill roots for known agents, relative to the user's home directory.
#: Add a line here when a new agent shows up; everything else follows.
AGENT_SKILL_DIRS = [
    ".agents/skills",
    ".claude/skills",
    ".codex/skills",
    ".cursor/skills",
    ".hermes/skills",
    ".gemini/antigravity-ide/skills",
    ".gemini/antigravity-backup/skills",
]

#: The main skill plus every /hf-* command.
def payload():
    items = [("higgsfield-prompt-master", REPO)]
    if COMMANDS.is_dir():
        items += [(d.name, d) for d in sorted(COMMANDS.iterdir())
                  if d.is_dir() and not d.name.startswith("_")]
    return items


def discover(create_missing=False):
    """Skill roots that exist (or that we are willing to create)."""
    home = Path.home()
    found = []
    for rel in AGENT_SKILL_DIRS:
        path = home / rel
        if path.is_dir():
            found.append(path)
        elif create_missing and path.parent.is_dir():
            found.append(path)
    return found


def link(src: Path, dest: Path, dry_run=False) -> str:
    """Point dest at src. Returns a one-word status."""
    if dest.is_symlink() or (os.name == "nt" and dest.is_dir()
                             and _is_junction(dest)):
        if _resolves_to(dest, src):
            return "ok"
        if dry_run:
            return "relink"
        _unlink(dest)
    elif dest.exists():
        # A real directory someone put there by hand. Never clobber it.
        return "skip(real dir)"

    if dry_run:
        return "would-link"

    dest.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        # Junctions work without developer mode or admin rights; symlinks do not.
        r = subprocess.run(["cmd", "/c", "mklink", "/J", str(dest), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            return f"FAILED({r.stderr.strip()[:40]})"
    else:
        dest.symlink_to(src, target_is_directory=True)
    return "linked"


def _is_junction(path: Path) -> bool:
    try:
        return bool(os.readlink(str(path)))
    except OSError:
        return False


def _resolves_to(dest: Path, src: Path) -> bool:
    try:
        return dest.resolve() == src.resolve()
    except OSError:
        return False


def _unlink(dest: Path):
    if os.name == "nt" and dest.is_dir():
        subprocess.run(["cmd", "/c", "rmdir", str(dest)], capture_output=True)
    else:
        dest.unlink()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change, touch nothing")
    ap.add_argument("--list", action="store_true",
                    help="list discovered agent skill directories and exit")
    ap.add_argument("--create-missing", action="store_true",
                    help="also create skill dirs for agents that lack one")
    args = ap.parse_args()

    roots = discover(create_missing=args.create_missing)
    if args.list:
        print(f"{len(roots)} agent skill director(ies):")
        for r in roots:
            print(f"  {r}{'' if r.is_dir() else '  (would be created)'}")
        return 0
    if not roots:
        print("No agent skill directories found.", file=sys.stderr)
        return 1

    items = payload()
    print(f"Linking {len(items)} skill(s) into {len(roots)} agent director(ies) "
          f"on {platform.system()}\n")

    totals = {}
    for root in roots:
        statuses = []
        for name, src in items:
            st = link(src, root / name, dry_run=args.dry_run)
            statuses.append(st)
            totals[st] = totals.get(st, 0) + 1
        summary = ", ".join(f"{v}×{k}" for k, v in
                            sorted({s: statuses.count(s) for s in set(statuses)}.items()))
        print(f"  {str(root):<58} {summary}")

    print("\n" + ", ".join(f"{v} {k}" for k, v in sorted(totals.items())))
    if not args.dry_run:
        print(f"\nAll agents now read from {REPO}\nA commit here is a release "
              f"to every agent.")
    failed = sum(v for k, v in totals.items() if k.startswith("FAILED"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

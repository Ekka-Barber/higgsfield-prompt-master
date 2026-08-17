#!/usr/bin/env python3
"""Higgsfield Prompt Master — argparse CLI.

Subcommands: search, generate, guide, stats, random, enrich, verify.
--json selects machine-readable output (works before or after the
subcommand). Run via `python higgsfield_prompt.py <cmd>` or directly.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent


def _print_json(obj):
    print(json.dumps(obj, indent=2, default=str))


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # cp1252 consoles choke on corpus text
    try:
        from higgsfield_prompt import HiggsfieldPromptMaster
    except ImportError:  # US-025: packaged layout
        from .higgsfield_prompt import HiggsfieldPromptMaster

    parser = argparse.ArgumentParser(
        prog="higgsfield_prompt",
        description="Search, analyze, and generate GPT Image 2 prompts from the 7,613-prompt corpus.")
    parser.add_argument("--json", action="store_true", help="machine-readable JSON output")
    sub = parser.add_subparsers(dest="command", required=True)

    # --json also accepted after the subcommand (SUPPRESS keeps the
    # subparser from clobbering a main-parser --json with its default).
    json_flag = argparse.ArgumentParser(add_help=False)
    json_flag.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                           help="machine-readable JSON output")

    p = sub.add_parser("search", parents=[json_flag], help="search prompts (relevance-ranked)")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--category", default="")
    p.add_argument("--model", default="")
    p.add_argument("--structure", default="")
    p.add_argument("--limit", type=int, default=5)

    p = sub.add_parser("generate", parents=[json_flag], help="generate a prompt (prints result['prompt'])")
    p.add_argument("goal")
    p.add_argument("--category", default="App / Web Design")
    p.add_argument("--structure", default="Template")
    p.add_argument("--style", default="")
    p.add_argument("--aspect-ratio", default="")

    p = sub.add_parser("guide", parents=[json_flag], help="category guide (structure/technique breakdown)")
    p.add_argument("category", nargs="?", default="App / Web Design")

    sub.add_parser("stats", parents=[json_flag], help="corpus-wide statistics")

    p = sub.add_parser("random", parents=[json_flag], help="random prompt matching filters")
    p.add_argument("--category", default="")
    p.add_argument("--model", default="")
    p.add_argument("--structure", default="")

    sub.add_parser("enrich", parents=[json_flag], help="enrich prompts (writes; reopens DB read-write)")

    sub.add_parser("verify", parents=[json_flag], help="run scripts/verify-generation-diversity.py")

    args = parser.parse_args(argv)
    hpm = HiggsfieldPromptMaster()

    if args.command == "search":
        results = hpm.search(query=args.query, category=args.category, model=args.model,
                             structure=args.structure, limit=args.limit)
        if args.json:
            _print_json([asdict(r) for r in results])
        else:
            for r in results:
                print(f"[{r.id}] {r.title[:60]} ({r.structure_type}, {r.length_chars} chars)")
                print(f"    {r.prompt_text[:120]}...\n")
        return 0

    if args.command == "generate":
        result = hpm.generate_prompt(args.goal, args.category, args.structure,
                                     style=args.style, aspect_ratio=args.aspect_ratio)
        if args.json:
            _print_json(result)
        else:
            print(result["prompt"])
        return 0

    if args.command == "guide":
        _print_json(hpm.category_guide(args.category))
        return 0

    if args.command == "stats":
        _print_json(hpm.stats())
        return 0

    if args.command == "random":
        r = hpm.random_prompt(category=args.category, model=args.model,
                              structure=args.structure)
        if r is None:
            print("No matching prompt found.")
            return 1
        if args.json:
            _print_json(asdict(r))
        else:
            print(f"[{r.id}] {r.title}")
            print(r.prompt_text[:500])
        return 0

    if args.command == "enrich":
        hpm.enrich_all()
        return 0

    if args.command == "verify":
        script = _REPO_ROOT / "scripts" / "verify-generation-diversity.py"
        return subprocess.run([sys.executable, str(script)]).returncode

    return 1  # unreachable: subparsers are required


if __name__ == "__main__":
    raise SystemExit(main())

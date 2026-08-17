#!/usr/bin/env python3
"""
RSC Prompt Extractor — Extracts prompts from Next.js App Router sites via curl.
=============================================================================
Reusable pattern: extracts content from any Next.js RSC (React Server Components)
flight data without a browser. 50x faster than CDP, Cloudflare-safe.

This is the minimal pattern for reuse on other Next.js sites.

Usage:
  python3 scripts/rsc-prompt-extractor.py --url https://example.com/page/123
  python3 scripts/rsc-prompt-extractor.py --start 27000 --end 30000

Output is JSONL: one JSON object per line on stdout; status messages go to
stderr, so stdout can be piped straight into a JSONL consumer.

ENGLISH-ONLY POLICY: the shared langcheck.is_english() filter skips any prompt
containing CJK, Arabic, Cyrillic, Thai, Hebrew, or Devanagari characters. This
is mandatory per user policy — never save non-English prompts.
"""
import subprocess, json, re, argparse, sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent.parent))  # langcheck lives at repo root
from langcheck import is_english


def _validated_url(url):
    """Accept only absolute http(s) URLs (blocks file:// and curl flag injection)."""
    parsed = urlparse(url)
    if url.startswith("-") or parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"URL must be absolute http(s), got: {url!r}")
    return url


def fetch_page(url):
    """Fetch a page via curl."""
    r = subprocess.run(
        ["curl", "-sf", "-L", "--max-time", "10", "-o", "-", _validated_url(url)],
        capture_output=True, text=True, timeout=15
    )
    return r.stdout

def extract_from_rsc(html):
    """
    Extract content from Next.js RSC flight data.

    RSC flight data is embedded in self.__next_f.push([1,"..."]) calls.
    The content is escaped JSON. We look for "text":"..." fields containing
    the actual content (50+ chars to filter out UI labels).
    """
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html)
    if not chunks:
        return None

    full_rsc = ""
    for chunk in chunks:
        try:
            unescaped = json.loads('"' + chunk + '"')
            full_rsc += unescaped
        except json.JSONDecodeError:
            full_rsc += chunk

    # Find "text":"..." fields with substantial content
    text_matches = re.findall(r'"text"\s*:\s*"((?:[^"\\]|\\.){50,})"', full_rsc)
    if text_matches:
        best = max(text_matches, key=len)
        try:
            prompt = json.loads('"' + best + '"')
        except json.JSONDecodeError:
            prompt = best.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

        if len(prompt) > 30:
            return prompt.strip()

    return None

def extract_meta(html, prompt_id):
    """Extract title, model, category from meta tags."""
    data = {"id": prompt_id}

    m = re.search(r'<title>([^<]+)</title>', html)
    if m:
        full_title = m.group(1).strip()
        data["title"] = full_title
        model_m = re.search(r'- (GPT Image 2|Nano Banana|Seedream|Flux)\b', full_title)
        data["model"] = model_m.group(1) if model_m else ""
        cat_m = re.search(r'AI Prompt for (.+?)(?:\s*\||$)', full_title)
        data["categories"] = [cat_m.group(1).strip()] if cat_m else []

    m = re.search(r'<meta name="description" content="([^"]+)"', html)
    if m:
        data["description"] = m.group(1).strip()

    return data

def scrape_single(url_or_id):
    """Scrape a single URL or prompt ID from youmind.com."""
    if url_or_id.isdigit():
        url = f"https://youmind.com/prompts/x-{url_or_id}"
    else:
        url = url_or_id

    html = fetch_page(url)
    if not html or len(html) < 500:
        return None

    prompt_id = int(url_or_id) if url_or_id.isdigit() else 0
    data = extract_meta(html, prompt_id)

    prompt_text = extract_from_rsc(html)
    if prompt_text:
        if not is_english(prompt_text):
            return None  # Skip non-English
        data["prompt_text"] = prompt_text

    return data

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # titles may carry non-cp1252 chars
    except AttributeError:
        pass

    parser = argparse.ArgumentParser(description="RSC Prompt Extractor")
    parser.add_argument("--url", help="Single URL to scrape")
    parser.add_argument("--start", type=int, help="Start ID")
    parser.add_argument("--end", type=int, help="End ID")
    args = parser.parse_args()

    if args.url:
        try:
            result = scrape_single(args.url)
        except ValueError as e:
            sys.exit(f"error: {e}")
        if result:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print("No content found or non-English", file=sys.stderr)
    elif args.start is not None or args.end is not None:
        if args.start is None or args.end is None:
            parser.error("--start and --end must be used together")
        for pid in range(args.start, args.end + 1):
            result = scrape_single(str(pid))
            if result and "prompt_text" in result:
                print(json.dumps(result, ensure_ascii=False))
            else:
                print(f"[{pid}] no content", file=sys.stderr)

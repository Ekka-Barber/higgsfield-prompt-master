#!/usr/bin/env python3
"""
RSC Prompt Extractor — Extracts prompts from Next.js App Router sites via curl.
=============================================================================
Reusable pattern: extracts content from any Next.js RSC (React Server Components)
flight data without a browser. 50x faster than CDP, Cloudflare-safe.

The scraper at ~/.agents/scripts/gpt-image2-rsc-scraper.py is the full production
version with parallel workers, progress tracking, and the is_non_english() filter.
This is the minimal pattern for reuse on other Next.js sites.

Usage:
  python3 scripts/rsc-prompt-extractor.py --url https://example.com/page/123
  python3 scripts/rsc-prompt-extractor.py --start 27000 --end 30000

ENGLISH-ONLY POLICY: The is_non_english() function filters out any prompt
containing CJK (Japanese/Chinese/Korean) or Arabic characters. This is mandatory
per user policy — never save non-English prompts.
"""
import subprocess, json, re, argparse
from pathlib import Path

def is_non_english(text):
    """Check if text contains CJK or Arabic characters."""
    for ch in text:
        if ('\u3040' <= ch <= '\u309f' or   # Hiragana
            '\u30a0' <= ch <= '\u30ff' or   # Katakana
            '\u4e00' <= ch <= '\u9fff' or   # CJK Unified Ideographs
            '\uac00' <= ch <= '\ud7af' or   # Hangul (Korean)
            '\u0600' <= ch <= '\u06ff'):    # Arabic
            return True
    return False

def fetch_page(url):
    """Fetch a page via curl."""
    r = subprocess.run(
        ["curl", "-sf", "-L", "--max-time", "10", "-o", "-", url],
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
        except:
            full_rsc += chunk
    
    # Find "text":"..." fields with substantial content
    text_matches = re.findall(r'"text"\s*:\s*"((?:[^"\\]|\\.){50,})"', full_rsc)
    if text_matches:
        best = max(text_matches, key=len)
        try:
            prompt = json.loads('"' + best + '"')
        except:
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
        if is_non_english(prompt_text):
            return None  # Skip non-English
        data["prompt_text"] = prompt_text
    
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RSC Prompt Extractor")
    parser.add_argument("--url", help="Single URL to scrape")
    parser.add_argument("--start", type=int, help="Start ID")
    parser.add_argument("--end", type=int, help="End ID")
    args = parser.parse_args()
    
    if args.url:
        result = scrape_single(args.url)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("No content found or non-English")
    elif args.start and args.end:
        for pid in range(args.start, args.end + 1):
            result = scrape_single(str(pid))
            if result and "prompt_text" in result:
                print(f"[{pid}] {result.get('title', '?')[:60]}")
                print(f"     {result['prompt_text'][:100]}...")

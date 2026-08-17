#!/usr/bin/env python3
"""US-026 regression checks: scraper hardening (URL scheme, --start 0, JSONL, shared is_english)."""
import io, json, runpy, sys, types
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from langcheck import is_english

SCRIPT = str(Path(__file__).parent / "rsc-prompt-extractor.py")


def fake_html(prompt):
    body = '\\"text\\":\\"' + prompt + '\\"'
    html = ('<html><head><title>Poster AI Prompt for Minimalist | youmind</title></head><body>'
            + 'self.__next_f.push([1,"' + body + '"])' + ' ' * 500 + '</body></html>')
    assert len(html) >= 500
    return html


def run_main(argv, html):
    """Run the scraper's __main__ with subprocess stubbed; return (stdout, stderr, exit_code)."""
    real = sys.modules.get("subprocess")
    sys.modules["subprocess"] = types.SimpleNamespace(
        run=lambda *a, **k: types.SimpleNamespace(stdout=html, stderr="", returncode=0))
    old_argv = sys.argv[:]
    sys.argv = ["rsc-prompt-extractor.py"] + argv
    out, err, code = io.StringIO(), io.StringIO(), 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            runpy.run_path(SCRIPT, run_name="__main__")
    except SystemExit as e:
        if isinstance(e.code, int):
            code = e.code
        else:
            code = 1
            if e.code:
                err.write(str(e.code) + "\n")  # mirror interpreter's sys.exit(msg) print
    finally:
        sys.argv = old_argv
        sys.modules.pop("subprocess")
        if real is not None:
            sys.modules["subprocess"] = real
    return out.getvalue(), err.getvalue(), code


# 1. URL scheme restriction
mod = runpy.run_path(SCRIPT)  # loads functions, __main__ guard skips CLI
for bad in ["file:///etc/passwd", "ftp://example.com/x", "-oC:/stolen.txt",
            "not-a-url", "http://", ""]:
    try:
        mod["_validated_url"](bad)
        raise AssertionError(f"accepted bad URL: {bad!r}")
    except ValueError:
        pass
for good in ["http://example.com/p/1", "https://youmind.com/prompts/x-123"]:
    assert mod["_validated_url"](good) == good
print("[OK] _validated_url: file://, ftp://, leading-dash, relative all rejected; http(s) accepted")

# 2. --start 0 works + JSONL output + stubbed curl is unreachable network-free
out, err, code = run_main(["--start", "0", "--end", "0"], fake_html("A minimalist product poster with soft studio lighting and pastel palette"))
assert code == 0, code
lines = [l for l in out.splitlines() if l.strip()]
assert len(lines) == 1, f"expected 1 JSONL line, got {lines!r}"
row = json.loads(lines[0])
assert row["id"] == 0 and "prompt_text" in row, row
print("[OK] --start 0 --end 0: loop ran (old code silently skipped it), stdout is 1-line JSONL")

# 3. Non-English prompt filtered at fetch time
out, err, code = run_main(["--start", "0", "--end", "0"],
                          fake_html("Минималистичный постер продукта со студийным светом" + "x" * 40))
assert code == 0 and not out.strip() and "no content" in err, (out, err)
print("[OK] Cyrillic prompt skipped, nothing on stdout")

# 4. Bad --url exits non-zero with message
out, err, code = run_main(["--url", "file:///etc/passwd"], "")
assert code == 1 and "http(s)" in err, (code, err)
print("[OK] --url file:// rejected from CLI with exit 1")

# 5. Shared is_english covers all policy scripts
for sample in ["日本語", "한국어", "中文", "العربية", "Привет", "สวัสดี", "שלום", "नमस्ते"]:
    assert not is_english(sample), sample
assert is_english("A clean studio product shot with soft shadows")
print("[OK] is_english: CJK/Arabic/Cyrillic/Thai/Hebrew/Devanagari rejected, English accepted")

# 6. Single implementation: no local language check left in the scraper
src = Path(SCRIPT).read_text(encoding="utf-8")
assert "def is_non_english" not in src and "from langcheck import is_english" in src
print("[OK] scraper imports the single shared langcheck.is_english")

print("ALL CHECKS PASSED")

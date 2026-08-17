#!/usr/bin/env python3
"""Checks for scripts/fetch-db.py — network-free (local http.server).

Proves: happy path over the real URL shape (.../download/<tag>/<asset>),
SHA mismatch refusal (download deleted, nothing installed), unpinned-tag
refusal, --tag override, and that the DEFAULT_TAG pin drives lookups.
"""
import hashlib
import runpy
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = runpy.run_path(str(Path(__file__).parent / "fetch-db.py"))
ASSET = BASE["ASSET"]
ASSET_BYTES = b"fake-corpus-db " * 4096
GOOD_SHA = hashlib.sha256(ASSET_BYTES).hexdigest()

SERVER_ROOT = Path(tempfile.mkdtemp(prefix="fetchdb-serve-"))


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def fresh_ns(tmp, checksum_lines):
    """runpy namespace pointed at a local server + its own checksums/target.

    run_path returns a COPY of the globals — patch the live module dict the
    functions actually look up (main.__globals__), not the returned dict."""
    (tmp / "checksums.txt").write_text(
        "# sha256  asset  tag\n" + "".join(checksum_lines), encoding="utf-8")
    ns = runpy.run_path(str(Path(__file__).parent / "fetch-db.py"))
    g = ns["main"].__globals__
    g["RELEASES_URL"] = f"http://127.0.0.1:{PORT}"
    g["TARGET_DIR"] = tmp
    return ns


def expect_refusal(fn, label):
    try:
        fn()
    except SystemExit as e:
        assert e.code, f"{label}: SystemExit must be a failure (non-zero/message)"
        msg = e.code if isinstance(e.code, int) else str(e.code)
        print(f"  refused ({label}): {str(msg)[:72]}")
        return
    raise AssertionError(f"{label}: should have refused but returned normally")


def main():
    global PORT
    tag_dir = SERVER_ROOT / "download" / "vTEST"
    tag_dir.mkdir(parents=True)
    (tag_dir / ASSET).write_bytes(ASSET_BYTES)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler,
                                                         directory=str(SERVER_ROOT)))
    PORT = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        # 1. happy path: pinned tag, matching sha -> installed
        t1 = Path(tempfile.mkdtemp(prefix="fetchdb-t1-"))
        ns = fresh_ns(t1, [f"{GOOD_SHA}  {ASSET}  vTEST\n"])
        ns["main"](["--tag", "vTEST"])
        target = t1 / ASSET
        assert target.exists() and target.read_bytes() == ASSET_BYTES
        assert not list(t1.glob("*.part")), ".part left behind"
        print("  ok: --tag vTEST installed + verified, no .part residue")

        # 2. mismatch: served bytes differ from pinned sha -> refuse, delete
        t2 = Path(tempfile.mkdtemp(prefix="fetchdb-t2-"))
        ns2 = fresh_ns(t2, [f"{'0' * 64}  {ASSET}  vTEST\n"])
        expect_refusal(lambda: ns2["main"](["--tag", "vTEST"]), "sha mismatch")
        assert not (t2 / ASSET).exists() and not list(t2.glob("*.part"))
        print("  ok: mismatch refused, nothing installed")

        # 3. unpinned tag -> refuse before any network call
        t3 = Path(tempfile.mkdtemp(prefix="fetchdb-t3-"))
        ns3 = fresh_ns(t3, [f"{GOOD_SHA}  {ASSET}  vTEST\n"])
        expect_refusal(lambda: ns3["main"](["--tag", "vOTHER"]), "unpinned tag")
        print("  ok: unpinned --tag refused")

        # 4. default pin: no args resolves DEFAULT_TAG. Serve a tampered
        #    asset under the default tag with a wrong pinned sha -> the sha
        #    mismatch refusal names the default tag (pin drives the lookup).
        dtag = SERVER_ROOT / "download" / BASE["DEFAULT_TAG"]
        dtag.mkdir(parents=True)
        (dtag / ASSET).write_bytes(b"tampered " * 100)
        t4 = Path(tempfile.mkdtemp(prefix="fetchdb-t4-"))
        ns4 = fresh_ns(t4, [f"{'1' * 64}  {ASSET}  {BASE['DEFAULT_TAG']}\n"])
        try:
            ns4["main"]([])
            raise AssertionError("default-tag run should have refused (wrong sha)")
        except SystemExit as e:
            assert BASE["DEFAULT_TAG"] in str(e.code), (
                f"refusal must name the default tag {BASE['DEFAULT_TAG']}: {e.code}")
        print(f"  ok: no-args run uses DEFAULT_TAG pin ({BASE['DEFAULT_TAG']})")

        # 5. URL shape sanity (both constant and override path)
        assert f"/download/{BASE['DEFAULT_TAG']}/{ASSET}" in BASE["url_for"](BASE["DEFAULT_TAG"])
        print("  ok: release URL shape .../download/<tag>/<asset>")

        # 6. unknown argument -> refusal
        expect_refusal(lambda: fresh_ns(t1, [f"{GOOD_SHA}  {ASSET}  vTEST\n"])["main"](["--tags", "x"]),
                       "unknown arg")
        print("  ok: unknown argument refused")
    finally:
        srv.shutdown()
        srv.server_close()
    print("fetch-db checks: all OK")


if __name__ == "__main__":
    main()

"""Keep pytest out of scripts/.

The `scripts/test_*.py` files are standalone verification scripts, not pytest
modules: they run their checks at import time and call `sys.exit(1)` on failure.
That is fine when invoked directly (`python scripts/test_pqs.py`), but if pytest
ever collects them the `sys.exit` fires during import and aborts the whole run
with an INTERNALERROR rather than a test failure.

pytest.ini already scopes `testpaths = tests`, so a bare `pytest` run is safe.
This guard covers the explicit-path invocations that override it -- `pytest .`,
`pytest scripts/`, or an IDE "run tests in this folder".

The real test suite lives in tests/.
"""

collect_ignore_glob = ["test_*.py"]

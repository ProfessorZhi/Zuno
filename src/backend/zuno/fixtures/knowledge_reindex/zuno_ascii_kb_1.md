ZunoTestA

Auto retrieval smoke test.

This fixture exists so save-and-reindex can replay the original local smoke-test file.
It is used to validate automatic route selection for the current smart multi-round retrieval pipeline.

Expected defaults:
- retrieval mode: auto
- top_k: 5
- rerank: disabled unless explicitly enabled by the knowledge config

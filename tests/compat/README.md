# Compatibility Tests

This folder keeps repo-level runtime regression tests that are still useful even when they are not part of the main front path.

Why it lives here instead of `src/backend/zuno/`:

- `src/backend/zuno/` is the runtime package, not a source-owned test tree
- keeping these checks under the repo-level `tests/` tree keeps the runtime boundary cleaner
- legacy-oriented assertions can be rewritten here without reintroducing alias packages

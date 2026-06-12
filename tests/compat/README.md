# Compatibility Tests

This folder keeps compatibility and historical regression tests that still exercise the `agentchat` compatibility surface.

Why it lives here instead of `src/backend/agentchat/`:

- `src/backend/agentchat/` is now a thin compatibility package, not a source-owned test tree
- keeping legacy tests under the repo-level `tests/` tree makes the runtime boundary cleaner
- the test names and import targets stay unchanged, so existing compatibility coverage still works

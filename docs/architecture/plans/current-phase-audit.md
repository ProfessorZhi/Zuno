# Current Phase Audit

## Status Snapshot (2026-06-11)

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: next serial phase
- `Phase 4`: pending
- `Phase 5`: pending
- `Phase 6`: pending
- `Phase 7`: pending

## Phase 2 Closure Evidence

This branch closes the new serial `Phase 2` gate by making repository structure, maintainer docs, and publish-boundary rules visible and testable from the updated `main` line.

Current evidence from the repo state:

- `docs/README.md` now exists as the docs entry index
- `docs/development/README.md` now exists as the maintainer-facing engineering-doc entrypoint
- `docs/development/backend-layering-guidelines.md` now makes the `api / services / dao` structure explicit
- `docs/development/github-publish-boundary.md` now separates public project surfaces from local/private/generated surfaces
- `.gitignore` now clearly excludes `.agent/`, `.agentmd`, `.local/`, `docs/superpowers/`, and generated eval artifacts
- `README.md` now has a dedicated `Repository Layout` section plus Phase 2 verification commands
- `tools/scripts/verify_repo_structure.py` now provides a one-command structure verifier

## Phase 2 Minimum Verification

The Phase 2 minimum gate now passes on this branch:

1. `python tools/scripts/verify_repo_structure.py`
2. `pytest -q tests/test_repo_structure_consistency.py`
3. `pytest -q tests/test_publish_boundary.py`

These checks verify:

- required repository paths exist
- `src/backend` / `src/frontend` / `apps/desktop` / `docs` / `tools` / `infra` / `tests` roles are documented consistently
- publish-boundary and ignore rules are explicit

## Phase 1 Closure Evidence

The earlier `Phase 1` runtime closure remains stable underneath this branch:

- `src/backend/zuno/` remains the runtime-facing package root
- `README.md` local backend start path still uses `uvicorn zuno.main:app`
- Docker backend/worker startup and config mounts still point to the `zuno` path
- `src/backend/agentchat/settings.py` still prefers `ZUNO_CONFIG` and `zuno/config.yaml`

## Next Default Step

Proceed to `Phase 3`: documentation and presentation hard closure.

The default next action is:

- keep the new `Phase 1-2` repository surface stable
- hard-close public docs and presentation entrypoints next
- keep later `Phase 4-7` goals as pending, not pre-claimed

# Current Phase Audit

## Status Snapshot (2026-06-11)

- `Phase 1`: completed
- `Phase 2`: completed
- `Phase 3`: completed
- `Phase 4`: completed
- `Phase 5`: next serial phase
- `Phase 6`: pending
- `Phase 7`: pending

## Phase 4 Closure Evidence

This branch closes the new serial `Phase 4` gate by hardening stable service-layer imports for high-value runtime paths and adding dedicated layering guardrails.

Current evidence from the repo state:

- `src/backend/zuno/core/callbacks/usage_metadata.py` no longer reaches upward into `zuno.api.services.*`
- `src/backend/zuno/database/init_data.py` now depends on stable application-service exports instead of controller-facing service paths
- `src/backend/zuno/services/capability_registry.py`, `services/pipeline/manager.py`, `services/retrieval/retrievers.py`, `services/rag/handler.py`, and `services/tool_creation_service.py` no longer import `zuno.api.services.*` directly
- `src/backend/zuno/services/application/` now exists as a stable lower-layer service export surface
- `docs/development/backend-layering-guidelines.md` now documents the `zuno.services.application.*` boundary rule explicitly
- `tools/scripts/verify_backend_layering.py` now verifies forbidden imports and required application-layer imports
- `tests/test_backend_layering_boundaries.py` and `tests/test_phase4_runtime_boundary_smoke.py` now provide automated guardrails and runtime smoke coverage

## Phase 4 Minimum Verification

The Phase 4 minimum gate now passes on this branch:

1. `python tools/scripts/verify_backend_layering.py`
2. `pytest -q tests/test_backend_layering_boundaries.py`
3. `pytest -q tests/test_phase4_runtime_boundary_smoke.py`
4. minimum `import zuno.main` smoke

These checks verify:

- lower runtime-oriented layers no longer import `zuno.api.services.*` directly
- stable service-layer exports exist for high-value paths
- the tightened boundary still preserves minimum runtime imports
- the repo structure and publish-boundary checks remain stable underneath the Phase 4 change

## Phase 3 Closure Evidence

This branch closes the new serial `Phase 3` gate by hard-closing the public reading path, removing stale phase conflicts from public entry docs, and adding a dedicated docs-surface verifier.

Current evidence from the repo state:

- `README.md` now exposes a stable `First-Read Path`
- `docs/README.md` now separates the first-read path from the maintainer path
- `docs/architecture/README.md` now routes first readers through `specs/README.md`, `plans/README.md`, and `current-phase-audit.md`
- `docs/architecture/zuno_refactor_plan.md` no longer mixes the new serial ledger with the old phase narrative
- `docs/architecture/plans/zuno-refactor-execution-plan.md` now contains a single consistent `Phase 1-7` execution contract
- `docs/architecture/plans/README.md` now distinguishes active plan entrypoints from retained future-phase prep docs
- `tools/scripts/verify_docs_surface.py` now verifies the public docs surface and blocks stale phrases from re-entering the main reading path
- `tests/test_docs_surface_consistency.py` now checks the docs-route contract directly

## Phase 3 Minimum Verification

The Phase 3 minimum gate now passes on this branch:

1. `python tools/scripts/verify_docs_surface.py`
2. `pytest -q tests/test_docs_surface_consistency.py`
3. `pytest -q tests/test_publish_boundary.py`

These checks verify:

- the public reading path is explicit
- README / docs / plans / specs stay aligned
- stale public-demo and old-phase routing no longer leak into the main reading path
- publish-boundary docs still remain explicit

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

Proceed to `Phase 5`: LangGraph + GraphRAG mainline deepening.

The default next action is:

- keep the new `Phase 1-4` repository surface stable
- deepen `LangGraph + GraphRAG` mainline next
- keep later `Phase 6-7` goals as pending, not pre-claimed

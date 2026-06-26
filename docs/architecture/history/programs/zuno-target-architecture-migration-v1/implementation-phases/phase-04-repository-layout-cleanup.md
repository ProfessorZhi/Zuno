# Phase 04: Repository Layout Cleanup

## Goal

Align repository structure with target layout rules after active runtime
dependencies are removed.

## Dependency

Phase 01 through Phase 03 complete.

## Scope

- Move history to `docs/architecture/history/`.
- Keep executable Agent programs in `.agent/programs/`.
- Keep references as indexes, not duplicated target architecture prose.
- Remove or archive dead compatibility folders after grep proof.

## Files To Change

- `.agent/`
- `docs/architecture/history/`
- `tools/scripts/verify_repo_structure.py`
- `.agent/scripts/verify_repo_hygiene.py`
- matching repository structure tests

## Files Not To Change

- Runtime code unless a move is already proven by prior phases.
- Generated or local data.
- Catch-all packages named only `services`, `core`, `utils`, `common`, or
  `helpers`.

## Acceptance Gates

- No duplicate active program front paths.
- No superseded execution plan remains in `.agent/programs/`.
- `docs/architecture/history/` is the only history archive.
- Verifiers protect target layout without treating Blocked Legacy as target.

## 2026-06-26 Safe Prework

Retired Domain Pack UI capture and responsive-check scripts were moved out of
active `tools/scripts/` and archived under:

- `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/`

The move preserves old UI evidence while keeping active repository tools from
generating `docs/ui-gallery/knowledge-product-refactor-deep-graphrag-v1` or
mocking retired `/api/v1/domain-packs` and Domain Pack settings pages.

The old Phase 6 bundle staging helper scripts were also moved out of active
`tools/scripts/` and archived under the same historical program scripts path:

- `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/preview_phase6_bundle_scope.py`
- `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/verify_phase6_bundle_ready.py`

The move preserves local staging evidence for the completed historical Phase 6
work without keeping a stale Phase 6 bundle tool on the active maintenance path.

Superseded migration specs were moved from active `docs/architecture/specs/`
to `docs/architecture/history/specs/`:

- `deep-graphrag-v1-runtime.md`
- `domain-pack-langgraph-graphrag-architecture.md`
- `domain-pack-builder.md`
- `knowledge-product-boundary.md`

Active docs entrypoint verification now scans stable specs and rejects
Domain Pack-as-current/target-driver phrases outside the specs index, which may
link to history but may not keep Domain Pack-era target prose on the active
specs front path.
This keeps old migration evidence reachable while preventing active specs from
becoming a second target front path for Domain Pack.

Active public-release staging helpers no longer expose `retired_runtime_legacy`
as a staging or commit-order group, and they no longer print commands for
retired Domain Pack route/API, graph, runtime, or service source paths. Public
demo and architecture-maintenance docs now prefer GraphRAG Project /
query-policy and migration-compatibility wording instead of Domain Pack-first
workflow language.

Superseded ADR 0001 Domain Pack Binding was moved from active architecture
decisions to:

- `docs/architecture/history/decisions/0001-domain-pack-binding.md`

The active decisions index now points only to decisions that still influence
the current mainline, while history keeps the old Domain Pack binding decision
reachable.

Public-release staging commands no longer use a broad `git add
src/backend/zuno/` command for `backend_public_entrypoints`, because that could
stage `backend_domain_runtime` or `backend_rag_graphrag_eval` changes into the
wrong commit group. The public-release audit also treats the whole
`docs/superpowers/` tree as local-only instead of only
`docs/superpowers/specs/`, and preview output points to the existing
`docs/architecture/history/development/docs-and-readme-ready.md` note.

The superseded reference migration guide was also moved from
`docs/reference/history/migration.md` to
`docs/architecture/history/reference/migration.md`, leaving
`docs/architecture/history/` as the only tracked docs history archive.

## 2026-06-26 Closure Evidence

The superseded `official-graphrag-cleanup-v1` executable program was moved from
`.agent/programs/official-graphrag-cleanup-v1/` to:

- `docs/architecture/history/programs/official-graphrag-cleanup-v1/`

The move leaves `.agent/programs/` with only `current.md`, `README.md`, and the
active `zuno-target-architecture-migration-v1/` program. Agent references,
workflow scripts, docs entrypoints, repo-structure verifiers, and the target
layout HTML now point to the archived program as history rather than an active
execution front path.

Capability and tool API controllers now route runtime/discovery work through
`zuno.api.services`:

- `src/backend/zuno/api/v1/capability.py` calls `CapabilityService`.
- `src/backend/zuno/api/v1/tool.py` calls `ToolRuntimeService`.

The runtime service imports remain in API service adapters, so API route files
no longer directly import `zuno.services.*`, `zuno.core.*`, or `zuno.tools.*`.
This closes the first low-risk backend ownership boundary without broad
database, service, core, or frontend moves.

## Verification Commands

```powershell
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_repo_hygiene.py
pytest -q tests/test_repo_structure_consistency.py tests/test_repo_hygiene.py
pytest -q tests/test_zuno_public_entrypoints.py tests/test_zuno_runtime_chain_guard.py tests/test_layered_api_boundaries.py
pytest -q tests/test_capability_registry.py tests/test_cli_tool_discovery.py tests/test_tool_service_runtime_type.py tests/test_user_defined_tool_runtime.py
git diff --check
```

## Evidence To Return

- move table
- verifier output
- final `git status --short`

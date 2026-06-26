# Phase 01: Official Cleanup 11C Dependency Removal

## Status

Complete for active runtime cleanup; live graph data backfill remains an
operational migration step.

## Goal

Remove active dependencies that keep Domain Pack, `DomainQAGraph`,
`MultiAgentSupervisorGraph`, and migration compatibility tests on the current
path.

## Dependency

Phase 00 complete.

## Scope

- Continue `official-graphrag-cleanup-v1` Phase 11C.
- Replace remaining active compatibility tests and migration surfaces with
  GraphRAG Project equivalents or archived history. Keep already-retired root
  assets, Docker mounts, route, service, frontend, and graph sources absent.
- Keep migration-only compatibility only where a test proves it is still
  required.

## Files To Change

- `src/backend/zuno/api/`
- `src/backend/zuno/api/services/`
- `src/backend/zuno/core/`
- `apps/web/src/apis/`
- `tools/evals/zuno/`
- `tests/`
- `docs/architecture/history/programs/official-graphrag-cleanup-v1/`

## Files Not To Change

- Database migrations unless explicitly approved.
- Dependency versions.
- Java, microservice, event worker, or product-level multi-agent code.

## Acceptance Gates

- No active current route depends on `/domain-packs`.
- No current `GeneralAgent` path imports `DomainQAGraph`.
- `MultiAgentSupervisorGraph` is removed from current runtime or explicitly
  moved to history/compat with proof.
- migration compatibility tests are reduced, replaced, or reclassified with
  exact evidence.

## Verification Commands

```powershell
pytest -q tests/test_phase11a_knowledge_query_service.py tests/test_phase11b_single_generalagent_cutover.py
pytest -q tests/test_zuno_public_entrypoints.py tests/test_zuno_runtime_chain_guard.py
git grep -n "domain_pack_id"
git grep -n "DomainQAGraph"
git grep -n "MultiAgentSupervisorGraph"
git diff --check
```

## Evidence To Return

- moved/deleted file list
- replacement tests
- grep classification
- commit hash and push result

## 2026-06-25 Progress

Removed from the active current path:

- Current FastAPI router no longer imports or includes
  `zuno.api.v1.domain_packs.router`; `/api/v1/domain-packs` is no longer a
  mounted current route.
- Active Vue knowledge routes and settings-shell mappings no longer expose
  Domain Pack list/create/detail pages.
- Knowledge create/settings pages no longer call `getDomainPacksAPI`; they use
  `graphrag_project_id` as the GraphRAG Project field.
- Workspace knowledge prefetch and Workspace `search_knowledge_base` no longer
  import `AgentRuntime`, expose `domain_qa_runtime`, or call
  `_run_domain_pack_query`; they use `KnowledgeQueryService` and
  `KnowledgeQueryResult` payload mapping.
- The standalone `src/backend/zuno/core/runtime/agent_runtime.py` facade has
  been removed from current backend source; `zuno.core` and
  `zuno.core.runtime` no longer export `AgentRuntime`.
- `DomainQAGraph` and `MultiAgentSupervisorGraph` are no longer exported from
  `zuno.core` or `zuno.core.graphs`; the direct `DomainQAGraph` source and
  legacy graph state module have been removed from current backend source.
- The direct `src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py`
  source has been removed from current backend source; root Phase 11C tests now
  keep retirement evidence that the module stays absent.
- Phase 0 recovery/current-truth tests no longer treat `DomainQAGraph` or
  `DomainPackLoader` as high-value current imports; they use
  `KnowledgeQueryService`, `GraphRAGQueryService`, and
  `GraphRAGProjectSnapshot`.
- Root Phase 5 runtime import tests no longer import Domain Pack loader or the
  legacy graph as current mainline; root Phase 11C tests own retired-import
  coverage.
- Former Phase 5 and Phase 1 `DomainQAGraph` behavior compat tests have been
  removed after the direct graph source retired; root Phase 11C tests now keep
  retirement evidence for the old module instead of behavior coverage. Former
  `MultiAgentSupervisorGraph` compat guard files have also been retired after
  root Phase 11C tests took over the source/import boundary.
- Domain Pack formalization and Contract Review asset-runtime tests have moved
  into root migration compatibility tests while Phase 02 completes asset
  migration evidence.
- Root Phase 5 domain runtime path tests no longer assert direct legacy graph
  source availability; root Phase 11C tests own retired-import coverage.
- The stale tracked backend package asset copy
  `src/backend/zuno/domain_packs/contract_review/` has been removed from the
  current package path and archived under
  `docs/architecture/history/domain-packs/backend-package-contract-review/`
  after grep showed it was not the current project asset source.
- `tests/test_phase5_domain_runtime_paths.py` no longer expects
  `GeneralAgent` to expose `KnowledgeService` or `AgentRuntime`; it now records
  the current 11B fact that `GeneralAgent` uses `KnowledgeQueryService` and a
  single react loop while protecting the retired `AgentRuntime` facade boundary.
- `tests/test_general_agent_project_query_runtime.py` has been reclassified
  from legacy Domain Pack runtime coverage to project query runtime and retired
  compatibility evidence: it now proves `GeneralAgent` no longer exposes the
  old `KnowledgeService` / `AgentRuntime` / `RagHandler` path.
- Root Phase 11C tests prove the direct `DomainQAGraph` module and legacy graph
  state module remain retired from current backend source.
- `KnowledgeService.get_runtime_settings` no longer auto-loads
  `DomainPackLoader` from `domain_pack_id`. It preserves the migration field
  and explicit `domain_pack` compatibility payloads while keeping
  `graphrag_project_id` as the GraphRAG Project configuration field.
- `GraphRetriever` no longer loads Domain Pack retrieval policy from a bare
  `domain_pack_id`; graph policy must be provided as explicit `query_policy`.
  Contract Review compatibility graph tests now load that policy from the
  GraphRAG Project example assets.
- `GraphRetrieverAdapter`, `GraphRetriever`, `GraphWriter`, and the Neo4j
  client now use `graphrag_project_id` as the primary graph scope for new graph
  writes and project-scoped graph retrieval. Neo4j queries dual-read legacy
  `domain_pack_id` properties until backfill is applied.
- Stackless local eval can build its Contract Review local graph from
  GraphRAG Project schema, prompt, retrieval policy, and eval assets without
  loading `DomainPackLoader` for `contract_review`.
- The dedicated Contract Review eval now loads the same GraphRAG Project
  compatibility payload and eval fixture without loading `DomainPackLoader` or
  executing through `DomainQAGraph`.
- Stackless local eval no longer has a generic Domain Pack loader fallback;
  when an id is provided, it must resolve to GraphRAG Project assets.
- The former stackless Contract Review local eval test has been reclassified
  from `test_stackless_local_eval_contract_domain_pack.py` to
  `test_stackless_local_eval_contract_project_query_policy.py`; it now builds
  with `graphrag_project_id="contract_review"` and explicit GraphRAG Project
  `query_policy` instead of presenting the behavior as Domain Pack runtime
  coverage.
- The `src/backend/zuno/services/domain_pack/` runtime service package has
  been removed from current backend source. Root tests now prove the current
  project query/eval paths work without importing it, and root Phase 11C tests
  keep the retired-import boundary.
- Root `domain-packs/contract_review/` has been archived under
  `docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
  longer copies or mounts `/app/domain-packs`.

## 2026-06-26 Progress

Public contract cleanup started:

- Agent create/update DTOs now expose `graphrag_project_id` as the public
  project field. Legacy `domain_pack_id` is accepted only as migration input
  and is mapped to the existing Agent database column inside
  `AgentService`.
- Knowledge config DTOs now accept legacy `domain_pack_id` as migration input,
  but normalized public knowledge config output no longer re-emits
  `domain_pack_id`.
- Frontend knowledge API/config types no longer include `domain_pack_id` in
  the target payload or patch contract. `normalizeKnowledgeConfig` still reads
  old `domain_pack_id` input for migration compatibility, but
  `toKnowledgeConfigPatch` no longer sends it.
- A non-destructive Neo4j migration helper was added at
  `tools/migrations/migrate_domain_pack_id_to_graphrag_project_id.py`. It
  defaults to dry-run counts and requires explicit `--apply` to backfill
  `graphrag_project_id` from legacy `domain_pack_id` on graph nodes and
  relations.
- `tests/test_domain_pack_api_skeleton.py` was renamed to
  `tests/test_phase11c_domain_pack_api_retirement.py` so the test name matches
  the current retirement guard role instead of implying an active API skeleton.

2026-06-26 additional closure:

- Graph writer metadata, structured graph extraction, pipeline graph indexing,
  `GraphRetrieverAdapter`, `GraphRetriever`, and the Neo4j client now use
  `graphrag_project_id` as the primary project scope for active graph writes
  and retrieval calls.
- Neo4j query filters dual-read old `domain_pack_id` properties with
  `COALESCE` only so pre-backfill graph data remains readable.
- Tests now prove new graph payloads and extractor output carry
  `graphrag_project_id` and do not emit `domain_pack_id` when project payloads
  are present.

Still retained as bounded migration evidence:

- Agent database model/initialization still uses the old persisted column name
  until a separate database migration exists.
- Legacy API/schema/frontend input aliases accept `domain_pack_id` only to map
  old callers onto `graphrag_project_id`.
- Eval CLIs and report payloads still expose compatibility fields where current
  tests name that role.
- The Neo4j backfill helper must be run with explicit `--apply` before old
  graph data can be considered fully migrated.

Retired from current source:

- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `src/backend/zuno/core/graphs/states.py`
- `src/backend/zuno/services/domain_pack/`
- `src/backend/zuno/api/v1/domain_packs.py`
- `src/backend/zuno/api/services/domain_pack.py`
- `apps/web/src/apis/domain-packs.ts`
- `apps/web/src/pages/knowledge/domain-pack-list.vue`
- `apps/web/src/pages/knowledge/domain-pack-create.vue`
- `apps/web/src/pages/knowledge/domain-pack-detail.vue`

No longer blocked by current eval runtime:

- `tools/evals/zuno/contract_review_eval/` no longer depends on
  `DomainPackLoader` or `DomainQAGraph`.
- GraphRAG Project scope reaches graph storage through `graphrag_project_id`
  without restoring Domain Pack policy loading.
- Stackless Contract Review local eval behavior is now protected by a
  project-query-policy named test instead of a Domain Pack named current test.
- Root `tests/` still contains migration/current compatibility coverage for
  Workspace, Domain Pack migration fields, and Contract Review GraphRAG Project
  compatibility payloads. The main root compatibility tests now use project or
  retirement naming instead of Domain Pack runtime naming. Retired runtime
  import/source guards have moved to root Phase 11C tests.

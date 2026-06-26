# Current Agent Program

The current executable program is:

- [Zuno Target Architecture Migration V1](zuno-target-architecture-migration-v1/README.md)

Current status:

- Phase 00 is complete for the current run: Git, focused Phase 11A/11B tests,
  and legacy grep evidence were re-verified.
- Phase 01 active runtime cleanup is complete; live graph data backfill remains
  an operational migration step. The current FastAPI router
  no longer mounts `/domain-packs`, and active Vue knowledge routes/pages no
  longer open Domain Pack entrypoints. Workspace knowledge prefetch/tools no
  longer import `AgentRuntime` or call `_run_domain_pack_query`; they use
  `KnowledgeQueryService`. `KnowledgeService.get_runtime_settings` preserves
  `domain_pack_id` as a migration field but no longer auto-loads
  `DomainPackLoader` from it. `GraphRetriever` now requires explicit
  `query_policy` for project policy defaults instead of loading
  `DomainPackLoader` from `domain_pack_id`. `GraphRetrieverAdapter`,
  `GraphRetriever`, `GraphWriter`, structured graph extraction, pipeline graph
  indexing, and the Neo4j client now use `graphrag_project_id` as the primary
  graph scope while dual-reading legacy graph properties until the migration
  helper is applied. The
  `src/backend/zuno/services/domain_pack/` runtime service package is retired
  from current backend source. Agent and Knowledge public DTOs now prefer
  `graphrag_project_id`; legacy `domain_pack_id` is accepted only as migration
  input and mapped to existing storage boundaries where required. Frontend
  knowledge config patches no longer send `domain_pack_id`. A dry-run-first
  Neo4j migration helper exists under `tools/migrations/` for backfilling
  `graphrag_project_id` from legacy graph `domain_pack_id` properties; live
  graph data backfill remains an operational step, not active code debt.
- Phase 11A and Phase 11B from `official-graphrag-cleanup-v1` are complete.
- Phase 11C active runtime cleanup is closed for the current code path; bounded
  migration aliases remain only where tests name their storage/eval/DB role.
  The former `tests/compat/` holding area is retired. Root
  Domain Pack assets are archived under
  `docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
  longer copies or mounts `/app/domain-packs`. Domain Pack backend endpoint/API-service
  wrappers and frontend API/page files are retired from current source. The
  standalone `AgentRuntime` facade and direct `MultiAgentSupervisorGraph`
  source have been removed from current backend source and exports. The direct
  `DomainQAGraph` source and its legacy graph state module have also been
  removed from current backend source.
  `DomainQAGraph` and
  `MultiAgentSupervisorGraph` are no longer exported from current core package
  public surfaces.
- Phase 02 is complete:
  `examples/graphrag-projects/contract_review/` now holds the Target
  GraphRAG Project copy of Contract Review schema, prompts, retrieval policy,
  and eval fixture. The project loader materializes `retrieval_policy.yaml`
  plus schema/eval assets for explicit graph query policy and stackless local
  eval. Contract Review eval now reads the GraphRAG Project compatibility
  payload and eval fixture without loading `DomainPackLoader` or executing
  through `DomainQAGraph`; its extractor calls now use
  `project_payload=project_payload` as the primary internal contract. Root
  Domain Pack assets are archived as History and Docker no longer carries
  Domain Pack mounts. Stackless local eval now requires GraphRAG Project assets
  when an id is provided and no longer keeps the private
  `_load_graph_project_domain_payload` alias.
- Phase 03 is complete for the public GraphRAG Project mainline:
  `/knowledge/search` now routes through
  `KnowledgeQueryService`, Contract Review project assets expose
  `to_project_payload()`, graph extractors accept `project_payload` as the
  active payload parameter without the old `domain_pack` payload alias, and
  stackless eval entrypoints prefer `graphrag_project_id` /
  `--graphrag-project-id` while retaining legacy compatibility aliases where
  explicitly tested. Graph scope now uses `graphrag_project_id` as the primary
  field for graph writes and retrieval while dual-reading old graph properties
  for pre-backfill data. Active stable architecture specs now describe
  GraphRAG Project / query policy as the mainline driver instead of Domain
  Pack, and the docs entrypoint verifier guards against reintroducing Domain
  Pack-as-target wording outside explicit migration specs. Active near-term
  target docs now also reject wording that marks retired `DomainQAGraph`,
  retired Domain Pack endpoint/page wrappers, or bare `domain_pack_id` query
  policy as current target evidence.
- Phase 04 has safe prework started: retired Domain Pack UI capture and responsive-check scripts
  were archived under
  `docs/architecture/history/programs/knowledge-product-refactor-deep-graphrag-v1/scripts/`.
  The old Phase 6 bundle staging helpers were archived under the same
  historical program path, and superseded migration specs were moved from
  active `docs/architecture/specs/` to `docs/architecture/history/specs/`.
  Active docs verifiers now scan stable specs so `.agent` and `docs/` keep the
  Current / Target / History boundary without treating migration context as
  target layout. Active public-release staging helpers no longer expose a
  `retired_runtime_legacy` group or `git add` commands for already-retired
  Domain Pack route/API, graph, runtime, and service source paths; active demo
  and maintenance docs prefer GraphRAG Project / migration compatibility
  wording. Superseded ADR 0001 Domain Pack Binding is archived under
  `docs/architecture/history/decisions/`, and public-release stage commands no
  longer use a broad `src/backend/zuno/` add path that could cross backend
  release groups.
- Phase 12 is partial / not closed.
- Context/Memory implementation is folded into this program after repository
  layout and GraphRAG mainline gates.

Superseded candidate program:

- `context-memory-agent-runtime-v1` is archived under
  `docs/architecture/history/programs/context-memory-agent-runtime-v1/`.

Formal public status is summarized in:

- `docs/architecture/roadmap.md`

# Zuno

Zuno is a local-first Agent Workspace. It combines a Vue web app, an Electron
desktop shell, a FastAPI backend, LangGraph orchestration, RAG / GraphRAG,
tools, MCP integration, and local evaluation into one monorepo.

## Current Status

Current:

- `apps/web` is the Vue web workspace.
- `apps/desktop` is the Electron desktop workspace.
- `src/backend/zuno` is the only active Python backend runtime boundary.
- Phase 0-6 architecture closure remains complete historical truth.
- Target Architecture Migration V1 is closed and archived.
- The active executable Agent program is
  `.agent/programs/zuno-target-runtime-v2/`.
- Phase 11A is complete: `KnowledgeQueryService`, `GraphRAGQueryService`,
  `GraphRAGProjectSnapshot`, and `KnowledgeQueryResult` exist in the current
  runtime.
- Phase 11B is complete: the current knowledge-answering call chain is
  `Completion API -> CompletionService -> GeneralAgent single loop ->
  search_knowledge_base -> KnowledgeQueryService -> GraphRAGQueryService ->
  RetrievalPlanner / RetrievalOrchestrator -> Evidence / Citation / Trace ->
  GeneralAgent answer`.

Target:

- Keep one stable monorepo baseline.
- Keep the target architecture as: Single GeneralAgent Runtime + Context /
  Memory Engine + Capability / Tool Retrieval + Knowledge / GraphRAG Retrieval
  + Evidence / Citation / Trace / Eval + Typed API + Web/Desktop.
- Use Summary Compression + Structured Extraction as the Memory target
  strategy.
- Use a ToolCard Registry with keyword / alias lookup, Native BM25, optional
  vector search, permission / health / cost filtering, and capability selection
  trace as the Capability target.
- Use Native BM25 as a local ranking algorithm; Elasticsearch is an optional
  external adapter, not the BM25 algorithm itself.
- Use multi-query and multi-retriever retrieval with RRF coarse fusion
  (`k=60`), optional rerank, evidence check, citations, and trace in enhanced
  paths.
- Keep GraphRAG query methods as `basic`, `local`, `global`, and `drift`;
  `auto` is a router, not a fifth query mode.
- Keep Java services, microservices, event workers, product-level multi-agent
  mode, and Coding Agent direction as future direction only.

Phase 11C closure / Bounded Legacy Compatibility:

- Phase 11C active runtime cleanup is complete. `/api/v1/domain-packs` is no
  longer mounted on the current FastAPI router, the active Vue knowledge
  routes/pages no longer open the Domain Pack builder/list/detail flow, and
  the old frontend Domain Pack API/page files have been retired from
  `apps/web/src/`.
- Workspace knowledge prefetch/tools now use `KnowledgeQueryService`; the
  `/knowledge/search` API service path also uses `KnowledgeQueryService`
  instead of the legacy `RagHandler` search path. The standalone `AgentRuntime`
  facade and direct `MultiAgentSupervisorGraph` source have been removed. The
  direct `DomainQAGraph` source and legacy graph state module have also been
  removed. `DomainQAGraph` /
  `MultiAgentSupervisorGraph` are no longer current core package public
  exports.
- `KnowledgeService.get_runtime_settings` preserves `domain_pack_id` as a
  migration field but no longer auto-loads `DomainPackLoader` from that field;
  GraphRAG Project defaults come from `graphrag_project_id` or explicit
  `project_payload` runtime configuration. Legacy `domain_pack` runtime
  payload input is accepted only as a migration fallback.
- `GraphRetriever` no longer loads Domain Pack retrieval policy from a bare
  `domain_pack_id`; graph policy must come from explicit `query_policy`, such
  as a GraphRAG Project `retrieval_policy.yaml`.
- Graph writer/client/retriever paths now use `graphrag_project_id` as the
  primary graph scope for new graph writes and project-scoped graph retrieval.
  Legacy graph properties are dual-read only for migration until the
  dry-run-first Neo4j backfill is applied.
- Stackless local eval and the dedicated Contract Review eval can build from
  GraphRAG Project assets without loading `DomainPackLoader`; stackless local
  eval now requires GraphRAG Project assets when an id is provided. The
  `src/backend/zuno/services/domain_pack/` runtime service package is also
  retired from current backend source.
- Root `domain-packs/` assets have been archived under
  `docs/architecture/history/domain-packs/root-contract-review/`, and Docker no
  longer copies or mounts `/app/domain-packs`. Remaining `domain_pack_id`
  references are bounded migration aliases, existing database-column
  compatibility, eval CLI compatibility, and retirement/history tests. The
  former `tests/compat/` holding area is retired. Root Phase 11C tests guard
  the retired
  `DomainQAGraph`, `MultiAgentSupervisorGraph`, `AgentRuntime`, and Domain Pack
  runtime service imports. The old Domain Pack backend endpoint/API-service
  wrappers are retired.
- These surfaces are not the future public mainline, but compatibility fields
  are retained only where existing storage, eval, or retirement evidence still
  requires them. Neo4j legacy graph data backfill is an operational migration
  helper / live data step, not active code debt.
- Phase 12 closure evidence is complete: full pytest, formal Contract Review
  eval, stackless eval baseline comparison, trace metadata, legacy grep
  classification, and docs/evidence sync are complete.

## Default Reading Path

First-time readers start here:

1. [README.md](./README.md)
2. [docs/architecture/current-architecture.md](./docs/architecture/current-architecture.md)
3. [docs/architecture/target-architecture.md](./docs/architecture/target-architecture.md)
4. [docs/architecture/roadmap.md](./docs/architecture/roadmap.md)
5. [docs/evidence/public-demo.md](./docs/evidence/public-demo.md)

Maintainers and Agents should then read:

- [AGENTS.md](./AGENTS.md)
- [.agent/README.md](./.agent/README.md)
- [.agent/references/current-program.md](./.agent/references/current-program.md)

## Repository Layout

```text
.
├─ apps/
│  ├─ desktop/                  # Electron desktop shell
│  └─ web/                      # Vue web workspace
├─ docs/                        # stable human-facing documentation
│  ├─ architecture/             # current, target, roadmap, decisions, history
│  ├─ development/              # maintainer runbooks
│  ├─ evidence/                 # selected public evidence
│  └─ reference/                # stable reference material
├─ examples/graphrag-projects/  # Target GraphRAG Project examples
├─ infra/                       # deployment and environment infrastructure
├─ src/backend/zuno/            # current backend runtime truth
├─ tests/                       # repo-level verification
├─ tools/                       # scripts, launchers, evals, maintenance tooling
├─ .agent/                      # local Agent workflow library
└─ AGENTS.md                    # repository-level Agent entrypoint
```

## Local Run

Backend:

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

Frontend:

```powershell
cd apps\web
npm ci
npm run dev -- --host 127.0.0.1 --port 8090
```

Desktop:

```powershell
cd apps\desktop
npm ci
npm start
```

Docker:

```powershell
copy infra\docker\docker_config.example.yaml infra\docker\docker_config.local.yaml
docker compose -f infra/docker/docker-compose.yml up --build -d
```

## Verification

Focused documentation and repository checks:

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/test_docs_entrypoints.py
pytest tests/test_phase0_runtime_recovery.py
pytest -q tests/test_repo_structure_consistency.py
pytest -q tests/test_publish_boundary.py
```

Full test run:

```powershell
pytest -q
```

## License

[MIT](./LICENSE)

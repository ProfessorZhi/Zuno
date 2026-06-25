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
- The active executable program is Target Architecture Migration V1, which
  continues the unfinished official GraphRAG alignment program gates.
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
- Move the front-path GraphRAG language toward GraphRAG Project, Prompt
  Tuning, Query Method, index versions, evidence, and trace metadata.
- Keep Context & Memory Engine, Capability System, and GraphRAG Project query
  concepts as the near-term target direction until implemented and verified.
- Keep Java services, microservices, event workers, product-level multi-agent
  mode, and Coding Agent direction as future direction only.

Phase 11C progress / Blocked Legacy:

- Phase 11C has started, but remains blocked. `/api/v1/domain-packs` is no
  longer mounted on the current FastAPI router, and the active Vue knowledge
  routes/pages no longer open the Domain Pack builder/list/detail flow. The
  old frontend Domain Pack API/page files have also been retired from
  `apps/web/src/`.
- Workspace knowledge prefetch/tools now use `KnowledgeQueryService`; the
  standalone `AgentRuntime` facade and direct `MultiAgentSupervisorGraph`
  source have been removed. `DomainQAGraph` / `MultiAgentSupervisorGraph` are
  no longer current core package public exports.
- `KnowledgeService.get_runtime_settings` preserves `domain_pack_id` as a
  migration field but no longer auto-loads `DomainPackLoader` from that field;
  GraphRAG Project defaults come from `graphrag_project_id` or explicit
  runtime configuration.
- `GraphRetriever` no longer loads Domain Pack retrieval policy from a bare
  `domain_pack_id`; graph policy must come from explicit `query_policy`, such
  as a GraphRAG Project `retrieval_policy.yaml`.
- Stackless local eval and the dedicated Contract Review eval can build from
  GraphRAG Project assets without loading `DomainPackLoader`; generic legacy
  `domain_pack_id` fallback remains for unmigrated packs.
- Remaining blockers still exist in `domain-packs/`, Domain Pack runtime
  services, direct `DomainQAGraph` loader fallback paths, Docker
  surfaces, retained `MultiAgentSupervisorGraph` compat retirement evidence,
  and `tests/compat/`. The old Domain Pack backend endpoint/API-service
  wrappers are retired.
- These surfaces are not the future public mainline, but they must not be
  deleted before active dependency removal is proven.
- Phase 12 is partial / not closed: final full `pytest` and formal Eval
  baseline comparison are not complete.

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
├─ domain-packs/                # Blocked Legacy runtime assets
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

# Official GraphRAG Cleanup V1 Implementation Roadmap

## Program Goal

Move Zuno from the current Domain Pack and legacy query-mode implementation
toward the near-term GraphRAG Project architecture without reopening future
platform work.

## Current State

Current truth is still the Python monorepo runtime:

- `src/backend/zuno/` is the backend runtime boundary.
- `apps/web/` and `apps/desktop/` are the application shells.
- `domain-packs/` still exists as current or migration evidence; the old
  `src/backend/zuno/domain_packs/` asset copy has been removed from the current
  package path and archived under `docs/architecture/history/domain-packs/`.
- Domain Pack services, retained frontend/API assets, graph names, eval/Docker
  references, and tests still exist in active or Blocked Legacy paths. The
  current FastAPI router, active Vue knowledge entrypoints, `GeneralAgent`, and
  Workspace knowledge prefetch/tools no longer use the Domain Pack runtime
  path.
- Retrieval already has `RetrievalPlanner`, `RetrievalOrchestrator`,
  `RetrievalFusion`, BM25/vector/graph adapters, community services, requery,
  index version fields, and trace metadata.

Read-only evidence gathered for this roadmap found active references under:

- `src/backend/zuno/api/v1/domain_packs.py`
- `src/backend/zuno/api/services/domain_pack.py`
- `src/backend/zuno/api/services/knowledge.py`
- `src/backend/zuno/core/graphs/domain_qa_graph.py`
- `src/backend/zuno/core/graphs/states.py`
- `src/backend/zuno/services/domain_pack/`
- `src/backend/zuno/services/graphrag/`
- `src/backend/zuno/services/retrieval/`
- `apps/web/src/apis/domain-packs.ts`
- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `apps/web/src/utils/retrieval.ts`
- `tests/compat/`
- `tools/evals/zuno/`
- `tools/launchers/windows/_Zuno-Web-Common.cmd`

## Target State

The near-term target is:

```text
GraphRAG Project / settings.yaml / prompts / prompt tuning / index versions
  -> public query_method: auto/basic/local/global/drift
  -> Enhanced Mode Pipeline
  -> Multi-Retriever Recall
  -> Evidence Bundle / Citation / Trace
```

The public contract should use `graphrag_project_id`, `query_method`,
`prompt_version`, `index_version`, `community_version`, evidence metadata, and
trace metadata. Old internal names must not leak into current public contracts.

## Non-Goals

This roadmap does not implement:

- Java business services
- microservice extraction
- event-driven workers
- default multi-agent mode
- independent GraphRAG, indexing, or eval services
- a long-term Domain Pack shim

## Phase Overview

| Phase | Title | Dependency | Main Output |
| --- | --- | --- | --- |
| 01 | Legacy Surface Audit | none | classified legacy migration inventory |
| 02 | Docs / Spec / Current Truth Cleanup | 01 | current docs no longer mislead implementation |
| 03 | Domain Pack Contract Retirement | 01-02 | public contracts move toward GraphRAG Project |
| 04 | GraphRAG Project Contracts | 03 | core types and DTOs for project identity |
| 05 | GraphRAG Project Loader / Settings | 04 | loader and settings validation contract |
| 06 | Prompt Registry And Tuning Boundary | 04-05 | prompt versions and indexing-side prompt rules |
| 07 | Index / Update / Versioning | 04-06 | version and rebuild semantics |
| 08 | Query Method Router | 04, 07 | public query methods and fallback trace |
| 09 | Enhanced Mode Pipeline | 08 | full Enhanced pipeline and trace evidence |
| 10 | Frontend API Contract Migration | 03, 08-09 | frontend uses target public fields |
| 11A | GraphRAG Project Runtime Replacement | 03-10 | project-first query runtime that does not depend on Domain Pack |
| 11B | Single GeneralAgent Cutover | 11A | knowledge queries run through the single Agent loop as tools |
| 11C | Runtime Legacy Deletion | 11A-11B | old surfaces removed or migration-only |
| 12 | Tests / Eval / Trace Closure | 01-11C | final proof package and legacy grep gate |

## Implementation Status

- Phase 01 is complete as read-only legacy surface evidence.
- Phase 02 cleans current docs, specs, and Agent references so the active front
  path points to GraphRAG Project, Query Method, and Enhanced Mode instead of
  Domain Pack-era target language.
- Phase 03 introduces `graphrag_project_id` as the preferred public knowledge
  config field while keeping `domain_pack_id` as bounded migration/runtime
  compatibility input.
- Phase 04 adds first-class GraphRAG Project contract fields for project
  identity, settings path, prompt/index/query/community versions, hashes, and
  status without claiming a loader.
- Phase 05 adds `settings.yaml` loading, prompt discovery, validation errors,
  and readiness metadata without changing retrieval behavior.
- Phase 06 adds Prompt Registry categories and prompt-version impact rules
  without implementing automatic tuning.
- Phase 07 adds index version, hash flow, full rebuild boundary, and stale-index
  trace detection without database migration.
- Phase 08 adds the backend Query Method Router for
  `auto/basic/local/global/drift`, keeps old names as bounded compatibility or
  internal routes, and records requested/resolved method plus fallback reason in
  trace metadata.
- Phase 09 hardens Enhanced Mode pipeline trace for query method routing,
  query rewrite, multi-retriever recall, fusion/rerank, evidence check,
  conditional requery, citation coverage, and standard-floor preservation.
- Phase 10 migrates frontend API/types/config utilities to GraphRAG Project and
  public query-method trace fields, removes old route names from `apps/web`,
  and keeps Domain Pack runtime deletion for Phase 11.
- Phase 11A is complete; commit `24abdd9` introduced the project query runtime
  (`KnowledgeQueryService`, `GraphRAGQueryService`, `GraphRAGProjectSnapshot`,
  `KnowledgeQueryResult`).
- Phase 11B is complete; commit `b160c4b` unified knowledge queries under the
  single `GeneralAgent` path through `search_knowledge_base`.
- Phase 11C is blocked by active dependencies in `domain-packs/`, Domain Pack
  service/retained endpoint/frontend/eval/Docker surfaces, direct graph source
  modules, and `tests/compat/`. Workspace knowledge prefetch/tools have been
  cut over to `KnowledgeQueryService`, the standalone `AgentRuntime` facade has
  been removed from current backend source and exports, and `DomainQAGraph` /
  `MultiAgentSupervisorGraph` are no longer current core package public
  exports.
- Phase 12 is partially complete / not closed. Final full `pytest` and formal
  Eval baseline comparison are not complete.

## Dependency Rules

- Phase 01 must run before code deletion.
- Phase 03 must precede removal of Domain Pack runtime paths.
- Phase 04 must precede loaders, prompt registry, index versioning, router, and
  frontend contract migration.
- Phase 08 must precede final Enhanced Mode and frontend advanced method work.
- Phase 11A may run while legacy imports still exist because it creates the
  replacement runtime path.
- Phase 11B cuts conversation flow to the single `GeneralAgent` path after 11A
  proves the replacement query service.
- Phase 11C can delete old runtime surfaces only after 11A and 11B remove
  active dependencies on old names.
- Phase 12 closes the program only after 11C removal/migration, full pytest,
  eval baseline comparison, trace evidence, and final grep classification pass.

## Global Acceptance Gates

1. Domain Pack is no longer the frontend mainline.
2. Public contract uses `graphrag_project_id` and `query_method`.
3. Query methods are `auto/basic/local/global/drift`.
4. Basic uses BM25 plus dense vector plus fusion/rerank plus citation.
5. Enhanced Mode is a complete pipeline, not a single retriever.
6. Community reports are `global` and `drift` assets, not first-level methods.
7. Prompt Tuning belongs to indexing-side work.
8. Index, Update, and Full Rebuild have version boundaries.
9. `DomainQAGraph` and `DomainQAState` are replaced or kept only in migration
   compatibility notes.
10. `agentchat`, `services/api`, `zuno/legacy`, and compat aliases are not
    active paths.
11. Frontend does not leak `rag_graph_deep`, `local_graphrag`,
    `community_global`, or `drift_like`.
12. Tests, evals, and trace prove requested method, resolved method, retrievers
    used, fallback reason, evidence bundle, and citation coverage.
13. Legacy grep gates allow old terms only in history, audits, retired
    terminology, migration notes, and compatibility tests until final closure.

## Global Validation Commands

Run the smallest meaningful subset for each phase, and run the full set before
final closure:

```powershell
powershell -ExecutionPolicy Bypass -File .agent\scripts\verify-workflow.ps1
python tools\scripts\verify_docs_entrypoints.py
pytest -q tests\test_docs_entrypoints.py
pytest -q
git diff --check
git grep -n "domain_pack_id"
git grep -n "Domain Pack"
git grep -n "rag_graph_deep"
git grep -n "local_graphrag"
git grep -n "community_global"
git grep -n "drift_like"
git grep -n "agentchat"
```

Legacy grep commands are classification gates. They do not require zero hits
until final closure.

Allowed legacy locations:

- `docs/architecture/history/`
- `docs/architecture/audits/`
- retired terminology tables
- migration notes
- `tests/compat/` until final phase

Not allowed after final closure:

- current public docs
- frontend user-facing labels
- public API contracts
- active runtime main path

## GitHub Workflow

Before editing:

```powershell
git branch --show-current
git status --short
git log -1 --oneline
```

Before commit:

```powershell
git status --short
git diff --stat
git diff --check
```

After validation passes:

```powershell
git add only relevant files
git commit -m "<phase-specific message>"
git push
```

Forbidden:

- force push
- force-with-lease
- amend
- unrelated files
- claiming done when validation failed

If validation fails, do not push. Return the failing command, output summary,
modified files, blocker, and next recommendation.

## Final Closure Checklist

- All implementation phase documents have evidence packages.
- Current docs and Agent references point to this roadmap.
- Runtime and frontend contracts use target names.
- Legacy terms are classified by grep gate.
- Basic and Enhanced Mode gates pass.
- Eval evidence proves baseline preservation and trace coverage.
- Final commit and push are complete.

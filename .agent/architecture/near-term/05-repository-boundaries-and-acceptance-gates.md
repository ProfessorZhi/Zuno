# Repository Boundaries And Acceptance Gates

## Purpose

Define canonical repository ownership, file placement, archive policy, and
acceptance gates. This replaces the old persistence, frontend API contract,
migration roadmap, acceptance gates, implementation phase map, and repository
layout fragments.

## Current Layout

```text
apps/
  web/
  desktop/
src/backend/zuno/
docs/
.agent/
tools/
tests/
infra/
examples/graphrag-projects/
```

`src/backend/zuno` is the current Python backend runtime. `.agent` is the Agent
workflow and target-design workspace. `docs` is the formal human-facing
documentation surface. Historical material lives under
`docs/history/`.

## Target Backend Ownership

```text
api/
  HTTP routes, DTO boundary, auth, response envelopes, SSE

services/application/
  use cases: chat, knowledge, context, memory, capability, project

core/
  GeneralAgent runtime, LangGraph/LangChain loop, model/tool orchestration

services/graphrag/
  GraphRAG Project query/index/community/prompt concepts

services/retrieval/
  retrieval planning, retriever adapters, fusion, rerank, evidence

services/memory/
  raw events, summaries, structured memory, promotion policy

database/ and services/storage/
  durable persistence, object/file storage, versioned artifacts
```

Dependency direction:

```text
api -> application services -> core/runtime -> providers/adapters
services -> retrieval / graphrag / storage / persistence boundaries
```

Core/runtime must not depend backward on API routes. API routes must not own
business logic or retrieval strategy.

## Frontend And Desktop Boundary

`apps/web` and `apps/desktop` are product clients. They may show GraphRAG
Project settings, query method, evidence, citations, trace, memory state, and
capability state through typed API contracts. They must not expose retired
Domain Pack pages, internal graph route names, provider details, or
migration-only fields as product concepts.

## Docs And Agent Boundary

- `docs/`: current truth, high-level target, roadmap, public evidence,
  terminology, formal decisions, and history.
- `.agent/architecture/near-term/`: detailed canonical target architecture.
- `.agent/references/`: navigation indexes only, not long target prose.
- `.agent/programs/`: current active program only.
- `docs/history/`: superseded plans, old programs, old fragments,
  retired designs, and replaced references.

## Front-path Slimming Target

The target repository shape is not "fewer files at any cost." It is a small
front path plus a reachable archive.

Keep in the front path:

| Area | Keep | Why |
| --- | --- | --- |
| Root | `AGENTS.md`, `README.md`, package/test config | first-read and tooling contracts |
| `docs/` | `README.md`, Current, Target, Roadmap, ADRs, Evidence, Terminology | formal human truth |
| `.agent/` | `README.md`, active program, near-term target design, references, scripts, skills, templates, workflows | executable Agent workflow |
| Runtime | `src/`, `apps/`, `tools/`, `tests/`, `infra/` | code and verification surfaces |

Move or keep out of the front path:

| Material | Target Placement | Rule |
| --- | --- | --- |
| old lessons | `docs/history/agent-lessons/` | useful as history, not active guidance |
| old phase files | `docs/history/phases/` or archived program folder | do not recreate phase sprawl under active `.agent/programs/` |
| retired plans/specs | `docs/history/` | preserve evidence, remove from active reading order |
| screenshots and browser snapshots | outside repo or ignored local scratch | never commit transient QA artifacts |
| generated caches | ignored local directories | `.pytest_cache`, `.playwright-mcp`, `.test-tmp`, local reports |

The active target mode is:

```text
formal truth in docs/
executable workflow in .agent/
completed or superseded material in docs/history/
transient local artifacts outside the repository
```

## Forbidden Catch-all Directories

Do not create vague new packages or directories named only:

- `common`
- `helpers`
- catch-all `utils`
- generic `services` without a capability owner

Existing `src/backend/zuno/utils` is legacy/current utility surface; new code
should prefer a clear owner.

## Move Acceptance Gates

Before moving or deleting files:

1. Run `git status --short`.
2. Search imports, links, routes, scripts, evals, docs, and tests.
3. Classify each touched file as Current, Foundation, Target, Future, History,
   Generated, Local, or Migration Compatibility.
4. Preserve historical evidence under `docs/history/`.
5. Update docs, `.agent` references, verifiers, and tests in the same change.
6. Run the smallest meaningful verifier/test set plus `git diff --check`.

Stop if the move requires runtime changes outside the authorized scope, erases
history, breaks many links without a clear replacement, or requires Target to
be described as Current.

## Verification Matrix

Documentation and Agent workflow changes use:

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/test_docs_entrypoints.py tests/test_repo_structure_consistency.py tests/test_publish_boundary.py tests/test_agent_system.py tests/test_repo_hygiene.py -p no:cacheprovider
```

Runtime phases add focused runtime tests. Eval phases add eval-specific commands
and must not overwrite historical baselines.

## Phase Execution Plan

The active `zuno-target-runtime-v2` program executes the target architecture in
linear phases. The plan intentionally stays in one active roadmap file instead
of adding many phase files back under `.agent/programs/`.

| Phase | Target Slice | Main Owner | Exit Signal |
| --- | --- | --- | --- |
| 05 | Memory Engine | `services/application/context`, `services/memory`, `core/agents` | Raw Event Log, Summary Compression, Structured Extraction, `source_event_ids`, and ContextTrace are test-covered. |
| 06 | Capability / Tool Retrieval | `services/application/capabilities`, `core/agents` | ToolCard Registry, Native BM25 capability search, filters, and `CapabilitySelectionTrace` are test-covered. |
| 07 | Knowledge Retrieval / Fusion | `services/retrieval`, `services/graphrag`, `services/application/knowledge` | Native BM25, multi-query, multi-retriever recall, deduplication, RRF `k=60`, optional rerank boundary, evidence, citation, and trace are test-covered. |
| 08 | GeneralAgent LangGraph Runtime | `core/agents`, context, capability, retrieval boundaries | Explicit `prepare_context -> agent_loop -> post_turn_commit` graph preserves one chat runtime and streaming compatibility. |
| 09 | Product Boundary / Trace / Eval Closure | API, frontend contract, eval docs, evidence docs | Typed API, frontend-facing state, trace/eval closure evidence, and archive hygiene are complete. |

Execution rule:

```text
Phase 05 must close before Phase 06.
Phase 06 must close before Phase 07.
Phase 07 must close before Phase 08.
Phase 08 must close before Phase 09.
```

Each phase must update Current / Foundation / Target wording only for behavior
proved by code and tests. Unproved design remains Target.

## Current / Target Boundary

Current:

- Single GeneralAgent mainline.
- KnowledgeQueryService at the application knowledge boundary.
- GraphRAGQueryService and GraphRAGProjectSnapshot.
- Minimal ContextOrchestrator.
- Foundation memory and capability contracts.

Target:

- mature Memory Engine
- ToolCard retrieval and Native BM25 capability search
- product-level dynamic capability orchestration
- full LangGraph `prepare_context -> agent_loop -> post_turn_commit`
- multi-query, multi-retriever, RRF, optional rerank, evidence trace closure

Future:

- Java services
- microservices
- event-driven workers
- product-level multi-agent mode
- Coding Agent mode

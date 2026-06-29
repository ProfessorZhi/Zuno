# 仓库边界与验收门

## 用途

Define canonical repository ownership, file placement, archive policy, and
acceptance gates. This replaces the old persistence, frontend API contract,
migration roadmap, acceptance gates, implementation phase map, and repository
layout fragments.

## 当前布局

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

## 目标后端所有权

```text
api/
  HTTP routes、DTO boundary、auth、response envelopes、SSE

agent/
  Single GeneralAgent runtime、context、post_turn、state、streaming、tool_bridge

memory/
  raw events、summaries、structured memory、review、retrieval、rendering

capability/
  ToolCard、capability registry / selector / policy / execution / trace

knowledge/
  KnowledgeQueryService、GraphRAG、evidence、citation、retrieval、fusion、trace

platform/
  config、database、compatibility、middleware、model gateway、security、observability、storage
```

Dependency direction:

```text
api -> agent / knowledge / capability / memory -> platform providers / adapters
agent -> context / capability / knowledge / memory / trace contracts
```

`services/application`、`core`、`services/graphrag`、`services/retrieval`、`services/memory`
可以作为物理实现或 legacy compatibility owner 保留在 `platform/` 或 legacy alias 语境中，
但它们不再是目标前台所有权表达。Runtime 代码不能反向依赖 API routes；API routes
不能拥有业务逻辑或检索策略。

## 前端与桌面端边界

`apps/web` and `apps/desktop` are product clients. They may show GraphRAG
Project settings, query method, evidence, citations, trace, memory state, and
capability state through typed API contracts. They must not expose retired
Domain Pack pages, internal graph route names, provider details, or
migration-only fields as product concepts.

## 文档与 Agent 边界

- `docs/`: current truth, high-level target, roadmap, public evidence,
  terminology, formal decisions, and history.
- `.agent/architecture/near-term/`: detailed canonical target architecture.
- `.agent/references/`: navigation indexes only, not long target prose.
- `.agent/programs/`: current active program only.
- `docs/history/`: superseded plans, old programs, old fragments,
  retired designs, and replaced references.

## 前台路径瘦身目标

The target repository shape is not "fewer files at any cost." It is a small
front path plus a reachable archive.

Keep in the front path:

| Area | Keep | Why |
| --- | --- | --- |
| Root | `AGENTS.md`, `README.md`, package/test config | first-read and tooling contracts |
| `docs/` | `README.md`, Current, Target, Roadmap, ADRs, Evidence, Terminology | formal human truth |
| `.agent/` | `README.md`, optional active program, near-term target design, references, scripts, skills, templates, workflows | executable Agent workflow |
| Runtime | `src/`, `apps/`, `tools/`, `tests/`, `infra/` | code and verification surfaces |

Move or keep out of the front path:

| Material | Target Placement | Rule |
| --- | --- | --- |
| old lessons | `docs/history/agent-lessons/` | useful as history, not active guidance |
| old phase files | `docs/history/phases/` or archived program folder | only current executable phase files stay flat under active `.agent/programs/` |
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

## 禁止使用的兜底目录

Do not create vague new packages or directories named only:

- `common`
- `helpers`
- catch-all `utils`
- generic `services` without a capability owner

Existing `src/backend/zuno/utils` is legacy/current utility surface; new code
should prefer a clear owner.

## 移动验收门

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

## 验证矩阵

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
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```

Runtime phases add focused runtime tests. Eval phases add eval-specific commands
and must not overwrite historical baselines.

## Program 执行计划

When a program is active, `.agent/programs/` executes it through linear flat
phase files. Current execution files stay visible at one directory level;
completed or replaced detail moves to `docs/history/programs/`. When no program
is active, `.agent/programs/` only keeps `README.md`, `current.md`,
`implementation-roadmap.md`, and `closure-checklist.md`.

| Future Program | Target Slice | Main Owner | Exit Signal |
| --- | --- | --- | --- |
| `zuno-repo-layout-cleanup-v1` | Repository and facade layout | `docs`, `.agent`, `tools`, `tests`, backend facade boundaries | Directory truth is cleaner, generated/local artifacts stay out of front path, and verifier/tests pin the layout. |
| `zuno-runtime-architecture-upgrade-v1` | Memory, Capability, Knowledge, Trace hardening | `core/agents`, memory, capability, retrieval boundaries | GraphRAG LLM extraction, extractor configs, memory/capability/trace hardening have code and tests. |
| `zuno-architecture-visuals-v1` | Architecture HTML / Mermaid display | `docs/architecture`, `.agent/architecture`, `tools/agent` | Visuals are clearer, generated from one source, and do not become a second architecture truth. |

Execution rule:

```text
Open only one program at a time.
Move queued files into .agent/programs before execution.
Every new program starts at PHASE01.
Archive completed programs under docs/history/programs.
```

Each phase must update Current / Foundation / Target wording only for behavior
proved by code and tests. Unproved design remains Target.

## 当前与目标边界

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

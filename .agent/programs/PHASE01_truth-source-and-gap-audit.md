# PHASE01 Truth Source 与 Gap Audit

status: active
program: zuno-enterprise-document-ingestion-platform-v2
phase: PHASE01_truth-source-and-gap-audit
mode: read-only-audit

## 目标

确认 Program 1A 已归档且不改写历史 evidence；审计当前 `ParseGateway`、`WorkspaceTaskRuntimeService`、`KnowledgeIndexRuntime` 和相关 API / tests 的真实状态，形成 Program 1B / V2 的持久化改造输入事实。

本 phase 的核心问题只有一个：哪些状态仍在 local / in-process / in-memory，哪些必须在后续 phase 进入 source object store、SQLModel durable store、queue adapter、worker runner、OCR / VLM blocked diagnostics 和 restart recovery。

## 范围

- 读取并审计 Program 1A 归档 closure、当前架构文档和 Program 1B / V2 计划。
- 审计 `src/backend/zuno/api/services/workspace_task_runtime.py` 中 workspace file、ingest job、task、artifact、feedback 的状态来源。
- 审计 `src/backend/zuno/knowledge/ingestion/` 中 ParseGateway、parser job、attempt、snapshot、adapter diagnostics 的状态来源。
- 审计 `src/backend/zuno/knowledge/indexing/` 中 index job、index manifest、index chunks、retrieval payload、citation lineage 的状态来源。
- 审计 `src/backend/zuno/platform/` 中是否已有可复用 DB、SQLModel、storage、config 或 runtime persistence 工具。
- 审计 tests 中已有 workspace ingest、knowledge ingestion/index、restart recovery、blocked diagnostics 覆盖。

## 禁止范围

- 不修改 runtime 代码。
- 不新增 DB schema、store、queue、worker 或 API。
- 不把 source object store、Redis、outbox、worker lease、external OCR / VLM、external index 写成 Current。
- 不启动 Runtime Subsystems、Memory、Tool、Planning 或 Eval program。
- 不改写 `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/` 的完成事实。

## 验收闸门

- current gap matrix 完成，明确每个状态面是 durable、local-file、class-level dict、instance dict、fixture-only、target-blocked 还是 unknown-needs-test。
- storage target matrix 完成，明确 PHASE02-PHASE09 每个后续 phase 的输入边界。
- API compatibility map 完成，明确 `/workspace/file`、`/workspace/ingest`、task、artifact、feedback 哪些 response 字段必须保持兼容。
- dependency probe 完成，说明 SQLModel / DB session / Redis 依赖是否已存在、是否能直接复用、是否需要 adapter skeleton。
- PHASE02 输入清单完成，列出最小 store contract、需要先写的 focused tests 和禁止触碰路径。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 需要先读取

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE01_truth-source-and-gap-audit.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/closure-summary.md`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/knowledge/ingestion/`
- `src/backend/zuno/knowledge/indexing/`
- `src/backend/zuno/platform/`
- `tests/api/`
- `tests/knowledge/`

## 需要修改的文件

PHASE01 启动时只修改 Agent workflow / program truth source：

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_truth-source-and-gap-audit.md`
- `.agent/programs/queued-programs/README.md`
- `.agent/references/current-program.md`
- `.agent/system.yaml`
- `.agent/scripts/verify_agent_system.py`
- `.agent/scripts/verify-workflow.ps1`
- `tools/scripts/verify_repo_structure.py`
- `tests/repo/test_agent_system.py`
- `tests/repo/test_repo_structure_consistency.py`
- `AGENTS.md`
- `README.md`

PHASE01 audit evidence 只能写回本 phase 文件和必要的 current-program 摘要；不得修改 runtime。

## 执行拆解

1. 启动安全门：确认 branch、status、latest commit 和 no-active -> active 切换。
2. Program truth source：把 Program 1B / V2 设为 active，当前 phase 设为本文件。
3. 只读审计 workspace runtime：列出 `_tasks`、`_files`、`_file_text`、`_ingest_jobs`、`_artifacts`、`_feedback` 等状态来源和 API 兼容风险。
4. 只读审计 ParseGateway：列出 jobs、snapshots、attempts、diagnostics、blocked 状态来源和 durable store gap。
5. 只读审计 KnowledgeIndexRuntime：列出 spaces、jobs、manifests、chunks、retrieval payload、citation lineage 状态来源和 rehydrate gap。
6. 只读审计 platform storage / DB：确认是否已有 SQLModel、DB session、local storage、config、migration 工具可复用。
7. 只读审计 tests：列出现有覆盖和 PHASE02 first failing tests。
8. 写回 PHASE01 evidence：current gap matrix、storage target matrix、API compatibility map、PHASE02 input。
9. 运行验证、提交、推送。

## 多 agent 分工

PHASE01 可以使用只读 subagent 并行审计，但主线程负责最终判断和写回：

- Subagent A：审 `WorkspaceTaskRuntimeService` 与 API tests。
- Subagent B：审 `ParseGateway` / ingestion contracts / parser diagnostics。
- Subagent C：审 `KnowledgeIndexRuntime` / index manifest / citation lineage。
- Subagent D：审 platform storage / DB / Redis dependency 和 repo verifier impact。

所有 subagent 禁止修改文件；只返回证据、文件路径、行号和风险判断。

## 需要返回的证据

- branch / commit / status。
- current gap matrix。
- storage target matrix。
- API compatibility map。
- dependency probe summary。
- PHASE02 focused test seed list。
- 验证命令和结果。
- commit / push evidence。

## 停止条件

- 工作树出现用户未说明的冲突修改。
- 发现当前 active-state 启动会破坏 verifier 且无法用最小同步修复。
- 发现需要先做用户决策的 public API / DB schema 兼容分歧。
- 发现现有代码事实与 Program 1B / V2 目标冲突，且无法在 PHASE01 只读审计中安全归类。
- 需要真实外部服务、凭据、Redis、Postgres、OCR / VLM 或 external index 才能继续。

## PHASE01 Evidence

启动提交前，本节只记录启动事实；审计执行后必须补全矩阵和 PHASE02 输入清单。

- 启动状态：Program 1B / V2 从 queued 切换为 active。
- 当前 phase：PHASE01 Truth Source 与 Gap Audit。
- 运行模式：主线程挂机，只读审计；runtime 修改从 PHASE02 开始。

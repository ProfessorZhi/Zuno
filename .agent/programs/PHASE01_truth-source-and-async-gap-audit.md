# PHASE01 Truth Source 与 Async Gap Audit

status: active
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE01_truth-source-and-async-gap-audit
mode: read-only-audit

## 目标

确认 Program 1 / Program 2 已完成事实，冻结 Program 3 的真实起点，并把企业异步输入层缺口拆成可执行的后续 phase。核心判断：Program 3 不是继续堆 parser，而是把 Program 2 的 SQLite / local synchronous durable baseline 升级为 enterprise ingestion async infrastructure baseline。

Program 3 采用 1-6 program 编号体系：Program 1 和 Program 2 已归档，Program 3 当前 active，原 Runtime Subsystems、Planning、Eval 后移为 Program 4-6。

## 范围

- 审计 `.agent/programs/`、Program 1 / Program 2 归档和当前 architecture docs。
- 审计 `src/backend/zuno/knowledge/storage/` 的 SQLite store、SQLModel 表、record contracts 和 local object store。
- 审计 `WorkspaceTaskRuntimeService` 中 `/workspace/file`、`/workspace/ingest`、task、event、artifact、feedback 的 durable 接入点。
- 审计 `ParseGateway`、`KnowledgeIndexRuntime`、restart rehydrate 和 blocked diagnostics。
- 审计现有 tests 对 source object、parse snapshot、document version、index chunks、citation lineage、artifact / feedback rehydrate 的覆盖。
- 对照外部参考输入中的 RAGFlow ingestion-first、Onyx background sync / connector / ACL、AnythingLLM workspace / event log、Letta / mem0 memory boundary，提炼 Program 3 只应吸收的 infrastructure 要点。

## 禁止范围

- 不修改 runtime 代码。
- 不新增 DB schema、queue、worker、Redis、object store adapter 或 API。
- 不把 PostgreSQL、MinIO / S3、RabbitMQ、Redis、external OCR / VLM、external index 写成 Current。
- 不启动 Program 4 Runtime Subsystems Parallel。
- 不改写 Program 1 / Program 2 历史归档完成事实。

## 验收闸门

- 当前事实源确认：Program 1 / Program 2 completed / archived，Program 3 active，Program 4-6 queued。
- Gap matrix 完成：PostgreSQL fact store、ObjectStore binary、QueueBackend、RabbitMQ boundary、Redis runtime state、ParserWorker、IndexWorker、Outbox、Dead Letter、Reconciler、OCR / VLM worker boundary、ingest status / retry / cancel / replay。
- Program 3 完成定义写清：`Enterprise ingestion async infrastructure baseline completed`。
- 后续 PHASE02-PHASE12 的输入、验收和禁止范围清楚。
- 当前 front path、queued program 文件和 verifier 需要同步的清单明确。

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
- `README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/references/current-program.md`
- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/closure-summary.md`
- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/closure-summary.md`
- `src/backend/zuno/knowledge/storage/`
- `src/backend/zuno/knowledge/ingestion/`
- `src/backend/zuno/knowledge/indexing/`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`
- `tests/knowledge/`

## 需要修改的文件

PHASE01 开轮主要修改 program / workflow truth source：

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_truth-source-and-async-gap-audit.md`
- `.agent/programs/PHASE02_storage-interface-and-postgres-boundary.md`
- `.agent/programs/PHASE03_object-store-abstraction-and-binary-input.md`
- `.agent/programs/PHASE04_queue-backend-and-rabbitmq-boundary.md`
- `.agent/programs/PHASE05_parser-index-worker-runtime.md`
- `.agent/programs/PHASE06_redis-runtime-state-boundary.md`
- `.agent/programs/PHASE07_outbox-dead-letter-reconciler.md`
- `.agent/programs/PHASE08_async-ingest-status-retry-cancel-replay.md`
- `.agent/programs/PHASE09_ocr-vlm-worker-boundary.md`
- `.agent/programs/PHASE10_end-to-end-async-restart-recovery.md`
- `.agent/programs/PHASE11_docs-verifier-sync.md`
- `.agent/programs/PHASE12_closure-archive-commit-push.md`
- `.agent/programs/queued-programs/`
- `.agent/system.yaml`
- `.agent/references/current-program.md`
- repo verifier / repo tests that hard-code current program files.

## 执行拆解

1. 确认 git safety gate：branch、status、recent log。
2. 将 Program 3 active 状态写入 `.agent/programs/`。
3. 将旧 queued Program 3-5 重排为 Program 4-6。
4. 写入 PHASE01-PHASE12 文件。
5. 同步 `.agent/system.yaml`、`.agent/references/current-program.md`、README、AGENTS 和 repo tests / verifiers。
6. 运行文档和 workflow verifier。
7. 提交并推送 Program 3 open / roadmap 变更。

## 多 agent 分工

- Architecture / Docs Agent：只读审计架构文档 Current / Target 边界。
- Runtime / Code Agent：只读审计 storage、ingestion、indexing、workspace runtime hook point。
- Verification Agent：审计 verifier / repo tests 中 Program 1-6 文件清单。
- Integration Reviewer Agent：确认 Program 3 不侵入 Program 4-6 范围。

## 需要返回的证据

- 当前 branch、commit、git status。
- Program 3 active 状态和 PHASE01 文件路径。
- Program 1-6 roadmap 摘要。
- Gap matrix。
- 修改文件清单。
- verifier / tests 结果。
- commit hash 和 push status。

## 停止条件

- 工作树出现用户未说明的修改。
- 需要真实 PostgreSQL / RabbitMQ / Redis / MinIO / OCR / VLM 服务才能继续 PHASE01。
- Program 3 和 Program 4-6 边界无法在文档和 verifier 中同时表达。
- verifier 要求恢复 no-active 状态且不能合理更新为 active Program 3。

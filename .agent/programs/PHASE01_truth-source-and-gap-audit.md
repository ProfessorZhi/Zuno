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

### 启动事实

- 当前 worktree：`F:\internship-work\resume&resume project\02_projects\Zuno`。
- 当前 branch：`codex/zuno-truth-source-production-readiness-baseline`。
- 启动 commit：`9218cbe3 docs: open enterprise ingestion platform phase 1`。
- 工作树状态：`git status --short --branch` 显示当前 branch 与 origin 同步，启动审计前没有未提交修改。
- 目标文件 `C:\Users\Administrator\.codex\attachments\3ef2df83-fa21-4598-b9e6-6148a4720ec9\goal-objective.md` 仍是 Program 1A 的 PHASE01-PHASE08 执行口径；本轮以后续用户目标调整和仓库 active truth source 为准，执行 Program 1B / V2 的持久化平台雏形审计。
- 运行模式：主线程挂机，只读审计；runtime 修改从 PHASE02 开始。

### Current Gap Matrix

| 状态面 | 当前代码事实 | 当前状态 | Program 1B / V2 gap |
| --- | --- | --- | --- |
| workspace file metadata | `WorkspaceTaskRuntimeService.register_file()` 写入 class-level `_files`，文本写入 `_file_text`；hash 在缺省时由 workspace / file / uri / name / mime 合成。见 `src/backend/zuno/api/services/workspace_task_runtime.py:76-80`、`:102-139`。 | class-level dict | 没有 source object、storage uri、真实 file bytes / content store、dedupe 事实源；服务重启后 file metadata 和 content 丢失。 |
| workspace ingest job | `/workspace/ingest` 调用 `ParseGateway.submit_parse_job()`，再把成功结果同步交给 `KnowledgeIndexRuntime.index_document()`；job payload 写 `_ingest_jobs`。见 `src/backend/zuno/api/services/workspace_task_runtime.py:142-217`。 | class-level dict + in-process sync | 已不再走旧 `_document_from_file()` 主链路，但 parse / index / ingest 状态未落库，没有 queue、worker runner、retry / cancel / replay API store。 |
| blocked / failed ingest | 当 `parse_job.status != "succeeded"` 时返回 parse snapshot 且 `index_job=None`。见 `src/backend/zuno/api/services/workspace_task_runtime.py:176-194`。 | local runtime behavior | 语义正确，但 blocked / failed reason 只存在内存 payload；没有 dead letter / retry audit table。 |
| workspace task / events | `_tasks`、`_task_inputs`、`_events`、`_task_recovery`、`_trace_spans`、`_release_evals`、`_trace_replays` 都是 class-level dict；durable runtime store 是 `InMemoryDurableRuntimeStore()`。见 `src/backend/zuno/api/services/workspace_task_runtime.py:76-99`。 | class-level dict / in-memory durable runtime | task、events、trace、eval、approval recovery 不能跨服务重启恢复。 |
| artifact | `_complete_task()` 生成 `memory://workspace/...` URI，artifact metadata 写 `_artifacts`，内容写 `_artifact_content`。见 `src/backend/zuno/api/services/workspace_task_runtime.py:588-603`。 | class-level dict | artifact 无 local file store / object store；download 依赖内存 content。 |
| feedback | `record_feedback()` 写 `_feedback` 和 `_feedback_ids_by_task`，再追加内存事件。见 `src/backend/zuno/api/services/workspace_task_runtime.py:906-936`。 | class-level dict | feedback 不能跨重启保存，也没有 eval dataset durable candidate。 |
| legacy workspace text document helper | `_document_from_file()` 仍存在，parser_id 为 `workspace_text_runtime`。见 `src/backend/zuno/api/services/workspace_task_runtime.py:793-820`。 | legacy helper / not main ingest | 当前 `/workspace/ingest` 测试已断言 parse snapshot parser 不再是 `workspace_text_runtime`；后续应保留兼容或删除前先证明没有调用方。 |
| ParseGateway jobs | `ParseGateway` 持有 class-level `_jobs` 和 `_job_snapshots`；`submit_parse_job()` 同步 parse 并保存 snapshot。见 `src/backend/zuno/knowledge/ingestion/gateway.py:40-59`。 | class-level dict | 没有 parse job / attempt durable store、idempotency lookup、restart replay、worker lease。 |
| ParseGateway retry / cancel | `retry_parse_job()` 创建新 result job_id，snapshot 记录 attempt / previous_job_id；`cancel_parse_job()` 更新当前 snapshot。见 `src/backend/zuno/knowledge/ingestion/gateway.py:76-143`。 | local lifecycle | retry / cancel 语义已有，但 lineage、attempt、dead_letter 只在内存；没有 durable attempt ledger。 |
| parser contract / Document IR | `DocumentMetadata` 已包含 `source_sha256`、`parser_config_hash`、`document_version_id`、`ir_schema_version`、ACL 和 sensitivity；`ParseJobSnapshot` 已包含 attempt、idempotency、metrics、diagnostics、source provenance。见 `src/backend/zuno/knowledge/ingestion/contracts.py:61-85`、`:212-247`。 | contract current | 字段 contract 足够做 V2 schema 输入，但还没有 SQLModel 表和 IR artifact 持久化。 |
| PDF / Office / OCR / VLM boundary | router 将 PDF、Office、image、scanned 标为 target-blocked adapter 或 derived enrichment gate；`submit_parse_job()` 会让 target-blocked adapter 进入 blocked。见 `src/backend/zuno/knowledge/ingestion/router.py:65-160`、`:164-309` 和 `gateway.py:431-458`。 | target-blocked current diagnostics | blocked 诊断可复现，但未落库；真实 OCR / VLM worker 仍是 Target。 |
| index space / manifest / chunks | `KnowledgeIndexRuntime` 的 `_spaces`、`_jobs`、`_latest_job_by_space`、`_indexes` 都是 instance dict。见 `src/backend/zuno/knowledge/indexing/runtime.py:14-22`。 | instance dict | index manifest、chunks、latest pointer 和 retrieval payload 无 durable rehydrate。 |
| index lineage | index manifest 和 chunk metadata 写入 parse job、attempt、document version、source hash、diagnostics digest、citation lineage。见 `src/backend/zuno/knowledge/indexing/runtime.py:41-130`、`:266-379`。 | local lineage current | lineage 字段可作为 durable schema 输入；缺 index_jobs / index_chunks 持久化。 |
| platform DB/session | `zuno.platform.database` 已有 SQLModel engine/session、现有 KnowledgeFile / KnowledgeTask 表和 DAO；默认配置偏 Postgres。见 `src/backend/zuno/platform/database/__init__.py:73-88`、`session.py:13-39`、`models/knowledge_file.py:17-40`、`models/knowledge_task.py:16-65`。 | existing platform infra | 可复用 SQLModel pattern，但旧表不覆盖 source object、document version、parse attempt、index chunk、workspace artifact / feedback。V2 应先定义兼容 SQLite 的 local durable store contract。 |
| platform object storage | `storage_client` 是 MinIO / OSS lazy facade。见 `src/backend/zuno/platform/services/storage/__init__.py:1-25`。 | external storage facade | 可作为未来 object store adapter；缺 Product V1 local file store 和 object key contract。 |

### Storage Target Matrix

| 后续 phase | 输入事实 | 最小落点 | 禁止误写 |
| --- | --- | --- | --- |
| PHASE02 Durable Storage Contract | 现有 SQLModel pattern、Document IR / ParseJobSnapshot / IndexJobManifest 字段已经足够建 schema。 | 定义 `source_objects`、`workspace_files`、`document_versions`、`document_blocks`、`parse_jobs`、`parse_attempts`、`knowledge_spaces`、`index_jobs`、`index_chunks`、`workspace_tasks`、`task_events`、`artifacts`、`feedback` 的 store contract 和 first failing tests。 | 不把旧 `KnowledgeFileTable` / `KnowledgeTaskTable` 直接宣称覆盖 V2 durable store。 |
| PHASE03 Local Object Store / File Input | `/workspace/file` 当前只注册 metadata 和 text。 | 保存 source content / bytes / file ref，计算 `source_sha256`，返回兼容 file payload 外加 source object evidence。 | 不引入必须联网的 MinIO / OSS 作为本地 V1 必需依赖。 |
| PHASE04 Parse Job Store / Queue Boundary | ParseGateway lifecycle 已有状态、attempt、snapshot 和 diagnostics。 | `ParseGateway` 支持 store 注入；`LocalQueueBackend` contract；blocked / failed / retry / cancel 写 store。 | 不把 Redis / lease / outbox 写成 Current。 |
| PHASE05 Document IR Persistence | `CanonicalDocumentIR` 已带 document version 和 source provenance。 | 保存 IR artifact、document version、document blocks；同 source + parser config idempotency 可查。 | 不静默覆盖旧 document version。 |
| PHASE06 Index Persistence / Rehydrate | manifest 和 chunks 已有完整 lineage。 | 保存 index job、manifest、chunks、latest ready pointer；新 runtime / service 能 query 已持久化 chunks。 | 不接 external vector / graph DB 作为当前验收。 |
| PHASE07 OCR / VLM / PDF / Office Boundary Persistence | target-blocked diagnostics 已可稳定生成。 | 将 dependency probe、privacy/network/budget gate 和 blocked reason 写入 parse attempt diagnostics。 | 不假装真实 OCR / VLM 或 Office parser 已可用。 |
| PHASE08 Workspace API Durable Closure | API response shape 已稳定，核心状态目前在 class dict。 | task、events、artifact、feedback 从 durable store 读写；SSE 可从 persisted events 重放。 | 不破坏现有 `/workspace/file`、`/workspace/ingest`、task、artifact、feedback response shape。 |
| PHASE09 Restart Recovery Tests | 现有 tests 覆盖 local loop，但不覆盖 service restart。 | 新建 store/runtime/service 后仍可查询 file、parse job、document version、index manifest、task、events、artifact、feedback，并能生成 cited artifact。 | 不用 monkeypatch 内存 payload 当作恢复证明。 |

### API Compatibility Map

| API | 现有入口 | 必须保持兼容的 response / behavior | V2 可新增 |
| --- | --- | --- | --- |
| `POST /api/v1/workspace/file` | `src/backend/zuno/api/v1/workspace.py:145-163` | 返回 `file`、`name`、`uri`；`file.file_id`、`workspace_id`、`owner`、`mime_type`、`hash`、`security_label`、`parse_status` 不改名。 | `source_id`、`source_sha256`、`storage_uri`、`size_bytes`、`durable_status`。 |
| `POST /api/v1/workspace/ingest` | `src/backend/zuno/api/v1/workspace.py:166-180` | 返回 `ingest_task_id`、`workspace_id`、`file_id`、`knowledge_space_id`、`trace_id`、`status`、`file`、`parse_job`、`parse_snapshot`、`index_job`；blocked / failed 不创建 fake index。 | `source_object`、`document_version`、`index_manifest_ref`、`retry_url`、`cancel_url`、`replay_url`。 |
| `POST /api/v1/workspace/task` | `src/backend/zuno/api/v1/workspace.py:183-193` | 返回 task snapshot、artifacts、events、lifecycle、runtime、observability；现有 task 状态流不改名。 | persisted `task_store_status`、event cursor / replay token。 |
| `GET /task/{task_id}` / events / stream | `src/backend/zuno/api/v1/workspace.py:204-267` | snapshot、events 和 SSE event payload 形状保持；重启后 404 行为要由 store 决定而不是内存缺失。 | event replay cursor、persisted trace refs。 |
| artifact get / download | `src/backend/zuno/api/v1/workspace.py:270-293` | `artifact`、`content`、`download.url`、filename、markdown media type 保持。 | `storage_uri`、`content_hash`、signed/local download adapter。 |
| feedback | `src/backend/zuno/api/v1/workspace.py:296-310` | `feedback_id`、`task_id`、rating、label、comment、dataset_candidate 保持。 | durable eval candidate ref。 |

### Dependency Probe Summary

- SQLModel 已存在，且平台层已有 Postgres-oriented `engine` / `async_engine` / `session_getter`；可复用模型风格和 session pattern，但 Product V1 需要 SQLite-compatible local durable store，不能要求开发环境先启动 Postgres。
- 旧 knowledge pipeline 已有 `KnowledgeFileTable`、`KnowledgeTaskTable`、`KnowledgeTaskEventTable` 和 DAO，可作为迁移参考；但字段不覆盖 source object、parse attempt、document version、index chunk、citation lineage，也没有 workspace artifact / feedback。
- Object storage facade 已有 MinIO / OSS lazy client；V2 仍需 local file store adapter，避免把外部对象存储作为一两天内的必需条件。
- Redis 配置和 Redis key helper 存在，但没有 parse / index `QueueBackend` contract；PHASE04/PHASE09 应先落 `LocalQueueBackend`，Redis adapter 只能作为 optional dependency probe。
- OCR / VLM / PDF / Office 依赖均通过 adapter contract 标记 target-blocked / missing；当前可验收的是 blocked diagnostics 持久化，不是真实解析能力。

### PHASE02 Focused Test Seed List

1. `tests/knowledge/test_enterprise_ingestion_storage_contract.py::test_sqlite_store_round_trips_source_file_parse_snapshot_and_index_manifest`
   - 先只测 store contract：source object、workspace file、parse job、parse attempt、document version、index job、index chunk 可以 SQLite round-trip。
2. `tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_file_register_persists_source_object_and_content_ref`
   - `POST /workspace/file` 后 new store/service 仍能查 file metadata、source hash 和 content/ref。
3. `tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_ingest_persists_parse_snapshot_document_version_and_index_chunks`
   - `/workspace/ingest` 仍走 `ParseGateway`，成功后 parse snapshot、document version、index manifest、chunks 落 store。
4. `tests/api/test_workspace_durable_ingest_runtime.py::test_workspace_restart_rehydrates_cited_answer_artifact_and_feedback`
   - file -> ingest -> task -> artifact -> feedback 后重建 service/store，仍能查 task、events、artifact、feedback，并能从 persisted index chunk 生成 citation。
5. `tests/knowledge/test_enterprise_ingestion_queue_contract.py::test_local_queue_contract_preserves_retry_cancel_blocked_dead_letter_status`
   - 先定义 `QueueBackend` 行为，不要求 Redis；blocked 不 index，retry 新增 attempt，不覆盖旧 lineage。
6. `tests/knowledge/test_enterprise_ingestion_storage_contract.py::test_target_blocked_parser_diagnostics_are_persisted_without_fake_index`
   - image / scanned / PDF / Office 缺依赖时 blocked reason 写 parse attempt diagnostics，`index_job` 不假成功。

### PHASE02 输入边界

- 先写 tests 和 store contract，再改 `WorkspaceTaskRuntimeService` / `ParseGateway` / `KnowledgeIndexRuntime`。
- 首轮实现优先使用 `.local/zuno/zuno.db` 和 `.local/zuno/objects/`；Postgres、MinIO、Redis 只保留 adapter boundary。
- public API response 字段默认保持向后兼容；新增字段必须 additive。
- 不动 `GeneralAgent` 主循环，不启动 Program 3 Memory / Tool / Security / GraphRAG。

### 验证结果

2026-07-01 已运行：

- `git diff --check`：通过；仅出现 Windows 工作树 CRLF 提示。
- `python tools/agent/render_architecture.py --check`：通过。
- `python tools/scripts/verify_docs_entrypoints.py`：通过。
- `python tools/scripts/verify_repo_structure.py`：通过。
- `python .agent/scripts/verify_agent_system.py`：通过。
- `python .agent/scripts/verify_doc_boundaries.py`：通过。
- `python .agent/scripts/verify_repo_hygiene.py`：通过。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1`：通过。
- `pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider`：`72 passed in 2.36s`。

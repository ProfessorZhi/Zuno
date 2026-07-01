# Program 3 Closure Checklist

state: active
active_program: `zuno-enterprise-ingestion-async-infrastructure-v1`
current_phase: `PHASE01_truth-source-and-async-gap-audit.md`
latest_completed_program: `zuno-enterprise-document-ingestion-platform-v2`

## Program 3 收口目标

Program 3 完成时必须达到：

```text
Enterprise ingestion async infrastructure baseline completed.
```

这句话只在以下事实都由代码、focused tests、verifier 或可复现 evidence 证明后才能写入 closure summary。

## Phase 清单

- [ ] PHASE01 完成 truth source 与 async gap audit。
- [ ] PHASE02 完成 `DurableIngestionStore` interface 和 PostgreSQL-compatible boundary。
- [ ] PHASE03 完成 `ObjectStore` abstraction 和 binary input。
- [ ] PHASE04 完成 `QueueBackend`、`LocalQueueBackend` 和 RabbitMQ boundary。
- [ ] PHASE05 完成 `ParserWorker` / `IndexWorker` local runner。
- [ ] PHASE06 完成 Redis runtime state boundary 和 local fallback。
- [ ] PHASE07 完成 outbox、dead letter、worker lease / heartbeat 和 reconciler。
- [ ] PHASE08 完成 ingest status / retry / cancel / replay API 或 service contract。
- [ ] PHASE09 完成 OCR / VLM worker boundary 和 blocked diagnostics。
- [ ] PHASE10 完成 end-to-end async restart recovery focused test。
- [ ] PHASE11 完成 docs、architecture mirror、verifier 和 repo tests 同步。
- [ ] PHASE12 完成 closure、archive、commit 和 push。

## Runtime 验收清单

- [ ] `/workspace/file` 继续保存 source object、source hash、storage uri 和 workspace file metadata。
- [ ] `LocalObjectStore` 支持 text 和 bytes，`source_sha256` 与真实 bytes 一致。
- [ ] `/workspace/ingest` 支持 async queued path，response 字段保持 additive compatibility。
- [ ] `LocalQueueBackend` 支持 enqueue、consume、ack、nack、dead_letter。
- [ ] `ParserWorker` 能消费 `parse_requested`，调用 `ParseGateway`，持久化 parse job / snapshot / document version / blocks。
- [ ] `IndexWorker` 能消费 `index_requested`，持久化 index manifest / chunks / citation lineage。
- [ ] blocked / failed parser diagnostics 落库，blocked 不创建 fake index。
- [ ] ingest status 可查询 queued / parsing / parsed / indexing / indexed / blocked / failed / dead_letter。
- [ ] outbox 能防止“DB 写了任务但队列消息丢失”。
- [ ] reconciler 能发现 uploaded_without_parse、parse_succeeded_without_index、blocked_without_diagnostics、index_chunks_missing、citation_lineage_missing、object_missing。
- [ ] OCR / VLM worker boundary 能表达 queued / blocked / succeeded / failed，默认无 provider 时 target-blocked，不 fake success。
- [ ] restart recovery 后仍能 rehydrate file、parse、document、index、task、artifact、feedback，并生成带 citation 的 artifact。

## Current / Target 边界

- [ ] SQLite 和 local implementations 可作为 Current。
- [ ] PostgreSQL-compatible boundary 只有在代码和 tests 证明时才能写成 Current。
- [ ] RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index 没有真实 provider 和 tests 前只能写成 Target / target-blocked evidence。
- [ ] Codex 多线程施工不写成 Zuno 产品 runtime 多 Agent 架构。
- [ ] Program 4-6 是 queued program，不是当前 active program。

## 文档同步检查

- [ ] `.agent/programs/current.md` 与 Program 3 active 状态一致。
- [ ] `.agent/programs/implementation-roadmap.md` 覆盖 Program 1-6 顺序。
- [ ] `.agent/programs/queued-programs/` 中 Program 4-6 计划仍是 queued。
- [ ] `.agent/references/current-program.md` 与 `.agent/programs/current.md` 一致。
- [ ] `AGENTS.md` 和 README 当前 program 摘要一致。
- [ ] `docs/architecture/architecture.md`、`.agent/architecture/architecture.md` 和两个 architecture HTML 同步。
- [ ] `docs/architecture/production-readiness.md` 与 Program 3 Current / Target 边界一致。
- [ ] `docs/architecture/document-ingestion-foundation.md` 与 async ingestion infrastructure 边界一致。
- [ ] verifier / repo tests 覆盖 active program 文件清单、queued Program 4-6 和 latest completed archive。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/knowledge -p no:cacheprovider
pytest -q tests/repo/test_agent_system.py tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## 归档目标

Program 3 完成后整体归档到：

- `docs/history/programs/zuno-enterprise-ingestion-async-infrastructure-v1/`

归档必须包含：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `closure-checklist.md`
- `closure-summary.md`
- PHASE01-PHASE12 文件

# 当前程序

state: active
active_program: zuno-enterprise-ingestion-async-infrastructure-v1
current_phase: PHASE01_truth-source-and-async-gap-audit.md
latest_completed_program: zuno-enterprise-document-ingestion-platform-v2

## 当前状态

`.agent/programs/` 当前已打开 Program 3：

- Program 3：`zuno-enterprise-ingestion-async-infrastructure-v1`
- 中文名：Enterprise Ingestion Async Infrastructure / 企业文档输入异步基础设施
- 当前 phase：`PHASE01_truth-source-and-async-gap-audit.md`

Program 3 承接 Program 2 的 Product V1 local durable ingestion baseline，目标是把文档输入层升级为本地可验证的企业异步基础设施 baseline：PostgreSQL-compatible durable store boundary、binary ObjectStore、QueueBackend、local async workers、Redis runtime state boundary、outbox、dead letter、reconciler、OCR / VLM worker boundary、ingest status / retry / cancel / replay contract。

目标产品口径固定为 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace。用户在聊天里提出目标，并在勾选知识库时选择标准检索 / 深度检索；GraphRAG、BM25、vector、re-query、rerank 和工具调用由 Single Controller Agent 内部自动规划。Basic RAG 和 Static GraphRAG 只作为 Program 6 的评测对照组，不是最终产品模式。

当前 Program 1-6 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的前台数字化执行序列；旧 Program 1A / 1B 命名已收敛为 Program 1 / Program 2，后续 queued program 自动后移为 Program 4-6。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。Current 只写代码、focused tests、trace / eval 或 verifier 已证明的事实。

## 已完成前置 Program

1. Program 1：`zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
   - 完成：ParseGateway、CanonicalDocumentIR、parser job snapshot、adapter boundary、native parser fixtures、index manifest lineage 和 citation lineage。
2. Program 2：`zuno-enterprise-document-ingestion-platform-v2`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
   - 完成：SQLite durable store、local source object、workspace file metadata、parse job / snapshot、document version / blocks、index manifest / chunks、citation lineage、task / events / artifact / feedback rehydrate 和 restart recovery。

## 历史归档锚点

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成成熟目标架构和四大总交付物完成的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：上一轮八大治理交付物闭环。

## 当前 Program 3 Phase

1. `PHASE01_truth-source-and-async-gap-audit.md`：active。
2. `PHASE02_storage-interface-and-postgres-boundary.md`：pending。
3. `PHASE03_object-store-abstraction-and-binary-input.md`：pending。
4. `PHASE04_queue-backend-and-rabbitmq-boundary.md`：pending。
5. `PHASE05_parser-index-worker-runtime.md`：pending。
6. `PHASE06_redis-runtime-state-boundary.md`：pending。
7. `PHASE07_outbox-dead-letter-reconciler.md`：pending。
8. `PHASE08_async-ingest-status-retry-cancel-replay.md`：pending。
9. `PHASE09_ocr-vlm-worker-boundary.md`：pending。
10. `PHASE10_end-to-end-async-restart-recovery.md`：pending。
11. `PHASE11_docs-verifier-sync.md`：pending。
12. `PHASE12_closure-archive-commit-push.md`：pending。

## 后续 queued program

Program 4-6 仍为 queued，不是当前 active program：

1. Program 4：`zuno-runtime-subsystems-parallel-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM04_runtime-subsystems-parallel.md`
2. Program 5：`zuno-agent-planning-integration-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM05_agent-planning-integration.md`
3. Program 6：`zuno-enterprise-knowledge-eval-benchmark-v1`
   - 计划：`.agent/programs/queued-programs/PROGRAM06_enterprise-knowledge-eval-benchmark.md`

## 当前执行规则

- Program 3 必须先完成 PHASE01 truth source 与 async gap audit，再进入 runtime 代码实现。
- 新 runtime 行为必须 TDD：先写 focused failing test，再写最小实现。
- Program 3 的完成口径是 `Enterprise ingestion async infrastructure baseline completed`。
- 不要求真实部署 PostgreSQL、RabbitMQ、Redis、MinIO / S3 或 OCR / VLM provider；无外部服务时必须有 dependency probe / target-blocked evidence。
- 不把 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index 写成 Current，除非本轮有真实代码、focused tests 和可复现验证。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。

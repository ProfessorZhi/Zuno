# 当前 Program 状态

## Current Truth

state: active
active_program: zuno-enterprise-ingestion-async-infrastructure-v1
current_phase: PHASE01_truth-source-and-async-gap-audit.md
latest_completed_program: zuno-enterprise-document-ingestion-platform-v2

`.agent/programs/` 当前 active program 是：

- Program 3：`zuno-enterprise-ingestion-async-infrastructure-v1`
- 当前 phase：`.agent/programs/PHASE01_truth-source-and-async-gap-audit.md`

Program 3 承接 Program 2 已完成的 Product V1 local durable ingestion baseline，把文档输入层推进到 enterprise ingestion async infrastructure baseline。当前目标包括 PostgreSQL-compatible fact store boundary、ObjectStore binary support、QueueBackend / LocalQueueBackend、RabbitMQ boundary、Redis runtime state boundary、ParserWorker / IndexWorker、Outbox、Dead Letter、Reconciler、OCR / VLM worker boundary、ingest status / retry / cancel / replay contract。

目标产品口径固定为 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace。用户在聊天里提出目标，并在勾选知识库时选择标准检索 / 深度检索；GraphRAG、BM25、vector、re-query、rerank 和工具调用由 Single Controller Agent 内部自动规划。Basic RAG 和 Static GraphRAG 只作为 Program 6 的评测对照组，不是最终产品模式。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。Current 必须来自代码、focused tests、trace、eval、verifier 或可复现证据。真实 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index 未接入并测试前，仍只能写作 Target / target-blocked evidence。

## 当前 Front Path 文件

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
- `.agent/programs/queued-programs/README.md`
- `.agent/programs/queued-programs/PROGRAM04_runtime-subsystems-parallel.md`
- `.agent/programs/queued-programs/PROGRAM05_agent-planning-integration.md`
- `.agent/programs/queued-programs/PROGRAM06_enterprise-knowledge-eval-benchmark.md`

active 状态下，`.agent/programs/` 根目录保留当前 Program 3 的 PHASE 文件。completed program 的 phase 和 closure evidence 必须在 `docs/history/programs/` 归档。

## Program Suite 顺序

当前 Program 1-6 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的前台数字化执行序列；旧 Program 1A / 1B 命名已收敛为 Program 1 / Program 2，后续 queued program 自动后移为 Program 4-6。

1. Program 1：`zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
2. Program 2：`zuno-enterprise-document-ingestion-platform-v2`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
3. Program 3：`zuno-enterprise-ingestion-async-infrastructure-v1`
   - 状态：active。
   - 当前 phase：`.agent/programs/PHASE01_truth-source-and-async-gap-audit.md`
4. Program 4：`zuno-runtime-subsystems-parallel-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM04_runtime-subsystems-parallel.md`
5. Program 5：`zuno-agent-planning-integration-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM05_agent-planning-integration.md`
6. Program 6：`zuno-enterprise-knowledge-eval-benchmark-v1`
   - 状态：queued。
   - 计划：`.agent/programs/queued-programs/PROGRAM06_enterprise-knowledge-eval-benchmark.md`

## 最近完成归档

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`：完成 PHASE01-PHASE08、durable ingestion、restart recovery、验证和 no-active closure。
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 Program 1 的 Document IR、parser worker、native parser、adapter boundary、index manifest lineage、workspace ingest -> ParseGateway 闭环、runtime subsystems prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：历史 Program 4 / `zuno-six-layer-internalization-v1` 的六层内部入口、README、focused tests 和 verifier guard 完成事实。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成 PHASE01-PHASE10 的上一轮八大治理交付物闭环。
- `zuno-repo-layout-cleanup-v1`：repo layout cleanup 历史完成 program id，前台不恢复旧布局。

## 历史完成事实锚点

- 历史 Program 3 final alias surface closure 已完成；旧 public import path 通过 `legacy_aliases.py` 注册兼容，`src/backend/` 前台只保留 `zuno/`。
- `zuno-runtime-architecture-upgrade-v1` 和 `zuno-architecture-visuals-v1` 是旧队列 / 历史方向名称，不是当前 active program；当前 queued program 以 Program 4-6 列表为准。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- Program 3 必须从 PHASE01 开始，不跳过 truth source 与 async gap audit。
- 当前实现继续遵守 runtime-first / vertical-slice-first closure guard；runtime phase 只有在真实 API / runtime / focused tests / trace / eval / verifier 证明后才能关闭。
- 新 runtime 行为继续遵守 TDD；只写 contract、schema 或 README 不能关闭 runtime phase。
- queued program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- completed program 必须归档到 `docs/history/programs/`。
- 多线程模式只用于 Codex 工程执行；Zuno 产品 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
- Basic RAG 和 Static GraphRAG 是 Program 6 的评测对照组，不是最终产品模式。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`

# 当前 Program 状态

## Current Truth

state: active
active_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
current_phase: PHASE11_workspace-product-api-frontend-sync.md
latest_completed_program: zuno-enterprise-document-ingestion-platform-v2

`.agent/programs/` 当前 active program 是：

- Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
- 当前 phase：`.agent/programs/PHASE11_workspace-product-api-frontend-sync.md`

Program 3 Mega 合并原 active Program 3 与 queued Program 4-6：

1. 原 Program 3：`zuno-enterprise-ingestion-async-infrastructure-v1`
2. 原 Program 4：`zuno-runtime-subsystems-parallel-v1`
3. 原 Program 5：`zuno-agent-planning-integration-v1`
4. 原 Program 6：`zuno-enterprise-knowledge-eval-benchmark-v1`

合并后的目标是完成一个 launchable enterprise Agentic GraphRAG product baseline：输入层可靠、知识库层可查、能力层可编排、记忆层可进上下文、规划层可 plan / react / reflect / replan / reflexion、安全层可 gate、评测层可记录质量、成本和耗时，产品链路能 E2E 跑通。

目标产品口径固定为 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace。Agent Core 公式是 `Model Gateway + Memory & Context Engine + Planning & Control Runtime + Capability Layer + Governance / Trace / Eval Envelope`。用户在聊天里提出目标，并在勾选知识库时选择标准检索 / 深度检索；GraphRAG、BM25、vector、re-query、rerank、Skill、MCP 和工具调用由 Single Controller Agent 内部自动规划。Skill 是 Capability Layer 里的任务方法包，不是 Tool、不是 Knowledge、也不是产品级多 Agent runtime。Basic RAG 和 Static GraphRAG 只作为 eval baseline，不是最终产品模式。

成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。Current 必须来自代码、focused tests、trace、eval、verifier 或可复现证据。真实 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index 未接入并测试前，仍只能写作 Target / target-blocked evidence。

## 当前 Front Path 文件

- `.agent/programs/current.md`
- `.agent/programs/README.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_truth-source-and-merge-plan.md`
- `.agent/programs/PHASE02_shared-contract-freeze.md`
- `.agent/programs/PHASE03_enterprise-ingestion-async-infrastructure.md`
- `.agent/programs/PHASE04_knowledge-retrieval-and-graphrag-profile.md`
- `.agent/programs/PHASE05_memory-context-engine.md`
- `.agent/programs/PHASE06_capability-skill-tool-mcp-layer.md`
- `.agent/programs/PHASE07_security-governance-envelope.md`
- `.agent/programs/PHASE08_model-gateway-cost-latency.md`
- `.agent/programs/PHASE09_planning-contract-and-strategy-selector.md`
- `.agent/programs/PHASE10_react-reflection-replan-reflexion-runtime.md`
- `.agent/programs/PHASE11_workspace-product-api-frontend-sync.md`
- `.agent/programs/PHASE12_end-to-end-product-runtime.md`
- `.agent/programs/PHASE13_eval-trace-cost-benchmark.md`
- `.agent/programs/PHASE14_docs-architecture-expansion.md`
- `.agent/programs/PHASE15_verification-archive-closure.md`
- `.agent/programs/queued-programs/README.md`
- `.agent/programs/queued-programs/PROGRAM04_runtime-subsystems-parallel.md`
- `.agent/programs/queued-programs/PROGRAM05_agent-planning-integration.md`
- `.agent/programs/queued-programs/PROGRAM06_enterprise-knowledge-eval-benchmark.md`

active 状态下，`.agent/programs/` 根目录保留当前 Program 3 Mega 的 PHASE 文件。completed program 的 phase 和 closure evidence 必须在 `docs/history/programs/` 归档。

## Program Suite 顺序

当前 Program 1-3 是 `zuno-enterprise-agentic-graphrag-production-suite-v1` 的前台数字化执行序列；旧 Program 1A / 1B 命名已收敛为 Program 1 / Program 2，原 Program 3-6 已合并为 Program 3 Mega。

1. Program 1：`zuno-production-document-ingestion-and-thread-foundation-v1`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
2. Program 2：`zuno-enterprise-document-ingestion-platform-v2`
   - 状态：completed / archived。
   - 归档：`docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
   - 完成：Product V1 local durable ingestion baseline。
3. Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
   - 状态：active。
   - 当前 phase：`.agent/programs/PHASE11_workspace-product-api-frontend-sync.md`
   - 合并输入：`zuno-enterprise-ingestion-async-infrastructure-v1`、`zuno-runtime-subsystems-parallel-v1`、`zuno-agent-planning-integration-v1`、`zuno-enterprise-knowledge-eval-benchmark-v1`

## Mega Phase Gate

当前 active phase 文件为 PHASE01-PHASE15。PHASE01-PHASE02 是顺序闸门；PHASE03-PHASE08 可在 contract freeze 后按 workstream 并行；PHASE09-PHASE11 是 planning / runtime / product API 集成；PHASE12-PHASE15 是 E2E、eval、docs、archive closure。

## 最近完成归档

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`：完成 PHASE01-PHASE08、durable ingestion、restart recovery、验证和 no-active closure。
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`：完成 Program 1 的 Document IR、parser worker、native parser、adapter boundary、index manifest lineage、workspace ingest -> ParseGateway 闭环、runtime subsystems prompts 和 no-active closure。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”的本地可验证 baseline。
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：完成 PHASE01-PHASE12 的 runtime-first / vertical-slice-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：完成 PHASE01-PHASE12 的目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：完成 PHASE01-PHASE10 的上一轮八大治理交付物闭环。
- `docs/history/programs/zuno-six-layer-internalization-v1/`：历史 Program 4 / `zuno-six-layer-internalization-v1` 的六层内部入口、README、focused tests 和 verifier guard 完成事实。
- `zuno-repo-layout-cleanup-v1`：repo layout cleanup 历史完成 program id，前台不恢复旧布局；历史 Program 3 final alias surface closure 已完成，旧 public import path 通过 `legacy_aliases.py` 注册兼容。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- Program 3 Mega 必须从 PHASE01 开始，不跳过 truth source、merge plan 和 shared contract freeze。
- 当前实现继续遵守 runtime-first / vertical-slice-first closure guard；runtime phase 只有在真实 API / runtime / focused tests / trace / eval / verifier 证明后才能关闭。
- 新 runtime 行为继续遵守 TDD；只写 contract、schema 或 README 不能关闭 runtime phase。
- superseded program 只能放在 `.agent/programs/queued-programs/`，不得写成 active 或 completed。
- completed program 必须归档到 `docs/history/programs/`。
- 多线程模式只用于 Codex 工程执行；Zuno 产品 runtime 主线仍是 Single Controller / Single `GeneralAgent`。
- Basic RAG 和 Static GraphRAG 是评测对照组，不是最终产品模式。

## Future Reference Drafts

以下旧 draft 仍是未来参考输入，不是 active program：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`

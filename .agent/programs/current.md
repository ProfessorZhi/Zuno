# 当前程序

state: active
active_program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
current_phase: PHASE01_truth-source-and-merge-plan.md
latest_completed_program: zuno-enterprise-document-ingestion-platform-v2

## 当前状态

`.agent/programs/` 当前 active program 已合并为一个超大 Program：

- Program 3 Mega：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`
- 中文名：Zuno 可上线企业知识库 Agentic GraphRAG 全链路闭环 Program
- 当前 phase：`PHASE01_truth-source-and-merge-plan.md`
- Suite：`zuno-enterprise-agentic-graphrag-production-suite-v1`

本 program 合并原 active Program 3 和 queued Program 4-6：

1. 原 Program 3：`zuno-enterprise-ingestion-async-infrastructure-v1`
2. 原 Program 4：`zuno-runtime-subsystems-parallel-v1`
3. 原 Program 5：`zuno-agent-planning-integration-v1`
4. 原 Program 6：`zuno-enterprise-knowledge-eval-benchmark-v1`

合并原因：当前目标不是继续拆多个小 program，而是在一个可控的全链路 program 中把输入异步基础设施、Knowledge / Retrieval / GraphRAG、Memory & Context Engine、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost、Planning & Control Runtime、Eval / Trace / Benchmark、Product API / Frontend 最小同步、E2E、文档和归档统一收口成 launchable product baseline。

## 核心产品口径

Zuno 是 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace。Agent Core 公式是：

```text
Agent = Model Gateway
      + Memory & Context Engine
      + Planning & Control Runtime
      + Capability Layer
      + Governance / Trace / Eval Envelope
```

用户在聊天里提出目标，并在勾选知识库时选择标准检索 / 深度检索；GraphRAG、BM25、vector、re-query、rerank、Skill、MCP 和工具调用由 Single Controller Agent 内部自动规划。Skill 是 Capability Layer 里的任务方法包，不是 Tool、不是 Knowledge、也不是产品级多 Agent runtime。Basic RAG 和 Static GraphRAG 只作为 eval baseline，不是最终产品模式。

## 完成定义

本 program 完成时必须能说：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

这不表示已经部署真实 PostgreSQL / RabbitMQ / Redis / MinIO / OCR / VLM / external index 集群。完成口径是所有关键层都有 local runnable implementation、adapter boundary、dependency probe / target-blocked evidence、focused tests、E2E 闭环、trace/eval/cost 记录和文档成熟度边界。

成熟度和 Current / Target / Production Scale 边界以 `docs/architecture/production-readiness.md` 为准。

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
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`：runtime-first / vertical-slice-first 目标架构第一版闭环。
- `docs/history/programs/zuno-master-architecture-implementation-v1/`：目标架构分阶段实现、架构刷新和 release closure。
- `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`：八类治理交付物闭环。

## 当前 Phase Gate

1. `PHASE01_truth-source-and-merge-plan.md`：active。
2. `PHASE02_shared-contract-freeze.md`：pending。
3. `PHASE03_enterprise-ingestion-async-infrastructure.md`：pending。
4. `PHASE04_knowledge-retrieval-and-graphrag-profile.md`：pending。
5. `PHASE05_memory-context-engine.md`：pending。
6. `PHASE06_capability-skill-tool-mcp-layer.md`：pending。
7. `PHASE07_security-governance-envelope.md`：pending。
8. `PHASE08_model-gateway-cost-latency.md`：pending。
9. `PHASE09_planning-contract-and-strategy-selector.md`：pending。
10. `PHASE10_react-reflection-replan-reflexion-runtime.md`：pending。
11. `PHASE11_workspace-product-api-frontend-sync.md`：pending。
12. `PHASE12_end-to-end-product-runtime.md`：pending。
13. `PHASE13_eval-trace-cost-benchmark.md`：pending。
14. `PHASE14_docs-architecture-expansion.md`：pending。
15. `PHASE15_verification-archive-closure.md`：pending。

## Workstream 模型

本 program 是：

```text
一个总 Program
+ 多个 Phase Gate
+ 多条并行 Workstream
+ 多个 PR / commit
+ 一个 Coordinator 统一合并、验证、归档
```

核心原则：

```text
先冻结共享契约，再多 Agent 并行实现，最后统一集成、E2E、评测、文档归档。
```

并行 workstream：

- Coordinator：Program 状态、共享契约、roadmap、README / AGENTS、共享 API、最终 merge、验证、commit / push、archive。
- Workstream A：Input / Async Infrastructure。
- Workstream B：Knowledge / Retrieval / GraphRAG。
- Workstream C：Memory & Context Engine。
- Workstream D：Capability / Skill / Tool / MCP。
- Workstream E：Security / Governance。
- Workstream F：Planning / Agent Runtime。
- Workstream G：Eval / Trace / Cost。
- Workstream H：Product API / Frontend Minimal Sync。
- Workstream I：Docs / Verifier / Closure。

## 原 queued program 状态

原 Program 4-6 计划文件保留在 `.agent/programs/queued-programs/` 作为历史输入，但状态必须标注 `merged_into` / `superseded_by`，不得写成 completed。

## 当前执行规则

- 本轮先写 mega program，不启动 runtime 实现。
- 后续执行必须先完成 PHASE01 merge plan 和 PHASE02 shared contract freeze，再允许大规模并行实现。
- 新 runtime 行为必须 TDD：先写 focused failing test，再写最小实现。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
- 不把 PostgreSQL、RabbitMQ、Redis、MinIO / S3、external OCR / VLM、external index 写成 Current，除非有真实代码、focused tests 和可复现验证。
- Codex 多线程是工程执行方式，不是 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。

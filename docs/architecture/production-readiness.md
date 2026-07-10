# Production Readiness

status: implementation_available_measurement_blocked

本文件只维护状态事实源，不承担完整目标架构设计。完整产品与运行架构以 `docs/architecture/architecture.md` 为准。

## Current

Zuno 当前前台定位是 Lean Complete Agentic GraphRAG Product：本地优先、短期可闭环、可演示、可评测、可恢复的企业知识库 Agent 产品。

已具备的本地实现基线包括：

- Product & API：AgentChat、workspace、knowledge/file、message、model/tool DTO 和部分 task/event surface。
- Input & Knowledge：文本类文档 ingestion、local object store、durable ingestion store、chunk/index、retrieval、GraphRAG 和 evidence-span hardening surface。
- Agent Core：GeneralAgent single loop、model manager/gateway surface、Context/Memory 相关 contract、claim-level citation binder。
- Capability & Tool：capability registry/control plane、tool adapters、MCP/tool surfaces。
- Governance & Observability：local trace/eval helpers、EnterpriseRAG paired eval runner、failure bucket diagnostics、release gate output surface。
- Local Infrastructure：SQLite/SQLModel、local object store、config、database/storage surfaces。

## Short-term Closure Gap

P0：

- Agentic GraphRAG fixed benchmark 跑通并达到 baseline gate。
- 所有真实模型调用统一进入 Model Runtime / Gateway。
- Agent run trace 持久化并可查看。

P1：

- task / planner / retrieval / approval 状态本地持久化。
- 至少一个真实 PDF parser 跑通 source span citation。
- 2-3 个真实 Tool 完成 approval / timeout / trace 闭环。
- Memory ContextPack 在真实 AgentChat 中可观测。

P2：

- 前端 E2E、项目演示脚本和可复现启动方式。

## Measurement Blocked

Agentic GraphRAG 当前不能写成 quality completed。

```text
implementation available
measurement blocked
quality not yet proven
```

blocked 原因：真实 fixed EnterpriseRAG paired benchmark 尚未完整产出可比较的 agentic profile measured pass。

必须保留的质量门：

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

blocked、prepared、runtime observed 和 measured 必须严格区分。缺 trace 字段时输出 `unavailable_due_to_missing_trace_fields`，不得编造 failure bucket。

## Completed

近期可作为 completed 的内容只限已经由代码、测试、trace/eval 或 verifier 支撑的本地实现基线和文档/guardrail 收口。

历史 program 完成事实保留在：

- `docs/history/programs/README.md`

历史完成不等于当前 quality gate 已通过。

## Future Optional

以下内容是可选未来扩展，不是短期 blocker：

- Postgres、Redis、MinIO、RabbitMQ、Kafka、Kubernetes。
- 外部 Milvus / Neo4j 集群和分布式 graph/vector index。
- 复杂 SSO / DLP / Vault、Firecracker。
- 大规模在线评测平台和企业运维门户。
- 大量 parser/provider 并行接入、OCR/VLM enrichment 平台化。
- 产品级多 Agent runtime。

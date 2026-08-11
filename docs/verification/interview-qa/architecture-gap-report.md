# Architecture Gap Report

## 第一轮盲审结果

第一轮只允许使用 base main 的 canonical documents；不把聊天记录、第三方面经答案、代码猜测或行业惯例补进回答。

| 状态 | 数量 |
| --- | ---: |
| FULL | 159 |
| PARTIAL | 73 |
| MISSING | 0 |
| CONFLICTING | 0 |

PARTIAL 的主要原因不是缺少类名，而是文档已有相关词汇，却没有把输入、Owner、触发、状态、失败语义、恢复和 Eval 连成一条可防追问的机制。

## P0：高概率且需要明确补齐的缺口

### G-03-001：SourceSpan 与 CitationChunk 的关系

- 问题：无法直接回答二者是否一对一、为什么都需要、如何回到 DocumentVersion/SourceObject，以及 ChunkingPolicy 或文档版本变化后如何避免 Citation 漂移。
- Gap 类型：MISSING_EXPLANATION、MISSING_LINEAGE、MISSING_VERSION_BOUNDARY。
- 修复：docs/modules/03-knowledge-agentic-graphrag.md § 7.2 三种检索粒度，补充多对多关系、strict Citation、content hash 和版本迁移边界。
- 状态：CLOSED。

### G-03-002：SearchAction 层级与 1..N 选择

- 问题：旧文档同时出现 BM25/Vector/Local/Global/DRIFT，容易被理解成完全平级的五种 Planner Action，无法明确 HYBRID 内部 Operator 和一个 Requirement 如何选择多个互补 Action。
- Gap 类型：AMBIGUOUS_TERMINOLOGY、MISSING_OWNERSHIP、MISSING_TRIGGER。
- 修复：docs/modules/03-knowledge-agentic-graphrag.md § 14.1 SearchAction 层级，定义 HYBRID、GRAPH_LOCAL、GRAPH_GLOBAL、GRAPH_DRIFT、STRUCTURED 与 RetrieverAction 的关系。
- 状态：CLOSED。

### G-03-003：RRF、Rerank、Top-N/Top-K 与 Evidence Evaluation

- 问题：已有 Fusion/Rerank 名词，但第一阶段 Recall、rank-only RRF、有限候选 Rerank 和充分性判断的区别不够面试级；First-pass 与 Unified Rerank 也可能被误解为两套架构。
- Gap 类型：MISSING_EXPLANATION、MISSING_TRADEOFF、MISSING_EVAL。
- 修复：docs/modules/03-knowledge-agentic-graphrag.md § 15.1，明确 Recall、RRF、Unified Evidence Rerank、Evidence Evaluation 和可调参数边界。
- 状态：CLOSED。

### G-03-004：Graph/Hybrid Candidate Materialization 与 Canonical Dedup

- 问题：无法只凭一段文字回答 GraphPath、Community、DRIFT 如何转成 Source-backed Candidate，以及同一个 SourceSpan 被多路发现时如何只保留一个 Candidate。
- Gap 类型：MISSING_LINEAGE、MISSING_IDEMPOTENCY、MISSING_VERSION_BOUNDARY。
- 修复：docs/modules/03-knowledge-agentic-graphrag.md § 15.2，定义 Materialization、Dedup Key、retrieval_origins 和 Graph provenance。
- 状态：CLOSED。

## P1：重要系统设计追问

### G-X-001：跨模块合同案例缺少单一口述入口

此前模块分别有完整机制，但跨模块问“合同审查到发送邮件”时需要在多份文档间跳转。总架构 § 7.13 已提供统一案例、Ownership 和 A–E 异常边界；模块 QA 只引用该正式事实。状态：CLOSED。

### G-X-002：Tool/MCP Approval 与 Effect Reconciliation 的连续链

08/09 已有生命周期，但盲审要求把 Snapshot、Approval Hash、Epoch、UNKNOWN 和 Reconciliation 连成一条完整链。现有 08 § 16/20/30/36、09 § 12.1/29/35 可独立回答。状态：CLOSED（通过既有 canonical sections，不新增 Runtime）。

### G-X-003：Memory 冲突、污染和 ContextPack 的优先级

05 已有三正交维度、Candidate/Governance、Version、Conflict、Projection 和Protected Set；本轮按这些章节重生成 QA，不在 QA 内增加规则。状态：CLOSED（通过既有 canonical sections）。

### G-X-004：Agent Core 五种机制与 Replan Barrier

06 已有固定RunGraph、动态Plan DAG、StepExecutionGraph、Reflection/Retry/Replan、Join、Interrupt、Final Gate；盲审将其统一成层级控制，而不是五选一。状态：CLOSED（通过既有 canonical sections）。

### G-X-005：Current / Target / Future / History 边界

所有 QA 最终答案保留 Target 警告；生产规模、线上指标和实现状态不由面试语料推断。状态来源仍为 docs/status/production-readiness.md。状态：CLOSED。

## P2：低概率或未来压力题

### G-F-001：具体十万并发容量数字

这需要运行基线、压测和生产约束，不应为了面试写入 Target 文档。QA 只能回答架构上的 Capacity/Quota/Admission/Degradation 原则。状态：保留为 Future measurement，不是 Coverage Blocker。

### G-F-002：第三方 MCP Server 的部署回滚

Zuno 不拥有外部 Provider 部署时，不能承诺 rollback。QA 已明确写成 Capability/Binding 失效、停止使用、请求 Provider Owner 处理。状态：CLOSED as boundary；外部部署实现仍属 Future/Owner Required。

### G-F-003：完整 CI、生产 Trace 和真实质量数字

本轮不运行完整 CI，不制造 benchmark，不把文档覆盖当成实现证据。状态：明确为 Evidence/Current Gap，不阻断架构 QA Coverage Gate。

## 修复后最终状态

- 232 / 232 coverage_status=FULL。
- 0 PARTIAL、0 MISSING、0 CONFLICTING。
- 73 个第一轮 PARTIAL 已有对应 CLOSED-GAP 标记或由既有 canonical sections 关闭。
- QA 没有新增架构事实；正式架构修改仅为 Module 03 的四个明确机制段落。

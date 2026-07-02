# Agent Core Runtime

本文说明 Zuno 近期 runtime 主线的 Agent Core。它不替代 `architecture.md` 和 `production-readiness.md`；总架构和成熟度边界仍以后两者为准。

## 定位

Zuno 的近期产品主线是 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace。Agent Core 公式固定为：

```text
Agent = Model Gateway
      + Memory & Context Engine
      + Planning & Control Runtime
      + Capability Layer
      + Governance / Trace / Eval Envelope
```

这里的 Agent 是产品 runtime 里的 Single Controller Agent，不是 Codex 多线程施工模式，也不是产品级多 Agent 平台。

## Current Local Slice

Current 只写代码、测试、trace、eval 或 verifier 已证明的事实：

- `src/backend/zuno/platform/model_gateway.py` 已提供本地 `ModelGateway`、mock provider categories、token / latency / cost estimate、budget verdict、timeout fallback 和 redacted trace。
- `src/backend/zuno/memory/engine.py` 已提供 ContextPack、structured / hierarchical / evidence-bound / budget-aware compression、sensitive / stale / conflict / revoked exclusion reason 和 Reflexion lesson review candidate path。
- `src/backend/zuno/agent/planning.py` 已提供 deterministic Strategy Selector、PlannerOutput、PlanState、RetrievalPlan、CapabilityPlan、security / budget blocked verdict 和 planning trace events。
- `src/backend/zuno/agent/control_runtime.py` 已提供 AgentControlRuntime、ReAct observation runner、reflection gate、dynamic replan trajectory change、tool_failed / security_blocked stop path、ReflexionLesson pending review path 和 answer_finalized trace。
- `src/backend/zuno/agent/product_baseline.py` 已用真实 local runtime path 证明 PHASE12 E2E scenario summary、trace summary、feedback 和 restart rehydrate。
- `src/backend/zuno/platform/observability/product_benchmark.py` 已把 PHASE12 E2E 输出汇总成 PHASE13 regression summary。

对应 focused tests 包括 `tests/agent/test_planning_control_runtime.py`、`tests/agent/test_react_reflection_replan_runtime.py`、`tests/memory/test_context_pack_engine.py`、`tests/evals/test_model_gateway_cost_latency.py`、`tests/evals/test_agentic_graphrag_product_baseline.py` 和 `tests/evals/test_agentic_graphrag_regression_summary.py`。

## Runtime 主链路

```text
Workspace Task / AgentChat request
  -> product retrieval profile: standard / deep
  -> StrategySelector
  -> ContextPack
  -> RetrievalPlan / CapabilityPlan
  -> AgentControlRuntime step loop
  -> Reflection / Replan / Reflexion candidate
  -> cited artifact
  -> feedback
  -> trace / eval / cost summary
```

用户只选择知识库和标准检索 / 深度检索。BM25、vector、GraphRAG fallback、rerank、Skill、Tool 和 MCP boundary 由 Single Controller Agent 内部规划。

## Launchable Prototype Target

近期目标是把已完成的 local baseline 整理成可演示、可验证、可归档的产品雏形：

- 文档入口能解释 Agent Core 如何拼接 Model Gateway、Memory、Planning、Capability 和 Eval Envelope。
- PHASE15 archive 能把 Current evidence、focused tests、E2E scenario、metrics 和 remaining production targets 归档。
- Web / API surface 继续只暴露产品语义，不暴露内部 basic / local / global / drift 这类技术模式。

## Production Scale Target

以下仍是 Production Scale Target，不能写成 Current：

- 生产级 LangGraph-compatible DB persistence。
- 跨进程 / 跨 worker durable resume。
- 分布式 exactly-once tool execution。
- 真实外部模型供应商路由、在线账单和 SLA / quota 管理。
- 生产级 semantic / vector memory DB 和后台 consolidation scheduler。

## 不变量

- Skill 是 Capability Layer 的任务方法包，不是 Tool、Knowledge 或产品级多 Agent。
- Basic RAG 和 Static GraphRAG 只作为 eval baseline labels，不是最终产品模式。
- 未接真实 provider 的外部服务只能写成 adapter boundary、dependency probe 或 target-blocked evidence。

# Code Architecture Map

## 当前关键路径

```text
src/backend/zuno/agent/core/agents/general_agent.py
  真实 create_agent ReAct、ContextPack、Memory read/write、Knowledge tool、MCP/Skill/tool

src/backend/zuno/agent/planning.py
  StrategySelector、PlannerOutput、PlanState 规则 baseline

src/backend/zuno/agent/control_runtime.py
  handcrafted Observation 上的 Reflection/Replan/Reflexion baseline

src/backend/zuno/agent/harness.py
  controller node contract 和 checkpoint/interrupt contract

src/backend/zuno/agent/durable_runtime.py
  InMemory store + 顺序模拟 node runtime

src/backend/zuno/memory/engine.py
src/backend/zuno/memory/store.py
  Memory taxonomy、governance、durable store、ContextPack baseline

src/backend/zuno/capability/runtime.py
src/backend/zuno/capability/control_plane.py
  Tool Control Plane、approval、credential ref、sandbox policy、normalized result

src/backend/zuno/knowledge/agentic_graphrag.py
src/backend/zuno/knowledge/query_service.py
  retrieval routing、evidence/citation baseline

src/backend/zuno/platform/model_gateway.py
  目标统一模型入口

src/backend/zuno/platform/observability/
src/backend/zuno/platform/common/runtime_observability.py
  trace/eval 基础

src/backend/zuno/api/services/completion.py
src/backend/zuno/api/v1/completion.py
  AgentChat 产品入口
```

## 目标代码结构

```text
src/backend/zuno/agent/
  contracts.py
  planning.py
  control_runtime.py
  durable_runtime.py
  runtime/
    __init__.py
    state.py
    contracts.py
    dependencies.py
    limits.py
    events.py
    store.py
    graph.py
    service.py
    routing.py
    planning/
      selector.py
      planner.py
      validator.py
      executor.py
      replan.py
    nodes/
      input_gate.py
      build_context.py
      strategy_select.py
      create_plan.py
      execute_step.py
      observe.py
      evidence_gate.py
      draft_and_bind_claims.py
      reflect.py
      revise_draft.py
      replan.py
      tool_approval.py
      finalize.py
      post_turn_commit.py
    execution/
      registry.py
      react_step.py
      knowledge_step.py
      tool_step.py
      model_step.py
    synthesis/
      claims.py
      citation_binding.py
      grounded_answer.py
    reflection/
      deterministic.py
      critic.py
      engine.py
```

## Knowledge 目标增量

```text
src/backend/zuno/knowledge/
  agentic_graphrag.py
  agentic/
    contracts.py
    query_strategy.py
    evidence_ledger.py
    quality.py
    corrective.py
    runtime.py
```

如果拆分风险过大，可保留 facade，但以下 owner 必须独立：

- EvidenceLedger
- RetrievalQualityEvaluator
- CorrectiveRetrievalPolicy
- AgenticRetrievalRuntime

## Platform 持久化增量

```text
src/backend/zuno/platform/database/models/agent_runtime.py
  AgentRunRow
  AgentCheckpointRow
  AgentPlanRow
  AgentObservationRow
  AgentInterruptRow
  EvidenceLedgerRow
  ToolExecutionRow

src/backend/zuno/platform/observability/local_trace_store.py
```

表名和现有 SQLModel convention 以当前代码为准，不可盲目复制名称。

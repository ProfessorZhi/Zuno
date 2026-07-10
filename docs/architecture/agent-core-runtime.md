# Agent Core Runtime

所属运行域：Agent Core、Governance & Observability。

## 定位

Agent Core / Planning & Control 是 Single Controller 的协调层，负责 Strategy、Plan、ReAct step、Observation、Reflection、Replan、Stop condition、abstain、claim-level citation 和 answer synthesis 的任务级控制。它调用 Model Gateway、Memory、Knowledge、Capability 和 Tool Runtime，但不把这些能力物理吞成一个大层。

Agent Core 不是多 Agent 平台，也不是直接把 retrieval/tool 拼在 API route 里。正确边界是：

```text
Agent Core / Planning & Control
  -> Model Gateway
  -> Memory
  -> Knowledge
  -> Capability
  -> Tool Runtime
```

Model Gateway、Memory、Knowledge、Capability 和 Tool Runtime 必须保留独立 owner、contract、生命周期和测试边界。Agent Core 只通过 typed plan、context、observation 和 gate contract 协调它们。

## 核心 contract

- ModelDefinition、ModelSlotBinding、ModelCallRequest、ModelCallResponse。
- ContextPack：session、workspace、memory、knowledge scope、budget 和 redaction 后上下文。
- PlannerOutput：strategy、RetrievalPlan、CapabilityPlan、stop condition。
- PlanState：每一步观察、决策、错误、fallback 和 replan 记录。
- Observation：retrieval result、tool result、model result 或 gate result。
- ReflectionDecision：finish、re-retrieve、use tool、abstain。
- GroundedAnswer：claims、citations、unsupported claims、artifact refs。
- MemoryRecord、MemoryGovernanceRecord：post-turn memory candidate 和治理状态。

## Runtime Loop

```text
START
-> input_gate
-> build_context
   -> session state
   -> memory read
   -> knowledge scope
-> strategy_select
   -> direct
   -> react
   -> plan_and_execute
-> create_or_update_plan
-> execute_step
   -> knowledge retrieval
   -> graph expansion
   -> governed tool call
-> observe
-> evidence_gate
-> draft_and_bind_claims
-> reflection
   -> PASS -> finalize
   -> RETRIEVE_MORE -> replan -> execute_step
   -> USE_TOOL -> approval/tool -> observe
   -> ASK_USER -> interrupt
   -> ABSTAIN -> finalize
-> post_turn_commit
   -> raw event
   -> task summary
   -> Reflexion candidate
-> END
```

所有真实模型调用最终必须统一进入 `src/backend/zuno/platform/model_gateway.py` 或其明确 successor。`src/backend/zuno/agent/core/models` 可作为 legacy compatibility surface，但不得继续新增绕过 gateway 的 direct SDK call。

Plan-and-Execute、ReAct、Reflection、Replan 和 Reflexion 不是五层、五个独立 Agent 或五个产品模式。它们是 Agent Core / Planning & Control 内部机制：

- Plan-and-Execute 负责宏观计划、步骤、预算和停止条件。
- ReAct 负责单个步骤内的 reason-act-observe。
- Observation 归一化 retrieval、model、tool 和 gate 结果。
- Reflection 检查 evidence、citation、unsupported claim、tool failure 和 security blocked。
- Replan 修改剩余计划并重新进入 execute_step。
- Reflexion 只把可复用教训交给 Memory governance，不直接写入长期记忆。

必须有硬性控制：`max_steps`、`max_replans`、`max_reflections`、`timeout`、`budget`、`PASS`、`abstain`。命中上限时只能输出 partial/blocked/abstain 语义，不能写成 measured success。

## 失败语义

- evidence insufficient：允许 re-retrieve 或 abstain。
- citation missing：不能输出 strict citation。
- model unavailable：返回 blocked 或 fallback model，必须 trace。
- max steps reached：输出 partial/blocked，不写成 measured success。
- tool denied/timeout：Agent 观察失败并 replan 或 abstain。

## 当前与短期目标

Current：

- GeneralAgent single loop、model manager/gateway surface、memory contracts、claim binder、planning contracts 和 evidence-aware pieces 已存在。
- Memory 模块能力和本地 baseline 较完整，但完整 MemoryEngine 尚未全部接入真实 AgentChat 生命周期。
- Planning contract 和规则判断存在，但真实 LangChain/LangGraph ReAct、规则式 AgentControlRuntime、SingleControllerDurableRuntime 尚未统一为一条真实执行图。

Short-term：

- P0 所有真实模型调用统一进入 Model Runtime / Gateway。
- P0 统一 Agent Core 真实闭环：Strategy、Plan-and-Execute、ReAct、Observation、Reflection、Replan、Reflexion、Memory 和 Retrieval 进入同一条可执行、可恢复、可测量链路。
- P1 PlanState durable。
- P1 Memory ContextPack 在真实 AgentChat 中可观测。

Future Optional：

- 产品级多 Agent runtime。
- 分布式 controller 和 worker 编排。

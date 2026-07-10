# Agent Core Runtime

所属运行域：Agent Core、Governance & Observability。

## 定位

Agent Core 收口 Model Runtime / Gateway、ContextPack、Memory、Planning & Control、Single Controller Runtime、claim-level citation 和 answer synthesis。它不是多 Agent 平台，也不是直接把 retrieval/tool 拼在 API route 里。

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
AgentChat Request
-> build ContextPack
-> read Memory
-> choose strategy
-> create RetrievalPlan / CapabilityPlan
-> execute retrieval or tool
-> observe diagnostics
-> bind claims to evidence
-> synthesize grounded answer
-> reflect
-> finish / re-retrieve / use tool / abstain
-> post-turn memory commit
```

所有真实模型调用最终必须统一进入 `src/backend/zuno/platform/model_gateway.py` 或其明确 successor。`src/backend/zuno/agent/core/models` 可作为 legacy compatibility surface，但不得继续新增绕过 gateway 的 direct SDK call。

## 失败语义

- evidence insufficient：允许 re-retrieve 或 abstain。
- citation missing：不能输出 strict citation。
- model unavailable：返回 blocked 或 fallback model，必须 trace。
- max steps reached：输出 partial/blocked，不写成 measured success。
- tool denied/timeout：Agent 观察失败并 replan 或 abstain。

## 当前与短期目标

Current：

- GeneralAgent single loop、model manager/gateway surface、memory contracts、claim binder 和 evidence-aware pieces 已存在。

Short-term：

- P0 所有真实模型调用统一进入 Model Runtime / Gateway。
- P1 PlanState durable。
- P1 Memory ContextPack 在真实 AgentChat 中可观测。

Future Optional：

- 产品级多 Agent runtime。
- 分布式 controller 和 worker 编排。

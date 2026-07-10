# 当前程序

state: active
active_program: zuno-unified-agent-runtime-closure-v1
current_phase: PHASE03_model-gateway-closure
latest_completed_program: zuno-lean-complete-product-architecture-v1
baseline_commit: 72488a25fde59bc5ef86b2b1c84f25d42cb946ca

## 当前目标

把以下三个并存基线收敛为一条真实主链路：

```text
GeneralAgent
  = 真实 LangChain/LangGraph ReAct 与现有模型/工具/知识库入口

StrategySelector + AgentControlRuntime
  = Planning / Reflection / Replan / Reflexion 规则与 contract

SingleControllerDurableRuntime
  = checkpoint / approval / resume / cancel 的本地 deterministic runtime
```

目标链路：

```text
input_gate
-> build_context
-> strategy_select
-> create_or_update_plan
-> execute_step
-> observe
-> evidence_gate
-> draft_and_bind_claims
-> reflection
   -> PASS -> finalize
   -> REWRITE_ANSWER -> revise_draft -> claim binding -> reflection
   -> RETRIEVE_MORE -> replan -> execute_step
   -> USE_TOOL -> approval/tool -> observe
   -> ASK_USER -> interrupt/resume
   -> ABSTAIN -> finalize
-> post_turn_commit
-> END
```

## 当前 Phase

`PHASE03_model-gateway-closure`

PHASE01 已完成事实源、现状证据、运行命令、失败语义和 benchmark truth source 冻结，未修改生产 runtime。PHASE02 已建立 `zuno.agent.runtime` 版本化 contract、`AgentRuntimeState` / `AgentRuntimeSnapshot`、`NormalizedObservation`、runtime limits/counters、strategy/reflection/finalization 枚举和 legacy adapters；未实现模型网关闭环、持久化、LangGraph 主图或产品切换。下一步 PHASE03 只处理 Model Gateway closure。

## 不变边界

- 近期保持 Single Controller，不转向产品级 Multi-Agent。
- Model、Memory、Knowledge、Capability、Tool Runtime 保持独立 owner。
- 所有真实模型调用最终统一进入 Model Gateway。
- Tool 执行必须经过 Tool Control Plane。
- Graph evidence 必须回到 SourceSpan。
- Reflexion 不保存隐藏 CoT，只保存可审计的经验候选。
- `implementation available / measurement blocked / quality not yet proven` 在 measured gate 通过前保持不变。

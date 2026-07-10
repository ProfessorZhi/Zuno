# 当前程序

state: active
active_program: zuno-unified-agent-runtime-closure-v1
current_phase: PHASE08_corrective-agentic-graphrag-and-evidence-ledger
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

`PHASE08_corrective-agentic-graphrag-and-evidence-ledger`

PHASE01 已完成事实源、现状证据、运行命令、失败语义和 benchmark truth source 冻结，未修改生产 runtime。PHASE02 已建立 `zuno.agent.runtime` 版本化 contract、`AgentRuntimeState` / `AgentRuntimeSnapshot`、`NormalizedObservation`、runtime limits/counters、strategy/reflection/finalization 枚举和 legacy adapters。PHASE03 已建立 `ModelRole`、`ModelCallRequest` / `ModelCallResponse` aliases、role-aware gateway trace、LangChain-compatible gateway adapter、GeneralAgent gateway 注入和 direct-call boundary verifier；legacy SDK wrappers 仍以显式 allowlist 保留，不是产品主 unified runtime 入口。PHASE04 已建立 SQLite-backed `SQLiteAgentRunStore`、local trace store、tool idempotency claim、scope load、corrupt JSON rejection 和 restart resume tests。PHASE05 已建立 unified LangGraph topology、`UnifiedAgentRuntimeService`、conditional routes、stream、approval/ask_user interrupt、resume、cancel、checkpoint 和无 simulated marker 的 deterministic skeleton；产品 API/UI 尚未切换。PHASE06 已建立 runtime Strategy、Plan validation、PlanExecutor、StepExecutorRegistry 和多步 execution baseline。PHASE07 已接入 Tool Control Plane approval/resume/idempotency/blocked observation baseline。下一步 PHASE08 只处理 corrective Agentic GraphRAG 和 EvidenceLedger。

## 不变边界

- 近期保持 Single Controller，不转向产品级 Multi-Agent。
- Model、Memory、Knowledge、Capability、Tool Runtime 保持独立 owner。
- 所有真实模型调用最终统一进入 Model Gateway。
- Tool 执行必须经过 Tool Control Plane。
- Graph evidence 必须回到 SourceSpan。
- Reflexion 不保存隐藏 CoT，只保存可审计的经验候选。
- `implementation available / measurement blocked / quality not yet proven` 在 measured gate 通过前保持不变。

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
- PlanStep：goal、action_type、dependencies、input_refs、expected_output、acceptance_criteria、allowed_capabilities、retrieval_policy、tool_policy、model_role、budget、timeout、retry_policy 和 status。
- PlanState：每一步观察、决策、错误、fallback、version 和 replan 记录。
- Observation：retrieval result、tool result、model result 或 gate result。
- ReflectionDecision：PASS、REWRITE_ANSWER、RETRIEVE_MORE、USE_TOOL、ASK_USER、ABSTAIN。
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
   -> REWRITE_ANSWER -> revise_draft -> draft_and_bind_claims
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

## PlanStep contract

```yaml
plan_step:
  step_id: string
  goal: string
  action_type: retrieve | graph_expand | tool | model_transform | synthesize | verify
  dependencies: [step_id]
  input_refs: [artifact_or_state_ref]
  expected_output_schema: string
  acceptance_criteria:
    - type: evidence_count | citation_coverage | schema | tool_status | custom
      operator: gte | eq | contains | passed
      value: any
  allowed_capabilities: [capability_id]
  retrieval_policy: retrieval_profile_ref
  tool_policy: tool_policy_ref
  model_role: planner | executor | critic | synthesis | tool_call
  retry_policy:
    max_attempts: int
    retry_on: [failure_code]
  budget:
    token_limit: int
    cost_limit: number
    timeout_ms: int
  status: pending | running | completed | failed | blocked | skipped
```

Plan 质量检查：

| 检查 | 通过标准 | 失败动作 |
| --- | --- | --- |
| 完备性 | 所有用户目标均被某一步覆盖 | 重新规划 |
| 独立性 | 步骤职责无重复或冲突 | 合并或改写 |
| 原子性 | 一步有明确输入输出和 owner | 继续拆分 |
| 可验证性 | 每步有 acceptance criteria | 补验收标准 |
| 依赖正确性 | DAG 无环且依赖可满足 | 拒绝计划 |
| 并行性 | 无依赖步骤可 fan-out | 标记并行组 |
| 预算可行性 | 估算不超过策略预算 | 降级或 abstain |

近期可以先串行执行，但 contract 要能表达 DAG、并行组和动态细分，避免未来重写 PlanState。

## StrategyDecision

```yaml
strategy_decision:
  execution_mode: direct | react | plan_and_execute
  reflection_policy: none | final_only | critical_steps | every_step
  replan_policy: disabled | on_failure | on_low_evidence | on_material_change
  reflexion_policy: disabled | candidate_on_failure
  retrieval_mode: none | standard | deep | agentic
  planner_model_role: planner
  executor_model_role: executor
  critic_model_role: critic
  budget:
    max_steps: int
    max_actions_per_step: int
    max_replans: int
    max_reflections: int
    max_retrieval_rounds: int
```

Strategy 选择矩阵：

| 任务特征 | Execution | Reflection | Replan | Retrieval |
| --- | --- | --- | --- | --- |
| 简单、事实明确 | direct | final-only deterministic gate | disabled | standard/none |
| 开放式搜索、工具反馈多 | react | on failure | on failure | deep |
| 多步骤研究、报告、比较 | plan-and-execute | critical steps + final | enabled | agentic |
| 高风险、引用要求高 | plan-and-execute | required | enabled | agentic |
| 低延迟简单操作 | react/direct | deterministic only | disabled | minimal |

## Reflection rubric

Reflection 拆成 Deterministic gates 和可选 Model critic。

Deterministic gates：

- evidence_count；
- source span completeness；
- citation_coverage；
- unsupported_claim_count；
- schema validation；
- tool status；
- security verdict；
- budget/hard limit。

Model critic 只在高质量场景启用，检查 completeness、logical consistency、answer relevancy、evidence faithfulness、conflicting evidence handling 和 instruction compliance。

Reflection 必须有 PASS，通常最多 2-3 轮。简单任务不启用 model critic。

## Replan requirements

Replan 必须改变真实执行轨迹。每次至少修改以下一项：

- remaining steps；
- step dependency；
- query strategy；
- retrieval scope；
- retriever mix；
- graph traversal；
- tool selection；
- acceptance criteria；
- model role；
- budget allocation。

```text
Reflection RETRIEVE_MORE / tool failed / material change
-> ReplanDecision
-> update PlanState version
-> execute_step
-> new Observation
-> Reflection again
```

Replan 不能只生成一段诊断文字后结束。

## Reflexion candidate

```yaml
reflexion_candidate:
  lesson_id: string
  task_type: string
  failure_type: string
  trigger: string
  root_cause: string
  failed_action: string
  lesson: string
  recommended_strategy: string
  applicability_conditions: [condition]
  evidence_refs: [evidence_or_trace_ref]
  confidence: number
  sensitivity: public | workspace | user_private
  review_status: pending | approved | rejected
```

禁止保存原始隐藏推理链；只保存可审计的决策摘要、失败事实和可复用经验。

## 失败语义

- evidence insufficient：允许 re-retrieve 或 abstain。
- citation missing：不能输出 strict citation。
- model unavailable：返回 blocked 或 fallback model，必须 trace。
- max steps reached：输出 partial/blocked，不写成 measured success。
- tool denied/timeout：Agent 观察失败并 replan 或 abstain。

## 当前与短期目标

Current：

- GeneralAgent single loop、model manager/gateway surface、memory contracts、claim binder、planning contracts 和 evidence-aware pieces 已存在。
- `src/backend/zuno/agent/runtime/` 已提供 PHASE02 版本化 runtime contract：`AgentRuntimeState`、`AgentRuntimeSnapshot`、`NormalizedObservation`、runtime limits/counters、node outcome、strategy/reflection/finalization 枚举和 legacy adapters。它是后续统一 graph 的状态事实源，不等于真实 LangGraph 主图、SQLite restart recovery 或产品切换已经完成。
- `src/backend/zuno/platform/model_gateway.py` 已提供 PHASE03 role-aware gateway contract、cost/latency/fallback/redacted trace 和 LangChain-compatible legacy adapter；`GeneralAgent` 的 executor chat model 已经经由 gateway 获取。历史 legacy SDK wrappers 仍以 verifier allowlist 保留，不等于全仓所有旧服务已迁入统一 runtime。
- `SQLiteAgentRunStore` 已提供 PHASE04 SQLite-backed run/checkpoint/event/interrupt/plan/observation/tool claim baseline，并已用新 store 实例证明 pending interrupt 可恢复后 resume；完整 LangGraph 主图和产品 API/UI restart recovery 仍是后续目标。
- `UnifiedAgentRuntimeService` 已提供 PHASE05 unified LangGraph runtime skeleton：`build_agent_graph`、`RuntimeNode` routes、store-backed checkpoint/event、stream、approval / ask_user interrupt、resume、cancel 和 `get_snapshot`。该 skeleton 使用 deterministic node adapters，已移除 `status: simulated` marker；真实 Plan/ReAct step、Tool Control Plane、corrective retrieval、grounded synthesis 和产品 API/UI cutover 仍是后续 PHASE06-PHASE11 目标。
- PHASE06 已把 unified runtime skeleton 升级为逐步执行 baseline：`RuntimeStrategySelector`、`RuntimePlanner`、`PlanValidator`、`PlanExecutor`、`StepExecutorRegistry` 和 ReAct/Knowledge/Tool/Model step executors 已接入 `execute_step` 节点，复杂任务可执行多个 PlanStep 并记录 `status`、`attempt` 和 `observation_refs`。Tool executor 当前只产生 governed ToolCallIntent observation，真实 Tool Control Plane 执行和审批闭环仍属于 PHASE07。
- PHASE07 已把 `ToolStepExecutor` 接入 Tool Control Plane，approval/resume/idempotency/blocked observation baseline 已完成；产品 API/UI 切换仍属于 PHASE11。
- PHASE08 已把 corrective Agentic GraphRAG baseline 接入 unified runtime：`EvidenceLedger`、`RetrievalQualityGate`、`CorrectiveRetrievalPolicy` 和 `CorrectiveAgenticRetrievalRuntime` 可通过 `KnowledgeStepExecutor` 的 `knowledge_runtime` 依赖进入 retrieval step；fixed benchmark 仍未 measured。
- PHASE09 已把 Reflection / Replan / Grounded Synthesis 接入 unified runtime：`draft_and_bind_claims` 生成结构化 claims 和 strict citation binding，`reflection` 先执行 deterministic gate，`RETRIEVE_MORE` 会经 `ReplanEngine` 追加真实 `retrieve_evidence` step 并回到 `execute_step`，`REWRITE_ANSWER` 会先进入 `revise_draft` 再回到 claim binding 和 reflection。focused tests 已覆盖 first retrieval insufficient -> replan -> second retrieval -> grounded final；这仍不等于产品 API/UI cutover 或 fixed benchmark measured pass。
- Memory 模块能力和本地 baseline 较完整，但完整 MemoryEngine 尚未全部接入真实 AgentChat 生命周期。
- Planning / Reflection / Replan 的本地 unified runtime loop 已经形成 baseline；完整 Memory / Reflexion reuse、产品 cutover 和 release benchmark 仍是后续 PHASE10-PHASE13。

Short-term：

- P0 所有真实模型调用统一进入 Model Runtime / Gateway。
- P0 统一 Agent Core 真实闭环：Strategy、Plan-and-Execute、ReAct、Observation、Reflection、Replan、Reflexion、Memory 和 Retrieval 进入同一条可执行、可恢复、可测量链路。
- P1 PlanState durable。
- P1 Memory ContextPack 在真实 AgentChat 中可观测。

Future Optional：

- 产品级多 Agent runtime。
- 分布式 controller 和 worker 编排。

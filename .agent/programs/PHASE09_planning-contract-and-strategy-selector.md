# PHASE09 Planning Contract And Strategy Selector

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE09_planning-contract-and-strategy-selector
status: active

## 目标

把 Planning & Control Runtime 的契约和 Strategy Selector 落地，让 Agent 能根据 user goal、ContextPack、retrieval profile、Skill registry、Capability registry、security policy 和 budget 选择 direct_answer、react、plan_execute、plan_execute_with_replan、reflection_enabled、reflexion_enabled。

## 范围

- PlanStep、PlanState、PlannerOutput、StrategySelectorOutput。
- SelectedSkill、CapabilityPlan、RetrievalPlan。
- ReflectionVerdict、ReplanDecision、ReflexionLesson。
- 最小 deterministic / rule-based planner baseline。
- LLM planner boundary 保留为 Target，不依赖真实 LLM 才能过测试。

## 目标架构拼接点

本 phase 拼到 Agent Core 的 Planning & Control Runtime，是前面各层第一次合流：

- 从 Memory & Context Engine 读取 ContextPack。
- 从 Capability Layer 读取 SkillCard / ToolCard / KnowledgeCapability。
- 从 Knowledge Layer 读取 requested retrieval profile 和可用 index capability。
- 从 Security Envelope 读取 policy / risk / gate summary。
- 从 Model Gateway 读取 budget / cost constraints。
- 输出 plan、selected skill、retrieval plan、allowed tools、evidence requirements 和 trace events。

它不执行所有步骤，只决定“下一步该怎么做”。PHASE10 才让 plan 真正影响 runtime 轨迹。

## 并行开发可行性

本 phase 在 PHASE02、PHASE04、PHASE05、PHASE06、PHASE07、PHASE08 contract 可用后由 Workstream F 负责。它可以和 PHASE13 指标定义并行，但不能和 PHASE10 同时改同一 planning runtime。

可并行：

- Strategy matrix tests 与 SelectedSkill tests 可并行。
- RetrievalPlan construction 与 CapabilityPlan construction 可并行。
- Budget-aware strategy tests 可由 Workstream G review。

不可并行：

- 不得在 selector 中直接执行 tool 或 retrieval。
- 不得让 planner 输出未注册 capability。
- 不得绕过 security policy 直接选择高风险 tool。

## 详细执行卡

- 输入依赖：PHASE02 plan contracts、PHASE04 retrieval profiles、PHASE05 ContextPack、PHASE06 Skill registry、PHASE07 SecurityDecision、PHASE08 budget fields。
- 主要交付物：PlanStep、PlanState、PlannerOutput、StrategySelectorOutput、SelectedSkill、CapabilityPlan、RetrievalPlan、ReflectionVerdict、ReplanDecision、ReflexionLesson。
- 可并行工作包：strategy selector rules、skill selection tests、retrieval plan builder、clarification/unanswerable cases 可拆；PlanState contract 由单 owner 维护。
- Coordinator 锁点：Single Controller Agent 主线，不把 Codex 多线程执行误写成 Zuno product runtime 多 Agent。
- 下游交接：PHASE10 执行 PlanState；PHASE12 E2E 验证 planner 影响真实路径；PHASE13 记录 plan_step_count / strategy_selected / selected_skill。
- PR / commit 建议：`feat(planning): add strategy selector contracts` 与 `test(planning): cover lookup multihop tool report strategies`。

## 禁止范围

- 不把 planning 写成产品级多 Agent runtime。
- 不在本 phase 大改 workspace runtime public API。
- 不让 strategy selector 绕过 Security Gate 或 Capability Policy。

## 验收闸门

- lookup task 选择 direct / light retrieval。
- multi-hop task 选择 plan_execute_with_replan。
- tool task 选择 react。
- formal report task 选择 plan_execute + reflection。
- code / test task 可启用 reflexion_enabled。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_planning_control_runtime.py -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/agent/**`
- `src/backend/zuno/capability/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/knowledge/**`
- `tests/agent/**`

## 需要修改的文件

- `src/backend/zuno/agent/**`
- `tests/agent/test_planning_control_runtime.py`
- supporting tests under `tests/agent/**`

## 执行拆解

1. 写 StrategySelector tests。
2. 写 selected skill / retrieval plan tests。
3. 写 unavailable capability fallback test。
4. 实现 deterministic planner baseline。
5. 输出 planning trace fields。

## 多 agent 分工

- Workstream F owner。
- Workstream C/D/B/G 提供 frozen contract。
- Coordinator 审查任何 shared contract 变化。

## 需要返回的证据

- strategy selection matrix。
- focused tests。
- sample PlannerOutput。
- trace event 示例。

## 停止条件

- PHASE02 shared contract 未冻结。
- planner 需要真实 LLM 才能 deterministically 通过 tests。
- planning 输出会破坏 existing GeneralAgent compatibility。

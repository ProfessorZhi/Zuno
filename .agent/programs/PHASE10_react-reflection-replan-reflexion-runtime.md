# PHASE10 ReAct Reflection Replan Reflexion Runtime

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE10_react-reflection-replan-reflexion-runtime
status: active

## 目标

让 Planning & Control Runtime 影响真实 runtime 轨迹：ReAct step runner 执行步骤，Reflection gate 检查证据、引用、安全和工具结果，Dynamic Replan 能改变后续步骤，Reflexion 生成 lesson candidate 并进入 Memory review path。

## 范围

- ReAct step runner。
- Reflection gate：evidence enough、citation coverage、unsupported claim、tool failed、security blocked。
- Dynamic Replan：retrieval_empty、evidence_conflict、citation_coverage_low、tool_failed、security_blocked、budget_low、user_steered。
- ReflexionLesson candidate，进入 governance review path。
- trace events：strategy_selected、skill_selected、plan_created、step_completed、reflection_completed、replan_created、reflexion_candidate_created、answer_finalized。

## 目标架构拼接点

本 phase 是 Agent Core 从“能计划”变成“能控制执行”的关键：

- ReAct runner 调用 Capability Layer 的 Knowledge / Tool / Artifact capabilities。
- Reflection 用 EvidenceBundle、CitationLineage、Security verdict 和 cost metrics 检查是否可以继续。
- Dynamic Replan 根据 observation 改剩余 plan，而不是重开一轮任务。
- Reflexion 把失败原因写成 candidate，交给 Memory & Context Engine 的 governance review path。
- Trace / Eval 收到每个 step、reflection、replan、reflexion event。

完成后，Agent 不再只是固定检索回答，而具备最小 plan -> act -> observe -> reflect -> replan -> answer 控制闭环。

## 并行开发可行性

本 phase 高耦合，必须由 Workstream F 单 owner 推进。其他 workstream 只能修自己层的 failing tests，不能同时改主 runner。

可并行：

- Workstream B 修 retrieval observation。
- Workstream D 修 tool capability invocation。
- Workstream E 修 gate verdict。
- Workstream C 修 Reflexion review path。

不可并行：

- 多个 agent 同时改 Agent runner。
- Coordinator 未审查就改 `workspace_task_runtime.py`。
- 在 reflection failed 时继续生成 final answer。

## 详细执行卡

- 输入依赖：PHASE09 PlanState / ReplanDecision、PHASE04 EvidenceBundle、PHASE05 Reflexion memory review path、PHASE07 security verdict、PHASE08 budget guard。
- 主要交付物：ReAct step runner、Reflection gate、Dynamic Replan、ReflexionLesson candidate、trace events for plan/step/reflection/replan/reflexion/final answer。
- 可并行工作包：reflection predicates、replan trigger mapping、trace event writer、Reflexion candidate builder 可拆；主 runtime loop integration 单 owner。
- Coordinator 锁点：GeneralAgent / workspace runtime integration、用户 steer 时的优先级、低证据时是否允许 final answer。
- 下游交接：PHASE12 需要一次真实 replan 改变后续轨迹；PHASE13 需要 reflection_count / replan_count / reflexion_count；PHASE14 文档记录 planner 闭环。
- PR / commit 建议：`feat(agent): add reflection replan reflexion runtime baseline` 与 `test(agent): prove replan changes execution trajectory`。

## 禁止范围

- 不让 reflection 不通过时直接 final answer。
- 不让 ReflexionLesson 绕过 governance 直接写长期 memory。
- 不把 Codex 多 agent 施工模型写进 Zuno runtime。

## 验收闸门

- replan 真的改变后续 retrieval/tool 轨迹。
- reflection 不通过不会直接 final answer。
- security_blocked 会触发 stop / ask_user / refuse，而不是继续执行危险 tool。
- ReflexionLesson candidate 进入 Memory review path。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_planning_control_runtime.py -p no:cacheprovider
pytest -q tests/agent -p no:cacheprovider
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/agent/**`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/platform/security/**`
- `tests/agent/**`
- `tests/api/test_workspace_task_runtime.py`

## 需要修改的文件

- `src/backend/zuno/agent/**`
- focused tests under `tests/agent/**`
- API/runtime integration only through Coordinator-owned files when needed

## 执行拆解

1. 写 replan changes trajectory test。
2. 写 reflection blocks final answer test。
3. 写 tool_failed / security_blocked replan test。
4. 写 ReflexionLesson candidate test。
5. 实现 runtime runner 最小闭环。
6. 确认 trace event sequence 可被 Eval phase 消费。

## 多 agent 分工

- Workstream F owner。
- Coordinator controls `workspace_task_runtime.py` and shared API files。
- Workstream C/E/G review memory, security, trace contract integration。

## 需要返回的证据

- plan trace before / after replan。
- reflection verdict 示例。
- reflexion candidate 示例。
- focused tests 输出。

## 停止条件

- integration 需要大改 GeneralAgent 主循环且缺少兼容路径。
- replan 造成无限循环或不可控 token / cost 增长。
- safety blocked 被继续执行。

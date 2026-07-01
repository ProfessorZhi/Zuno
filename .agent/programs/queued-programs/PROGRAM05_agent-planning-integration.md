# PROGRAM05 Agent Planning Integration

state: queued
program: zuno-agent-planning-integration-v1
depends_on: zuno-runtime-subsystems-parallel-v1

## 目标

把 Program 4 的 Memory、Tool、安全和 GraphRAG 成果合并进 Single Controller Agent，实现真实 `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit`。Program 5 是 Zuno 从“能检索回答”走向“能计划、执行、反思、重规划”的关键 program。

## 核心边界

- 仍然是 Single Controller / Single `GeneralAgent` 主线。
- Planner、Reflection、Replan 是 Agent Core Runtime 内部控制点，不是产品多 Agent。
- LangGraph-compatible DB persistence 仍是 Production Target，除非本 program 真实接入 DB checkpointer 和跨 worker recovery。

## PHASE01 合并准备

目标：

- 拉取 Program 4 四个分支。
- 建立 diff map、conflict map、test map。
- 判断哪些变更先合并，哪些需要主线程重写。

验收：

- 每个分支 commit hash、push status、验证结果明确。
- 共享文件冲突清单明确。

## PHASE02 Planning Contract

目标：

- 定义 `PlanStep`、`PlanState`、`PlannerOutput`、`ReflectionVerdict`、`ReplanDecision`。
- 每个 plan step 包含目标、所需证据、允许工具、预算、失败条件、停止条件。

候选路径：

- `src/backend/zuno/agent/planning.py`
- 或 `src/backend/zuno/agent/planning/contracts.py`
- `tests/agent/test_planning_runtime.py`

验收：

- Planner contract tests 先失败后通过。
- 类型命名和 runtime event 字段稳定。

## PHASE03 Planner Node

目标：

- 输入用户问题、Context Pack、Memory、document metadata、security policy。
- 输出可执行 plan。
- 能区分 lookup、多跳、跨文档对比、表格查询、不可回答问题、需要澄清问题。

验收：

- 对不同 question type 产生不同 plan。
- plan 中声明 retrieval / tool / memory / ask-user 的使用条件。

## PHASE04 ReAct Step Runner

目标：

- 每个 plan step 可进入 `think / action / observe`。
- action 可调 retrieval、GraphRAG expansion、tool、memory lookup 或 ask-user。

验收：

- step observation 可进入 trace。
- tool / retrieval failure 不直接导致最终胡答。

## PHASE05 Reflection Gate

目标：

- 检查证据够不够、引用是否覆盖、是否有 unsupported claim、是否触发安全策略、工具是否失败。
- 输出 continue、finish、retrieve_more、replan、ask_user。

验收：

- evidence 不足时不会 final answer。
- unsupported claim 触发 replan 或 refuse。

## PHASE06 Replan Node

目标：

- 当召回不足、证据冲突、工具失败、预算不足、用户目标变化时，重写剩余 plan。

验收：

- replan 会实际改变后续 retrieval/tool 轨迹。
- replan reason 可进入 trace。

## PHASE07 Durable Runtime 接入

目标：

- 替换当前偏模拟的 plan / act / reflect / replan 节点。
- 接入 workspace task event、checkpoint、failure snapshot 和 exactly-once tool boundary。

验收：

- restart / resume 不丢失 plan state。
- exactly-once id boundary 不被 replan 破坏。

## PHASE08 End-to-End Agentic GraphRAG

目标：

- 企业文档问题进入系统后，能经历 plan、retrieval、reflection、replan、cited answer。

验收：

- 至少覆盖 lookup、多跳、跨文档、不可回答四类问题。
- trace 中可看到 plan_created、step_completed、reflection_completed、replan_created、answer_finalized。

## 验证基线

```powershell
git diff --check
pytest -q tests/agent/test_planning_runtime.py -p no:cacheprovider
pytest -q tests/agent/test_general_agent_project_query_runtime.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
pytest -q tests/agent/test_knowledge_graphrag_runtime_contracts.py tests/evals/test_multihop_eval_real_runtime_runner.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
```

## 停止条件

- Program 4 分支未完成或验证不可信。
- Planning 需要 public API 或 DB schema 变更，但未经过单独 phase 审批。
- Planner 只能生成静态模板，无法通过测试证明会影响 runtime 行为。
- replan 无法被 trace 或 tests 观察。

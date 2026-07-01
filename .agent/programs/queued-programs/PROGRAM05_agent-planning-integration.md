# PROGRAM05 Agent Planning Integration

state: queued
program: zuno-agent-planning-integration-v1
depends_on: zuno-runtime-subsystems-parallel-v1

## 目标

把 Program 4 的 Memory & Context Engine、Capability / Skill / Tool / MCP、安全和 GraphRAG 成果合并进 Single Controller Agent，实现真实 `prepare_context -> strategy_select -> plan -> skill_select -> ReAct / Plan-and-Execute -> observe -> reflect -> dynamic_replan -> reflexion -> post_turn_commit`。Program 5 是 Zuno 从“能检索回答”走向“能计划、执行、反思、重规划并沉淀 lesson”的关键 program。

产品口径必须固定：用户在 AgentChat 提目标，在勾选知识库时选择标准检索 / 深度检索；用户不手动选择 RAG、GraphRAG、local、global 或 drift。Program 5 的核心是 Planning & Control Runtime + Agentic Retrieval Planner：它读取每个知识库的 requested profile、index capability、ACL、selected / pinned Skill、Capability Router、Memory state、证据质量和预算，自动决定 strategy、query rewrite、retriever selection、GraphRAG expansion、tool / memory capability use、re-query、rerank、reflection、dynamic replan、reflexion 和 final cited answer。

## 核心边界

- 仍然是 Single Controller / Single `GeneralAgent` 主线。
- Strategy Selector、Planner、Reflection、Dynamic Replan 和 Reflexion 是 Agent Core Runtime 内部控制点，不是产品多 Agent。
- 标准检索 / 深度检索是知识库级 retrieval profile，不是全局 Agent 工作模式。
- GraphRAG 是 Agent 可调用的 retrieval tool，不是用户可见主模式。
- Skill 是 Capability Layer 里的任务方法包，不是 Tool，也不是 Knowledge。
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
- 定义 `StrategySelectorOutput`、`SelectedSkill`、`CapabilityPlan` 和 `ReflexionLesson`。
- 每个 plan step 包含目标、所需证据、允许工具、预算、失败条件、停止条件。
- 定义 `RetrievalPlan` 或等价 contract，包含 `knowledge_retrieval_profiles`、`requested_profile`、`effective_profile`、`fallback_reason`、`retrievers`、`max_rounds`、`evidence_requirements` 和 `citation_required`。

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
- 输入被勾选的 knowledge spaces、每个 knowledge space 的标准检索 / 深度检索 profile、index capability 和 ACL scope。
- 输入 available skills、pinned skill、available capabilities、MCP / Tool registry、Reflexion lessons 和 budget。
- 输出可执行 plan。
- 能区分 lookup、多跳、跨文档对比、表格查询、不可回答问题、需要澄清问题。

验收：

- 对不同 question type 产生不同 plan。
- Strategy Selector 能区分 direct_answer、react、plan_execute、plan_execute_with_replan、reflection_enabled 和 reflexion_enabled。
- Skill selection 记录 selected_skill_id、skill_version、selection_reason、required_evidence、allowed_tools 和 eval_rubric。
- plan 中声明 retrieval / tool / memory / ask-user 的使用条件。
- 深度检索不会一上来强制跑所有通道；它必须表现为 staged retrieval：先便宜召回，证据不足才 graph expand / re-query / strong rerank。

## PHASE04 ReAct Step Runner

目标：

- 每个 plan step 可进入 `think / action / observe`。
- action 可调 standard retrieval、deep retrieval、GraphRAG expansion、tool capability、MCP capability、memory read / write capability 或 ask-user。

验收：

- step observation 可进入 trace。
- tool / retrieval failure 不直接导致最终胡答。
- trace 记录每个知识库的 `requested_profile`、`effective_profile` 和 `fallback_reason`。

## PHASE05 Reflection Gate

目标：

- 检查证据够不够、引用是否覆盖、是否有 unsupported claim、是否触发安全策略、工具是否失败。
- 输出 continue、finish、retrieve_more、replan、ask_user。
- 对可复用失败原因输出 reflexion_candidate，但不能绕过 Memory governance 直接写长期记忆。

验收：

- evidence 不足时不会 final answer。
- unsupported claim 触发 replan 或 refuse。

## PHASE06 Dynamic Replan 与 Reflexion Node

目标：

- 当召回不足、证据冲突、工具失败、预算不足、用户目标变化时，重写剩余 plan。
- 当测试失败、citation coverage low、unsupported claim、tool failed 或 security blocked 有可复用教训时，生成 ReflexionLesson candidate。

验收：

- replan 会实际改变后续 retrieval/tool 轨迹。
- replan reason 可进入 trace。
- ReflexionLesson 带 task_type、failure_type、root_cause、lesson、recommended_fix、trigger_condition、evidence_refs、scope、safety_label 和 expiry，并进入 Memory review path。

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
- 至少覆盖：标准检索单文档事实、深度检索跨文档分析、深度检索但 graph index 未就绪时 `deep_without_graph` 降级。
- 至少覆盖：contract_review 或 research_report Skill 自动选择 / pinned skill 两条路径。
- 至少覆盖：一次 retrieval_empty 或 citation_coverage_low 触发 dynamic replan，且一次可复用失败写入 ReflexionLesson candidate。
- trace 中可看到 strategy_selected、skill_selected、plan_created、step_completed、reflection_completed、replan_created、reflexion_candidate_created、answer_finalized。

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

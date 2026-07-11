# 当前程序

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-real-unified-runtime-cutover-v1
latest_completed_archive: docs/history/programs/zuno-real-unified-runtime-cutover-v1/

## 当前状态

`.agent/programs/` 当前没有 active program。

最近完成并归档的 program 是 `zuno-real-unified-runtime-cutover-v1`。

关闭口径：

```text
implementation_status: implementation_complete
measurement_status: measurement_blocked
measurement blocked
quality_gate_status: quality_not_proven
blocked_reason: enterprise_rag_sample8_external_db_unavailable_and_agentic_profile_incomplete
```

## 完成事实

本轮已完成本地实现切换：

- `UnifiedAgentRuntimeService` 使用 compiled LangGraph。
- `RuntimeDependencyFactory` 统一装配 Model Gateway、Memory、Knowledge 和 Tool Control Plane。
- ModelStep 经 Model Gateway 执行。
- ReActStep 执行当前 PlanStep 的单步 reason / act / observe。
- Knowledge / Tool / Memory 已接入 unified runtime。
- Completion 默认进入 unified runtime；legacy GeneralAgent 只通过 `ZUNO_AGENT_RUNTIME=legacy_general_agent` rollback。

## 未证明事项

fixed EnterpriseRAG paired benchmark 没有完成完整 measured profile。tracked sample-8 复跑暴露 profile runner 依赖本地 Postgres / LLM 配置，当前环境不可用。不得把本地 implementation tests passed 写成 quality pass，也不得把 Agentic GraphRAG superiority 写成已证明。

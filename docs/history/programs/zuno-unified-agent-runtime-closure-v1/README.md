# Agent 执行计划

`.agent/programs/` 已恢复 no-active 前台状态；本目录保存 `zuno-unified-agent-runtime-closure-v1` 的归档快照和收口证据。

## 当前状态

- State: completed / archived
- Program: `zuno-unified-agent-runtime-closure-v1`
- Current phase: none
- Latest completed program: `zuno-unified-agent-runtime-closure-v1`
- Closure status: `implementation_complete_measurement_blocked`

## 本轮 Program 口径

本 program 的目标是把 `GeneralAgent`、`StrategySelector + AgentControlRuntime` 和 `SingleControllerDurableRuntime` 收敛为同一条真实、可恢复、可测量的 Single Controller Agent Runtime。

完成范围：

- PHASE01-PHASE12 完成本地 unified runtime implementation baseline。
- PHASE13 修复 paired benchmark / release gate 的 measurement semantics：profile 不完整、provider 不可用、sample-80 缺少 tracked set 时都不得写成 measured。
- Completion / Workspace API 已有 unified runtime trace surface；真实 text PDF SourceSpan vertical slice 已通过。

未完成质量证明：

- fixed EnterpriseRAG paired benchmark 没有完整 measured pass。
- sample-8 运行产出 `blocked_not_measured`，原因是本地 embedding profile runner 未配置。
- sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。
- Agentic GraphRAG 质量仍是 `implementation available / measurement blocked / quality not yet proven`。

## 归档文件

- 根目录 PHASE / roadmap / checklist 文件：归档时 active program 的平铺快照。
- `programs/`：归档时 `.agent/programs/` 的完整目录快照。
- `closure-summary.md`：PHASE01-PHASE13 完成事实、blocked 原因和验证证据。

## 使用规则

- 本目录是历史证据，不是 active execution path。
- 后续不得把本目录的 PHASE 文件复制回 `.agent/programs/` 当作当前计划。
- 后续只有真实 fixed paired benchmark 完整产出 standard/deep/agentic measured profile 后，才能改变 quality gate 结论。

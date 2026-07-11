# Agent 执行计划

`.agent/programs/` 当前处于 no-active 等待态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-unified-agent-runtime-closure-v1`

## 最近完成归档

- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`

该 program 关闭为 `implementation_complete_measurement_blocked`：本地 unified runtime implementation baseline 已完成，但 fixed EnterpriseRAG paired benchmark 没有 measured pass。

## 当前文件

- `current.md`：no-active state、最近完成 program 和下一步边界。
- `implementation-roadmap.md`：最近 completed program 的归档摘要和后续 program 入口规则。
- `closure-checklist.md`：最近 completed program 的 closure evidence 与未完成质量门。
- `queued-programs/README.md`：queued program 索引。
- `queued-programs/PROGRAM01_real-unified-runtime-cutover.md`：下一轮候选实现 program，状态为 queued / not active。

## 使用规则

- no-active 状态下不得保留 active PHASE 文件。
- 新 program 必须从 PHASE01 开始，并先更新 `current.md`、roadmap、closure checklist、verifier 和 tests。
- queued program 不等于 active program；不得把 queued 内容写成 Current、Completed 或 measured。
- completed program 的 phase、closure summary 和执行证据必须留在 `docs/history/programs/`。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。

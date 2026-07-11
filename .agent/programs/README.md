# Agent 执行计划

`.agent/programs/` 当前处于 active program 状态。

## 当前状态

- State: active
- Active program: `zuno-real-unified-runtime-cutover-v1`
- Current phase: `PHASE01_real-runtime-baseline`
- Latest completed program: `zuno-unified-agent-runtime-closure-v1`

## 最近完成归档

- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`

该 program 关闭为 `implementation_complete_measurement_blocked`：本地 unified runtime implementation baseline 已完成，但 fixed EnterpriseRAG paired benchmark 没有 measured pass。

## 当前文件

- `current.md`：active state、当前 phase、冻结事实和质量边界。
- `implementation-roadmap.md`：PHASE01-PHASE07 执行顺序和每 phase 固定节奏。
- `closure-checklist.md`：implementation gate、quality gate 和禁止虚假关闭。
- `PHASE01_real-runtime-baseline.md` 至 `PHASE07_benchmark-and-closure.md`：本 program 的平铺 active phase 文件。
- `queued-programs/README.md`：queued program 索引。
- `queued-programs/PROGRAM01_real-unified-runtime-cutover.md`：下一轮候选实现 program，状态为 queued / not active。

## 使用规则

- 新 program 必须从 PHASE01 开始，并先更新 `current.md`、roadmap、closure checklist、verifier 和 tests。
- activated_from_queue 设计稿不等于完成证据；不得把 PHASE02-PHASE07 目标写成 Current、Completed 或 measured。
- completed program 的 phase、closure summary 和执行证据必须留在 `docs/history/programs/`。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。

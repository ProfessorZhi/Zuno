# Agent 执行计划

`.agent/programs/` 当前处于 no-active 状态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-real-unified-runtime-cutover-v1`
- Latest completed archive: `docs/history/programs/zuno-real-unified-runtime-cutover-v1/`

## 当前文件

- `current.md`：no-active state、最近完成 program 和质量边界。
- `implementation-roadmap.md`：no-active 状态和最近完成 program 摘要。
- `closure-checklist.md`：最近完成 program 的 closure checklist 和未证明事项。
- `queued-programs/README.md`：queued program 索引。
- `queued-programs/PROGRAM01_real-unified-runtime-cutover.md`：已激活并归档的 queued source，不再作为执行状态事实源。

## 使用规则

- 新 program 必须从 PHASE01 开始，并先更新 `current.md`、roadmap、closure checklist、verifier 和 tests。
- completed program 的 phase、closure summary 和执行证据必须留在 `docs/history/programs/`。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。

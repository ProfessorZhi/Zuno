# Agent 执行计划

`.agent/programs/` 当前处于 no-active 状态。

## 当前状态

- State: no-active
- Active program: none
- Current phase: none
- Latest completed program: `zuno-evidence-span-agentic-graphrag-hardening-v1`

最近完成并归档的 evidence-span hardening program 入口：

- `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/`

## 当前文件

- `current.md`：no-active state、最近完成 program 和前台文件边界。
- `implementation-roadmap.md`：最近完成 program 的归档入口和后续 Target。
- `closure-checklist.md`：最近完成 program 的关闭结论和后续重开条件。
- `queued-programs/README.md`：当前没有 queued program。

## 使用规则

- no-active 状态下，`.agent/programs/` 根目录不得保留平铺 `PHASE*.md`。
- 新 program 必须从 `PHASE01` 开始，不能复用已归档 phase 文件作为 active truth source。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。
- completed program 的 phase、closure summary 和 merged inputs 必须留在 `docs/history/programs/`。

# Agent 执行计划

`.agent/programs/` 当前保存 active program：`zuno-production-architecture-and-deliverables-completion-v1`。

## 当前状态

- State: active
- Active program: `zuno-production-architecture-and-deliverables-completion-v1`
- Current phase: `PHASE09_memory-context-production-governance`
- 最近完成 program: `zuno-target-architecture-runtime-full-implementation-v1`
- 最近完成归档位置: `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`

## 本轮定位

本轮不是继续做架构细化，也不是再做最小 runtime slice。它是一次性交付型成熟化 program，目标是完整推进四大总交付物：

1. 工作流自洽与自我维护。
2. 文档系统清晰无冗余。
3. 文件夹和代码 ownership 清晰。
4. 架构功能完整实现；该项展开为八类 runtime-first 交付物。

成熟度、Current / Target 边界和四大总交付物口径以 `docs/architecture/production-readiness.md` 为准；本目录保存执行计划、phase gate 和 closure 证据。

## 文件

- `current.md`：当前状态和 program 规则。
- `implementation-roadmap.md`：PHASE01-PHASE12 总路线。
- `closure-checklist.md`：最终收口闸门。
- `PHASE01_*.md` 到 `PHASE12_*.md`：当前 active phase 文件。

## 使用规则

- 必须按 PHASE01 -> PHASE12 顺序推进。
- 每个 phase 关闭前必须运行最小有效验证，并写回 phase 文件。
- completed program 必须归档到 `docs/history/programs/`。
- 允许使用主线程 coordinator + 多 agent / 多 worktree 模式；多 agent 是工程执行方式，不改变 Zuno 产品 runtime 的 Single Controller 主线。
- 只写 contract、schema 或 README 不能关闭 runtime phase。

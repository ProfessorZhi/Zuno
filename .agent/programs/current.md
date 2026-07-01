# 当前程序

state: active
active_program: zuno-production-architecture-and-deliverables-completion-v1
current_phase: PHASE09_memory-context-production-governance

## 目标

本 program 是一次性交付型成熟化 program：把 Zuno 从“第一版 runtime-first vertical slice 已完成”推进到“成熟目标架构和四大总交付物完成”。

四大总交付物以 `docs/architecture/production-readiness.md` 为准：

1. 工作流自洽与自我维护。
2. 文档系统清晰无冗余。
3. 文件夹和代码 ownership 清晰。
4. 架构功能完整实现；该项展开为八类 runtime-first 交付物。

本 program 允许使用主线程 coordinator + 多 agent / 多 worktree 模式。这里的多 agent 是 Codex 工程执行方式，不改变 Zuno 产品 runtime 的 Single Controller / Single GeneralAgent 主线。

## 当前阶段

- 当前 phase：`PHASE09_memory-context-production-governance`
- 当前动作：把 Memory 与 Context 推进到 semantic/vector memory、后台治理 scheduler、隐私删除平台和 memory eval baseline。
- 当前验收：PHASE09 只有在 memory 可跨任务读写、审查、删除和追责，semantic/vector adapter 有 local fallback 和 tests，memory eval baseline 进入 release gate 后才能关闭。

## 最近完成基线

最近完成并归档的 program：`zuno-target-architecture-runtime-full-implementation-v1`

归档位置：

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`

该 program 的 runtime-first closure evidence 保留在归档目录；本状态文件不重复闭环链路细节。

上一轮 foundation program：`zuno-master-architecture-implementation-v1`

- `docs/history/programs/zuno-master-architecture-implementation-v1/`

## 执行规则

- 必须按 PHASE01 -> PHASE12 顺序推进。
- 每个 phase 必须有代码、focused tests、trace / eval、verifier 或运行证据之一，才能把 Target 升为 Current。
- 只写 contract、schema 或 README 不能关闭 runtime phase。
- 不为目录好看直接删除兼容路径；compatibility、vendor、legacy alias 必须先有 import matrix、替代 owner 和 tests。
- 不把多 agent 执行方式写成 Zuno 产品 runtime 架构。
- 每个 phase 完成后更新 phase 文件状态、运行最小有效验证、提交并推送；最终 PHASE12 归档到 `docs/history/programs/` 并回到明确状态。

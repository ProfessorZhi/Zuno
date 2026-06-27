# 当前执行状态

当前 active program 就是 `.agent/programs/` 根目录这一层。不要再进入子目录找当前计划。

## 状态

- 当前 program：`zuno-workflow-doc-system-v1`。
- 上一个 program `zuno-architecture-surface-cleanup-v1` 已完成并归档到 `docs/history/programs/zuno-architecture-surface-cleanup-v1/`。
- 当前待打开 phase：`PHASE01` 工作流与文档系统只读审计。
- 后续剩余 phase：`PHASE02` Agent bootloader / routing、`PHASE03` skills / templates / programs、`PHASE04` workflow verifiers / drift tests、`PHASE05` closure / history archive。
- 当前执行顺序以 [implementation-roadmap.md](implementation-roadmap.md) 和各 phase 文件为准。
- 每次新 program 都从 `PHASE01` 开始编号；旧 active phase 先归档，再从前台移除。

## 工作模式

- 主线程负责 program 协调、线程拆分、合并、总验证和推送。
- 子线程必须使用独立 worktree、独立 branch、Codex UI 目标模式。
- 子线程内部默认使用多 agent 模式；无法使用时必须停止说明原因。
- Program 串行；Phase 按依赖执行；同一 phase 内可拆 2-4 个粗粒度线程并行。

## 当前计划文件

- [implementation-roadmap.md](implementation-roadmap.md)
- [PHASE01_workflow-doc-audit.md](PHASE01_workflow-doc-audit.md)
- [PHASE02_agent-bootloader-routing.md](PHASE02_agent-bootloader-routing.md)
- [PHASE03_skill-template-program-system.md](PHASE03_skill-template-program-system.md)
- [PHASE04_workflow-verifiers-drift-tests.md](PHASE04_workflow-verifiers-drift-tests.md)
- [PHASE05_closure-history-archive.md](PHASE05_closure-history-archive.md)
- [closure-checklist.md](closure-checklist.md)

## 停止线

本 program 只做工作流和文档系统收口。不要修改 runtime 行为、API、DB schema、依赖、frontend 产品行为或 eval baseline。不要在本 program 中整理后端物理目录；那属于后续 `zuno-repo-layout-cleanup-v1`。

正式面向人的状态汇总在 `docs/architecture/roadmap.md`。后续 queued program 草案在 `.agent/architecture/future/programs/`，但它们不是当前 active program。

## 后续 Program 队列

- Program 2：`zuno-target-architecture-refresh-v1`
- Program 3：`zuno-repo-layout-cleanup-v1`
- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

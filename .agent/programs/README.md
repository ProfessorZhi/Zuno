# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。

## 当前状态

当前没有 active program。

已完成并归档：

- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

后续 queued programs 仍在：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

## 打开新 Program 的规则

- 每次只打开一个 program。
- 打开前确认当前 `.agent/programs/` 没有残留旧 `PHASE*.md` 或 `thread-prompts/`。
- 把 queued program 的 roadmap 和 phase 文件迁入 `.agent/programs/` 后，才算 active。
- 每次新 program 都从 `PHASE01` 开始编号。
- 被替换或完成的 program 归档到 `docs/history/programs/`。
- 如果需要多线程执行，把本轮线程提示词放到 `.agent/programs/thread-prompts/`；下一轮提示词更新时默认替换或清理旧提示词，只有用户明确要求归档时才归档。

## 当前入口

- [current.md](current.md)：当前程序状态。
- [implementation-roadmap.md](implementation-roadmap.md)：无 active program 时的打开规则。
- [closure-checklist.md](closure-checklist.md)：通用收口清单。

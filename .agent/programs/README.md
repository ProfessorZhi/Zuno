# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。

## 当前状态

当前没有 active program。

`zuno-repo-layout-cleanup-v1` 已完成并归档到：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

`.agent/programs/` 当前只保留入口、状态、路线图和收口清单，不保留已完成 program 的 `PHASE*.md`。

## 等待打开的 Program

后续 program 仍是 queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

打开新 program 时必须从 `PHASE01` 开始，并先把 `.agent/programs/current.md`、`implementation-roadmap.md` 和相关 verifier/test 同步到新 active 状态。

## 打开新 Program 的规则

- 每次只打开一个 program。
- 新 program 从 `PHASE01` 开始编号。
- 被替换或完成的 program 归档到 `docs/history/programs/`。
- 如果需要多线程执行，把本轮线程提示词放到 `.agent/programs/thread-prompts/`；下一轮提示词更新时默认替换或清理旧提示词，只有用户明确要求归档时才归档。

## 当前入口

- [current.md](current.md)：当前程序状态。
- [implementation-roadmap.md](implementation-roadmap.md)：短期 program 队列和下一步打开规则。
- [closure-checklist.md](closure-checklist.md)：通用收口清单。

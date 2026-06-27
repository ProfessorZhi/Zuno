# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。

## 当前状态

当前没有 active program。`zuno-workflow-doc-system-v1` 和 `zuno-target-architecture-refresh-v1` 已完成并归档。

下一个候选 program 是：

```text
zuno-repo-layout-cleanup-v1
```

它仍然是 queued draft，位置是：

- `.agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/`

## 打开新 Program 的规则

- 每次只打开一个 program。
- 打开前确认当前 `.agent/programs/` 没有残留旧 `PHASE*.md`。
- 把 queued program 的 roadmap 和 phase 文件迁入 `.agent/programs/` 后，才算 active。
- 每次新 program 都从 `PHASE01` 开始编号。
- 被替换或完成的 program 归档到 `docs/history/programs/`。

## 当前入口

- [current.md](current.md)：当前无 active program 的状态面。
- [implementation-roadmap.md](implementation-roadmap.md)：下一 program 的打开规则和等待状态。
- [closure-checklist.md](closure-checklist.md)：通用收口清单。

# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。

## 当前状态

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

这是短期四目标中的 Program 3：仓库目录和 repo hygiene 收口。

已完成并归档：

- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

当前 phase 文件已平铺在 `.agent/programs/`：

```text
PHASE01_repo-layout-audit.md
PHASE02_root-docs-hygiene.md
PHASE03_backend-six-layer-migration-plan.md
PHASE04_small-boundary-cleanups.md
PHASE05_hygiene-verifier-closure.md
```

PHASE01 多线程提示词也平铺在 `.agent/programs/`，方便复制到对应 Codex 线程：

```text
THREAD_A_root-docs-agent-hygiene-prompt.md
THREAD_B_backend-six-layer-audit-prompt.md
THREAD_C_tools-tests-generated-artifacts-prompt.md
```

后续 queued programs 仍在：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

## 打开新 Program 的规则

- 每次只打开一个 program。
- 打开前确认当前 `.agent/programs/` 没有残留旧 `PHASE*.md`。
- 把 queued program 的 roadmap 和 phase 文件迁入 `.agent/programs/` 后，才算 active。
- 每次新 program 都从 `PHASE01` 开始编号。
- 被替换或完成的 program 归档到 `docs/history/programs/`。

## 当前入口

- [current.md](current.md)：当前 active program 和 phase 状态。
- [implementation-roadmap.md](implementation-roadmap.md)：Program 3 执行路线图。
- [closure-checklist.md](closure-checklist.md)：通用收口清单。

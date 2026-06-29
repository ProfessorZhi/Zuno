# Agent 执行计划

`.agent/programs/` 只存放当前可执行计划。

## 当前状态

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

Program 3 已根据用户反馈修正 Definition of Done：不仅要有目录计划和 guardrails，还要让 `src/backend` 在 VS Code / Explorer 里看起来清爽、必要、分门别类。

PHASE01-05 已归档为 Program 3 first slice：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

当前 continuation phase 文件平铺在 `.agent/programs/`：

```text
PHASE06_backend-directory-clarity-audit.md
PHASE07_fastapi-jwt-auth-compat-retirement-plan.md
PHASE08_backend-physical-cleanup-slices.md
```

## 打开新 Program 的规则

- 每次只打开一个 program。
- 新 program 从 `PHASE01` 开始编号。
- 同一 program 被用户明确要求修正定义并继续时，可以从已完成 phase 后继续编号。
- 被替换或完成的 program 归档到 `docs/history/programs/`。
- 如果需要多线程执行，把本轮线程提示词放到 `.agent/programs/thread-prompts/`；下一轮提示词更新时默认替换或清理旧提示词，只有用户明确要求归档时才归档。

## 当前入口

- [current.md](current.md)：当前程序状态。
- [implementation-roadmap.md](implementation-roadmap.md)：Program 3 continuation 路线图。
- [closure-checklist.md](closure-checklist.md)：通用收口清单。

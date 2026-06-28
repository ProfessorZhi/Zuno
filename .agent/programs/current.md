# 当前程序

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

## Program 3 目标

把整个仓库目录整理成必要、清晰、分门别类的结构。重点包括根目录必要入口、docs / `.agent` / tools / tests 边界、生成物和本地产物隔离，以及 `src/backend` 向目标六层结构靠拢。

## 当前 Phase

- `PHASE01_repo-layout-audit.md`：active / 当前打开，适合按 root/docs、backend layout、tools/tests/generated artifacts 三个线程并行审计。
- `PHASE02_root-docs-hygiene.md`：pending。
- `PHASE03_backend-six-layer-migration-plan.md`：pending。
- `PHASE04_small-boundary-cleanups.md`：pending。
- `PHASE05_hygiene-verifier-closure.md`：pending。

## 已清理的历史 Program

- `docs/history/programs/zuno-workflow-doc-system-v1/`
- `docs/history/programs/zuno-target-architecture-refresh-v1/`

Program 1 和 Program 2 不再作为 active 或 queued 计划出现，只作为历史完成事实保留。

## 后续队列

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

## 当前边界

- 不继续追加 Program 1 或 Program 2 的 phase。
- 不把 Program 4 或 Program 5 的 queued draft 当成 active program。
- 不实施 runtime、API、DB schema、frontend 或 eval baseline 修改。
- 不把目标架构能力写成 Current，除非代码和测试已经证明。

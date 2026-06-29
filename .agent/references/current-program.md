# 当前程序

当前可执行 Agent 程序目录是：

- `.agent/programs/`

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

## Program 3 当前定义

Program 3 已根据用户反馈修正 Definition of Done：

```text
目录本身要表达架构；文档只能解释边界，不能替目录背锅。
```

PHASE01-05 已完成并归档为 first slice，但 Program 3 继续执行 backend physical layout cleanup。

## 当前 Program Phase

- `PHASE06_backend-directory-clarity-audit.md`：first slice complete。
- `PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`：first slice complete，顶层 `fastapi_jwt_auth` shell 已退休。
- `PHASE08_backend-physical-cleanup-slices.md`：active，当前执行 backend physical layout migration；本轮由主线程挂机模式收口。

## 已完成 Program 3 first slice

- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_root-docs-hygiene.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_backend-six-layer-migration-plan.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_small-boundary-cleanups.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md`

## 等待打开的 program

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。

- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE06_backend-directory-clarity-audit.md`
- `.agent/programs/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`
- `.agent/programs/PHASE08_backend-physical-cleanup-slices.md`
- `.agent/programs/closure-checklist.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/README.md`

## 历史边界

之前的 Phase 0-6 closure、`zuno-architecture-surface-cleanup-v1`、`zuno-workflow-doc-system-v1` 和 `zuno-target-architecture-refresh-v1` 已完成，是历史事实。

Program 3 PHASE01-05 是 first slice 历史证据；不要把它们搬回 `.agent/programs/` 当前前台。Program 3 continuation 从 PHASE06 开始，当前执行点是 PHASE08。

不要把 V2 Target runtime 当作完全 Current，除非相关代码、测试和 trace evidence 已经证明。不要把 queued program 写成已经完成或已经 current。

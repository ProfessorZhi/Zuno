# 当前程序

当前可执行 Agent 程序目录是：

- `.agent/programs/`

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

当前 active phase：

- `.agent/programs/PHASE01_repo-layout-audit.md`

## 最近完成程序

- `zuno-workflow-doc-system-v1`：已完成本地文档系统、Agent 工作流、program 平铺规则、skill/template 边界和 verifier 防漂移收口，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
- `zuno-target-architecture-refresh-v1`：已完成目标架构升版文档收口，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。

Program 1 和 Program 2 只作为历史完成事实保留，不再进入 active 或 queued program。

## 当前 Program Phase

- `PHASE01_repo-layout-audit.md`：active。审计根目录、`src/backend/zuno`、`docs`、`.agent`、`tools`、`tests` 的杂乱点。
- `PHASE02_root-docs-hygiene.md`：pending。
- `PHASE03_backend-six-layer-migration-plan.md`：pending。
- `PHASE04_small-boundary-cleanups.md`：pending。
- `PHASE05_hygiene-verifier-closure.md`：pending。

## 等待打开的 program

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。打开其中任一 program 时，必须先完成或归档当前 active program，再把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 重新开始。

- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE01_repo-layout-audit.md`
- `.agent/programs/PHASE02_root-docs-hygiene.md`
- `.agent/programs/PHASE03_backend-six-layer-migration-plan.md`
- `.agent/programs/PHASE04_small-boundary-cleanups.md`
- `.agent/programs/PHASE05_hygiene-verifier-closure.md`
- `.agent/programs/closure-checklist.md`
- `.agent/architecture/future/programs/README.md`
- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md`
- `docs/architecture/roadmap.md`

## 历史边界

之前的 Phase 0-6 closure、`zuno-architecture-surface-cleanup-v1`、`zuno-workflow-doc-system-v1` 和 `zuno-target-architecture-refresh-v1` 已完成，是历史事实。不要把这些旧 phase 恢复到 `.agent/programs/` 当前前台；它们只属于 `docs/history/programs/`。

不要把 V2 Target runtime 当作完全 Current，除非相关代码、测试和 trace evidence 已经证明。不要把 queued program 写成已经完成或已经 current。

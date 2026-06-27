# 当前程序

当前可执行 Agent 程序目录是：

- `.agent/programs/`

当前没有 active program，也没有 active `PHASE*.md`。

## 最近完成程序

- `zuno-workflow-doc-system-v1`：已完成本地文档系统、Agent 工作流、program 平铺规则、skill/template 边界和 verifier 防漂移收口，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
- `zuno-target-architecture-refresh-v1`：已完成目标架构升版文档收口，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。

## 等待打开的 program

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。打开其中任一 program 时，必须先确认 `.agent/programs/` 没有旧 `PHASE*.md`，再把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 重新开始。

```text
Program 3：zuno-repo-layout-cleanup-v1
Program 4：zuno-runtime-architecture-upgrade-v1
Program 5：zuno-architecture-visuals-v1
```

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/architecture/future/programs/README.md`
- `.agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md`
- `docs/architecture/roadmap.md`

## 历史边界

之前的 Phase 0-6 closure、`zuno-architecture-surface-cleanup-v1`、`zuno-workflow-doc-system-v1` 和 `zuno-target-architecture-refresh-v1` 已完成，是历史事实。不要把这些旧 phase 恢复到 `.agent/programs/` 当前前台；它们只属于 `docs/history/programs/`。

不要把 V2 Target runtime 当作完全 Current，除非相关代码、测试和 trace evidence 已经证明。不要把 queued program 写成已经完成或已经 current。

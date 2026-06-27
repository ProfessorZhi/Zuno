# 无 Active Program

当前 `.agent/programs/` 处于等待状态，没有正在执行的 `PHASE*.md`。

## 已关闭

- `zuno-workflow-doc-system-v1`：已完成本地文档系统、Agent 工作流、program 平铺规则、skill/template 边界和 verifier 防漂移收口，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
- `zuno-target-architecture-refresh-v1`：已完成目标架构升版文档收口，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。

## 下一个候选

```text
zuno-repo-layout-cleanup-v1
```

候选源文件：

- `.agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/PHASE*.md`

## 打开规则

1. 确认 `.agent/programs/` 只有 `README.md`、`current.md`、`implementation-roadmap.md` 和 `closure-checklist.md`。
2. 把 queued program 的 roadmap 和 phase 文件迁入 `.agent/programs/`。
3. 每次新 program 都从 `PHASE01` 开始编号。
4. 更新 `docs/architecture/roadmap.md`、`.agent/references/current-program.md` 和相关 verifier/test。
5. 完成后归档到 `docs/history/programs/`。

## 仍在队列中

- Program 3：`zuno-repo-layout-cleanup-v1`
- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

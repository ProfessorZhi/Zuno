# 当前程序

当前没有 active program。

Program 3 `zuno-repo-layout-cleanup-v1` 已完成并归档到：

```text
docs/history/programs/zuno-repo-layout-cleanup-v1/
```

## 最近完成程序

- `zuno-workflow-doc-system-v1`：已完成本地文档系统、Agent 工作流、program 平铺规则、skill/template 边界和 verifier 防漂移收口，归档到 `docs/history/programs/zuno-workflow-doc-system-v1/`。
- `zuno-target-architecture-refresh-v1`：已完成目标架构升版文档收口，归档到 `docs/history/programs/zuno-target-architecture-refresh-v1/`。
- `zuno-repo-layout-cleanup-v1`：已完成仓库目录、root/docs hygiene、backend 六层迁移计划、小边界说明和 repo hygiene verifier 收口，归档到 `docs/history/programs/zuno-repo-layout-cleanup-v1/`。

## 等待打开的 program

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。打开其中任一 program 时，必须先确认 `.agent/programs/` 没有残留旧 `PHASE*.md`，再把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 重新开始。

- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/architecture/future/programs/README.md`
- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/README.md`

## 当前边界

- 不继续追加 Program 1、Program 2 或 Program 3 的 phase。
- 不把 Program 4 或 Program 5 的 queued draft 当成 active program。
- 不实施 runtime、API、DB schema、frontend 或 eval baseline 修改，除非用户明确打开对应 program。
- 不把目标架构能力写成 Current，除非代码和测试已经证明。

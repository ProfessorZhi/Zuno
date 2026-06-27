# 当前程序

当前可执行 Agent 程序是：

- `.agent/programs/`

当前 program 是 `zuno-workflow-doc-system-v1`。它是短期五个 program 的第一个，目标不是继续堆 runtime feature，而是先把本地文档系统、Agent 工作流、program 平铺规则、skill/template 边界和 verifier 防漂移机制收口。

## 为什么先做 Program 1

后续目标架构升版、文件夹整理、runtime 架构升级和架构 HTML 都会持续修改文档和边界。如果工作流不先自洽，后续每轮都会靠临时提示词推进，容易再次出现 active program 过长、phase 编号漂移、旧计划留在前台和 verifier 不同步。

## 当前执行顺序

```text
PHASE01：工作流与文档系统只读审计
PHASE02：Agent bootloader 与 routing 收口
PHASE03：Skill / Template / Program 系统收口
PHASE04：Workflow verifier 与漂移测试
PHASE05：Program closure 与 history 归档
```

## 后续 program 队列

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。打开其中任一 program 时，必须先归档当前 `.agent/programs/`，再把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 重新开始。

```text
Program 2：zuno-target-architecture-refresh-v1
Program 3：zuno-repo-layout-cleanup-v1
Program 4：zuno-runtime-architecture-upgrade-v1
Program 5：zuno-architecture-visuals-v1
```

## 最新完成程序

- `docs/history/programs/zuno-architecture-surface-cleanup-v1/`
- `docs/history/programs/zuno-target-architecture-migration-v1/`

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/PHASE01_workflow-doc-audit.md`
- `.agent/programs/PHASE02_agent-bootloader-routing.md`
- `.agent/programs/PHASE03_skill-template-program-system.md`
- `.agent/programs/PHASE04_workflow-verifiers-drift-tests.md`
- `.agent/programs/PHASE05_closure-history-archive.md`
- `.agent/programs/closure-checklist.md`
- `.agent/architecture/future/programs/README.md`
- `.agent/architecture/future/programs/zuno-target-architecture-refresh-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md`
- `docs/architecture/roadmap.md`

## 历史边界

之前的 Phase 0-6 closure 和 `zuno-architecture-surface-cleanup-v1` 已完成，是历史事实。不要把这些旧 phase 恢复到 `.agent/programs/` 当前前台；它们只属于 `docs/history/programs/`。

不要把 V2 Target runtime 当作完全 Current，除非相关代码、测试和 trace evidence 已经证明。不要把 queued program 写成已经完成或已经 current。

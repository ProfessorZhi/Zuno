# Zuno Repo Layout Cleanup V1
> 状态：active。当前平铺执行计划位于 `.agent/programs/`，从 `PHASE01` 开始。

Program ID：`zuno-repo-layout-cleanup-v1`

## 目标

按升版后的目标架构整理目录和边界，让仓库更清爽、更可读。

Program 3 的核心不是零散删文件，而是把整个仓库整理成“必要目录 + 清晰职责 + 可验证边界”。第一次看仓库的人应该能从目录直接读出：

```text
apps/       产品入口
src/        runtime 源码
tests/      测试
tools/      维护、verify、eval、render 工具
docs/       正式人类文档真相
examples/   可运行示例和示例数据
infra/      Docker、DB、部署基础设施
.agent/     本地 Agent Skill System
```

`src/backend` 是本轮重点：目标方向是让 `src/backend/zuno` 逐步靠近 `api / agent / memory / capability / knowledge / platform` 六层表达；`src/backend` 顶层不应该堆很多无解释目录。任何保留的额外目录都必须能说明职责、来源和验证方式。

## 当前边界

- Program 1 `zuno-workflow-doc-system-v1` 已完成并归档。
- Program 2 `zuno-target-architecture-refresh-v1` 已完成并归档。
- 每次新 program 都从 `PHASE01` 开始编号。
- 本 program 只处理目录、文档前台、repo hygiene 和迁移计划，不做 runtime 行为修改。
- 涉及 `src/backend/zuno` 时优先做审计、facade 计划和低风险边界清理，不做大搬家。
- `.codex/`、`.local/`、`.test-tmp/`、`node_modules/`、`reports/`、临时 `data/` 这类本地产物或生成物先审计 tracked/untracked 和 `.gitignore`，不能盲删。

后续 queued programs：

- `zuno-runtime-architecture-upgrade-v1`
- `zuno-architecture-visuals-v1`

## Phase

1. [PHASE01：Repo layout 审计](PHASE01_repo-layout-audit.md)
2. [PHASE02：根目录与 docs hygiene](PHASE02_root-docs-hygiene.md)
3. [PHASE03：后端六层迁移计划](PHASE03_backend-six-layer-migration-plan.md)
4. [PHASE04：小步边界清理](PHASE04_small-boundary-cleanups.md)
5. [PHASE05：Repo hygiene verifier closure](PHASE05_hygiene-verifier-closure.md)

## PHASE01 多线程提示词

- [Thread A：Root / Docs / Agent Hygiene](THREAD_A_root-docs-agent-hygiene-prompt.md)
- [Thread B：Backend / src Six-Layer Audit](THREAD_B_backend-six-layer-audit-prompt.md)
- [Thread C：Tools / Tests / Generated Artifacts](THREAD_C_tools-tests-generated-artifacts-prompt.md)

## 禁止范围

不做大搬家，不改 runtime 行为，不改 public API。

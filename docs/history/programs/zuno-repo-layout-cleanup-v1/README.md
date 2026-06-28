# Zuno Repo Layout Cleanup V1

> 状态：已完成并归档。此目录是历史证据，不是当前 active Agent 程序。

## Program 目标

Program 3 负责把仓库目录和边界从“能运行”继续收口到“必要、清晰、分门别类、可验证”。

重点包括：

- 根目录和 docs / `.agent` 前台说明收口。
- `src/backend/zuno` 向 `api / agent / memory / capability / knowledge / platform` 六层目标表达靠拢。
- 避免 runtime 大搬家，先形成 facade-first 迁移计划。
- 给六层目录补边界 README，帮助第一次读仓库的人理解当前与目标差距。
- 把 `.test-tmp/`、`.pytest_cache/`、`tmp/`、`output/`、`node_modules/`、`data/`、`reports/` 等生成物和本地产物规则机器化。
- 固定 `tools/`、`tests/`、`examples/`、`infra/` 的职责和允许子目录，避免继续变成杂物箱。

## 完成范围

- `PHASE01_repo-layout-audit.md`：完成三线程只读审计，形成 PHASE02 / PHASE03 / PHASE05 输入。
- `PHASE02_root-docs-hygiene.md`：完成 root/docs hygiene、目标模式模板瘦身和 data/reports 白名单语义。
- `PHASE03_backend-six-layer-migration-plan.md`：完成 `src/backend/zuno` 六层 facade-first 迁移计划，不改 runtime 行为。
- `PHASE04_small-boundary-cleanups.md`：新增六层目录 README 边界说明，不搬 Python runtime。
- `PHASE05_hygiene-verifier-closure.md`：把生成物、目录职责和 repo hygiene 规则接入 verifier / repo tests。

归档关键词：`backend 六层迁移计划`、`repo hygiene verifier`。

## 合并证据

- PHASE02 branch：`codex/program3-phase02-root-docs-hygiene`
- PHASE03 branch：`codex/program3-phase03-backend-six-layer-plan`
- PHASE04 branch：`codex/program3-phase04-small-boundary-cleanups`
- PHASE05 branch：`codex/program3-phase05-hygiene-verifier-closure`

## 归档边界

本 program 不代表 runtime 架构升级已经完成。它只完成目录、文档、边界说明、迁移计划和 repo hygiene guardrails。

后续 runtime 工作属于 queued program：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`

后续架构图和 HTML 展示工作属于 queued program：

- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

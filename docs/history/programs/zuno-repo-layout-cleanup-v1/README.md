# Zuno Repo Layout Cleanup V1

> 状态：completed / archived。PHASE01-09 和 Directory Surface Alignment V1 PHASE01-06 均已归档；此目录保存 Program 3 历史证据。

## Program 目标

Program 3 负责把仓库目录和边界从“能运行”继续收口到“必要、清晰、分门别类、可验证”。

重点包括：

- 根目录和 docs / `.agent` 前台说明收口。
- `src/backend/zuno` 向 `api / agent / memory / capability / knowledge / platform` 六层目标表达靠拢。
- 避免 runtime 大搬家，先形成 facade-first 迁移计划。
- 给六层目录补边界 README，帮助第一次读仓库的人理解当前与目标差距。
- 把 `.test-tmp/`、`.pytest_cache/`、`tmp/`、`output/`、`node_modules/`、`data/`、`reports/` 等生成物和本地产物规则机器化。
- 固定 `tools/`、`tests/`、`examples/`、`infra/` 的职责和允许子目录，避免继续变成杂物箱。
- 退休 `src/backend/fastapi_jwt_auth/` 顶层 compatibility shell。
- 把 resources / compatibility、MCP server implementation 和 HTTP middleware implementation 做真实物理收敛。
- 把只剩视觉噪音的 `mcp_servers/`、`middleware/`、`evals/` 顶层兼容壳退休为 `.py` alias module，让目录树更贴近目标架构。
- Directory Surface Alignment V1：把 `compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 等剩余旧顶层目录下沉到六层内部，让 `src/backend/zuno` 顶层目录只剩 `api / agent / memory / capability / knowledge / platform`。

## 已归档范围

- `PHASE01_repo-layout-audit.md`：完成三线程只读审计，形成 PHASE02 / PHASE03 / PHASE05 输入。
- `PHASE02_root-docs-hygiene.md`：完成 root/docs hygiene、目标模式模板瘦身和 data/reports 白名单语义。
- `PHASE03_backend-six-layer-migration-plan.md`：完成 `src/backend/zuno` 六层 facade-first 迁移计划，不改 runtime 行为。
- `PHASE04_small-boundary-cleanups.md`：新增六层目录 README 边界说明，不搬 Python runtime。
- `PHASE05_hygiene-verifier-closure.md`：把生成物、目录职责和 repo hygiene 规则接入 verifier / repo tests。
- `PHASE06_backend-directory-clarity-audit.md`：完成 backend 顶层目录清晰度审计，形成 backend physical cleanup 的处理表。
- `PHASE07_fastapi-jwt-auth-compat-retirement-plan.md`：退休 `src/backend/fastapi_jwt_auth/` 顶层 shell，改由 `zuno.compatibility.vendor.fastapi_jwt_auth` 承接。
- `PHASE08_backend-physical-cleanup-slices.md`：完成 resources / compatibility、MCP server implementation、HTTP middleware implementation 的物理迁移，并把仍保留旧目录纳入 README + verifier guard。
- `PHASE09_target-layout-visual-compat-shell-retirement.md`：把旧 `mcp_servers/`、`middleware/`、`evals/` 顶层兼容壳退休为 alias module，保留旧 import path，同时让 `src/backend/zuno` 目录树更贴目标架构。
- `PHASE01_directory-closure-master-plan.md`：重写 Program3 目录收口执行计划，明确最终只允许六层顶层目录。
- `PHASE02_platform-foundation-directory-migration.md`：下沉 `config/`、`database/`、`compatibility/` 到 `platform/`，保留旧 import alias。
- `PHASE03_schema-tools-resources-directory-migration.md`：下沉 `schema/`、`tools/`、`resources/` 到 `api/dto`、`capability/tools`、`platform/resources`。
- `PHASE04_services-thinning-directory-migration.md`：下沉 `services/` 到 `platform/services`，保留 `zuno.services.*` 兼容入口。
- `PHASE05_core-agent-runtime-directory-migration.md`：下沉 `core/` 到 `agent/core`，保留 `zuno.core.*` 兼容入口。
- `PHASE06_final-six-layer-guard-and-closure.md`：收紧 verifier、repo tests 和 docs，使六层目录完成态可机器检查。

归档关键词：`backend 六层迁移计划`、`repo hygiene verifier`、`capability/mcp/servers`、`platform/middleware`、`alias module`。

## Directory Surface Alignment V1

Program 3 已完成最终目录表层收口：

```text
src/backend/zuno/
├─ api/
├─ agent/
├─ memory/
├─ capability/
├─ knowledge/
└─ platform/
```

顶层文件只保留 `__init__.py`、`main.py` 和受控 alias module。旧 public import path 继续通过 `compatibility.py`、`config.py`、`core.py`、`database.py`、`evals.py`、`mcp_servers.py`、`middleware.py`、`resources.py`、`schema.py`、`services.py`、`settings.py`、`tools.py`、`utils.py` 兼容。

## 合并证据

- PHASE02 branch：`codex/program3-phase02-root-docs-hygiene`
- PHASE03 branch：`codex/program3-phase03-backend-six-layer-plan`
- PHASE04 branch：`codex/program3-phase04-small-boundary-cleanups`
- PHASE05 branch：`codex/program3-phase05-hygiene-verifier-closure`
- PHASE06-09 continuation：main thread hangup mode, final commits on `main`
- Directory Surface Alignment V1 PHASE01-06：main thread multi-agent mode, final commits on `main`

## 归档边界

本 program 不代表 runtime 架构升级已经完成。它完成目录、文档、边界说明、迁移计划、repo hygiene guardrails、低风险物理收敛和六层顶层目录完成态；`zuno.core.*`、`zuno.services.*`、`zuno.schema.*`、`zuno.tools.*`、`zuno.database.*` 等仍是 public compatibility surface，后续 runtime architecture upgrade 只能在 Program 4 中打开。

后续 runtime 工作属于 queued program：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`

后续架构图和 HTML 展示工作属于 queued program：

- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`

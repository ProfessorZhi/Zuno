# Agent Program 路线图

> 状态：Program 3 continuation active。每次新 program 都从 `PHASE01` 开始编号；Program 3 continuation 使用延续 phase 编号。

## 当前 Active

`zuno-repo-layout-cleanup-v1` 当前重新打开为 Directory Surface Alignment V1：

- active phases：`.agent/programs/PHASE01_directory-closure-master-plan.md` through `.agent/programs/PHASE06_final-six-layer-guard-and-closure.md`
- 历史归档：`docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 不能再写成“文件夹整理完成”。当前完成事实是：

- `src/backend/` 顶层只保留 `zuno/`。
- `src/backend/fastapi_jwt_auth/` 顶层 compatibility shell 已退休。
- `prompts/`、`fixtures/`、`system_skills/` 已迁入 `resources/`。
- `legacy/`、`vendor/` 已迁入 `compatibility/`。
- MCP server implementations 已迁入 `capability/mcp/servers/`，旧 `mcp_servers/` 顶层目录已退休为 `mcp_servers.py` alias module。
- HTTP middleware implementations 已迁入 `platform/middleware/`，旧 `middleware/` 顶层目录已退休为 `middleware.py` alias module。
- Eval tooling 仍在 `tools/evals/zuno/`，旧 `evals/` 顶层目录已退休为 `evals.py` alias module。
- `compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 等仍保留目录还不是目标完成态，PHASE01-06 负责分 PR 下沉、迁出、变薄和 final guard。

## Program 3 当前退出标准

Program 3 closure 不能只看六层目录是否出现。后续完成前至少要满足：

1. `src/backend/zuno` 顶层目录只剩 `api / agent / memory / capability / knowledge / platform`。
2. 顶层文件只允许 `__init__.py`、`main.py` 和受控 alias module。
3. `compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 不再作为顶层目录存在。
4. 旧路径如果必须保留，只能作为 compatibility facade 或 alias module，并且有 legacy import guard。
5. `verify_repo_structure.py` 在 final guard 阶段收紧为六层 allowlist。
6. docs / AGENTS / `.agent/references` 按六层指路，不把 Program 4 runtime upgrade 混进 Program 3。

## Program 3 PR 执行顺序

| PR | Phase | 交付 |
| --- | --- | --- |
| PR1 | PHASE01 | 重写执行计划、最终目录树和 guardrails |
| PR2 | PHASE02 | `config/`、`database/`、`compatibility/` 下沉到 `platform/` |
| PR3 | PHASE03 | `schema/`、`tools/`、`resources/` 收口 |
| PR4 | PHASE04 | `services/` 变薄，低风险模块迁入六层 |
| PR5 | PHASE05 | `core/` 变薄，Agent 主入口进入 `agent/` |
| PR6 | PHASE06 | final guard，顶层只允许六层目录并归档 Program3 |

## 等待打开的 Program

后续 program 仍是 queued draft / not active：

1. `zuno-runtime-architecture-upgrade-v1`
   - 位置：`.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
   - 目的：在 Program 3 已完成的目录边界上推进 runtime architecture slices。
   - 边界：不能把 Java、微服务、事件驱动 worker 或产品级多 Agent 模式写成近期实现。

2. `zuno-architecture-visuals-v1`
   - 位置：`.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
   - 目的：优化架构 HTML / Mermaid 展示面。
   - 边界：HTML 不能成为第二套架构真相。

## 打开下一 Program 的步骤

1. 确认用户目标和范围。
2. 更新 `.agent/programs/current.md` 和本文件为新的 active program。
3. 在 `.agent/programs/` 新建 `PHASE01_<name>.md`。
4. 同步 `AGENTS.md`、`.agent/references/current-program.md`、`docs/architecture/roadmap.md`、verifier 和 repo tests。
5. 按新 program 的实际修改范围运行最小有效验证。

## 禁止

- 禁止把 queued draft 当作 active program。
- 禁止在没有 `PHASE01` 的情况下开始新 program。
- 禁止把 Program 3 已完成事实改写成未完成。
- 禁止把 runtime architecture upgrade 或 architecture visuals 混回 Program 3。

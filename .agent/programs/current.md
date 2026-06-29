# 当前程序

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

模式：Program 3 continuation / Directory Surface Alignment V1。

当前 active phase：

- `.agent/programs/PHASE01_directory-closure-master-plan.md`

当前 active phase set：

- `PHASE01_directory-closure-master-plan.md`：Program3 总控计划 / PR1
- `PHASE02_platform-foundation-directory-migration.md`：platform 基础目录迁移 / PR2
- `PHASE03_schema-tools-resources-directory-migration.md`：schema、tools、resources 收口 / PR3
- `PHASE04_services-thinning-directory-migration.md`：services 变薄 / PR4
- `PHASE05_core-agent-runtime-directory-migration.md`：core 变薄 / PR5
- `PHASE06_final-six-layer-guard-and-closure.md`：六层 final guard / PR6

## 当前判断

Program 3 不能再写成“文件夹整理完成”。它已经完成六层 facade 起步、低风险资源/兼容目录物理收敛，以及 PHASE09 的视觉兼容壳退休；但 `compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 仍在顶层，目录结构还没有完全契合目标架构。

## 最新完成切片

最近完成并归档的 Program 3 切片：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

- MCP server implementations 已进入 `capability/mcp/servers/`。
- HTTP middleware implementations 已进入 `platform/middleware/`。
- PHASE09：旧 `mcp_servers/`、`middleware/`、`evals/` 顶层兼容壳已退休为 `.py` alias module。

## 当前 PHASE01 目标

- 重写 Program3 为 PHASE01-06 / PR1-PR6 执行计划。
- 最终退出标准固定为 `src/backend/zuno` 顶层只剩 `api / agent / memory / capability / knowledge / platform` 六层目录。
- `compatibility/`、`resources/`、`config/`、`database/`、`schema/`、`tools/`、`utils/`、`services/`、`core/` 必须下沉、迁出、变薄或退休。
- 保持 Program 4 queued / not active，不把 runtime architecture upgrade 混进 Program 3。

## 等待打开的 program

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。

- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `.agent/programs/PHASE01_directory-closure-master-plan.md`
- `.agent/programs/PHASE02_platform-foundation-directory-migration.md`
- `.agent/programs/PHASE03_schema-tools-resources-directory-migration.md`
- `.agent/programs/PHASE04_services-thinning-directory-migration.md`
- `.agent/programs/PHASE05_core-agent-runtime-directory-migration.md`
- `.agent/programs/PHASE06_final-six-layer-guard-and-closure.md`
- `.agent/references/zuno-repo-hygiene.md`
- `src/backend/zuno/DIRECTORY_MAP.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/README.md`

## 历史边界

之前的 Phase 0-6 closure、`zuno-architecture-surface-cleanup-v1`、`zuno-workflow-doc-system-v1`、`zuno-target-architecture-refresh-v1` 和 Program 3 PHASE01-09 是历史事实。

不要把 queued Program 4/5 写成 active、completed 或 Current。Program 3 completion 需要等目录地图、facade 补齐、低风险迁移和 verifier guardrails 收口后再判断。

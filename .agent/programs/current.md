# 当前程序

当前 active program：

```text
zuno-repo-layout-cleanup-v1
```

模式：Program 3 continuation / Directory Surface Alignment V1。

当前 active phase：

- `.agent/programs/PHASE10_directory-surface-map-and-guardrails.md`

## 当前判断

Program 3 不能再写成“文件夹整理完成”。它已经完成六层 facade 起步、低风险资源/兼容目录物理收敛，以及 PHASE09 的视觉兼容壳退休；但 `core/`、`services/`、`database/`、`schema/`、`tools/`、`utils/` 仍是当前 runtime 或 migration source，目录结构还没有完全契合目标架构。

## 最新完成切片

最近完成并归档的 Program 3 切片：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

- MCP server implementations 已进入 `capability/mcp/servers/`。
- HTTP middleware implementations 已进入 `platform/middleware/`。
- PHASE09：旧 `mcp_servers/`、`middleware/`、`evals/` 顶层兼容壳已退休为 `.py` alias module。

## 当前 PHASE10 目标

- 用 `src/backend/zuno/DIRECTORY_MAP.md` 固定一等目录的 `keep / migrate / facade / retire` 策略。
- 用 `.agent/references/zuno-repo-hygiene.md` 固定目录迁移 skill。
- 用 verifier/test 禁止新增未分类的一等 runtime 目录。
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
- `.agent/programs/PHASE10_directory-surface-map-and-guardrails.md`
- `.agent/references/zuno-repo-hygiene.md`
- `src/backend/zuno/DIRECTORY_MAP.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/README.md`

## 历史边界

之前的 Phase 0-6 closure、`zuno-architecture-surface-cleanup-v1`、`zuno-workflow-doc-system-v1`、`zuno-target-architecture-refresh-v1` 和 Program 3 PHASE01-09 是历史事实。

不要把 queued Program 4/5 写成 active、completed 或 Current。Program 3 completion 需要等目录地图、facade 补齐、低风险迁移和 verifier guardrails 收口后再判断。

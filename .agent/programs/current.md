# 当前程序

当前没有 active program。

## 最新完成

最近完成并归档的 program：

```text
zuno-repo-layout-cleanup-v1
```

归档位置：

- `docs/history/programs/zuno-repo-layout-cleanup-v1/`

Program 3 已完成 root/docs hygiene、repo hygiene guardrails、`src/backend` 顶层收口、`fastapi_jwt_auth` 顶层 shell 退休、resources / compatibility 物理收敛、MCP server implementations 迁入 `capability/mcp/servers/`、HTTP middleware implementations 迁入 `platform/middleware/`，并为仍保留的旧 runtime 顶层目录补齐 README 分类和 verifier guard。

## 等待打开的 program

后续 program 只作为 queued drafts 存放在 `.agent/architecture/future/programs/`，不能直接当作 active program 执行。

- Program 4：`zuno-runtime-architecture-upgrade-v1`
- Program 5：`zuno-architecture-visuals-v1`

## 当前参考文件

- `.agent/programs/README.md`
- `.agent/programs/current.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- `docs/architecture/roadmap.md`
- `docs/history/programs/zuno-repo-layout-cleanup-v1/README.md`

## 历史边界

之前的 Phase 0-6 closure、`zuno-architecture-surface-cleanup-v1`、`zuno-workflow-doc-system-v1`、`zuno-target-architecture-refresh-v1` 和 `zuno-repo-layout-cleanup-v1` 已完成，是历史事实。

不要把 queued program 写成 active、completed 或 Current。打开下一 program 时必须先建立新的 active phase 文件，并从 `PHASE01` 开始。

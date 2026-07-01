# PHASE11 Workspace Product API Frontend Sync

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE11_workspace-product-api-frontend-sync
status: pending

## 目标

把后端新增的 knowledge retrieval profile、planning summary、trace / eval / cost summary、artifact citation info 和 capability / skill snapshot 同步到 Workspace Product API 与前端 API types 的最小兼容层。

## 范围

- request contract 支持每个 knowledge space 的标准检索 / 深度检索。
- task snapshot 能返回 plan / reflection / replan / trace summary。
- artifact response 能返回 citation info。
- frontend API type 最小同步，避免 schema 漂移。
- 保持现有 `/workspace/file`、`/workspace/ingest` 和 task runtime compatibility。

## 目标架构拼接点

本 phase 拼到 Product Surface。用户看见的是 AgentChat、知识库选择、标准检索 / 深度检索、artifact、trace 和 feedback；后端实现细节不能泄露成复杂模式选择：

- Knowledge selection 传递 per-knowledge-space retrieval profile。
- Task snapshot 展示 plan / reflection / replan 摘要，而不是内部全部 trace。
- Artifact response 保留 citation refs。
- Feedback 能回到 eval / memory review。
- Frontend API type 与 backend DTO 保持最小一致。

本 phase 是目标架构的产品入口闭环，不负责 UI 大改，但必须保证 API 不漂移。

## 并行开发可行性

本 phase 由 Coordinator + Workstream H 处理，因为它触碰共享 API 和前端类型。

可并行：

- 后端 response schema test 与 frontend type sync 可分工。
- Artifact citation response 与 task trace summary 可分工。

不可并行：

- 多个 agent 同时改 workspace public API。
- 不经 Coordinator 改 `workspace_task_runtime.py`。
- 把 standard/deep 变成 basic/local/global/drift 下拉。

## 详细执行卡

- 输入依赖：PHASE02 API DTO contract、PHASE04 retrieval profile、PHASE09 planner summary、PHASE13 trace/eval summary target fields。
- 主要交付物：workspace API schema alignment、standard/deep request field、task snapshot plan/eval/trace summary、artifact citation fields、minimal frontend API type sync。
- 可并行工作包：backend schema tests、frontend API type update、compatibility docs 可拆；public response shape 由 Coordinator 统一审查。
- Coordinator 锁点：`src/backend/zuno/schema/workspace.py`、`workspace_task_runtime.py`、`apps/web/src/apis/workspace.ts`。
- 下游交接：PHASE12 使用同一 API path 做 E2E；PHASE14 文档记录产品层只暴露标准/深度检索；PHASE15 verifier 确保 entrypoint 不漂移。
- PR / commit 建议：`feat(api): expose knowledge retrieval profile and trace summaries` 与 `test(api): keep workspace runtime compatibility`。

## 禁止范围

- 不做大型 UI 改版。
- 不破坏现有 public API。
- 不把用户暴露给 basic / local / global / drift 技术模式。

## 验收闸门

- API response schema tests 通过。
- workspace task runtime compatibility tests 通过。
- frontend API type 或 existing frontend tests 通过。
- 标准检索 / 深度检索字段能进入后端 retrieval plan。

## 验证命令

```powershell
git diff --check
pytest -q tests/api/test_workspace_task_runtime.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
pytest -q tests/api -p no:cacheprovider
```

## 需要先读取

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/api/v1/workspace.py`
- `src/backend/zuno/api/dto/**`
- `apps/web/src/apis/workspace.ts`
- `tests/api/**`

## 需要修改的文件

- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `src/backend/zuno/api/v1/workspace.py`
- `src/backend/zuno/api/dto/**`
- `apps/web/src/apis/workspace.ts`
- `tests/api/**`

## 执行拆解

1. 写 API schema compatibility test。
2. 写 requested knowledge profile test。
3. 写 task trace summary response test。
4. 写 artifact citation info response test。
5. 最小同步 frontend API type。
6. 运行 existing API tests。

## 多 agent 分工

- Coordinator owner for shared API files。
- Workstream H executes scoped API/frontend changes under Coordinator review。
- Workstream F/B/G provide contract expectations。

## 需要返回的证据

- API request / response examples。
- compatibility tests。
- frontend type diff。
- no breaking change summary。

## 停止条件

- 需要 breaking public API change 且没有兼容策略。
- frontend sync 变成大规模 UI 改版。
- retrieval profile 被暴露成 basic/local/global/drift 技术选择。

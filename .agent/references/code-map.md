# 代码地图

## 当前 owner

- `src/backend/zuno/api/`：HTTP 路由、DTO、认证和 response envelope。
- `src/backend/zuno/api/services/product/`：Product Surface application services；
  `command_service.py` 拥有 Product command，`ingestion_service.py` 拥有文件与
  ingestion，`artifact_service.py` 拥有 artifact，`observability_service.py` 拥有
  projection query；`runtime_engine.py` 仅提供内部 mechanics，不是 HTTP owner。
- `src/backend/zuno/agent/`：当前 Agent control/runtime code；Target Owner 是 Agent Runtime，物理 Worker / Service 只有通过 Evidence Gate 才拆分，Multi-Agent profiles 不自动拆服务。
- `src/backend/zuno/capability/`：Capability / Skill 语义、选择和 Tool Runtime 请求。
- `src/backend/zuno/knowledge/`：Document ingestion、Index、GraphRAG、Evidence、Citation。
- `src/backend/zuno/memory/`：Memory 与 Context。
- `src/backend/zuno/platform/`：数据库、Security、Model Gateway、Observability、Storage、Queue。
- `apps/web/src/product/`：Product command、projection、action、artifact 和 stream client。
- `apps/web/src/apis/workspace.ts`：工作区配置/session API 与 Product ingestion client；不再声明 task runtime owner。
- `tools/scripts/`：repository、taxonomy、service-boundary 和当前 Lab verifier；旧 Red/Blue Protocol verifier 已从 active tree 移除，历史输出由 Git history 和 Round Archive 追溯。
- `docs/`：正式人类文档和当前证据。

## Product Runtime 调用链

```text
Web Product Client
  -> /api/v1/product/runtime-requests
  -> ProductService.submit_runtime_request
  -> durable Product command + outbox
  -> Agent Core owner
  -> Tool Runtime / Security / Infrastructure
  -> Product projection / stream / artifact / feedback
```

Product command 只有 `SUBMIT_USER_GOAL` 语义。不要新增 shadow、canary、rollback
或旧 `/workspace/task*` 入口来隐藏失败。

## 代码边界

- Route 只做输入校验、认证和 response mapping，不编排业务。
- Product Surface 不拥有 Plan、Step、Retry、Replan 或 Tool Effect。
- Agent Core 不反向依赖 API；模型只能提交 proposal。
- Tool Effect 必须经过 Capability、Security、Approval、Budget 和 Idempotency。
- 前端不得直接访问数据库或 provider；所有事实通过 Product/API projection 获取。
- 需要修改 runtime 时先读 `docs/architecture/architecture.md`、`docs/facts/`、ADR 和 `docs/evidence/`；不要把已归档的专题目录当作当前 Owner 文档。

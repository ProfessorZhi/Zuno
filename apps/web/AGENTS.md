# Zuno Web Agent 规则

修改 `apps/web` 前先读：

1. `docs/modules/01-product-surface.md`
2. `.agent/references/code-map.md`
3. `docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`
4. `.agent/references/workflow.md`

如果任务涉及前后端契约迁移、页面边界或仓库布局，还要读：

- `docs/architecture/architecture.html`
- `docs/status/production-readiness.md`

## Product Surface 规则

- 前端不是 AgentRun、Approval、Tool Effect、Evidence、Memory、Eval 或 Artifact 的事实源。
- API 字段变化必须同步后端 DTO、前端类型、Product Surface Contract 和契约测试。
- UI 必须消费 Product Projection / AuthorizedView，不直接拼接底层 Owner 对象。
- Retry、Approve、Deny、Cancel、Reconcile、Download 等按钮只能来自服务端 `AvailableAction`；不得根据状态字符串自行生成。
- HTTP 2xx、SSE close、Queue ACK 和本地 Store 状态不得显示为领域成功。
- `ProductDisplayStatus`、`ProjectionFreshness` 和 `ConnectionStatus` 必须分离。
- SSE 必须支持重复事件去重、断线恢复、Cursor 过期 Resync 和重新授权。
- Provisional Content 不是正式 Assistant Message；正式内容必须引用 Publication / RunOutcome Projection。
- 一个 Run 可以同时有多个 Interrupt；不得压缩成单一 `pendingToolApproval`。
- Tool Effect UNKNOWN 不显示普通 Retry，只显示 Owner 提供的受控恢复动作。
- Citation 内容、Artifact 下载和敏感 Admin View 必须独立授权。
- UI 不暴露 Raw Checkpoint、Prompt、隐藏思维链、Secret、Raw Tool Args、内部 Object URI 或迁移兼容字段。

## 交互与验证

- 视觉、交互和页面布局变化要先做隔离预览，预览产物放到 `.agent/local/previews/<task-id>/`。
- 需要给用户确认的 UI 变更必须提供桌面截图，必要时补移动端截图。
- 用户确认前，不要把视觉原型直接落到生产页面。
- 修改后运行 lint、build、受影响测试和 Product Surface Contract Test。
- 未运行浏览器 E2E、断线恢复、撤权、SSE Gap 和 UNKNOWN 故障测试时，不得声称产品流程完整。

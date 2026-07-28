# Goal04 PHASE10 Startup Audit

status: frozen-gap-list
phase: PHASE10 Web and Desktop Product Adaptation
branch: codex/goal04-phase10-product-adaptation
base_branch: main
base_sha: 1f864961fcdc9b7674c5bfb5ed304dbe4c352d67
audit_date: 2026-07-27
alembic_head: 20260727_41

## 启动检查

- `git fetch origin main` 已执行。
- `main` 与 `origin/main` 一致：`1f864961fcdc9b7674c5bfb5ed304dbe4c352d67`。
- 启动前工作区干净。
- Alembic 单一 head：`20260727_41`。
- 已读取 Product Surface 模块文档、Agent Core 模块文档、ADR 0003、Wave 1 Contract Registry、Production Readiness、PHASE10 Program、`.agent` workflow 和 Web 入口规则。

## Frozen Gap List

### P10-G01 Generated Product Contract 未实现

当前 Web 仍主要使用 `apps/web/src/apis/workspace.ts` 中手写 `WorkspaceTaskStatus`、`WorkspaceTaskLifecycleState`、`WorkspaceRuntimeSnapshot` 和 workspace API 类型。未发现 `apps/web/src/product/**` generated contract surface，也未发现 Web/Desktop 共享的 AgentDefinition、AgentDraft、AgentVersion、AgentPublication、AgentInstallation、AgentCatalogEntry、Problem Detail、AvailableAction 和 projection schema generated bundle。

### P10-G02 Product API Client 未成为默认前端入口

后端已有 `src/backend/zuno/api/v1/product.py` 与 `ProductService.submit_runtime_request`，但前端默认任务流仍调用 `/api/v1/workspace/simple/chat`、`/api/v1/workspace/task`、`/api/v1/workspace/task/{taskId}/events/stream`、`/api/v1/workspace/task/{taskId}/approve` 和旧 artifact/feedback endpoints。缺少 PHASE10 要求的 command/query/signal/download/feedback Product API client、Problem Detail 和 idempotency policy。

### P10-G03 Projection-first Pinia Store 未实现

`apps/web/src/store/` 当前只有 `user` 和 `agent_card`。未发现 Product projection-first normalized store、projection version、source watermark、gap/resync state、authorized view、available action token state、agent catalog/studio/install state 或 quality/artifact/citation normalized state。

### P10-G04 SSE Resume / Reauth / Dedup 未满足

前端使用 `fetchEventSource` 消费 workspace stream，但未发送 `Last-Event-ID`，事件 id 在部分路径使用 `crypto.randomUUID()`，无法证明 server cursor resume、dedup、cursor expired resync、workspace revoke reauthorization、ProjectionFreshness 与 ConnectionStatus 分离。

### P10-G05 多 Interrupt 与 AvailableAction UI 未实现

当前 API 类型仍包含 `pending_interrupt?: Record<string, any> | null` 和 approval request 字段；未证明一个 Run 的多个 Pending Interrupt、Approve/Deny/Cancel/Input/Reconcile 全部由服务端 `AvailableAction` 驱动，也未删除单一 pending approval 假设。

### P10-G06 Publication / Evidence / Artifact / Quality View 未切到正式 Product 语义

当前前端仍直接使用 task/artifact/citation/trace/eval workspace DTO 和 stream event 字段。未证明 Provisional Content 与正式 Publication 分离，Artifact 下载独立授权，Citation 内容授权，Quality Disclosure 区分 blocked / incomparable / unmeasured。

### P10-G07 Desktop Versioned Bridge 未实现

`apps/desktop` 仍是 `main.cjs`、`preload.cjs`、`bridge.cjs` 的轻量桌面壳。未发现 `apps/desktop/src/product/**` 或 versioned Product bridge contract、auth refresh、authorized delivery、offline/error smoke。

### P10-G08 Legacy UI Removal 未完成

生产前端仍包含旧 settings/pages/API surfaces 和 `workspace.ts/defaultPage.vue` 旧 Workspace loop。PHASE10 closure 前必须完成 shadow/canary/default-new/rollback 后删除旧 Store、旧 DTO、字符串状态推断和永久 compatibility 目录；当前只能作为 Gap，不是 completion evidence。

## 当前结论

PHASE10 已正式启动为 `in_progress`。本文冻结启动 Gap，并记录 P10-T01 的第一块实现进展；不证明 PHASE10 completed、quality proven 或 production ready。

## P10-T01 当前进展

已新增：

- `apps/web/src/product/contracts.ts`
- `apps/web/src/product/index.ts`
- `tests/frontend/test_phase10_product_contracts.py`

当前 contract surface 覆盖：

- AgentDefinition / AgentDraft / AgentVersion / AgentPublication / AgentInstallation / AgentCatalogEntry；
- ProductCommand / RuntimeRequest / CommandReceipt / ProductProjection / AvailableAction / ChannelDelivery；
- ProductProblemDetail；
- ProductDisplayStatus、ProjectionFreshness、ConnectionStatus；
- ProductStreamEvent；
- unknown enum fail-closed sentinel；
- frontend is not fact source sentinel；
- available actions are server-only sentinel。

仍未完成：

- 未从后端 schema 自动生成；
- 未与后端 `/api/v1/product` runtime request / stream fixture 做 round-trip；
- 未接入 Product API client；
- 未替换旧 Workspace DTO；
- 未覆盖 Desktop contract。

## P10-T02 当前进展

已新增：

- `apps/web/src/product/client.ts`

当前 Product API client 覆盖：

- `submitProductRuntimeRequest`：调用 `/api/v1/product/runtime-requests`，默认生成 `client_request_id`；
- `consumeProductAction`：调用 `/api/v1/product/actions/consume`，默认生成 `client_request_id`；
- `listProductStreamEvents`：查询 `/api/v1/product/stream-events`，支持 `Last-Event-ID`；
- `openProductProjectionStream`：消费 `/api/v1/product/stream`，发送 `Last-Event-ID`；
- `normalizeProductProblem`：把 transport / API 错误映射为 `ProductProblemDetail`；
- `shouldRetryProductTransportFailure`：显式禁止 Product command / action consume 自动重放，只允许非命令安全路径按 ProblemDetail retryable 策略处理。

仍未完成：

- 未替换旧 workspace API 默认页面调用；
- 未接入 Pinia projection store；
- 未覆盖下载和 feedback Product endpoint，因为后端 Product v1 当前尚未提供对应正式 endpoint；
- 未完成 401/403/409/410/429/5xx 真实后端 fixture round-trip；
- 未完成 Browser E2E。

## P10-T03 当前进展

已新增：

- `apps/web/src/product/store.ts`

当前 Projection-first Pinia store 覆盖：

- `useProductProjectionStore`：以 ProductProjection / ProductStreamEvent / AvailableAction 为输入，不读取 AgentRun、Approval、Effect 或 WorkspaceTask 状态；
- Projection metadata：`projectionVersion`、`sourceWatermark`、`freshness`、`gapDetected`、`resyncRequired`；
- SSE resume metadata：`lastEventId`、`lastSequenceNo`，仅持久化 cursor / watermark / projection version，不持久化授权视图；
- Connection 状态：`connectionStatus` 与 `ProjectionFreshness` 分离；
- Authorized view：AgentDefinition、AgentDraft、AgentVersion、AgentPublication、AgentInstallation、AgentCatalogEntry、AvailableAction、Interrupt、Artifact、Delivery、Quality；
- 多 Interrupt：支持 User Input、Approval、External Job、Security Review、Manual Reconciliation、Resource Available、Ingestion Completion；
- Gap / Resync / Revoke：gap 和 resync 标记驱动 `needsResync`，撤权事件清空授权视图；
- AvailableAction：Approve / Deny / Cancel / Input / Reconcile / Download / Resync 继续由服务端 action token 驱动。

仍未完成：

- 未替换旧 workspace store 和页面默认数据流；
- 未把 SSE client 与 store 连接为默认订阅；
- 未覆盖浏览器真实 E2E、Desktop smoke、shadow/canary/default-new/rollback；
- 未删除旧 DTO、旧状态字符串推断和永久兼容目录。

## P10-T04 当前进展

已新增：

- `apps/web/src/product/runtime.ts`

已接入：

- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`

当前 Product runtime adapter 覆盖：

- 页面 Agent runtime 提交前先调用 `submitWorkspacePayloadToProductRuntime`，把当前 workspace payload 转换为 Product `SUBMIT_USER_GOAL` command；
- Product command 明确携带 `client_request_id`、`runtime_request_ref`、`raw_intent_ref`、`tenant_id`、`workspace_id`、`conversation_id`、`active_agent_version_id`；
- Product receipt 转为前端投影并写入 `useProductProjectionStore`，页面不从 HTTP 2xx 或 receipt 推断领域成功；
- `connectProductRuntimeProjectionStream` 使用 store 中的 `lastEventId` 作为 `Last-Event-ID` resume cursor，并把 stream event 写入 `applyStreamEvent`；
- 401/403 清空授权视图并进入 `AUTH_REQUIRED`，Projection Gap 标记 `RESYNC_REQUIRED`；
- `consumeProductStoreAction` 只消费 store 中服务端下发的 `AvailableAction` token；
- `normalizeAvailableActionsFailClosed` 要求 action token 同时具备 `effective_security_epoch_ref` 和匹配的 `projection_version`，后端字段缺失时前端不会补假 action。

仍未完成：

- 旧 `createWorkspaceTaskAPI` 仍作为后续切流对象保留，当前不是 closure；
- 旧 `approveWorkspaceTaskAPI` 在 Product action token 缺失时仍作为 fallback，必须在后端 AvailableAction 完整投影后删除；
- 普通聊天路径仍使用 `workspaceSimpleChatStreamAPI`；
- Artifact download、feedback、Desktop bridge、Browser E2E、Desktop smoke、Build/Lint 仍未完成。

## P10-T05 当前进展

已更新：

- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/v1/product.py`
- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/memory/engine.py`
- `apps/web/src/product/client.ts`
- `apps/web/src/product/runtime.ts`

当前 Product API projection / action 契约闭环覆盖：

- `ProductProjectionResult` 增加 `redaction_decision_ref`，API runtime request receipt 直接返回服务端 projection 的 redaction decision；
- `ProductAvailableActionResult` 增加 `effective_security_epoch_ref` 和 `projection_version`，API runtime request receipt 返回完整 AvailableAction；
- `ProductProjectionEventRef` 增加 `redaction_decision_ref`，重复投影事件也能从数据库原始记录返回 redaction decision；
- Runtime request 默认 cancel action 从后端返回 `CANCEL`，与前端 `AvailableActionKind` 枚举保持一致；
- SSE heartbeat 返回完整 `ProductStreamEvent` 字段：`event_id`、`event_type`、`sequence_no`、`redaction_decision_ref`、`resync_required`；
- 前端 `ProductRuntimeRequestReceipt.projection.redaction_decision_ref` 改为必填，不再使用 `redaction:api-contract-missing` fallback。
- `MemoryEngine` 声明 `governed_context_runtime` slot，修复 Product / Workspace focused tests 触发 RuntimeDependencyFactory 时无法绑定 governed memory runtime 的根因。

仍未完成：

- 后端 Product v1 仍只提供 runtime request / action consume / stream，不含正式 artifact download、feedback、publication delivery endpoint；
- 默认页面仍保留旧 workspace task fallback；
- Browser E2E、Desktop smoke、Build/Lint 仍未完成。

P10-T05 验证：

```text
python -m pytest -q tests\frontend\test_phase10_product_contracts.py -p no:cacheprovider
8 passed
```

```text
python -m pytest -q tests\api\test_goal03_product_route.py -p no:cacheprovider
6 passed, 1 warning
```

```text
python -m pytest -q tests\integration\test_goal03_wave_a_persistence.py::test_phase09_product_service_bootstraps_legacy_runtime_agent_version -p no:cacheprovider
first run failure fingerprint:
command: python -m pytest -q tests\integration\test_goal03_wave_a_persistence.py::test_phase09_product_service_bootstraps_legacy_runtime_agent_version -p no:cacheprovider
test: test_phase09_product_service_bootstraps_legacy_runtime_agent_version
exception: AttributeError: 'ProductProjectionEventRef' object has no attribute 'redaction_decision_ref'
first relevant stack frame: src\backend\zuno\api\services\product\command_service.py:197
recovery: ProductProjectionEventRef 增加 redaction_decision_ref，并从 duplicate 查询返回该字段
targeted rerun: 1 passed
```

```text
python -m pytest -q tests\api\test_completion_unified_runtime.py -p no:cacheprovider
first run failure fingerprint:
test examples: test_completion_route_streams_unified_runtime_events; test_completion_route_forwards_explicit_cutover_mode
exception: AttributeError: 'MemoryEngine' object has no attribute 'governed_context_runtime'
first relevant stack frame: src\backend\zuno\agent\runtime\factory.py:82
recovery: MemoryEngine 声明 governed_context_runtime slot
targeted rerun: 5 passed
```

```text
python -m pytest -q tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_fails_closed_when_product_runtime_record_fails tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_canaries_phase08_cutover_from_product_entry tests\api\test_workspace_runtime_recovery.py::test_workspace_task_snapshot_and_stream_include_unified_runtime -p no:cacheprovider
first run failure fingerprint:
exception: AttributeError: 'MemoryEngine' object has no attribute 'governed_context_runtime'
first relevant stack frame: src\backend\zuno\agent\runtime\factory.py:82
targeted rerun: 3 passed
```

```text
command: python -m pytest -q tests\api\test_goal03_product_route.py tests\api\test_completion_unified_runtime.py tests\api\test_workspace_task_runtime.py tests\api\test_workspace_runtime_recovery.py tests\integration\test_goal03_wave_a_persistence.py::test_phase09_product_service_bootstraps_legacy_runtime_agent_version -p no:cacheprovider
exception: command timed out
first relevant stack frame: n/a; no output returned before timeout
environment signature: Windows PowerShell; pytest mixed API suite exceeded 124 seconds
retry_count: 0
recovery: 未重复同一大命令，改为按 Product route / service / targeted runtime tests 分组验证。
```

## P10-T06 当前进展

已更新：

- `src/backend/zuno/api/v1/product.py`
- `apps/web/src/product/client.ts`
- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`

当前 Product Artifact / Feedback 前台入口覆盖：

- 新增 `GET /api/v1/product/artifacts/{artifact_id}`，通过 Product v1 入口读取 artifact，并复用现有 `WorkspaceTaskRuntimeService.get_artifact` 的 artifact read 与 citation 授权检查；
- 新增 `GET /api/v1/product/artifacts/{artifact_id}/download`，通过 Product v1 入口下载 artifact，并复用现有 artifact download 再授权和 `Cache-Control: no-store`；
- 新增 `POST /api/v1/product/feedback`，通过 Product v1 入口记录用户反馈；
- `apps/web/src/product/client.ts` 新增 `getProductArtifact`、`downloadProductArtifact`、`submitProductFeedback`；
- 默认 workspace agent 页面读取 artifact、下载 artifact 和提交反馈时改走 Product API，不再直接调用 `getWorkspaceArtifactAPI`、`downloadWorkspaceArtifactAPI` 或 `createWorkspaceFeedbackAPI`。

仍未完成：

- Product artifact / feedback endpoint 当前底层复用 WorkspaceTaskRuntimeService，尚未完成最终 Publication / Delivery 独立领域模型切流；
- 旧 `apps/web/src/apis/workspace.ts` 仍保留 workspace artifact / feedback API 定义，等待 shadow/canary/default-new/rollback 后删除；
- Citation 专门 Product endpoint、Quality disclosure UI、Desktop bridge、Browser E2E、Desktop smoke、Build/Lint 仍未完成。

P10-T06 验证：

```text
python -m pytest -q tests\api\test_goal03_product_route.py -p no:cacheprovider
8 passed, 1 warning
```

```text
python -m pytest -q tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -p no:cacheprovider
14 passed
```

```text
git diff --check
无 whitespace error；仅 CRLF warning
```

## P10-T07 当前进展

已更新：

- `apps/desktop/preload.cjs`
- `apps/desktop/README.md`
- `apps/web/src/utils/api.ts`

当前 Desktop Versioned Product Bridge 覆盖：

- `window.__ZUNO_DESKTOP__` 新增 `productBridgeVersion = product-desktop-bridge-v1.phase10`；
- `productBridgeCapabilities` 明确声明 runtime request、action consume、projection stream、Last-Event-ID resume、dedup、reauthorization、artifact read/download 和 feedback；
- `productEndpoints` 明确声明 Product v1 runtime request、action consume、stream events、stream、artifact read/download 和 feedback endpoint；
- `productBridgeHealth` 暴露本地 bridge URL、token、workspace root 是否注入；
- Web 侧 `DesktopConfig` 增加 Product bridge 类型字段，并新增 `getDesktopProductBridge` 读取 versioned bridge。

仍未完成：

- 尚未运行 Electron Desktop smoke；
- 桌面本地 bridge `/execute` 仍是文件/命令 helper，不是 Product runtime 的独立离线 delivery engine；
- Desktop artifact/offline/error smoke、Build/Lint、Browser E2E 仍未完成。

P10-T07 验证：

```text
python -m pytest -q tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -p no:cacheprovider
16 passed
```

```text
git diff --check
无 whitespace error；仅 CRLF warning
```

## P10-T08 当前进展

已更新：

- `src/backend/zuno/api/v1/product.py`
- `apps/web/src/product/store.ts`
- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`

当前 Product Citation / Quality / Blocked disclosure 覆盖：

- `GET /api/v1/product/artifacts/{artifact_id}` 返回 `product_artifact`，包含 artifact ref、publication ref、projection version、downloadable、授权 citation refs、citation count、citation authorization 和 download policy；
- `GET /api/v1/product/artifacts/{artifact_id}` 返回 `product_quality`，包含 quality ref、projection version、`RUNTIME_OBSERVED` / `UNMEASURED` 状态、blocked reason、metrics 和 disclosure；
- `ProductArtifactProjection` 增加 citation count、citation authorization 和 download policy；
- `ProductQualityProjection` 增加 metrics 和 disclosure；
- 默认 workspace agent 页面读取 Product artifact 时把 `product_artifact` / `product_quality` 写入 Product store，并展示服务端返回的 quality disclosure 和授权 citation refs。

仍未完成：

- Quality disclosure 仍来自 Product artifact endpoint 的 runtime observed wrapper，尚未完成 PHASE19 Final Gate / Publication 独立质量判定；
- Blocked view 的失败态仍主要来自 runtime failure / security gate，不是最终 Publication blocking model；
- Browser E2E、Desktop smoke、Build/Lint、旧 workspace task/simple-chat 删除仍未完成。

P10-T08 验证：

```text
python -m pytest -q tests\api\test_goal03_product_route.py -p no:cacheprovider
8 passed, 1 warning
```

```text
python -m pytest -q tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -p no:cacheprovider
16 passed
```

```text
git diff --check
无 whitespace error；仅 CRLF warning
```

## P10-T09 当前进展

已更新：

- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`
- `tests/frontend/test_phase10_product_contracts.py`
- `tests/frontend/test_frontend_workspace_features.py`

当前 Product 默认路径切流覆盖：

- 默认 workspace Agent 模式不再调用 `createWorkspaceTaskAPI(payload)` 创建旧 workspace task；
- 默认 workspace Agent 模式不再调用 `workspaceTaskEventsStreamAPI` 读取旧 task SSE；
- 默认 workspace Agent 模式不再通过 `approveWorkspaceTaskAPI` 作为审批 fallback；
- Product runtime command receipt 现在直接写入页面执行事件，默认后续同步由 Product projection SSE 驱动；
- 多个服务器 `AvailableAction` 通过 `productProjectionStore.sortedAvailableActions` 渲染为 Product Actions 列表，由 `submitProductAvailableAction` 消费；
- 旧 tool approval panel 缺少匹配 Product `AvailableAction` token 时 fail closed，不再绕回旧 approval endpoint。

仍未完成：

- 非 Agent 普通聊天仍使用 `/api/v1/workspace/simple/chat`，尚未完成 Product runtime 默认化；
- `apps/web/src/apis/workspace.ts` 中旧 task、approval、artifact DTO/API 定义仍作为迁移期文件存在，尚未完成最终删除；
- Product stream event 当前仍只暴露投影 cursor/freshness，不足以证明 artifact、citation、failure、multi interrupt 的 Browser E2E；
- Browser E2E、Desktop smoke、Build/Lint、shadow/canary/default-new/rollback closure gate 仍未完成。

P10-T09 验证：

```text
python -m pytest -q tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -p no:cacheprovider
16 passed
```

## P10-T10 当前进展

已更新：

- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/services/product/__init__.py`
- `src/backend/zuno/api/v1/product.py`
- `apps/web/src/product/contracts.ts`
- `apps/web/src/product/client.ts`
- `tests/api/test_goal03_product_route.py`
- `tests/frontend/test_phase10_product_contracts.py`

当前 Agent Studio / Catalog / 发布 / 安装 / 撤销 Product surface 覆盖：

- Product repository 复用已迁移的 `product_agent_definitions`、`product_agent_versions`、`product_agent_drafts`、`product_agent_publications`、`product_agent_installations`、`product_agent_catalog_entries` 表，不新增临时表；
- `ProductService.create_agent_draft` 通过 Product UoW 创建 AgentDefinition 和 AgentDraft；
- `ProductService.publish_agent_version` 通过 Product UoW 创建 AgentVersion、AgentPublication，并 upsert AgentCatalogEntry；
- `ProductService.install_agent_version` 通过 Product UoW 创建 AgentInstallation；
- `ProductService.revoke_agent_installation` / `revoke_agent_publication` 通过 Product UoW 把安装、发布和对应 catalog entry 转为 REVOKED；
- `/api/v1/product/agent-drafts`、`/agent-publications`、`/agent-installations`、`/agent-catalog` 暴露 Product API surface；
- Web Product client 增加 `createProductAgentDraft`、`publishProductAgentVersion`、`installProductAgentVersion`、`revokeProductAgentInstallation`、`revokeProductAgentPublication`、`listProductAgentCatalog`；
- Web Product contract 扩展 AgentDefinition / AgentDraft / AgentPublication 状态，使前端可以表达数据库迁移允许的 DRAFT、LOCKED、REVOKED、SUPERSEDED 状态。

仍未完成：

- 尚未完成 Agent Studio 可视化编辑 UI、Catalog 管理 UI 和 Browser E2E；
- Agent publish/install/revoke 目前是 Product API/client surface，尚未接默认设置页或 Agent 管理页；
- Publication/Delivery 独立模型仍未完成，PHASE19 Final Gate 前不得把 AgentPublication 当最终回答 Publication；
- Build/Lint、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成。

P10-T10 验证：

```text
python -m pytest -q tests\api\test_goal03_product_route.py tests\frontend\test_phase10_product_contracts.py -p no:cacheprovider
19 passed, 1 warning
```

```text
python -m pytest -q tests\integration\test_goal03_wave_a_persistence.py::test_phase09_product_agent_assets_publish_install_and_catalog -p no:cacheprovider
1 passed
```

## P10-T11 当前进展

已更新：

- `apps/web/src/pages/agent/agent-editor.vue`
- `apps/web/src/pages/agent/agent.vue`
- `tests/frontend/test_phase10_product_contracts.py`

当前 Agent Studio / Catalog UI 接线覆盖：

- Agent Editor 在旧 Agent API 保存成功后，同步调用 Product `createProductAgentDraft`、`publishProductAgentVersion`、`installProductAgentVersion`；
- Product draft、publication、catalog entry、installation 返回值写入 `useProductProjectionStore`，前端仍不成为 AgentDefinition、Publication 或 Installation 的事实源；
- Agent 列表页调用 `listProductAgentCatalog` 读取服务器 Product Catalog；
- Agent 列表页展示 Product Catalog entries，并通过 `installProductAgentVersion` / `revokeProductAgentInstallation` 提供安装和撤销入口；
- 本轮 UI 接线复用 `workspace:agent-studio:web` 作为 Web Agent Studio Product workspace，不新增后端表或临时本地 catalog。

仍未完成：

- Agent Editor 仍保留旧 Agent API 保存路径作为迁移期双路径，尚未完成 default-new / rollback / 删除门；
- Product Agent Studio / Catalog 尚未完成 Browser E2E；
- Catalog UI 目前覆盖安装和撤销安装，发布撤销 route/client 已存在但未接入可视化撤销发布入口；
- 非 Agent simple-chat、旧 workspace API/DTO 删除、Build/Lint、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成。

P10-T11 验证：

```text
python -m pytest -q tests\frontend\test_phase10_product_contracts.py -p no:cacheprovider
10 passed
```

## P10-T12 当前进展

已更新：

- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/v1/product.py`
- `apps/web/src/product/contracts.ts`
- `apps/web/src/pages/agent/agent.vue`
- `tests/api/test_goal03_product_route.py`
- `tests/frontend/test_phase10_product_contracts.py`

当前 Product Catalog 发布撤销接线覆盖：

- Product repository 的 `list_catalog_entries` 通过 catalog latest version 关联 `product_agent_publications`，返回 `publication_id`；
- Product service / route / frontend contract 将 catalog projection 扩展为 `publication_ref`；
- Agent Catalog UI 在 Product Catalog entry 上显示“下架”动作，调用 `revokeProductAgentPublication`；
- 撤销发布返回的 `agent_publication` 写入 Product projection store，随后刷新 Product Catalog；
- route tests 覆盖 catalog entry 的 `publication_ref`，frontend static tests 覆盖下架 UI、client 调用和 store upsert。

仍未完成：

- Product Catalog 发布撤销尚未由 Browser E2E 证明；
- Agent Studio 仍保留旧 Agent API 双路径；
- 非 Agent simple-chat、旧 workspace API/DTO 删除、Build/Lint、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成。

P10-T12 验证：

```text
python -m pytest -q tests\api\test_goal03_product_route.py tests\frontend\test_phase10_product_contracts.py tests\integration\test_goal03_wave_a_persistence.py::test_phase09_product_agent_assets_publish_install_and_catalog -p no:cacheprovider
21 passed, 1 warning
```

## P10-T13 当前进展

已更新：

- `tools/scripts/run-full-e2e-smoke.ps1`
- `tests/tools/test_launcher_scripts.py`
- `package-lock.json`

当前验证环境恢复与 Browser E2E smoke helper 覆盖：

- 通过 `npm install` 恢复 root workspace dependencies，使 Web `vue-tsc` 和 Vite build 能从 workspace `node_modules` 正常解析；
- `npm run lint -w zuno-frontend` 通过；
- `npm run build -w zuno-frontend` 通过；
- 修正 `run-full-e2e-smoke.ps1` 的 repo root 解析：`$PSScriptRoot` 位于 `tools/scripts`，repo root 必须上溯两级，否则 auth、frontend、tmp log 和 QA API 路径都会错误落到 `tools/**`；
- 新增 `tests/tools/test_launcher_scripts.py::test_full_e2e_smoke_script_resolves_repository_root_not_tools_root`，防止 Browser E2E smoke helper 再把 `tools/` 当仓库根。

仍未完成：

- Browser E2E smoke 现在能定位正确 repo root，但当前环境缺少 `tmp-qa-playwright/auth.json`，无法继续到 backend/frontend/QA API/E2E 流程；
- Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成。

P10-T13 验证：

```text
npm install
added 310 packages, audited 313 packages; 8 npm audit vulnerabilities reported by npm dependency audit,未作为 PHASE10 功能 Gate 处理。
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures.
```

```text
python -m pytest tests\tools\test_launcher_scripts.py::test_full_e2e_smoke_script_resolves_repository_root_not_tools_root -q
1 passed
```

Browser E2E smoke failure fingerprint after helper fix：

```text
command: powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
exception: Missing auth state: F:\internship-work\resume&resume project\02_projects\Zuno\tmp-qa-playwright\auth.json
first relevant stack frame: tools\scripts\run-full-e2e-smoke.ps1:44
environment signature: Node.js v24.14.0; npm workspace dependencies installed; repo-root path resolved correctly; tmp-qa-playwright/auth.json absent
retry_count: 1 after script root fix
唯一恢复动作: 在本机浏览器完成登录并导出 Playwright storage state 到 `tmp-qa-playwright\auth.json` 后，从 browser E2E smoke 命令继续。
```

## P10-T14 当前进展

已更新：

- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`
- `tests/frontend/test_frontend_workspace_features.py`

当前非 Agent 普通聊天默认路径切流覆盖：

- 默认 workspace 页面不再导入或调用 `workspaceSimpleChatStreamAPI`；
- 非 Agent 普通聊天现在同样调用 `submitWorkspacePayloadToProductRuntime`，提交 Product `SUBMIT_USER_GOAL` command；
- 非 Agent 普通聊天打开 Product projection SSE，复用 `connectProductRuntimeProjectionStream`、Projection Version、Watermark、Gap / Resync 和重新授权问题处理；
- 前端只显示 Product command / projection 受控状态，不把旧 `/api/v1/workspace/simple/chat` SSE chunk 冒充为正式 Publication；
- 新增静态回归 `test_workspace_default_chat_uses_product_runtime_not_simple_chat_stream`，防止默认 workspace 页面回退到旧 simple-chat stream。

仍未完成：

- `/api/v1/workspace/simple/chat` API 定义仍在 `apps/web/src/apis/workspace.ts` 保留，等待 shadow/canary/default-new/rollback 和最终删除门；
- Browser E2E、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

P10-T14 验证：

```text
python -m pytest tests\frontend\test_frontend_workspace_features.py::test_workspace_default_chat_uses_product_runtime_not_simple_chat_stream tests\frontend\test_frontend_workspace_features.py::test_workspace_agent_mode_uses_product_runtime_projection_loop -q
2 passed
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

```text
python -m pytest tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -q
18 passed
```

## P10-T15 当前进展

已更新：

- `apps/web/src/apis/workspace.ts`
- `tests/frontend/test_workspace_product_loop_types.py`
- `tests/frontend/test_frontend_workspace_features.py`

当前旧 Workspace API / DTO 前端边界删除覆盖：

- `apps/web/src/apis/workspace.ts` 不再导出 `workspaceSimpleChatStreamAPI`；
- `apps/web/src/apis/workspace.ts` 不再导出旧 workspace task command/query/stream/approval/cancel API：`createWorkspaceTaskAPI`、`getWorkspaceTaskAPI`、`getWorkspaceTaskEventsAPI`、`workspaceTaskEventsStreamAPI`、`approveWorkspaceTaskAPI`、`cancelWorkspaceTaskAPI`；
- `apps/web/src/apis/workspace.ts` 不再导出旧 artifact / feedback API：`getWorkspaceArtifactAPI`、`downloadWorkspaceArtifactAPI`、`createWorkspaceFeedbackAPI`；
- 移除这些旧 stream 函数后，`workspace.ts` 不再依赖 `fetchEventSource` 或 `apiUrl`；
- 前端测试从“旧 API 必须存在”改为“旧 API 不得暴露”，同时保留当前仍使用的 Product runtime、Workspace file/ingest 和 task lifecycle contract。

仍未完成：

- 后端旧 workspace route 仍存在，等待 shadow/canary/default-new/rollback 和后端删除门；
- Browser E2E、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

P10-T15 验证：

```text
python -m pytest tests\frontend\test_workspace_product_loop_types.py tests\frontend\test_frontend_workspace_features.py tests\frontend\test_phase10_product_contracts.py -q
22 passed
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

## P10-T16 当前进展

已更新：

- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/v1/product.py`
- `apps/web/src/product/contracts.ts`
- `apps/web/src/pages/agent/agent-editor.vue`
- `tests/api/test_goal03_product_route.py`
- `tests/frontend/test_phase10_product_contracts.py`

当前 Agent Studio default-new / Product Catalog metadata 覆盖：

- Product Catalog repository 读取时 join `product_agent_definitions`，返回 `agent_definition_id`、`display_name`、`description`、`definition_status`；
- ProductService 和 Product API payload 暴露上述 catalog display metadata，前端不需要再为了展示 catalog 卡片读取旧 Agent 事实；
- Web Product contract `AgentCatalogEntry` 增加 catalog display metadata 字段；
- Agent Editor 保存动作不再调用旧 `createAgentAPI` / `updateAgentAPI`，改为直接创建 Product AgentDraft、发布 AgentVersion、安装 AgentInstallation，并写入 Product projection store；
- 前端静态测试新增负断言，防止 Agent Editor 保存路径回退到旧 Agent create/update API。

仍未完成：

- Agent 列表页仍保留旧 Agent list/search/delete 和编辑加载路径，等待 Product Catalog default-new / rollback 后继续删除；
- Browser E2E、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

P10-T16 验证：

```text
python -m pytest tests\api\test_goal03_product_route.py::test_goal03_product_agent_studio_catalog_routes_use_product_service tests\frontend\test_phase10_product_contracts.py -q
11 passed, 1 warning
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

```text
python -m py_compile src\backend\zuno\platform\database\product\domain.py src\backend\zuno\api\services\product\command_service.py src\backend\zuno\api\v1\product.py
passed
```

## P10-T17 当前进展

已更新：

- `apps/web/src/pages/agent/agent.vue`
- `tests/frontend/test_phase10_product_contracts.py`

当前 Agent Catalog default-new 列表页覆盖：

- Agent 列表页展示事实源改为 `listProductAgentCatalog` 返回的 Product Catalog projection，不再读取旧 Agent list API；
- 搜索改为基于当前 Product Catalog projection 的本地过滤，不再调用旧 Agent search API；
- 列表卡片下架动作改为 `revokeProductAgentPublication`，以 `publication_ref` 作为 Product publication 事实引用，不再调用旧 Agent delete API；
- Product projection store 继续接收 catalog entry、installation、publication receipt，前端不成为 Publication 事实源；
- 前端静态测试新增负断言，防止 Agent 列表页回退到旧 `getAgentsAPI`、`searchAgentsAPI`、`deleteAgentAPI`。

仍未完成：

- Agent Editor 编辑加载路径仍保留旧只读迁移入口，等待 Product draft/version configuration query 后切流；
- Browser E2E、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

P10-T17 验证：

```text
python -m pytest tests\frontend\test_phase10_product_contracts.py::test_phase10_agent_studio_and_catalog_ui_use_product_surface -q
1 passed
```

```text
python -m pytest tests\frontend\test_phase10_product_contracts.py -q
10 passed
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

## P10-T18 当前进展

已更新：

- `infra/db/alembic/versions/20260727_42_goal04_product_agent_editor_payloads.py`
- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/platform/database/product/__init__.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/api/services/product/__init__.py`
- `src/backend/zuno/api/v1/product.py`
- `apps/web/src/product/client.ts`
- `apps/web/src/pages/agent/agent-editor.vue`
- `tests/api/test_goal03_product_route.py`
- `tests/frontend/test_phase10_product_contracts.py`
- `tests/repo/test_goal03_wave_a_migration_contract.py`

当前 Agent Studio 编辑加载闭环覆盖：

- Product AgentDraft 和 AgentVersion 现在把可恢复的 JSON payload 一并落库，不再只有 hash；
- Product repository 提供 `get_agent_definition`、`get_latest_agent_draft`、`get_latest_agent_version` 读取能力；
- Product Service 新增 `load_agent_studio_snapshot`，返回 definition / draft / version / catalog / configuration 快照；
- Product API 新增 `GET /api/v1/product/agent-studio/{agent_definition_id}`，前端编辑页用它恢复表单；
- Agent Editor 删除旧 `getAgentByIdAPI`，改为只读 Product snapshot 后填充表单；
- 迁移合同测试新增对 20260727_42 migration 的校验，避免配置 payload 列被后续改掉。

仍未完成：

- Product AgentEditor 对旧无 payload 记录的兼容回填仍是弱的，现阶段只能靠新写入的数据恢复；
- Browser E2E、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

P10-T18 验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_agent_studio_snapshot_route_uses_product_service tests\\repo\\test_goal03_wave_a_migration_contract.py::test_goal04_product_agent_editor_payload_migration_adds_json_snapshots -q
2 passed
```

```text
python -m pytest tests\\frontend\\test_phase10_product_contracts.py::test_phase10_agent_studio_and_catalog_ui_use_product_surface -q
1 passed
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

## P10-T19 当前进展

已更新：

- `apps/web/src/pages/workspace/workspace.vue`
- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`
- `apps/web/src/pages/dashboard/dashboard.vue`
- `apps/web/src/product/runtime.ts`
- `apps/web/src/apis/agent.ts`（删除）
- `tests/frontend/test_phase10_product_contracts.py`

当前旧 Agent list surface 删除覆盖：

- `apps/web/src/apis/agent.ts` 已删除，不再保留旧 Agent create/list/delete/update/search API 的前端实现文件；
- Workspace sidebar、Workspace default agent picker 和 Dashboard 统计筛选改为读取 Product Catalog，不再调用旧 `getAgentsAPI`；
- `PRODUCT_AGENT_WORKSPACE_ID` 由 Product runtime 正式导出，避免前端页面各自硬编码 Product workspace；
- 前端合同测试新增对 `apps/web/src/apis/agent.ts` 不存在的断言，并检查工作区、默认页和仪表盘页面不再出现旧 Agent list API 字符串。

仍未完成：

- Browser E2E、Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

P10-T19 验证：

```text
python -m pytest tests\\frontend\\test_phase10_product_contracts.py tests\\frontend\\test_frontend_workspace_features.py -q
18 passed
```

```text
npm run lint -w zuno-frontend
passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

## P10-T20 Browser Smoke 闭环

已更新：

- `tools/qa/full-e2e/package.json`
- `tools/qa/full-e2e/qa_echo_api.py`
- `tools/qa/full-e2e/full_e2e.py`
- `tools/scripts/run-full-e2e-smoke.ps1`
- `tests/tools/test_launcher_scripts.py`

当前 Browser E2E smoke 闭环：

- QA echo API 不再依赖 `tmp-qa-playwright` 下的临时缺件，正式 helper 进入仓库可追踪目录 `tools/qa/full-e2e/`；
- `run-full-e2e-smoke.ps1` 现在显式指向正式 helper，并对含空格和 `&` 的路径做了 quoted `Start-Process` 参数，避免 Python 误拆路径；
- smoke 运行时通过 `ZUNO_FULL_E2E_*` 环境变量把 backend、frontend、QA API 和 `auth.json` 关联起来，不再依赖隐式当前目录；
- `full_e2e.py` 用 backend `/health`、QA API `/health`、Playwright storage state 和浏览器上下文里的 Product Catalog 请求做最小闭环验证。

本轮验证：

```text
python -m pytest tests\\tools\\test_launcher_scripts.py::test_full_e2e_smoke_script_resolves_repository_root_not_tools_root -q
1 passed
```

```text
powershell -ExecutionPolicy Bypass -File .\\tools\\scripts\\run-full-e2e-smoke.ps1
passed
```

已消失的 blocker：

- `tmp-qa-playwright/auth.json` 缺失；
- `tmp-qa-playwright/qa_echo_api.py` 缺失；
- `tmp-qa-playwright` 临时工程缺失；
- 未加引号的 `Start-Process` 路径在含 `&` 的仓库根下会被拆坏。

仍未完成：

- Desktop smoke、shadow/canary/default-new/rollback closure gate 仍未完成；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T21 Desktop Smoke 与 Catalog Schema 修复

已更新：

- `apps/desktop/main.cjs`
- `tools/scripts/run-desktop-smoke.ps1`
- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `infra/db/alembic/versions/20260727_43_goal04_product_agent_definition_description.py`
- `tests/tools/test_launcher_scripts.py`
- `tests/repo/test_goal03_wave_a_migration_contract.py`

当前 Desktop smoke 闭环：

- Electron 主进程新增只在 `DESKTOP_SMOKE_RESULT` 存在时启用的 smoke 模式，隐藏窗口启动真实 Electron；
- smoke 模式通过 preload 后的 renderer 读取 `window.__ZUNO_DESKTOP__`，验证 `product-desktop-bridge-v1.phase10`、Product bridge capabilities、Product endpoint contract 和 bridge health；
- renderer 使用 `DESKTOP_SMOKE_TOKEN` 访问真实 backend Product Catalog：`/api/v1/product/agent-catalog?tenant_id=tenant:web&workspace_id=workspace:agent-studio:web`；
- `tools/scripts/run-desktop-smoke.ps1` 负责确认 backend、启动 8091 desktop frontend、生成本地 JWT token、启动 Electron，并读取 `tmp/desktop-smoke-result.json` 作为可复核结果。

Desktop smoke 暴露的真实后端缺口：

- Product Catalog API 初次从桌面 renderer 请求时返回 HTTP 200 包裹的 `status_code=500`，根因是 repository 查询 `product_agent_definitions.description`，但当前 tracked Alembic schema 未创建该列；
- 已追加 append-only migration `20260727_43_goal04_product_agent_definition_description.py`，并让 Product repository / ProductService 在 AgentDefinition 创建时写入 description，避免 Catalog projection 丢字段。

本轮验证：

```text
python -m pytest tests\\tools\\test_launcher_scripts.py::test_desktop_smoke_script_runs_real_electron_bridge_check tests\\tools\\test_launcher_scripts.py::test_desktop_main_supports_product_bridge_smoke_mode -q
2 passed
```

```text
node --check apps\\desktop\\main.cjs
passed
```

```text
python -m pytest tests\\repo\\test_goal03_wave_a_migration_contract.py::test_goal04_product_agent_definition_description_migration_repairs_catalog_projection -q
1 passed
```

```text
python -m py_compile src\\backend\\zuno\\platform\\database\\product\\domain.py src\\backend\\zuno\\api\\services\\product\\command_service.py infra\\db\\alembic\\versions\\20260727_43_goal04_product_agent_definition_description.py
passed
```

```text
powershell -ExecutionPolicy Bypass -File .\\tools\\scripts\\run-desktop-smoke.ps1
Desktop smoke passed.
tmp\\desktop-smoke-result.json: ok=true, productBridgeVersion=product-desktop-bridge-v1.phase10, catalogStatus=200, catalogEntryCount=0
```

Alembic 状态：

```text
python -m alembic -c infra\\db\\alembic.ini heads
20260727_43 (head)
```

```text
python -m alembic -c infra\\db\\alembic.ini upgrade head
failed
exception: Can't locate revision identified by '20260727_45'
first relevant stack frame: Alembic version resolution before upgrade execution
environment signature: local PostgreSQL alembic_version contains 20260727_45; current branch tracked Alembic head is 20260727_43
recovery used for runtime smoke only: ALTER TABLE product_agent_definitions ADD COLUMN IF NOT EXISTS description text NOT NULL DEFAULT ''; ALTER COLUMN description DROP DEFAULT
```

仍未完成：

- shadow/canary/default-new/rollback closure gate 仍未完成；
- Alembic upgrade head 需要在数据库 stamp 与当前分支 revision graph 一致后重跑；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T22 Web Product Runtime Cutover Guard

已更新：

- `apps/web/src/product/runtime.ts`
- `tests/frontend/test_phase10_product_contracts.py`

当前 Web Product runtime cutover guard：

- Product Web runtime 显式声明 `ProductRuntimeCutoverMode = shadow | canary | new_default | rollback`；
- `resolveProductRuntimeCutoverMode()` 从 `localStorage['zuno.productRuntimeCutoverMode']` 或 `VITE_PRODUCT_RUNTIME_CUTOVER_MODE` 解析模式，未知值 fail-safe 到 `new_default`；
- `shadow` 发送 `SHADOW_SUBMIT_USER_GOAL`，`canary` 发送 `CANARY_SUBMIT_USER_GOAL`，`new_default` 发送 `SUBMIT_USER_GOAL`；
- 所有 Product runtime payload 带 `cutover_mode`，避免切流状态只存在前端隐式状态；
- `rollback` 在前端 Product runtime adapter 内 fail-closed，抛出 `ProductRuntimeRollbackError`，不会调用 `submitProductRuntimeRequest()`，也不会回到已删除的 legacy workspace task/simple chat 路径。

本轮验证：

```text
python -m pytest tests\\frontend\\test_phase10_product_contracts.py::test_phase10_product_runtime_cutover_modes_are_explicit_and_rollback_fail_closed -q
1 passed
```

```text
python -m pytest tests\\frontend\\test_phase10_product_contracts.py tests\\frontend\\test_frontend_workspace_features.py -q
19 passed
```

```text
npm run build -w zuno-frontend
passed；Vite chunk-size / Sass legacy-js-api / Rollup PURE annotation warnings retained as build warnings, not compile failures。
```

仍未完成：

- shadow/canary/default-new/rollback 仍缺完整闭环 closure evidence；当前只完成 Web runtime cutover guard；
- Alembic upgrade head 需要在数据库 stamp 与当前分支 revision graph 一致后重跑；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T23 Product API Rollback Fail-Closed Boundary

已更新：

- `src/backend/zuno/api/v1/product.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `tests/api/test_goal03_product_route.py`

当前 Product runtime rollback boundary：

- `/api/v1/product/runtime-requests` 在调用 `ProductService.submit_runtime_request()` 前检查 payload `cutover_mode`；
- `ProductService.submit_runtime_request()` 在构造 `ProductCommandSubmission` 和打开数据库 UoW 前重复执行同一 Product 边界检查；
- `cutover_mode=rollback` 抛出 `ValueError("Product runtime rollback mode is active...")`，不会写 `product_commands`、不会写 projection、不会发出 runtime dispatch outbox；
- 该边界防止外部调用方绕过 Web adapter 的 rollback fail-closed 行为。

RED 验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_runtime_request_route_rejects_rollback_before_service -q
failed
assertion: expected "Product runtime rollback mode is active"
actual: rollback request reached ProductService.submit_runtime_request
```

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_service_rejects_rollback_before_database_write -q
failed
exception: sqlalchemy.exc.IntegrityError / psycopg.errors.ForeignKeyViolation
first relevant stack frame: src\\backend\\zuno\\platform\\database\\product\\domain.py:1481 in _ensure_conversation
meaning: rollback reached the database write path before ProductService had a cutover boundary
```

本轮验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_runtime_request_route_rejects_rollback_before_service tests\\api\\test_goal03_product_route.py::test_goal03_product_service_rejects_rollback_before_database_write -q
2 passed, 1 warning
```

```text
python -m pytest tests\\api\\test_goal03_product_route.py -q
13 passed, 1 warning
```

仍未完成：

- shadow/canary/default-new/rollback 仍缺完整闭环 closure evidence；当前只完成 Web runtime guard 和 Product API rollback fail-closed boundary；
- Alembic upgrade head 需要在数据库 stamp 与当前分支 revision graph 一致后重跑；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T24 Product API Cutover Command Contract

已更新：

- `src/backend/zuno/api/v1/product.py`
- `src/backend/zuno/api/services/product/command_service.py`
- `tests/api/test_goal03_product_route.py`

当前 Product runtime cutover command contract：

- Product Service 定义服务端 cutover command 映射：`shadow -> SHADOW_SUBMIT_USER_GOAL`、`canary -> CANARY_SUBMIT_USER_GOAL`、`new_default -> SUBMIT_USER_GOAL`；
- `/api/v1/product/runtime-requests` 在调用 `ProductService.submit_runtime_request()` 前验证 `payload.cutover_mode` 与 `command_kind` 一致；
- `ProductService.submit_runtime_request()` 在构造 `ProductCommandSubmission` 和打开数据库 UoW 前重复验证；
- 未知 `cutover_mode` fail-closed；`rollback` 继续 fail-closed；mismatch 不会进入 Product command journal、projection 或 runtime dispatch outbox；
- 旧测试 fixture 中的 `CREATE_RUNTIME_REQUEST` 已改为 default-new `SUBMIT_USER_GOAL`，避免继续把旧 command kind 作为 Product runtime 入口。

RED 验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_runtime_request_route_rejects_cutover_command_mismatch_before_service tests\\api\\test_goal03_product_route.py::test_goal03_product_service_rejects_cutover_mismatch_and_unknown_mode_before_database_write -q
failed
route assertion: expected "Product runtime cutover command mismatch"
actual: cutover mismatch reached ProductService.submit_runtime_request
service exception: sqlalchemy.exc.IntegrityError / psycopg.errors.ForeignKeyViolation
first relevant stack frame: src\\backend\\zuno\\platform\\database\\product\\domain.py:1481 in _ensure_conversation
meaning: shadow/canary/new_default mismatch reached the database write path before ProductService had a cutover command contract
```

本轮验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_runtime_request_route_rejects_cutover_command_mismatch_before_service tests\\api\\test_goal03_product_route.py::test_goal03_product_service_rejects_cutover_mismatch_and_unknown_mode_before_database_write -q
2 passed, 1 warning
```

```text
python -m pytest tests\\api\\test_goal03_product_route.py -q
15 passed, 1 warning
```

```text
python -m py_compile src\\backend\\zuno\\api\\v1\\product.py src\\backend\\zuno\\api\\services\\product\\command_service.py
passed
```

仍未完成：

- shadow/canary/default-new/rollback 仍缺完整闭环 runtime closure evidence；当前已完成 Web runtime guard、Product API rollback fail-closed boundary、Product API cutover command contract；
- Alembic upgrade head 需要在数据库 stamp 与当前分支 revision graph 一致后重跑；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T25 Product Runtime Cutover Handoff Context

已更新：

- `src/backend/zuno/api/services/product/command_service.py`
- `src/backend/zuno/platform/database/product/domain.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/api/test_goal03_product_route.py`
- `tests/api/test_workspace_task_runtime.py`
- `tests/integration/test_goal03_wave_a_persistence.py`

当前 Product runtime cutover handoff context：

- Product outbox `product.runtime_request.dispatch` envelope now carries `command_kind` and `cutover_mode`;
- Agent Core dispatch consumer validates the cutover command contract before owner writes;
- Agent Core `GoalVersion.constraints_hash` now includes `active_agent_version_id`、`command_id`、`command_kind` 和 `cutover_mode`，so canary/shadow/default-new cannot collapse into the same owner constraints;
- Product owner receipt payload now records `command_kind`、`cutover_mode` and the derived `constraints_hash`;
- legacy workspace runtime bridge now submits `SUBMIT_USER_GOAL` with `cutover_mode=new_default` instead of `WORKSPACE_RUNTIME_REQUEST`.

RED 验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_service_builds_cutover_owner_context_for_agent_core_handoff -q
failed
exception: AttributeError
reason: ProductService.build_runtime_cutover_owner_context did not exist
```

```text
python -m pytest tests\\api\\test_workspace_task_runtime.py::test_workspace_task_runtime_links_task_events_artifact_and_feedback -q
failed
assertion: expected SUBMIT_USER_GOAL
actual: WORKSPACE_RUNTIME_REQUEST
```

本轮验证：

```text
python -m pytest tests\\api\\test_goal03_product_route.py::test_goal03_product_service_builds_cutover_owner_context_for_agent_core_handoff -q
1 passed, 1 warning
```

```text
python -m pytest tests\\api\\test_workspace_task_runtime.py::test_workspace_task_runtime_links_task_events_artifact_and_feedback -q
1 passed, 1 warning
```

```text
python -m pytest tests\\api\\test_goal03_product_route.py tests\\api\\test_workspace_task_runtime.py::test_workspace_task_runtime_links_task_events_artifact_and_feedback -q
17 passed, 1 warning
```

```text
python -m py_compile src\\backend\\zuno\\api\\services\\product\\command_service.py src\\backend\\zuno\\platform\\database\\product\\domain.py src\\backend\\zuno\\api\\services\\workspace_task_runtime.py
passed
```

未运行：

```text
python -m pytest tests\\integration\\test_goal03_wave_a_persistence.py ...
reason: 当前本地 PostgreSQL alembic_version=20260727_45，不在本分支 revision graph；该文件 fixture 会先执行 alembic upgrade head，命中已记录 blocker。
```

仍未完成：

- shadow/canary/default-new/rollback 仍缺完整闭环 runtime closure evidence；当前已完成 Web runtime guard、Product API rollback fail-closed boundary、Product API cutover command contract、Product runtime cutover handoff context；
- Alembic upgrade head 需要在数据库 stamp 与当前分支 revision graph 一致后重跑；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T26 Product Cutover Evidence Verifier

已更新：

- `tools/scripts/verify_phase10_product_cutover_evidence.py`
- `tests/repo/test_phase10_product_cutover_evidence.py`
- `docs/evidence/goal04-phase10-startup-audit.md`

当前 verifier 覆盖：

- Web runtime cutover mode、command kind 映射、rollback fail-closed 和 payload `cutover_mode`；
- Product API / ProductService rollback boundary、cutover command contract、unknown/mismatch fail-closed；
- Product outbox `command_kind` / `cutover_mode` handoff；
- Agent Core handoff `constraints_hash` 和 owner receipt cutover context；
- workspace legacy bridge default-new command contract；
- 对应 frontend/API/workspace tests 和 P10-T22..P10-T25 evidence sections。

RED 验证：

```text
python -m pytest tests\\repo\\test_phase10_product_cutover_evidence.py -q
failed
exception: FileNotFoundError
missing: tools\\scripts\\verify_phase10_product_cutover_evidence.py
```

本轮验证：

```text
python -m pytest tests\\repo\\test_phase10_product_cutover_evidence.py -q
1 passed
```

```text
python tools\\scripts\\verify_phase10_product_cutover_evidence.py
PHASE10 Product cutover evidence verifier passed.
```

仍未完成：

- verifier 证明的是当前 cutover evidence bundle 可机器检查，不等于 PHASE10 closure；
- shadow/canary/default-new/rollback 仍缺完整端到端 runtime closure evidence；
- Alembic upgrade head 需要在数据库 stamp 与当前分支 revision graph 一致后重跑；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T27 Browser Product Runtime Cutover Smoke Gate

已更新：

- `tools/qa/full-e2e/full_e2e.py`
- `tests/tools/test_launcher_scripts.py`
- `tools/scripts/verify_phase10_product_cutover_evidence.py`

当前 Browser Product runtime cutover smoke gate 覆盖：

- Full E2E smoke 在已登录 browser context 中调用 `/api/v1/product/runtime-requests`；
- `shadow` 提交 `SHADOW_SUBMIT_USER_GOAL`，`canary` 提交 `CANARY_SUBMIT_USER_GOAL`，`new_default` 提交 `SUBMIT_USER_GOAL`；
- 三个可提交模式必须返回 HTTP 200、Product `status_code=200`、`ACCEPTED` 或 `DUPLICATE` receipt、`command_id` 和 projection evidence；
- `rollback` 提交 `SUBMIT_USER_GOAL` + `cutover_mode=rollback`，必须返回 fail-closed Product error，错误信息包含 `Product runtime rollback mode is active`；
- 静态 launcher test 和 PHASE10 cutover verifier 会防止该 browser smoke gate 被移除。

RED 验证：

```text
python -m pytest tests\tools\test_launcher_scripts.py::test_full_e2e_smoke_covers_product_runtime_cutover_modes -q
no tests ran
ERROR: not found: tests\tools\test_launcher_scripts.py::test_full_e2e_smoke_covers_product_runtime_cutover_modes
```

本轮验证：

```text
python -m pytest tests\tools\test_launcher_scripts.py::test_full_e2e_smoke_covers_product_runtime_cutover_modes -q
1 passed
```

```text
python -m py_compile tools\qa\full-e2e\full_e2e.py tools\scripts\verify_phase10_product_cutover_evidence.py
passed
```

```text
python tools\scripts\verify_phase10_product_cutover_evidence.py
PHASE10 Product cutover evidence verifier passed.
```

```text
powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
passed
```

仍未完成：

- 本轮新增的是 Browser full-e2e cutover smoke gate，不等于已经完成并通过完整 PHASE10 closure；
- PHASE10 仍为 `in_progress`，不能写 completed。

## P10-T28 Branch-Scoped Alembic Upgrade Gate

本轮未修改默认 `zuno` 数据库的 `alembic_version=20260727_45` stamp。为避免把外部分支残留 stamp 当作当前分支 schema 失败，使用临时 PostgreSQL 数据库和临时 `ZUNO_CONFIG` 验证当前分支 revision graph：

```text
database=zuno_phase10_alembic_30ac1525d7ee4406a3e02ac2a7f4ecd8
python -m alembic -c infra/db/alembic.ini upgrade head
upgrade_returncode=0
python -m alembic -c infra/db/alembic.ini current
current_returncode=0
20260727_43 (head)
cleanup=dropped
```

结论：

- 当前分支 Alembic 单一 head 仍为 `20260727_43`；
- 当前分支可从空 PostgreSQL 数据库 `upgrade head` 到 `20260727_43`；
- 默认本地 `zuno` 数据库的 `20260727_45` stamp 仍是外部环境残留，不再作为 PHASE10 分支迁移 gate 的失败证据；
- PHASE10 仍为 `in_progress`，不能写 completed。

## 本轮验证

已通过：

```text
git diff --check
python tools\scripts\verify_current_program.py
python -m pytest -q tests\repo\test_current_program_contract.py -p no:cacheprovider
python -m pytest -q tests\frontend\test_phase10_product_contracts.py -p no:cacheprovider
npm install
npm run lint -w zuno-frontend
npm run build -w zuno-frontend
python -m pytest tests\tools\test_launcher_scripts.py::test_full_e2e_smoke_script_resolves_repository_root_not_tools_root -q
powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
python -m pytest tests\tools\test_launcher_scripts.py::test_desktop_smoke_script_runs_real_electron_bridge_check tests\tools\test_launcher_scripts.py::test_desktop_main_supports_product_bridge_smoke_mode -q
node --check apps\desktop\main.cjs
python -m pytest tests\repo\test_goal03_wave_a_migration_contract.py::test_goal04_product_agent_definition_description_migration_repairs_catalog_projection -q
python -m py_compile src\backend\zuno\platform\database\product\domain.py src\backend\zuno\api\services\product\command_service.py infra\db\alembic\versions\20260727_43_goal04_product_agent_definition_description.py
powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-desktop-smoke.ps1
python -m pytest tests\tools\test_launcher_scripts.py tests\repo\test_goal03_wave_a_migration_contract.py tests\api\test_goal03_product_route.py -q
python -m pytest tests\frontend\test_phase10_product_contracts.py::test_phase10_product_runtime_cutover_modes_are_explicit_and_rollback_fail_closed -q
python -m pytest tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -q
npm run build -w zuno-frontend
python -m pytest tests\frontend\test_frontend_workspace_features.py::test_workspace_default_chat_uses_product_runtime_not_simple_chat_stream tests\frontend\test_frontend_workspace_features.py::test_workspace_agent_mode_uses_product_runtime_projection_loop -q
python -m pytest tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -q
python -m pytest tests\frontend\test_workspace_product_loop_types.py tests\frontend\test_frontend_workspace_features.py tests\frontend\test_phase10_product_contracts.py -q
python -m pytest tests\api\test_goal03_product_route.py::test_goal03_product_agent_studio_catalog_routes_use_product_service tests\frontend\test_phase10_product_contracts.py -q
python -m py_compile src\backend\zuno\platform\database\product\domain.py src\backend\zuno\api\services\product\command_service.py src\backend\zuno\api\v1\product.py
python -m pytest tests\frontend\test_phase10_product_contracts.py::test_phase10_agent_studio_and_catalog_ui_use_product_surface -q
python -m pytest tests\frontend\test_phase10_product_contracts.py -q
python -m pytest tests\api\test_goal03_product_route.py::test_goal03_product_agent_studio_snapshot_route_uses_product_service tests\repo\test_goal03_wave_a_migration_contract.py::test_goal04_product_agent_editor_payload_migration_adds_json_snapshots -q
python -m pytest tests\frontend\test_phase10_product_contracts.py tests\frontend\test_frontend_workspace_features.py -q
python -m pytest tests\api\test_goal03_product_route.py::test_goal03_product_runtime_request_route_rejects_rollback_before_service tests\api\test_goal03_product_route.py::test_goal03_product_service_rejects_rollback_before_database_write -q
python -m pytest tests\api\test_goal03_product_route.py -q
python -m pytest tests\api\test_goal03_product_route.py::test_goal03_product_runtime_request_route_rejects_cutover_command_mismatch_before_service tests\api\test_goal03_product_route.py::test_goal03_product_service_rejects_cutover_mismatch_and_unknown_mode_before_database_write -q
python -m pytest tests\api\test_goal03_product_route.py -q
python -m py_compile src\backend\zuno\api\v1\product.py src\backend\zuno\api\services\product\command_service.py
python -m pytest tests\api\test_goal03_product_route.py::test_goal03_product_service_builds_cutover_owner_context_for_agent_core_handoff -q
python -m pytest tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_links_task_events_artifact_and_feedback -q
python -m pytest tests\api\test_goal03_product_route.py tests\api\test_workspace_task_runtime.py::test_workspace_task_runtime_links_task_events_artifact_and_feedback -q
python -m py_compile src\backend\zuno\api\services\product\command_service.py src\backend\zuno\platform\database\product\domain.py src\backend\zuno\api\services\workspace_task_runtime.py
python -m pytest tests\repo\test_phase10_product_cutover_evidence.py -q
python tools\scripts\verify_phase10_product_cutover_evidence.py
python -m pytest tests\tools\test_launcher_scripts.py::test_full_e2e_smoke_covers_product_runtime_cutover_modes -q
python -m py_compile tools\qa\full-e2e\full_e2e.py tools\scripts\verify_phase10_product_cutover_evidence.py
powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
ZUNO_CONFIG=<temp phase10 config> python -m alembic -c infra/db/alembic.ini upgrade head
ZUNO_CONFIG=<temp phase10 config> python -m alembic -c infra/db/alembic.ini current
```

未通过 / 未完成：

```text
command: powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
status: resolved
first relevant stack frame: tools\scripts\run-full-e2e-smoke.ps1:73
environment signature: Node.js v24.14.0; npm workspace dependencies installed; repo-root path resolved correctly; smoke helper now tracked in tools/qa/full-e2e; auth.json generated locally from backend JWT config
retry_count: 2 total; first run failed on missing auth state, second run failed on missing QA helper, third run passed
resolved_by: formal helper package plus quoted Start-Process path plus generated Playwright storage state
```

```text
command: python -m alembic -c infra\db\alembic.ini upgrade head
status: resolved with branch-scoped temporary PostgreSQL database
previous_exception: Can't locate revision identified by '20260727_45'
first relevant stack frame: Alembic version resolution before upgrade execution
environment signature: local PostgreSQL alembic_version contains 20260727_45; current branch tracked Alembic head is 20260727_43
recovery_used: create temporary PostgreSQL database, point Alembic at it with ZUNO_CONFIG, run upgrade head/current, then drop the temporary database
result: 20260727_43 (head)
```

```text
Browser cutover smoke gate 已补入 full-e2e helper，完整 run-full-e2e-smoke.ps1 已在 Docker Desktop 恢复、PostgreSQL/backend/frontend/QA API/auth state 可用后重跑通过；当前分支 Alembic upgrade head/current 已在临时 PostgreSQL 数据库通过并清理临时库；PHASE10 仍为 in_progress，不能写 completed。
```

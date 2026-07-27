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

## 本轮验证

已通过：

```text
git diff --check
python tools\scripts\verify_current_program.py
python -m pytest -q tests\repo\test_current_program_contract.py -p no:cacheprovider
python -m pytest -q tests\frontend\test_phase10_product_contracts.py -p no:cacheprovider
```

未通过 / 未完成：

```text
command: npm run lint
exception: Error: Cannot find module 'F:\internship-work\resume&resume project\02_projects\Zuno\node_modules\vue-tsc\bin\vue-tsc.js'
first relevant stack frame: node:internal/modules/cjs/loader:1456
environment signature: Node.js v24.14.0; root node_modules absent; apps/web node_modules absent
retry_count: 0
唯一恢复动作: 安装 npm workspace 依赖后从 `npm run lint -w zuno-frontend` 继续。
```

```text
command: npx --yes vue-tsc --noEmit -p apps/web/tsconfig.app.json
exception: command timed out
first relevant stack frame: n/a; no compiler output returned before timeout
environment signature: Node.js v24.14.0; root node_modules absent; apps/web node_modules absent; npx transient package resolution exceeded 124 seconds
retry_count: 0
唯一恢复动作: 安装 npm workspace 依赖后从 `npm run lint -w zuno-frontend` 继续，不在无环境变化时重复 npx。
```

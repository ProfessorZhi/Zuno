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

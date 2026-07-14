# PHASE10 Web and Desktop Product Adaptation

phase_id: PHASE10
status: planned
depends_on: PHASE09
owner: Module 01 Product Surface

## Phase 目标

让 Web 和 Desktop 完整消费新 Product Contract、Authorized Projection、AvailableAction、SSE Cursor 和版本化 Delivery。迁移期允许双 Client Shadow，但 Program 关闭前删除旧 Store、旧 DTO、字符串状态推断和 `legacy`/`compatibility` 前端目录。

## Minimal Read Set

- `apps/web/AGENTS.md`
- `docs/modules/01-product-surface.md`
- PHASE09 API/Projection Contract
- PHASE02 frontend compatibility matrix
- PHASE01 frontend inventory

## Current Anchors

```text
apps/web/src/**
apps/desktop/src/**
current API clients, Pinia stores, SSE handlers, approval UI, trace/eval UI
```

## Allowed Paths

```text
apps/web/src/product/**
apps/web/src/router/**
apps/web/src/pages/** only migration wiring
apps/desktop/src/product/**
apps/desktop/src/** only bridge wiring
frontend contract/e2e tests
.agent/local/previews/**
docs/evidence/**
```

## Forbidden Paths

- Frontend 成为领域事实源。
- 根据 status 字符串猜动作或成功。
- 暴露 raw checkpoint、prompt、hidden reasoning、secret、raw tool args。
- 永久保留旧/新两套 Store。

## Work Packages

### P10-T01 Generated/Typed Product Contracts
- Goal：建立 Web/Desktop DTO、enum、problem、event、projection、available action 类型与 schema compatibility test。
- Tests：backend fixture round-trip、unknown enum/version、required security fields。
- Acceptance：前端不导入后端 ORM/Internal Enum。

### P10-T02 Product API Client and Error Mapping
- Goal：实现 command/query/signal/download/feedback client、idempotency key、problem detail、retry policy。
- Tests：401/403/409/410/429/5xx、network timeout、duplicate command。
- Acceptance：只对安全的 transport failure retry，不重放副作用 command。

### P10-T03 Projection-first Pinia Store
- Goal：实现 conversation/run/interrupt/ingestion/artifact/quality normalized store，按 projection version/watermark 更新。
- Tests：out-of-order、duplicate、stale projection、revocation purge、resync replace。
- Acceptance：不在 store 内重建 Agent 状态机。

### P10-T04 SSE Cursor, Reconnect and Resync
- Goal：实现 Last-Event-ID、dedup、exponential reconnect、cursor expired resync、reauthorization。
- Tests：断网、重复、gap、cursor 过期、token refresh、workspace revoked。
- Acceptance：ConnectionStatus、ProjectionFreshness、DomainStatus 分离。

### P10-T05 Multi-interrupt and Controlled Actions UI
- Goal：支持多个 Interrupt；Approve/Deny/Cancel/UserInput/Reconcile 只显示 AvailableAction。
- Tests：并行 interrupt、stale token、approval denied/expired、UNKNOWN no retry、cancel race。
- Acceptance：删除单一 `pendingToolApproval` 假设。

### P10-T06 Evidence, Citation, Artifact and Quality Views
- Goal：显示 Publication、claim/citation、source span、artifact、quality/blocked/freshness，独立授权下载。
- Tests：redacted citation、missing evidence、artifact expired、quality blocked/incomparable。
- Acceptance：Provisional Content 与正式 Assistant Publication 分离。

### P10-T07 Desktop Versioned Bridge
- Goal：实现 Desktop product bridge/contracts/authorization/delivery，复用服务端 API，不复制业务状态机。
- Tests：contract smoke、auth refresh、download、deep link、offline/error。
- Acceptance：旧 bridge 只在 rollout window 内存在，最终删除。

### P10-T08 Shadow, Canary, Default-new and Legacy UI Removal
- Goal：旧/新页面 projection shadow compare、canary、default new、rollback、删除旧 client/store/components/routes。
- Tests：Browser E2E、visual snapshot、mobile/desktop viewport、rollback rehearsal、bundle no old imports。
- Acceptance：`apps/web`/`apps/desktop` 生产源码无 `legacy` 文件夹、无永久 compatibility store、无旧 DTO 泄漏。

## Phase 完成定义

- Web/Desktop 新产品流程可用。
- SSE 断线、Gap、撤权、多 Interrupt、UNKNOWN UI E2E 通过。
- Lint/Build/Browser E2E/Desktop Smoke 通过。
- 旧前端目录和临时 compatibility 代码有 PHASE21/22 删除证据。

## Validation

```bash
cd apps/web && npm run lint && npm run build
# run repository browser E2E command discovered in PHASE01
# run desktop smoke/build command discovered in PHASE01
pytest -q tests/api/product tests/integration/product -p no:cacheprovider
```

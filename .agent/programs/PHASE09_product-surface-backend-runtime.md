# PHASE09 Product Surface Backend Runtime

phase_id: PHASE09
status: ready
depends_on: PHASE08
owner: Module 01 Product Surface

## Phase 目标

建立 Thin FastAPI Product Surface：AgentDefinition、AgentDraft、AgentVersion、AgentPublication、AgentInstallation、AgentCatalogEntry、Conversation、Submission、Command、RuntimeRequest、Receipt、Projection、SSE Stream、Signal、Artifact/Citation/Quality Query 和 Delivery。Product 只拥有 Agent 产品资产、交互与读模型，不拥有 AgentRun、Approval、Effect、Evidence、Memory 或 Eval。

## Minimal Read Set

- `docs/modules/01-product-surface.md`
- PHASE03 Contract Bundle
- PHASE05 Security
- PHASE06 Projection/Trace
- PHASE08 Agent Core
- 当前 API/completion/workspace routes/services

## Current Anchors

```text
src/backend/zuno/api/**
src/backend/zuno/api/services/completion.py
src/backend/zuno/api/services/workspace_task_runtime.py
current workspace/file/task/SSE DTO
apps/web current clients
```

## Allowed Paths

```text
src/backend/zuno/api/product/**
src/backend/zuno/api/services/product/**
src/backend/zuno/api/projection/**
src/backend/zuno/platform/database/product/**
alembic/**
tests/api/product/**
tests/integration/product/**
docs/evidence/**
```

## Forbidden Paths

- Route 中编排 Agent/Knowledge/Tool 或直接写其表。
- ORM Row 直接作为 API DTO。
- Product 复制 Approval、Effect、Evidence、RunOutcome 事实。

## Work Packages

### P09-T01 Product Domain and PostgreSQL Schema
- Goal：实现 AgentDefinition、AgentDraft、AgentVersion、AgentPublication、AgentInstallation、AgentCatalogEntry、ConversationThread、UserSubmission、Message、ProductCommand、CommandReceipt、RuntimeRequest、Delivery、Feedback、Projection/Watermark/Cursor。
- Tests：状态机、唯一约束、tenant scope、append-only receipt、Migration。
- Acceptance：Product 表不复制其他模块权威表。

### P09-T02 Command Service and Idempotent Submission
- Goal：同事务提交 submission/message/command/receipt/outbox，使用 client_request_id/request_hash。
- Tests：duplicate same hash、conflict different hash、authorization deny、transaction rollback。
- Acceptance：外部 owner dispatch 在事务外，由 Outbox 交付。

### P09-T03 Owner Command Ports and Receipts
- Goal：接 AgentCore/Ingestion/Memory/Security command port，记录 accepted/rejected/blocked receipt version。
- Tests：owner unavailable、duplicate receipt、late receipt、wrong causation、timeout。
- Acceptance：Receipt 不冒充 owner domain success。

### P09-T04 Projection Reducers and Authorized Views
- Goal：从 Agent/Knowledge/Tool/Security/Observability Event 构建 agent catalog、effective permission preview、run/interrupt/ingestion/artifact/quality projection。
- Tests：out-of-order、duplicate、gap、rebuild、revocation、redaction。
- Acceptance：Projection 可重建，查询返回 freshness/completeness。

### P09-T05 SSE Stream, Cursor and Resync
- Goal：实现 opaque cursor、Last-Event-ID、dedup、gap、cursor expiry、resync、reauthorization。
- Tests：disconnect/reconnect、duplicate event、expired cursor、permission revoked、multiple interrupts。
- Acceptance：SSE close 不等于 Run success。

### P09-T06 Signals and AvailableAction
- Goal：Approve/Deny/Cancel/UserInput/Reconcile/Download、Agent Publish、Install、Archive、Revoke 等命令只由服务端 AvailableAction 提供并绑定 action token。
- Tests：stale action、replay、wrong epoch、unknown effect no normal retry、cancel race。
- Acceptance：Frontend 不根据状态字符串自行生成动作。

### P09-T07 Compatibility API and Backend Cutover
- Goal：为旧 completion/workspace API 提供版本化 adapter，shadow/canary/default new/rollback。
- Tests：old/new response contract、SSE mapping、no duplicate run、rollback。
- Acceptance：adapter 位于正常 versioned API 包，有 sunset；最终删除旧 service/route 和 compatibility 目录，不保留 Legacy Product API。

## Phase 完成定义

- Product Backend 新 API/Command/Query/Projection/SSE 可运行。
- Agent Studio / Catalog / Publication / Installation 后端 Contract 可运行，并且一次 RuntimeRequest 绑定一个 Primary AgentVersion。
- 旧 API 有受控版本 Adapter 和删除任务。
- Product 不拥有下游领域事实。
- API Contract Test 和 SSE Fault Test 通过。

## Validation

```bash
git diff --check
python tools/scripts/verify_product_surface_target_protocols.py
pytest -q tests/api/product tests/integration/product -p no:cacheprovider
```

# PHASE15 Tool Runtime Definition and Read-only Cutover

phase_id: PHASE15
status: blocked
depends_on: PHASE08, PHASE14
owner: Module 08 Tool Runtime

## Phase 目标

建立唯一 ToolInvocationGateway、ToolProvider/Definition/Version/Operation/Installation/Activation/AdapterBinding、PreparedToolAction、ToolAttempt/Observation/ExecutionReceipt，并先迁移无副作用和只读 Tool。Side Effect 的完整 Effect Assurance 在 PHASE16。

## Minimal Read Set

- `docs/modules/08-tool-runtime.md`
- PHASE03 Tool Contracts
- PHASE05 Security
- PHASE06 Trace/Audit
- PHASE08 StepExecutionGraph
- PHASE14 Capability Projection
- PHASE01 Tool bypass inventory

## Current Anchors

```text
src/backend/zuno/capability/**
GeneralAgent LangChain tools
MCP manager/client tool.coroutine / tools/call
CLI/OpenAPI adapters
httpx/subprocess/browser/SDK execution points
```

## Allowed Paths

```text
src/backend/zuno/capability/tool_runtime/**
src/backend/zuno/platform/database/tool_runtime/**
alembic/**
tests/tool_runtime/**
tests/integration/tool_runtime/**
tools/scripts/*tool*bypass*.py
docs/evidence/**
```

## Forbidden Paths

- Agent Core/Capability 直接执行 adapter。
- 在本 Phase 允许有副作用 Tool 绕过 PHASE16 Gate。
- HTTP 2xx 当领域 Effect 成功。

## Work Packages

### P15-T01 Tool Definition, Version, Operation and Installation
- Goal：实现 provider/definition/version/operation/input-output schema/effect class/install/activation/adapter binding。
- Tests：immutable version、schema hash、activation CAS、unsupported operation、tenant scope。
- Acceptance：Definition/Installation/Activation 分离。

### P15-T02 Adapter SPI and Conformance Harness
- Goal：定义 prepare/invoke/status/cancel/normalize 接口和 capability matrix。
- Tests：timeout/error/cancel/output schema/hidden retry/credential leakage/status query。
- Acceptance：所有 adapter 只在 `capability/tool_runtime/adapters/**`。

### P15-T03 PreparedToolAction Canonicalization
- Goal：从 ActionProposal 生成 immutable canonical args、target resources、effect classification、prepared hash、policy refs。
- Tests：arg ordering、schema default、resource normalization、hash tamper、version mismatch。
- Acceptance：Approval/Idempotency 后续绑定同一 hash。

### P15-T04 ToolAttempt, Observation and ExecutionReceipt
- Goal：实现 attempt lifecycle、native result ref、normalized observation、execution receipt、failure taxonomy。
- Tests：success、provider error、timeout、invalid output、duplicate callback、late result。
- Acceptance：ExecutionReceipt 只证明一次执行尝试，不证明外部 Effect。

### P15-T05 Builtin and HTTP Read-only Adapter Cutover
- Goal：迁移 low-risk builtin/search/read-only HTTP，进入 Gateway/Security/Trace。
- Tests：real dispatch count、timeout、schema、SSRF、redaction、no hidden retry。
- Acceptance：旧 handler 仅 adapter bridge，默认新路径。

### P15-T06 MCP Read-only Snapshot and Binding
- Goal：实现 MCP server installation、capability snapshot、tool binding、session/task refs 和 read-only call。
- Tests：schema change、session reconnect、duplicate delivery、malicious annotation、transport failure。
- Acceptance：MCP delivery id 不等于 business idempotency/effect。

### P15-T07 CLI/OpenAPI Read-only Sandbox Baseline
- Goal：实现 read-only CLI/OpenAPI adapter 的 working dir/env/network/path/output limits。
- Tests：path traversal、env leak、SSRF/DNS rebinding、oversized output、timeout/cancel。
- Acceptance：真实隔离能力按证据声明；进程参数对象不能冒充 sandbox。

### P15-T08 Read-only Bypass Cutover and Guard
- Goal：收口 `tool.ainvoke/tool.coroutine/adapter.execute/httpx/subprocess/MCP tools/call` 的只读旁路。
- Tests：static guard allowlist 减少；Agent read-tool E2E；rollback 无双执行。
- Acceptance：只读生产路径全部进入 Gateway；不保留 `legacy_tools` 目录，旧 bridge PHASE22 删除。

## Phase 完成定义

- Tool 领域基础和只读执行面可用。
- Read-only Adapter Conformance/Security/Fault Test 通过。
- Side-effect Tool 仍被明确阻止或路由 PHASE16。

## Goal03 Wave B Closure

status: superseded_by_goal05_audit
coordinator_approval: approved
evidence_ref: docs/evidence/goal03-wave-b-gate-review.md

默认 Tool Control Plane、GeneralAgent LangChain middleware、user-defined CLI/OpenAPI runtime 已收口到唯一 `ToolInvocationGateway`，并通过 `ToolUnitOfWork` / `ToolRepository` 写入 Definition、Version、Operation、Installation、Activation、AdapterBinding、PreparedToolAction、Attempt、Observation、ExecutionReceipt 和 Bypass Guard Receipt。有副作用 Tool 在 PHASE15 fail-closed，等待 PHASE16。

## Goal05 Reopen

status: blocked
evidence_ref: docs/evidence/goal05-target-coverage-audit.md
gap_ledger: .agent/programs/work-products/goal05-target-gap-ledger.yaml

Goal05 一次性 Target Coverage Audit 发现 PHASE15 的 Agent Sandbox Closure 过早：当前主线已有 Gateway、Security、Effect 和 Reconciliation 证据，但没有真实 Deno + Pyodide/WASM 与 OCI Process Sandbox 默认执行证据。Goal05 已把 sandbox profile resolution、session isolation、limits/allowlist hash 和 `tool_sandbox_receipts` 接入 `ToolInvocationGateway` 默认链；该修复仍只是 contract + persistence + fail-closed gate，不足以关闭 PHASE15。

关闭 PHASE15 前必须补齐：

- Deno + Pyodide/WASM 真实执行证据；
- OCI short-lived container 真实执行证据；
- Postgres integration 通过；
- sandbox failure/recovery/security/concurrency/idempotency evidence。

## Validation

```bash
git diff --check
python tools/scripts/verify_tool_runtime_target_protocols.py
pytest -q tests/tool_runtime tests/integration/tool_runtime -k 'readonly or definition or adapter or prepared' -p no:cacheprovider
python tools/scripts/verify_tool_execution_bypass.py
```

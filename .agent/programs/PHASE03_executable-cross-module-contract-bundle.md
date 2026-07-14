# PHASE03 Executable Cross-module Contract Bundle

phase_id: PHASE03
status: planned
depends_on: PHASE02
owner: Shared Contract Governance

## Phase 目标

把 Wave 1 Confirmed Target 和十一模块跨边界对象实现为唯一版本化 Pydantic/JSON Schema Contract Bundle，具备确定性序列化、Hash、Enum、Failure Namespace、Producer/Consumer Fixture 和兼容测试。旧 Contract 仅作为有期限的版本 Adapter，最终不保留 `legacy_contracts` 包。

## Minimal Read Set

- ADR 0003 与 Wave 1 Registry
- 模块 04、06、08、09、10、11 文档
- PHASE02 API/数据兼容矩阵
- 当前 contracts/DTO/frontend types

## Current Anchors

```text
src/backend/zuno/agent/contracts.py
src/backend/zuno/agent/runtime/contracts.py
src/backend/zuno/knowledge/**/contracts*.py
src/backend/zuno/memory/**/contracts*.py
src/backend/zuno/capability/**/contracts*.py
src/backend/zuno/platform/**/contracts*.py
src/backend/zuno/api/dto/**
apps/web/src/**/types*
```

## Allowed Paths

```text
src/backend/zuno/platform/contracts/**
module-owned contracts/**
tests/contracts/**
tests/repo/**
tools/scripts/verify_*contract*.py
docs/evidence/**
```

## Forbidden Paths

- Provider SDK、ORM、FastAPI、Vue 或 LangGraph 类型进入 Domain Contract。
- 同名 Contract 在多个模块复制定义。
- 为兼容旧代码删除 Tenant、Scope、Epoch、Hash、Generation 或 Version 字段。

## Work Packages

### P03-T01 Contract Bundle Registry
- Goal：实现 contract_name/major/minor/schema_hash/owner/producer/consumer/compatibility registry。
- Steps：定义 Bundle Version、加载 API、未知 Major/Enum 和冻结规则。
- Tests：重复 Owner、同版本不同 Schema、未知 Major 被拒绝。
- Acceptance：Registry 是唯一跨模块 Contract 索引。

### P03-T02 CrossModuleEnvelopeV1
- Goal：实现 Envelope、PayloadRef、Tenant/Workspace/Run/Step、Correlation/Causation、Idempotency、Generation、Security、Deadline、Trace、Classification、Hash。
- Tests：canonical round-trip、hash tamper、missing scope、stale schema、payload/payload_ref 互斥。
- Acceptance：后续事件复用同一 Envelope，不另造删减版。

### P03-T03 Security, Identity and Failure Contracts
- Goal：实现 PrincipalContextRef、SecurityContextRef、EffectiveSecurityEpochRefV1、AuthorizationDecisionRef、ApprovalRef、RedactionRef、FailureCodeV1。
- Tests：Unknown Security Enum fail-closed；Failure Namespace 稳定映射。
- Acceptance：Contract 不携带 Secret Material。

### P03-T04 Agent, Knowledge, Memory and Model Contracts
- Goal：实现 RuntimeRequest、TaskContract、GoalVersionRef、Plan/Step/Action refs、KnowledgeQueryRequest/Outcome/Proposal、ContextPackVersionRef、ModelRoleRequirement/Attempt/Usage refs。
- Tests：Proposal 与 Final Fact 类型不可互换；Retry/Replan reason 分开。
- Acceptance：Agent Core 不拥有 Evidence、Memory、Model Attempt 事实。

### P03-T05 Capability, Tool, Observability and Infrastructure Contracts
- Goal：实现 CapabilityRequirement/Availability/Selection、ActionProposal、PreparedToolAction、ToolObservation、EffectReceipt/Reconciliation、TelemetryEnvelope、Audit/Idempotency/Lease/Checkpoint receipts。
- Tests：HTTP 2xx、Queue ACK、Audit Receipt、Checkpoint Receipt 不能解析成 EffectReceipt/DomainSuccess。
- Acceptance：每个 Receipt 明确 Owner 范围。

### P03-T06 Canonical Serialization, Hash and Schema Export
- Goal：统一 datetime/decimal/bytes/map ordering/null/unknown field，导出 JSON Schema/Bundle Manifest。
- Tests：跨进程 Hash 稳定；字段顺序不影响 Hash；语义变化改变 Schema Hash。
- Acceptance：Idempotency、Approval、PreparedAction 使用同一 canonicalizer。

### P03-T07 Producer/Consumer Fixtures and Compatibility CI
- Goal：为共享 Contract 建 golden fixture、producer/consumer test 和 backward/forward matrix。
- Tests：旧 Minor fixture 可读；未知可选字段策略明确；Major fail/quarantine。
- Acceptance：旧版本 Adapter 放正常 `adapters/versioned/`，包含 sunset；不得出现 `legacy_contracts/`。

## Phase 完成定义

- 共享 Contract 只有一个代码 Owner 和 Registry。
- Schema、Fixture、Hash、兼容测试通过。
- 无业务模块复制 Envelope/Security/Receipt。
- 临时版本 Adapter 均有 PHASE22 删除或保留 ADR；不保留 Legacy 包。

## Validation

```bash
git diff --check
python tools/scripts/verify_wave1_contract_freeze.py
pytest -q tests/contracts tests/repo -k 'contract or wave1' -p no:cacheprovider
```

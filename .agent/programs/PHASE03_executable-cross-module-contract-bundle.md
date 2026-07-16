# PHASE03 Executable Cross-module Contract Bundle

phase_id: PHASE03
status: ready
depends_on: PHASE02
owner: Shared Contract Governance

## 订正说明

2026-07-16 撤回此前 `completed` 结论。现有 `platform/contracts`、Canonical JSON、Hash、Registry 和少量 Fixture 作为部分实现保留，但它们只覆盖 Wave 1 的一部分共享对象，尚未证明十一模块完整跨边界 Contract、真实 Producer/Consumer 接入、Web/Desktop 类型生成、版本兼容和重复定义清理。

本 Phase 不再以“Contract 类存在、8 个 focused tests 通过”作为完成标准。必须让 Contract Bundle 成为所有真实跨模块调用的唯一可执行边界。

## Phase 目标

把 accepted ADR、共享 Contract Registry 和十一模块所有跨 Owner 边界对象实现为完整、唯一、版本化的 Pydantic/JSON Schema Contract Bundle，并完成当前真实 Producer/Consumer 的接入或有期限版本 Adapter。

Contract Bundle 必须提供：

```text
owner and semantic version
canonical serialization and hash
JSON Schema and bundle manifest
producer fixture and consumer fixture
backward/forward compatibility policy
unknown major/enum/field behavior
Python import surface
Web/Desktop generated or verified client types
adoption and duplicate-definition guard
```

Domain Contract 不得依赖 Provider SDK、ORM、FastAPI、Vue、LangGraph Checkpoint 实现或 Observability SDK。

## Minimal Read Set

- ADR 0003、Wave 1 Registry 和全部 accepted ADR
- 十一份模块 Target 文档中的 Contract/Ownership/Failure 表
- PHASE01 Requirement Ledger 与调用链 Inventory
- PHASE02 API/Data/Compatibility Matrix
- 当前 Backend DTO、module contracts、event payload、Web/Desktop types 和真实调用者

## Current Anchors

```text
src/backend/zuno/platform/contracts/**
src/backend/zuno/agent/**/contracts*.py
src/backend/zuno/knowledge/**/contracts*.py
src/backend/zuno/memory/**/contracts*.py
src/backend/zuno/capability/**/contracts*.py
src/backend/zuno/platform/**/contracts*.py
src/backend/zuno/api/dto/**
apps/web/src/**/types*
apps/desktop/**
tests/contracts/**
```

## Allowed Paths

```text
src/backend/zuno/platform/contracts/**
module-owned contracts/**
src/backend/zuno/api/adapters/versioned/**
apps/web/src/product/contracts/**
apps/desktop/src/product/contracts/**
tests/contracts/**
tests/integration/**
tests/repo/**
tools/scripts/verify_*contract*.py
tools/scripts/generate_*contract*.py
docs/evidence/**
.agent/programs/work-products/**
```

## Forbidden Paths

- Provider SDK、ORM、FastAPI、Vue 或 LangGraph Checkpointer 类型进入 Domain Contract。
- 同名/同语义 Contract 在多个模块复制定义。
- 为兼容旧代码删除 Tenant、Scope、Epoch、Classification、Hash、Generation、Version、Correlation、Causation 或 Deadline。
- 把 Proposal、Receipt、Projection 和最终领域事实混为同一类型。
- 只导出 Schema、不接入真实 Producer/Consumer 就关闭 Phase。
- 创建 `legacy_contracts`、永久旧 DTO 或无 Sunset 的版本 Adapter。

## Work Packages

### P03-T01 Complete Contract Registry and Ownership Index

- Goal：从十一模块文档和 Requirement Ledger 生成完整 contract_name/major/minor/schema_hash/owner/producer/consumer/compatibility/adoption registry。
- Required：每个跨 Owner 对象只有一个 Owner；Registry 能检测缺失 Contract、重复 Owner、同版本不同 Schema 和未登记 Consumer。
- Tests：Registry 与模块 Contract 表双向一致；未知 Major、重复 Schema Identity 和 Owner 漂移被拒绝。
- Acceptance：Registry 是唯一跨模块 Contract 索引，不允许手工维护第二份事实源。

### P03-T02 Complete CrossModuleEnvelope and Transport-neutral References

- Goal：完整实现 Envelope、Payload/PayloadRef、Tenant/Workspace/Conversation/Run/Plan/Step/Action、Correlation/Causation、Idempotency、Generation、Security、Deadline、Trace、Classification、ContractRef 和 Hash。
- Tests：canonical round-trip、tamper、missing scope、stale schema、payload/ref 互斥、deadline、classification downgrade、correlation chain。
- Acceptance：Queue、API、Outbox、Tool、Model、Knowledge、Memory 和 Observability 复用同一 Envelope 或明确的 Owner-specific nested payload，不另造删减版。

### P03-T03 Complete Security, Identity, Failure and Control Contracts

- Goal：实现 Principal、Task/Session/Workload Identity、On-Behalf-Of、Security Context、Epoch、Authorization、Approval、Redaction、SecretLease Ref、Information Flow、FailureCode、Retry/Replan/Recovery/Reconciliation Reason。
- Tests：未知 Security Enum fail-closed；Epoch/Hash 绑定；Secret Material 拒绝序列化；Failure Namespace 与 Owner 稳定映射。
- Acceptance：模型 Proposal 不可解析成授权、批准或最终 Control Decision。

### P03-T04 Complete Product, Agent, Knowledge, Memory and Model Contracts

- Goal：实现 Product Command/Receipt/Projection/Event/AvailableAction、RuntimeRequest、TaskContract、GoalVersion、Plan/Step/Action/Dispatch/Join/Interrupt/RunOutcome、Knowledge Query/Outcome/Evidence/Citation/Control Proposal、ContextPack/Memory Candidate/Activation、Model Role/Call/Attempt/Usage/Cancel Contracts。
- Tests：Proposal 与 Final Fact 不可互换；Retry/Replan 分开；RunOutcome 不被 DTO 扁平化；Evidence/Citation/Memory/Usage Owner 不转移。
- Acceptance：当前 Backend Producer 和 Consumer 全部使用 Canonical Contract 或受控版本 Adapter。

### P03-T05 Complete Capability, Tool, Observability and Infrastructure Contracts

- Goal：实现 Capability/Skill Version/Requirement/Availability/Selection、Tool Definition/PreparedAction/Attempt/Observation/Execution/Effect/Reconciliation/Compensation、Telemetry/Audit/Eval/Release Gate、Outbox/Inbox/Idempotency/Lease/Fencing/Object/Checkpoint/Queue Receipts。
- Tests：HTTP 2xx、Queue ACK、Audit Persistence、Checkpoint Commit、Model Attempt 和 Tool Observation 不得解析为 EffectReceipt 或领域成功。
- Acceptance：每个 Receipt 明确只证明 Owner 范围内的事实。

### P03-T06 Canonical Serialization, Schema Export and Multi-client Type Pipeline

- Goal：统一 datetime/decimal/bytes/map ordering/null/unknown field、Canonical JSON/Hash、Schema Bundle Manifest，并生成或验证 Python/Web/Desktop 类型。
- Tests：跨进程/语言 Hash 稳定；字段顺序不影响 Hash；语义变化改变 Schema Hash；生成物无手工漂移。
- Acceptance：Idempotency、Approval、PreparedAction、Evidence、Projection 和 Audit 使用同一 canonicalizer；Client 不维护平行手写共享 Contract。

### P03-T07 Complete Producer/Consumer Adoption and Compatibility CI

- Goal：为 Registry 中每个共享 Contract 建 Producer Fixture、Consumer Fixture、Backward/Forward Matrix、真实集成测试和 Adoption Guard。
- Tests：旧 Minor 可读策略、未知可选字段、未知 Major fail/quarantine、真实 API/Queue/Store/Frontend Consumer、重复 Contract 扫描。
- Acceptance：所有当前 Producer/Consumer 已采用 Bundle 或登记有 Sunset 的 `adapters/versioned/`；不存在 `legacy_contracts/` 或无调用者的占位 Contract。

## Phase 完成定义

- Registry 覆盖十一模块所有跨 Owner Contract，并与模块文档和 Requirement Ledger 双向一致。
- 每个 Contract 有唯一 Owner、Schema、Canonical Hash、Producer Fixture、Consumer Fixture、Compatibility Policy 和 Adoption 状态。
- 当前真实 Backend Producer/Consumer 已接入；Web/Desktop 共享类型由 Schema 生成或有自动一致性验证。
- 重复 Envelope、Security、Failure、Receipt、Projection 和共享 DTO 已删除或进入有期限版本 Adapter。
- Contract、Integration、Compatibility、Tamper、Unknown Version/Enum 和跨语言 Hash 测试通过。
- Evidence 包含 Bundle Manifest Hash、完整 Contract 数量、Producer/Consumer Coverage 和未采用项；未采用项不为零时不得关闭。
- 所有 Work Package 经 Coordinator 批准，不能停留在 `completion_candidate`。

## Validation

```bash
git diff --check
python tools/scripts/verify_current_program.py
python tools/scripts/verify_wave1_contract_freeze.py
python tools/scripts/verify_phase03_contract_bundle.py
python tools/scripts/verify_complete_contract_adoption.py
pytest -q tests/contracts tests/integration tests/repo -k 'contract or schema or fixture or compatibility or canonical' -p no:cacheprovider
# Web/Desktop generated-contract consistency and build commands recorded in docs/evidence/
```

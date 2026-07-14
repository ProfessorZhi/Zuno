# PHASE05 Security Control Plane

phase_id: PHASE05
status: planned
depends_on: PHASE03, PHASE04
owner: Module 09 Security

## Phase 目标

实现 Principal、Tenant、Workspace、Scope、Effective Security Epoch、Authorization、Approval、SecretLease、Redaction、Audit Requirement 和 Revocation。Security 是唯一授权事实 Owner；旧 boolean approved、散落 middleware 判断和前端状态推断只作为迁移输入，最终删除。

## Minimal Read Set

- `docs/modules/09-security.md`
- Wave 1 Registry
- PHASE03 Security Contracts
- PHASE04 PostgreSQL/UoW/Outbox
- 当前 auth/security/middleware/approval/credential 代码

## Current Anchors

```text
src/backend/zuno/platform/security/**
src/backend/zuno/api/**/auth*
src/backend/zuno/api/**/approval*
src/backend/zuno/capability/**/credential*
src/backend/zuno/agent/**/approval*
apps/web/**/approval*
```

## Allowed Paths

```text
src/backend/zuno/platform/security/**
src/backend/zuno/platform/database/security/**
src/backend/zuno/api/product/dependencies/security*.py
tests/security/**
tests/integration/security/**
tests/fault/security/**
docs/evidence/**
```

## Forbidden Paths

- Agent Core、Tool、Product 自己批准权限。
- Secret Material 进入 Contract、Trace、Prompt 或前端。
- 旧 approval boolean 永久保留为权威事实。

## Work Packages

### P05-T01 Principal, Tenant, Workspace and Scope Domain
- Goal：实现 PrincipalContext、Tenant/Workspace membership、OrgUnit/Role/Grant、resource/action scope。
- Tests：cross-tenant deny、workspace isolation、role removal、scope narrowing。
- Acceptance：所有下游只引用 versioned context/decision ref。

### P05-T02 Effective Security Epoch
- Goal：实现 tenant/workspace/principal/policy epoch 聚合、hash、增量与缓存失效。
- Tests：revocation bump、stale epoch deny、并发 policy update、resume 重新验证。
- Acceptance：Epoch 不是时间戳猜测，持久且可审计。

### P05-T03 Authorization Decision Service
- Goal：实现 prepare/execute/read/download/admin 等 action 的确定性 Decision、reason、policy refs。
- Tests：allow/deny/conditional、unknown enum fail-closed、deadline、resource hash mismatch。
- Acceptance：Middleware 只传 Principal，不成为授权 Owner。

### P05-T04 Approval Aggregate and Binding
- Goal：实现 ApprovalRequest/Decision 状态机，绑定 prepared_action_hash、arguments、resource、epoch、deadline、approver scope。
- Tests：approve/deny/expire/revoke/replay、参数变更、epoch 变化、多 interrupt。
- Acceptance：旧 boolean approved 只通过迁移 Adapter 读取，PHASE22 删除。

### P05-T05 Secret Reference and Lease Broker
- Goal：实现 SecretRef、SecretLease、audience/scope/attempt/deadline、rotation/revocation。
- Tests：lease expiry、wrong audience、revoked secret、trace/error leakage、retry 不复用过期 lease。
- Acceptance：业务数据库和模型上下文不存 Secret。

### P05-T06 Redaction and Data Classification
- Goal：实现输入、持久化前、外部导出前两阶段 redaction 和 classification policy。
- Tests：PII/secret、redaction failure fail-closed、audit minimal envelope、external sink deny。
- Acceptance：Observability/Product 不得把 REDACT 改 ALLOW。

### P05-T07 Security Audit Requirement and Integration Gate
- Goal：实现高风险动作 mandatory audit requirement、prepare/execute 双 Gate 和统一 Port。
- Tests：audit store unavailable、approval 后 policy revoke、tool execute gate、download/citation authorization。
- Acceptance：散落 security checks 收口；生产路径无 `legacy_security` 目录和旧 boolean owner。

## Phase 完成定义

- Security 核心领域、持久化、决策、Approval、Epoch、Secret、Redaction 可用。
- Agent/Product/Tool 只能消费 Decision/Ref。
- Revocation、Replay、Audit unavailable 等 Fault Test 通过。
- 临时旧 Approval Adapter 有明确 PHASE22 删除任务。

## Validation

```bash
git diff --check
python tools/scripts/verify_security_target_protocols.py
pytest -q tests/security tests/integration/security tests/fault/security -p no:cacheprovider
```

# PHASE14 Capability and Skill Control Plane

phase_id: PHASE14
status: planned
depends_on: PHASE05, PHASE08
owner: Module 07 Capability / Skill

## Phase 目标

实现 CapabilityDefinition/Version、SkillDefinition/Version、Installation/Activation、AvailabilitySnapshot、CapabilityRequirement、Feasibility、Selection、Progressive Loading、Supply-chain Verification 和 Planner 可见投影。07 不执行 Tool Effect，不拥有 Approval/Credential/ToolAttempt。

## Minimal Read Set

- `docs/modules/07-capability-skill.md`
- PHASE03 Capability Contracts
- PHASE05 Security
- PHASE08 Planner/Step Requirement
- 当前 capability/skill/MCP registry/selector

## Current Anchors

```text
src/backend/zuno/capability/**
manifest/registry/selector/policy/execution/trace
MCP capability discovery
skill loading and prompt/context surfaces
```

## Allowed Paths

```text
src/backend/zuno/capability/domain/**
src/backend/zuno/capability/application/**
src/backend/zuno/capability/registry/**
src/backend/zuno/capability/projection/**
src/backend/zuno/platform/database/capability/**
alembic/**
tests/capability/**
tests/integration/capability/**
docs/evidence/**
```

## Forbidden Paths

- Capability 直接执行 Tool/SDK/MCP side effect。
- 07 拥有 Approval、Credential、ToolAttempt、EffectReceipt。
- Planner 读取未授权 Secret 或完整 Tool Adapter 实现。

## Work Packages

### P14-T01 Capability and Skill Versioned Domain
- Goal：实现 definition/version/schema/owner/source/signature/status/compatibility。
- Tests：immutable version、duplicate hash、invalid schema、supersession、tenant installation。
- Acceptance：Definition 与 Installation/Activation 分离。

### P14-T02 Installation, Activation and Policy Binding
- Goal：实现 tenant/workspace installation、active version、policy/security refs、CAS activation。
- Tests：stale activation、revocation、policy mismatch、cross-tenant、rollback version。
- Acceptance：激活不等于运行授权。

### P14-T03 Supply-chain and Integrity Verification
- Goal：签名/hash/source/license/dependency/runtime requirement 扫描，产生 conformance status。
- Tests：tampered package、unknown signer、malicious manifest、dependency mismatch、revoked source。
- Acceptance：未验证版本不能进入 AvailabilitySnapshot。

### P14-T04 AvailabilitySnapshot
- Goal：按 principal/scope/epoch/runtime health/installation/capacity 构建不可变 snapshot。
- Tests：epoch change、tool provider down、quota exhausted、snapshot expiry、concurrent activation。
- Acceptance：Planner 使用 snapshot，不实时遍历 registry。

### P14-T05 Capability Feasibility and Selection
- Goal：将 Step CapabilityRequirement 匹配 candidate、constraints、estimated cost/risk、selection reason。
- Tests：no candidate、multiple candidate deterministic order、security denied、resource conflict、fallback。
- Acceptance：Selection 是 Proposal/Projection，执行仍归对应 Owner。

### P14-T06 Progressive Loading and Skill Context
- Goal：只向模型加载必要 capability summary/schema/skill instructions，完整实现留在 runtime。
- Tests：token budget、prompt injection、stale schema、large registry、sensitive metadata。
- Acceptance：模型不能获得 Secret、未经授权 capability 或 adapter internals。

### P14-T07 Legacy Registry Cutover and Ownership Guard
- Goal：迁移旧 registry/selector/skill loader，删除 07 中的 tool execution/approval/credential owner 代码。
- Tests：planner contract、tool projection、bypass static guard、rollback。
- Acceptance：最终目录清晰；无 `legacy_capability`，无 `execution.py` 继续直接副作用；PHASE22 删除 alias。

## Phase 完成定义

- Version/Installation/Availability/Feasibility/Selection 可用。
- Supply-chain、Epoch、Progressive Loading 测试通过。
- 07/08 Ownership 无重叠。

## Validation

```bash
git diff --check
python tools/scripts/verify_capability_skill_target_protocols.py
pytest -q tests/capability tests/integration/capability -p no:cacheprovider
```

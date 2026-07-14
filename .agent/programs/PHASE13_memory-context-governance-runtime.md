# PHASE13 Memory and Context Governance Runtime

phase_id: PHASE13
status: planned
depends_on: PHASE08, PHASE12
owner: Module 05 Memory & Context

## Phase 目标

实现 Working/Session/Long-term Memory、Episodic/Semantic/Procedural 分类、MemoryCandidate、Governance、Activation、ContextPackVersion、压缩/重载、Privacy Delete、Reflexion Candidate 和负迁移防护。Memory 不冒充企业 Knowledge，也不直接改 Agent Plan。

## Minimal Read Set

- `docs/modules/05-memory-context.md`
- PHASE03 Memory Contract
- PHASE04 PostgreSQL/Object
- PHASE05 Security/Redaction
- PHASE08 ExecutionContextSnapshot
- PHASE12 Knowledge/Evidence refs
- 当前 memory engine/store/context/post_turn

## Current Anchors

```text
src/backend/zuno/memory/**
src/backend/zuno/agent/context/**
src/backend/zuno/agent/post_turn/**
DatabaseMemoryStore / local stores
ContextPack / Reflexion surfaces
```

## Allowed Paths

```text
src/backend/zuno/memory/**
src/backend/zuno/platform/database/memory/**
alembic/**
tests/memory/**
tests/integration/memory/**
tests/fault/memory/**
docs/evidence/**
```

## Forbidden Paths

- 模型直接写 ACTIVE Long-term Memory。
- Memory 保存企业文档 Evidence 的权威副本。
- Checkpoint 当 Session Memory，或 Session Summary 当 Knowledge。
- 敏感数据未经 Policy 持久化。

## Work Packages

### P13-T01 Memory Domain and Versioning
- Goal：实现 MemoryRecord/Version、scope、type、content ref/hash、source refs、confidence、validity、status、supersession。
- States：CANDIDATE→REVIEWING→APPROVED/REJECTED→ACTIVE→SUPERSEDED/REVOKED/DELETED。
- Tests：immutability、CAS activation、scope isolation、duplicate content、revocation。
- Acceptance：Working/Session/Long-term 生命周期明确。

### P13-T02 Candidate Extraction and Proposal Boundary
- Goal：从 RunOutcome/Feedback/Reflexion 生成 Candidate，不直接激活。
- Tests：unsupported claim、prompt injection、sensitive content、duplicate candidate、low confidence。
- Acceptance：模型只产生 proposal，包含 provenance 和 policy refs。

### P13-T03 Governance Review and Activation
- Goal：实现 deterministic policy、human/model-assisted review、approval/rejection、activation snapshot。
- Tests：review timeout、policy change、reviewer unauthorized、conflict with existing memory、rollback。
- Acceptance：最终 Activation 由 Memory Application Service 持久提交。

### P13-T04 ContextPackVersion Builder
- Goal：按 TaskContract、scope、budget、recency、relevance、sensitivity、negative transfer 选择不可变 ContextPack。
- Tests：budget overflow、stale memory、revoked item、cross-tenant、knowledge/memory dedup、deterministic order。
- Acceptance：Agent Core 固定版本 ref，resume 不隐式换包。

### P13-T05 Compression, Summary and Fidelity
- Goal：实现 recent window、task summary、compression ledger、source refs、reload policy 和 fidelity checks。
- Tests：summary loses critical constraint、source revoked、compression retry、token budget、reconstruction。
- Acceptance：摘要不能丢失权限、deadline、approval 或关键用户约束。

### P13-T06 Privacy Delete, Retention and Legal Hold
- Goal：实现 visibility revoke、candidate/active/index/cache cleanup、verification receipt、legal hold。
- Tests：delete during active run、backup/restore、shared memory reference、hold release、crypto shred。
- Acceptance：Audit/legal tombstone 按策略保留；前端不再显示已撤销内容。

### P13-T07 Legacy Memory Cutover and Reuse Evaluation
- Goal：迁移旧 store/四层 engine 到新 domain/ports，shadow context compare，记录 positive/negative transfer。
- Tests：old/new context diff、rollback、reuse trace、privacy delete、no double write after cutover。
- Acceptance：生产代码无 `legacy_memory` 包或永久双写；旧 read adapter 在 PHASE22 删除。

## Phase 完成定义

- Candidate→Governance→Activation→ContextPack 全链路可运行。
- Privacy Delete、Revocation、Compression/Fidelity、Negative Transfer 测试通过。
- Memory 与 Knowledge/Checkpoint 边界保持。

## Validation

```bash
git diff --check
python tools/scripts/verify_memory_context_target_protocols.py
pytest -q tests/memory tests/integration/memory tests/fault/memory -p no:cacheprovider
```

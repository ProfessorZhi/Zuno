# PHASE04 Contract Ownership Boundaries Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_ids:
  - ARCH-INFRA-046
  - ARCH-INFRA-047
  - ARCH-INFRA-056
status: implementation_available
date: 2026-07-18

## 边界

本证据证明三类 PHASE04 contract boundary 已经可机器验证：Index write、write receipt、visibility receipt 与 Knowledge acceptance 分层；IndexManifest/Acceptance 归 Knowledge/Memory 等领域 Owner，不归 Infrastructure receipt；PreparedToolAction 归 Tool Runtime，ActionProposal/Binding 归 Agent Core，SecurityApprovalDecision 归 Security，AuditPersistenceReceipt 归 Infrastructure，owner 不重叠。

本证据不证明 Milvus、Neo4j、BM25/Search 当前 server adapter、index rebuild drill、Tool Runtime effect 执行器、Security approval runtime 或完整 PHASE04 recovery set 已完成。

## Verification Results

- index_write_visibility_contract_layering: passed
- index_manifest_acceptance_domain_owner: passed
- write_receipt_not_domain_acceptance: passed
- visibility_consistency_explicit: passed
- prepared_tool_action_owner_distinct: passed
- prepared_tool_action_canonical_hash_fail_closed: passed
- phase_completion: blocked_official_checkpointer_and_full_recovery_set

## Commands

```powershell
python tools/scripts/verify_phase04_contract_ownership_boundaries.py
```

Expected result:

```text
PHASE04 contract ownership boundary verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_contract_ownership_boundaries.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `IndexWriteBatchV1` 由 Knowledge/Memory 生产给 Infrastructure，包含 tenant、workspace、index kind、source snapshot、schema spec、idempotency key、expected generation、security epoch 和 deadline。
- `IndexWriteReceiptV1` 与 `WriteVisibilityReceiptV1` 由 Infrastructure 生产给 Knowledge/Memory，只表达物理写入和可见性，不表达领域 acceptance。
- `KnowledgeVersionRefV1` 由 Knowledge 拥有，并持有 `index_manifest_hash` 与 `visibility_receipt_ref`，因此 IndexManifest/Acceptance 不归 Infrastructure。
- `PreparedToolActionV1` 由 Tool Runtime 拥有，`ActionProposalV1` / `ActionExecutionBindingV1` 由 Agent Core 拥有，`SecurityApprovalDecisionV1` 由 Security 拥有，`AuditPersistenceReceiptV1` 由 Infrastructure 拥有。
- `PreparedToolActionV1` 的 canonical hash 包含 tenant、workspace、principal、tool definition、operation、args hash、target resource hash、side effect class、credential scope、idempotency scope、policy snapshot、security epoch hash 和 deadline；operation 被篡改时 fail closed。

## Remaining Target

- Index adapter runtime、visibility probe、acceptance test 和 rebuild drill 仍是后续 target。
- Tool effect provider execution、approval runtime、audit durable-before-effect runtime 和 audit capacity fail mode 仍是独立 target。
- Official LangGraph PostgreSQL Checkpointer、PITR 和完整 RecoverySet 仍阻塞 PHASE04 关闭。

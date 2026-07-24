---
phase: PHASE11
status: completion_candidate
date: 2026-07-24
branch: integration/goal02-final-closure-repair
commit: 03fe48cdced867f5bf83c5fb3b9a3664556bf481
---

# PHASE11 Pre-Closure

## 结论

本 Pre-Closure 在 Goal02 final closure repair 中重新整理为 `completion_candidate`。当前证据已经覆盖 P11-T01～P11-T08 的主要生产路径、PostgreSQL 持久化、RabbitMQ cleanup contract、MinIO delete / restore、Human Review resume、outbox replay 和故障恢复线索，但 PHASE11 仍必须等待 Coordinator Closure；本文件不把 PHASE11 标记为 completed，也不声明 production ready。

## 证据包

- `docs/evidence/phase11-ingestion-source-lineage.md`
- `docs/evidence/phase11-p11-t04-t07-runtime.md`
- `docs/evidence/phase11-p11-t08-delete-recovery-cutover.md`
- `docs/evidence/phase11-e2e-fault.md`

## 关键结论

- Input 生产默认路径已进入 SourceObject → DocumentVersion → ParsePlan / Job / Attempt → ParseSnapshot → CanonicalDocumentIR → SourceSpan → Quality Gate / Human Review → IndexableDocumentSnapshot → Outbox Handoff。
- PostgreSQL 是 PHASE11 领域事实源；SQLite、本地队列和 legacy adapter 只保留为开发/兼容边界。
- Queue ACK 不冒充领域成功；Package A worker 在 domain commit / replay consistency 后才 ACK。
- Human Review task、decision receipt、resume handoff 与 DeleteLifecycle 已有 PostgreSQL 审计事实；Package A production worker 对 human_review 进入 `review_pending`，不再写成 failed。
- Human Review task 绑定 reviewer principal/scope、Security Decision Ref、Security Epoch、review idempotency key、trace_id 和 audit_ref。
- Human Review decision 已覆盖重复相同 Decision 幂等返回原 Receipt、不同 Decision 运行时 conflict，以及 PostgreSQL 唯一约束拒绝不同 decision hash。
- Human Review decision 已接入授权 Port，revoked reviewer 和 stale Security Epoch 均拒绝 approval，PostgreSQL 只留下 rejected receipt 且不创建 Indexable Snapshot / Handoff Outbox。
- Approved Review Resume 已覆盖从已有 ParseSnapshot 恢复、恰好一次 Indexable Snapshot / Handoff Outbox，以及 Knowledge handoff / outbox publish 均保持 pending replayable。
- Non-approved Review Decision 已覆盖 `rejected`、`expired`、`cancelled` 永不 resume handoff，PostgreSQL 不创建 Indexable Snapshot / Handoff Outbox。
- Delete / Restore 通过明确 Port 推进 visibility revoke、cleanup confirmation、MinIO physical delete、absence verification、fresh authorization 和 reconciliation。
- Delete coordinator 已覆盖重复 delete command replay 复用已有 PostgreSQL lifecycle 和 cleanup outbox，且相同 `delete_ref` 的不同 payload fail closed。
- Input 不直接拥有 Chunk、Entity、Relation、KnowledgeVersion 或 Index。

## 验证结果

- `python tools/scripts/verify_phase11_ingestion_source_lineage.py`：通过。
- `python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py`：通过。
- PHASE11 E2E/Fault 测试组合：`120 passed in 154.80s (0:02:34)`。
- P11-T08 focused regression：`tests/integration/test_phase11_ingestion_persistence_runtime.py` 为 `20 passed in 25.23s`；`tests/knowledge/test_ingestion_delete_restore.py` 为 `7 passed in 8.38s`。
- Delete coordinator idempotency focused regression：`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_duplicate_delete_after_snapshot_reuses_lifecycle_and_cleanup_outbox` 为 `1 passed in 10.13s`。
- Human Review decision focused regression：`tests/knowledge/test_ingestion_human_review.py` 为 `5 passed in 7.95s`；`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_human_review_resume_round_trips_review_task_and_receipt_after_restart` 为 `1 passed in 9.68s`。
- Human Review review_pending focused regression：`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_parse_attempt_can_wait_for_human_review_without_failure` 为 `1 passed in 9.07s`；`tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_quality_review_records_snapshot_without_indexable_handoff` 为 `1 passed in 8.61s`。
- Human Review binding focused regression：`tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_quality_review_records_snapshot_without_indexable_handoff` 为 `1 passed in 9.71s`；`tests/knowledge/test_ingestion_human_review.py` 为 `5 passed in 7.47s`。
- Human Review authorization focused regression：`tests/knowledge/test_ingestion_human_review.py` 为 `6 passed in 9.36s`；`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_review_decision_revoked_reviewer_rejects_without_handoff` 为 `1 passed in 12.32s`；Package A review_pending regression 为 `1 passed in 7.97s`。
- Approved Review Resume pending/replay focused regression：`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_approved_review_resume_persists_snapshot_and_outbox_once` 为 `1 passed in 14.23s`。
- Non-approved Review focused regression：`tests/integration/test_phase11_ingestion_persistence_runtime.py::test_ingestion_non_approved_review_never_resumes_handoff` 为 `3 passed in 10.76s`。
- Alembic head：`20260724_31 (head)`。

## Closure 边界

本 Pre-Closure 不声明 production ready、quality proven、PHASE11 completed、PHASE12 completed 或 PHASE09/10 当前化。Coordinator Closure 仍为 `pending`，PR #41 不得合并。

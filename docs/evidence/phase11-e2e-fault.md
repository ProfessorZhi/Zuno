---
phase: PHASE11
scope: full_phase_e2e_fault
status: passed
date: 2026-07-23
branch: integration/goal02-agent-core-ingestion-closure
commit: 932603014fefecaeb55291c0f0f6eff581c3812a
---

# PHASE11 E2E / Fault Evidence

## 结论

PHASE11 P11-T01～P11-T08 已在 Goal02 分支完成完整验证组合：生产默认 ingestion path、PostgreSQL UoW、RabbitMQ delivery / ACK / retry / DLQ / replay、MinIO object path、Parser Gateway、CanonicalDocumentIR、SourceSpan、Quality Gate、Human Review、Indexable Snapshot、Snapshot Outbox、Delete / Restore / Legal Hold 和 legacy upload/parser cutover 均有代码、迁移、测试或 verifier 证据。

本证据不声明 Zuno production ready、quality proven、PHASE12 completed 或完整 CI completed。

## 验证命令

```powershell
python tools/scripts/verify_phase11_ingestion_source_lineage.py
python tools/scripts/verify_phase11_legacy_upload_parser_cutover.py
pytest -q tests/repo/test_phase11_ingestion_source_lineage.py tests/integration/test_phase11_ingestion_persistence_runtime.py tests/integration/test_phase11_package_a_production_runtime.py tests/knowledge/test_parse_gateway_runtime.py tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_ingestion_human_review.py tests/knowledge/test_ingestion_snapshot_handoff.py tests/knowledge/test_ingestion_delete_restore.py tests/repo/test_phase11_legacy_upload_parser_cutover.py tests/knowledge/test_legacy_cutover_adapter.py tests/storage/test_pipeline.py -p no:cacheprovider --tb=short
alembic -c infra/db/alembic.ini heads
alembic -c infra/db/alembic.ini upgrade head
```

## 验证结果

- Source lineage verifier：通过。
- Legacy upload/parser cutover verifier：通过。
- PHASE11 E2E/Fault 测试组合：`120 passed in 154.80s (0:02:34)`。
- Alembic head：`20260724_25 (head)`。
- Alembic upgrade：通过。

## 覆盖范围

- P11-T01～T03：Package A production default path 证据来自 `docs/evidence/phase11-ingestion-source-lineage.md` 与 `tests/integration/test_phase11_package_a_production_runtime.py`。
- P11-T04～T07：Parser / IR / Review / Handoff 证据来自 `docs/evidence/phase11-p11-t04-t07-runtime.md`。
- P11-T08：Delete / Restore / Legacy Cutover 证据来自 `docs/evidence/phase11-p11-t08-delete-recovery-cutover.md`。

## 保留边界

- PHASE12 KnowledgeVersion / Standard RAG 尚未启动。
- PHASE09 / PHASE10 Product Backend / Web Desktop 尚未因 PHASE11 closure 提升为 Current。
- 完整 release gate、fixed benchmark、quality measurement 和 production readiness 仍由后续 PHASE20～PHASE22 负责。

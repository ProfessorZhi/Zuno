---
phase: PHASE11
scope: P11-T04..P11-T07
status: completion_candidate
date: 2026-07-23
branch: integration/goal02-agent-core-ingestion-closure
---

# PHASE11 P11-T04～T07 Runtime Evidence

## 结论

本证据包覆盖 P11-T04 Parser Adapter Conformance、P11-T05 CanonicalDocumentIR / SourceSpan / TransformLedger、P11-T06 Quality Gate and Human Review、P11-T07 Indexable Snapshot Handoff。

结论为 `completion_candidate`，不是 PHASE11 整体完成。PHASE11 仍需 P11-T08 Delete / Recovery / Legacy Parser Cutover 与完整 Phase Closure。

## 本轮实际变更

- 新增 PostgreSQL 审计表：
  - `ingestion_review_tasks`
  - `ingestion_review_decision_receipts`
- 新增 `IngestionRepository.record_review_task()`、`record_review_decision_receipt()`、`get_review_task()`、`get_review_decision_receipt()`。
- Package A production runtime 在质量闸门进入 `human_review` 时持久化 ReviewTask。
- 低质量文档不会创建 `ingestion_indexable_document_snapshots` 或 handoff outbox，但会留下 ParseSnapshot、QualityGateDecision 和 ReviewTask。

## 为什么本轮不重写 Parser / IR / Handoff

代码与测试已存在并通过以下覆盖：

- Parser adapters 已覆盖 Native、PDF、OCR/VLM fallback、Office、Archive、Markdown、HTML、Code，以及 encrypted / corrupt / oversized / sandbox-denied 等 typed failure。
- `CanonicalDocumentIR` 已包含 block、table、figure、SourceSpan 和 TransformLedger，并有 schema round-trip 与 SourceSpan 证据测试。
- `SnapshotHandoffRuntime` 已生成 immutable `IndexableDocumentSnapshotV1`，并要求质量闸门通过或人工复核批准后才允许创建 handoff。

缺口不在对象模型，而在 P11-T06 的生产数据库审计闭环：此前质量闸门只有 `review_task_ref` 字符串，没有 ReviewTask / ReviewDecisionReceipt 的 PostgreSQL 事实。本轮补齐该根因。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_agent_core_target_protocols.py
pytest -q tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider --tb=short
pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_quality_review_records_snapshot_without_indexable_handoff -p no:cacheprovider --tb=short
pytest -q tests/knowledge/test_parse_gateway_runtime.py tests/knowledge/test_document_ingestion_contract.py tests/knowledge/test_ingestion_human_review.py tests/knowledge/test_ingestion_snapshot_handoff.py tests/integration/test_phase11_ingestion_persistence_runtime.py tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_quality_review_records_snapshot_without_indexable_handoff -p no:cacheprovider --tb=short
alembic -c infra/db/alembic.ini heads
alembic -c infra/db/alembic.ini upgrade head
```

## 验证结果

- `git diff --check`：通过。
- `python tools/scripts/verify_current_program.py`：通过。
- `python .agent/scripts/verify_agent_system.py`：通过。
- `python tools/scripts/verify_docs_entrypoints.py`：通过。
- `python tools/scripts/verify_agent_core_target_protocols.py`：通过。
- `pytest -q tests/integration/test_phase11_ingestion_persistence_runtime.py -p no:cacheprovider --tb=short`：`6 passed in 18.20s`。
- `pytest -q tests/integration/test_phase11_package_a_production_runtime.py::test_gate_b_quality_review_records_snapshot_without_indexable_handoff -p no:cacheprovider --tb=short`：`1 passed in 8.45s`。
- P11-T04～T07 组合测试：`69 passed in 23.13s`。
- Alembic head：`20260724_24 (head)`。
- Alembic upgrade：通过。

## 剩余边界

- 本文件不关闭 P11-T08。
- 本文件不声明 PHASE11 completed。
- 本文件不把 PHASE12 Knowledge indexing 作为 Input 责任；Input 只提交 Indexable Snapshot / Outbox handoff。

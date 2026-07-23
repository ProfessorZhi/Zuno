# PHASE11 Package A Evidence Review

date: 2026-07-23
branch: integration/goal02-agent-core-ingestion-closure
status: reviewed
phase_id: PHASE11
scope: Package A evidence only

## 结论

Package A production default ingestion path 可作为 P11-T01～P11-T03 的 `completion_candidate` 输入。该结论来自 `docs/evidence/phase11-ingestion-source-lineage.md` 中 2026-07-22 之后的 Gate B/C 证据，而不是早期环境阻塞记录。

本审查不关闭 PHASE11，不批准 Coordinator Closure，也不证明 P11-T04～P11-T08。PHASE11 仍为 `in_progress`，Coordinator Approval 仍为 `pending_reopened`。

## 可采信证据

- Gate A：46 passed。
- Gate B/C Package A production runtime integration：32 passed，覆盖 PostgreSQL lease/fencing/replay、真实 MinIO ObjectRef 读取、PostgreSQL transactional outbox、RabbitMQ publish/consume/ACK/DLQ/replay 和 upload-to-snapshot-outbox。
- Package A failed replay Retry Outbox consistency：delivery settlement / persistence fencing / retry boundary 66 passed；upload replay / queue worker 22 passed。
- Package A 后续 lineage/fault gates 已补齐 retry counter、producer/workspace/trace/classification/version/header/payload/ParseJob pre-Inbox lineage，以及 DLQ replay counter、deadline propagation、filename/format lineage 等局部证据。

## 不可采信为 Closure 的内容

- 2026-07-20 早期 Gate B 记录中 PostgreSQL localhost:5432 connection timeout 属于历史环境阻塞，不能单独作为 passed。
- Package A 证据不覆盖 Parser Adapter Conformance、CanonicalDocumentIR / SourceSpan / TransformLedger、Quality Gate / Human Review、Indexable Snapshot Handoff 完整闭环、Delete / Recovery / Legacy Parser Cutover。
- Package A evidence 不等于 PHASE11 completed，也不等于 production ready 或 quality proven。

## 对后续 P11-T04～T07 的输入

- P11-T04 必须复用 Package A 的生产默认入口，不新增第二套 parser job/attempt/queue owner。
- P11-T05 必须把 SourceSpan、TransformLedger 和 CanonicalDocumentIR 建在 Package A 的 SourceObject / DocumentVersion / ParseSnapshot 事实链上。
- P11-T06 必须在 Indexable Snapshot 发布前强制 Quality Gate / Human Review 结论，不允许缺质量自动 handoff。
- P11-T07 必须只输出 immutable IndexableDocumentSnapshotV1 Envelope，通过 outbox handoff 给 Knowledge，不直接写 Chunk / Entity / Relation / KnowledgeVersion。

## 审查来源

- `docs/evidence/phase11-ingestion-source-lineage.md`
- `.agent/programs/PHASE11_durable-ingestion-and-source-lineage.md`
- `.agent/programs/work-products/phase11-readiness.yaml`
- `docs/modules/02-input-document-ingestion.md`

# PHASE11 Coordinator Closure Decision

status: reopened
phase_id: PHASE11
coordinator_approval: pending_reopened
phase11_state: in_progress
decision_time: 2026-07-19
reopened_at: 2026-07-20

## Closure Decision

原 PHASE11 Durable Ingestion and Source Lineage closure 结论已撤回。既有证据保留为历史审查输入和部分实现线索，但不再证明 PHASE11 completed。

当前决定：

- PHASE11 = `in_progress`
- Coordinator Approval = `pending_reopened`
- PHASE08 保持 `ready`，因为它只依赖 PHASE04、PHASE05、PHASE06、PHASE07
- PHASE12 保持 `planned`，等待 PHASE08 completed 与 PHASE11 completed

## 原审查输入

- PHASE04 Coordinator Closure：`docs/evidence/phase04-complete-infrastructure-blocker.md`
- PHASE05 Coordinator Closure：`docs/evidence/phase05-coordinator-closure.md`
- PHASE11 Pre-Closure：`docs/evidence/phase11-pre-closure.md`
- Source Lineage Evidence：`docs/evidence/phase11-ingestion-source-lineage.md`
- Input Runtime Batch Evidence：`docs/evidence/input-runtime-batch.md`
- Requirement Ledger：PHASE11 80 个 mandatory requirement 曾被标记为 `implementation_available`

## 撤回原因

PHASE11 原始完成定义要求生产默认 upload/parser 路径使用 PostgreSQL Repository/UoW、PHASE04 S3/MinIO、真实 RabbitMQ、lease/heartbeat/fencing、Parser Adapter Conformance、可执行 OCR/VLM 边界、Human Review receipt、Snapshot handoff、Delete/Legal Hold/Restore 和 Legacy Cutover。

当前 closure 依赖 LocalQueue、SQLite runtime batch、target-blocked OCR/VLM 诊断，以及未完整实现的 Human Review 状态机，不能覆盖完整 Mandatory Scope。

## 边界

Input / Document Ingestion 不拥有 Chunk、Entity、Relation、KnowledgeVersion 或 Knowledge Index；只向 Knowledge handoff immutable IndexableDocumentSnapshot。外部 parser、RabbitMQ、OCR/VLM 不可用时必须以 target-blocked diagnostics 暴露，不能冒充生产依赖成功。

## 重新关闭条件

只有 PHASE11 Closure Matrix 的 Mandatory 行全部达到 `completion_candidate` 或 `completed`，且 Requirement Ledger 中 PHASE11 80 项均有真实 Code/Test/Runtime Evidence 后，才能重新运行 PHASE11 Pre-Closure 与 Coordinator Closure。

# Goal02 Final Closure Repair Gap Audit

status: frozen
created_at: 2026-07-23
branch: integration/goal02-final-closure-repair
implementation_start_sha: d6c43dfc6a2063bf1b0571c608071388319d66e5
reopen_commit: 1b6b14d1

## 范围边界

本文件是本轮唯一局部 Gap Audit。范围冻结为：

- A. PHASE08 真实 Owner、Domain Commit、持久幂等和产品 Cutover。
- B. PHASE11 Human Review 的 `review_pending -> decision -> resume`。
- C. PHASE11 Delete / Restore 的真实外部资源和 Reconciliation。

本轮不做全仓开放审计，不实现 Dynamic DAG、并行 Plan、Replan、PHASE09、PHASE10、PHASE12+、新微服务、Kafka 或事件溯源。

## A. PHASE08 冻结 Gap

当前部分证据：

- `src/backend/zuno/agent/runtime/phase08.py` 已有固定 AgentRunGraph 和 StepExecutionGraph 节点。
- `phase08_postgres_checkpointer()` 使用官方 `langgraph-checkpoint-postgres` 的 `PostgresSaver`。
- `src/backend/zuno/platform/database/agent/domain.py` 已有 AgentRun、TaskContract、GoalVersion、PlanVersion、ExecutionContextSnapshot、BudgetReservation/Settlement 等 PostgreSQL repository 部分。
- `src/backend/zuno/agent/runtime/phase08_cutover.py` 已有 `shadow/canary/new_default/rollback` skeleton。

必须修复的 Gap：

1. `execute_owner_port` 当前只改 state，没有调用明确 Security / Model Gateway / Capability-Knowledge-Memory-Tool Owner / Trace-Audit / Budget / Agent Domain Repository Port。
2. Final Gate 当前只检查字符串 ref 是否存在，没有确定性检查 AnswerPolicy、Evidence、Security Decision、Budget、Step Acceptance、Citation/Schema、Deadline/Cancel、Publication Eligibility，也没有把 FinalGate 与 RunOutcome 幂等提交到 PostgreSQL。
3. `Phase08RunService.resume()` 在无有效 interrupt 时会重新 invoke graph，不能保证返回明确 conflict 或终态，也不能证明不重复 initialize、create_plan、model usage、effect、step commit、finalization。
4. `Phase08RunService.cancel()` 仍把 phase 设置为 `initialize`，不符合“Cancel 必须通过持久 Signal/Command 进入合法状态”的要求。
5. `SideEffectLedger` 是进程内 `set`，不能作为正式持久 Effect Ledger；同一 idempotency key 不同 payload 的冲突没有 PostgreSQL 唯一约束和 payload hash 证明。
6. `reconcile_generations()` 只有 `checkpoint_fail/checkpoint_ahead/orphan_run/reconciled`，未覆盖并定义 `aligned/domain_ahead/checkpoint_ahead/orphan_checkpoint/orphan_domain/stale_schema/stale_controller_epoch/unrecoverable_conflict` 的 owner、自动修复、重放、终止、Audit Event 和幂等规则。
7. Product Cutover skeleton 未证明模式来自可审计配置，未在已提交 Effect 后禁止 legacy fallback 重复执行，shadow/canary/new_default/rollback 缺 PostgreSQL 持久审计与主路径接入证据。

## B. PHASE11 Human Review Resume 冻结 Gap

当前部分证据：

- `src/backend/zuno/knowledge/ingestion/review.py` 有 `ReviewTask`、`ReviewDecisionReceipt` 和 `HumanReviewRuntime`。
- `src/backend/zuno/platform/database/ingestion/persistence.py` 有 `record_quality_decision()`、`record_review_task()`、`record_review_decision_receipt()`、`record_indexable_snapshot()` 和 replay receipt 查询。
- 现有 tests 覆盖部分 review decision、duplicate resume 与 handoff replay。

必须修复的 Gap：

1. 触发 review 时尚未形成一个明确生产事务方法，原子保存 ParseSnapshot、QualityDecision、ReviewTask、ParseJob/ParseAttempt=`review_pending`、Audit，并保证 ACK 只能在事务提交后发生。
2. ReviewTask 缺少完整绑定字段或验证：tenant/workspace、parse snapshot、document version、reviewer principal/scope、Security Decision Ref、Security Epoch、deadline、reason、idempotency key、trace/audit ref。
3. Review decision 当前以 receipt 记录为主，缺少数据库唯一约束驱动的 approved/rejected/expired/cancelled 幂等语义：相同 key 相同 decision 返回原 receipt，相同 key 不同 decision 返回 conflict。
4. 过期、撤权、Security Epoch 变化当前会被 runtime 转为 rejected，不能证明“拒绝审批并保留明确原因/receipt/audit”。
5. Approved Resume 缺少正式服务边界证明：必须从已有 ParseSnapshot 恢复，不重新 Parser/IR，幂等创建一个 IndexableDocumentSnapshot 和一个 Snapshot Handoff Outbox，Knowledge 不可用时保持 pending/replay。
6. Non-approved 路径需要证明永不创建 Indexable Snapshot / Handoff Outbox，late parser result 被拒绝并保留 receipt/audit。

## C. PHASE11 Delete / Restore / Reconciliation 冻结 Gap

当前部分证据：

- `src/backend/zuno/knowledge/ingestion/delete_restore.py` 有 `DeleteLifecycleReceipt` 和状态机 skeleton。
- `src/backend/zuno/platform/database/ingestion/persistence.py` 有 `record_delete_lifecycle()`、`reconcile_delete_lifecycle()` 和 ingestion outbox。
- 部分 tests 覆盖 legal hold、restore、late worker 和 delete lifecycle persistence。

必须修复的 Gap：

1. DeleteLifecycle 当前主要表达 receipt 状态，缺少明确 Port：VisibilityRevocationPort、KnowledgeCleanupPort、ObjectDeletePort、ObjectVerificationPort、AuthorizationPort、AuditPort。
2. Cleanup 没有形成完整 Transactional Outbox 链路：visibility revoked 与 cleanup outbox 同事务，RabbitMQ published 不等于 Knowledge cleanup confirmed。
3. MinIO delete 返回不能代替 absence verification；当前 `physical_delete_verified` 是布尔输入，缺少 ObjectVerificationPort 的真实 absence proof。
4. Delete chain 缺少完整状态 `delete_requested -> visibility_revoked -> cleanup_outbox_committed -> rabbitmq_published -> knowledge_cleanup_confirmed -> minio_object_deleted -> absence_verified -> delete_completed` 的 PostgreSQL 持久转移和幂等 key。
5. Crash-safe reconciliation 未覆盖 cleanup publish crash、cleanup 成功但确认丢失、cleanup 成功但 MinIO 失败、MinIO 成功但 DB commit 失败、object already missing、DLQ replay、stale fencing token。
6. Restore 需要重新授权并创建新的恢复事实，不能篡改删除历史，也不能自动恢复旧权限；当前 `restored_authorization=False` 只是字段，不是 AuthorizationPort 证明。

## 冻结执行顺序

1. PHASE08 Domain Repository / Owner Ports。
2. PHASE08 Resume / Reconcile / Persistent Idempotency。
3. PHASE08 Product Cutover。
4. PHASE08 Integration / Fault evidence。
5. PHASE11 Review Pending / Decision / Resume。
6. PHASE11 Delete / Restore / External Ports。
7. PHASE11 PostgreSQL / RabbitMQ / MinIO E2E / Fault evidence。

只有以上 Gap 全部由代码、迁移、真实依赖或明确环境阻塞证据证明后，才允许重新进入 Pre-Closure、Coordinator Review、Post-Closure 和 completed 状态更新。

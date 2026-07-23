# Goal02 Current / Gap 一次性审计

status: frozen_gap_list
branch: integration/goal02-agent-core-ingestion-closure
implementation_start_sha: d353e099845730ac54333607b156bbd2b440f94d
audit_scope: PHASE08 Deterministic Single Controller Runtime; PHASE11 Durable Ingestion and Source Lineage

## 启动检查

- 当前分支：`integration/goal02-agent-core-ingestion-closure`。
- 本地 HEAD 与远端 HEAD 一致：`d353e099845730ac54333607b156bbd2b440f94d`。
- 工作树干净。
- `9fc86d324f5cea51b19a33ede14518a38460a0e3` 与 `d353e099845730ac54333607b156bbd2b440f94d` 均在当前祖先链。
- Alembic 路径存在：`infra/db/alembic.ini` 与 `infra/db/alembic/versions`。
- Alembic single head：`20260720_20 (head)`。

## 读取事实源

- `AGENTS.md`
- `.agent/programs/current.md`
- `.agent/programs/program-manifest.yaml`
- `.agent/programs/task-execution-contract.md`
- `.agent/programs/PHASE08_deterministic-single-controller-runtime.md`
- `.agent/programs/PHASE11_durable-ingestion-and-source-lineage.md`
- `.agent/programs/work-products/requirement-ledger.yaml`
- `docs/modules/02-input-document-ingestion.md`
- `docs/modules/06-agent-core-planning-control.md`
- `docs/modules/09-security.md`
- `docs/modules/10-observability-eval.md`
- `docs/modules/11-infrastructure.md`
- `docs/governance/wave1-cross-module-contract-registry.md`
- `docs/status/production-readiness.md`

## Current

- PHASE04、PHASE05、PHASE06、PHASE07 已在 Program / Readiness 中记录为 `completed`，作为 PHASE08 和 PHASE11 的依赖输入；这不代表 Goal02 已完成。
- PHASE08 当前状态为 `ready`。代码中存在 `src/backend/zuno/agent/runtime/**`、`src/backend/zuno/agent/runtime_batch.py`、`src/backend/zuno/agent/durable_runtime.py`、`src/backend/zuno/agent/control_runtime.py` 以及对应 `tests/agent/**`。
- PHASE08 当前实现主要证明局部 runtime batch、SQLite/local store、graph route、interrupt/resume、reflection/replan、tool idempotency 和 grounded synthesis 等能力；尚未证明目标要求的 PostgreSQL domain fact + official LangGraph PostgreSQL checkpointer 默认产品主路径。
- PHASE11 当前状态为 `in_progress`。Package A 相关代码和证据存在，包括 `production_runtime.py`、RabbitMQ publisher/worker tests、retry/replay tests、Package A persistence tests，以及 `20260719_18_ingestion_source_lineage.py`、`20260720_19_ingestion_package_a_control.py`。
- PHASE11 已有 parser gateway、source object、parse control、lease recovery、snapshot handoff、human review、delete/restore 等测试文件；这些是可复用实现输入，不等于完整 PHASE11 B/C 与 Closure。

## 冻结 Gap List

本清单是 Goal02 后续执行的固定 Gap List。后续 Work Package 只围绕本清单收敛，不开放式追加新目标。

### P08-T01 AgentRun, TaskContract and GoalVersion Domain

- 已有实现：Agent runtime batch、runtime state、部分 durable runtime 和规划控制测试。
- 缺失 Contract：正式 TaskContract / GoalVersion aggregate 与产品请求默认入口绑定仍需证明。
- 缺失状态转换：create / authorize / start / cancel / fail / complete / illegal transition / optimistic conflict 的 PostgreSQL 事实状态机。
- 缺失恢复与幂等：duplicate request 与 optimistic conflict 的真实数据库证据。
- 缺失 Migration：Agent Core domain tables、唯一约束、generation / version 字段若未覆盖需新增 Alembic。
- 缺失测试和真实证据：PostgreSQL integration、illegal transition、duplicate request、optimistic conflict。

### P08-T02 Deterministic PlanVersion and Step Definition

- 已有实现：`planning`、`runtime/planning` 与局部 Plan 执行测试。
- 缺失 Contract：不可变 Deterministic Single-Step PlanVersion、StepDefinition hash、activation once。
- 缺失状态转换：draft / activated / obsolete / rejected。
- 缺失恢复与幂等：重复激活、无效依赖、unsupported executor 的稳定失败。
- 缺失 Migration：PlanVersion / StepDefinition 持久化与 hash 约束。
- 缺失测试和真实证据：hash stability、mutation reject、invalid dependency、unsupported executor。

### P08-T03 ExecutionContextSnapshot and Budget Ledger

- 已有实现：上下文与 runtime budget 表面、Model Gateway / Security / Observability batch 输入。
- 缺失 Contract：不可变 ExecutionContextSnapshot 与 security/context/model/capability/knowledge/answer policy refs。
- 缺失状态转换：budget reserve / consume / settle / release。
- 缺失恢复与幂等：stale epoch、deadline、budget insufficient、resume same refs。
- 缺失 Migration：snapshot 与 budget ledger 表、唯一约束和结算约束。
- 缺失测试和真实证据：预算耗尽不重复计费、resume 不变更 refs。

### P08-T04 Fixed AgentRunGraph

- 已有实现：LangGraph route / local graph tests。
- 缺失 Contract：initialize → authorize → context → plan → activate → execute → finalize 固定图作为产品默认入口。
- 缺失状态转换：node routing、checkpoint receipt、interrupt/wait/resume/cancel/deadline。
- 缺失恢复与幂等：restart 后从 domain generation 恢复。
- 缺失 Migration：graph control receipts 与 domain generation 对账字段。
- 缺失测试和真实证据：官方 PostgreSQL checkpointer integration、产品主路径调用 compiled graph。

### P08-T05 Fixed StepExecutionGraph

- 已有实现：model / knowledge / tool step executor 与局部测试。
- 缺失 Contract：load step → resolve input → security → proposal → owner port → observation → evaluation → acceptance。
- 缺失状态转换：success / blocked / denied / invalid proposal / retryable failure / abstain。
- 缺失恢复与幂等：Action Evaluation 与 Step Acceptance 每步必有，不因失败绕过。
- 缺失 Migration：StepRun、ActionRun、Observation、Acceptance 的持久事实。
- 缺失测试和真实证据：Security deny、invalid proposal、retryable / non-retryable failure、abstain。

### P08-T06 Domain/Checkpoint Generation Reconciliation

- 已有实现：PHASE04 checkpointer 证据与 Agent runtime checkpoint 表面。
- 缺失 Contract：domain_generation / checkpoint_generation 对账、安全 resume node。
- 缺失状态转换：domain ahead、checkpoint ahead、orphan run / dispatch detection。
- 缺失恢复与幂等：domain commit 后 checkpoint fail、checkpoint ahead、restart、duplicate resume、stale schema。
- 缺失 Migration：DomainCommitMarker、RecoveryWatermark、checkpoint receipt refs。
- 缺失测试和真实证据：真实 PostgreSQL + official checkpointer fault tests。

### P08-T07 Interrupt, Signal, Cancel and Deadline

- 已有实现：局部 interrupt/resume tests。
- 缺失 Contract：多 Interrupt、signal journal、approval/user input/external wait、cancel precedence、deadline。
- 缺失状态转换：pending / consumed / duplicate / stale / expired / cancelled。
- 缺失恢复与幂等：duplicate signal、wrong run/epoch、deny、expire、cancel while waiting、resume after restart。
- 缺失 Migration：Interrupt 与 SignalJournal 表及幂等约束。
- 缺失测试和真实证据：PostgreSQL restart / duplicate / stale signal fault tests。

### P08-T08 Legacy Runtime Shadow and Deterministic Cutover

- 已有实现：旧 `GeneralAgent`、workspace simple agent、runtime harness 与若干 legacy guard tests。
- 缺失 Contract：真实产品请求 shadow 到新 runtime、canary/default new/rollback、no double side effect。
- 缺失状态转换：shadow / canary / default_new / rollback。
- 缺失恢复与幂等：new runtime unavailable fallback、同一 request hash 比对。
- 缺失 Migration：cutover flag state 如果需要持久化，必须有 schema 或正式配置证据。
- 缺失测试和真实证据：产品主路径 shadow/canary/rollback focused tests。

### P11-T01 SourceObject and Object Integrity

- 已有实现：Package A upload/source object commit 代码、MinIO/ObjectStore 相关接口、source object tests。
- 缺失 Contract：upload init / commit 默认路径与 SourceObject / object manifest / dedup conflict 的完整证明。
- 缺失状态转换：staging / committed / quarantined / delete_intent。
- 缺失恢复与幂等：partial upload、hash mismatch、same content、tenant scope、malicious mime。
- 缺失 Migration：如现有 migration 未覆盖 dedup / conflict / manifest 约束，需补齐。
- 缺失测试和真实证据：真实 MinIO object commit integration 与 fault evidence。

### P11-T02 DocumentVersion and ParseSnapshot Domain

- 已有实现：DocumentVersion、ParseSnapshot、SourceSpan persistence 与 tests。
- 缺失 Contract：源内容变化创建 DocumentVersion；parser/model/config/schema 变化创建 ParseSnapshot。
- 缺失状态转换：version immutability、same source no duplicate、reparse。
- 缺失恢复与幂等：optimistic concurrency 与 replay receipt。
- 缺失 Migration：DocumentVersion / ParseSnapshot 唯一约束和 lineage hash 约束。
- 缺失测试和真实证据：PostgreSQL concurrency and reparse evidence。

### P11-T03 Parse Planner, Job, Attempt and Queue

- 已有实现：Package A production runtime、RabbitMQ publisher/worker、retry/replay tests。
- 缺失 Contract：parser route、job/attempt state、outbox dispatch、lease/fencing、heartbeat、retry/dead letter 完整默认路径证明。
- 缺失状态转换：queued / claimed / running / succeeded / failed / retry_scheduled / dead_letter / cancelled。
- 缺失恢复与幂等：worker crash、duplicate delivery、lease loss、retry exhausted、cancel/deadline。
- 缺失 Migration：若 Queue/Inbox/Attempt 状态约束不完整，需补齐。
- 缺失测试和真实证据：真实 RabbitMQ delivery / ACK / reconnect / DLQ runtime evidence。

### P11-T04 Parser Adapter Conformance

- 已有实现：Native、Markdown/Text、CSV、JSON、HTML、PDF、PPTX、image OCR、Archive、Code adapter 表面和 golden tests。
- 缺失 Contract：Native/Layout/PDF/OCR/VLM/Archive/Office adapter 统一 input/output/failure/quality/timeout/cancel。
- 缺失状态转换：typed failure、timeout、cancel、fallback。
- 缺失恢复与幂等：encrypted/corrupt/oversized、remote provider failure、sandbox。
- 缺失 Migration：通常不需要，除非 parser capability registry 持久化。
- 缺失测试和真实证据：Office adapter 深覆盖、OCR/VLM 不能只 target_blocked、remote parser security gate。

### P11-T05 CanonicalDocumentIR, SourceSpan and TransformLedger

- 已有实现：CanonicalDocumentIR、DocumentBlock、SourceSpan、PDF vertical source span tests。
- 缺失 Contract：Page、Block、Region、BBox、Reading Order、Table、Image、TransformLedger 完整 lineage。
- 缺失状态转换：schema round-trip、normalization provenance、source span validation。
- 缺失恢复与幂等：stable hash / serialization / replay。
- 缺失 Migration：IR artifact refs、source span persistence、transform ledger persistence。
- 缺失测试和真实证据：text PDF citation、table span、OCR bbox、normalization trace、schema round-trip。

### P11-T06 Quality Gate and Human Review

- 已有实现：review.py、human review tests、`blocked=review_pending` 修正。
- 缺失 Contract：publish / review / reject Quality Decision；ReviewTask created → review_pending → approved / rejected / expired / cancelled。
- 缺失状态转换：approved 后 snapshot handoff；reject/expire/cancel 不产生 Indexable Snapshot。
- 缺失恢复与幂等：approved 后不重新解析、不重复 Snapshot、不重复 Outbox；crash/restart 后恢复。
- 缺失 Migration：ReviewTask / Decision / Receipt / deadline / scope / security epoch / idempotency。
- 缺失测试和真实证据：duplicate decision、reviewer scope、Security Epoch、decision hash、approved restart。

### P11-T07 Indexable Snapshot Handoff

- 已有实现：handoff.py、snapshot handoff tests、outbox persistence。
- 缺失 Contract：immutable IndexableDocumentSnapshotV1 Envelope，version/span/security/delete refs。
- 缺失状态转换：created / queued / published / accepted / rejected / replayed。
- 缺失恢复与幂等：duplicate handoff、knowledge unavailable、outbox replay。
- 缺失 Migration：snapshot outbox uniqueness and payload/schema hash constraints。
- 缺失测试和真实证据：Input 不直接写 Knowledge Index 的 repo/contract guard 和 RabbitMQ outbox runtime evidence。

### P11-T08 Delete, Recovery and Legacy Parser Cutover

- 已有实现：delete_restore.py、legacy_cutover.py、delete/restore tests、legacy upload/parser cutover inventory。
- 缺失 Contract：visibility revoke → cleanup request → physical delete → verification；legal hold；restore；late worker；DLQ replay；stale lease；MinIO object missing。
- 缺失状态转换：delete requested / hidden / cleanup_requested / physically_deleted / verified / held / restored。
- 缺失恢复与幂等：duplicate delete/restore、delete during parse/review、late worker、crash recovery。
- 缺失 Migration：delete lifecycle receipts、legal hold binding、verification refs。
- 缺失测试和真实证据：真实 MinIO/RabbitMQ/PostgreSQL delete/recover E2E and fault evidence。

## 执行顺序

固定顺序：

1. P08-T01～P08-T03
2. P08-T04～P08-T07
3. P08-T08
4. PHASE08 Pre-Closure、Coordinator Review、Post-Closure
5. 复核 PHASE11 Package A Evidence
6. P11-T04～P11-T07
7. P11-T08
8. PHASE11 全链 E2E/Fault
9. PHASE11 Pre-Closure、Coordinator Review、Post-Closure
10. Goal02 最终一致性验证

## 状态边界

- 该审计只冻结 Gap List，不把 PHASE08 或 PHASE11 提升为 completed。
- PHASE08 remains ready。
- PHASE11 remains in_progress。
- PHASE12 remains planned。
- production ready not established。

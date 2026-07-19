# Program Closure Checklist

program: zuno-canonical-architecture-runtime-realization-v1
state: active
current_phase: PHASE11
program_version: 2

PHASE04 completed
PHASE05 completed / PHASE06 completed / PHASE07 completed / PHASE11 ready

## PHASE01–04 订正状态

- [x] 旧完成结论已撤回，已有产物保留为部分证据。
- [x] Program Manifest、Roadmap、Current 和 Phase 文件已改为完整范围完成标准。
- [x] PHASE01 完整 Current/Gap/Requirement 双向追踪重新关闭。
- [x] PHASE02 可执行 Adapter/Flag/Cutover/Rollback/Guard 重新关闭。
- [x] PHASE03 十一模块完整 Contract/Producer/Consumer Adoption 重新关闭。
- [x] PHASE04 PostgreSQL/RabbitMQ/Object/Checkpointer/Backup/Restore/Fault 重新关闭。
- [x] PHASE05 Security Control Plane 已由 Coordinator Closure 批准为 completed。
- [x] PHASE06 Observability Minimum Black Box 已由 Coordinator Closure 批准为 completed。
- [x] PHASE07 Model Gateway Runtime 已由 Coordinator Closure 批准为 completed。
- [x] PHASE11 ready；PHASE08 仍 planned。

## Phase 状态

- [x] PHASE01 Current Baseline and Requirement Ledger
- [x] PHASE02 Legacy Runtime Compatibility and Cutover Control
- [x] PHASE03 Executable Cross-module Contract Bundle
- [x] PHASE04 PostgreSQL Domain and Transaction Foundation
- [x] PHASE05 Security Control Plane
- [x] PHASE06 Observability Minimum Black Box
- [x] PHASE07 Model Gateway Runtime
- [ ] PHASE08 Deterministic Single Controller Runtime
- [ ] PHASE09 Product Surface Backend Runtime
- [ ] PHASE10 Web and Desktop Product Adaptation
- [ ] PHASE11 Durable Ingestion and Source Lineage
- [ ] PHASE12 Knowledge Version and Standard RAG
- [ ] PHASE13 Memory and Context Governance Runtime
- [ ] PHASE14 Capability and Skill Control Plane
- [ ] PHASE15 Tool Definition and Read-only Cutover
- [ ] PHASE16 Tool Side Effect and Reconciliation
- [ ] PHASE17 Dynamic Plan DAG and Parallel Control
- [ ] PHASE18 Agentic GraphRAG Inner Loop
- [ ] PHASE19 Final Synthesis, Publication and Reflexion
- [ ] PHASE20 Observability Eval, Benchmark and Release Gate
- [ ] PHASE21 Fault Recovery, Full E2E and Cutover
- [ ] PHASE22 Fixed Benchmark, Production Readiness and Closure

## Phase 完整关闭纪律

- [ ] 最小 Vertical Slice 只作为中间检查点，没有被用作 Phase Completion。
- [ ] Phase 范围内不存在仍标记 `target_not_current` 的 Mandatory Requirement。
- [ ] Readiness 中全部 Mandatory Work Package 为 `completed`。
- [ ] Coordinator Approval 为 `approved`，不是 `pending`。
- [ ] 真实默认路径接入，不只有 Stub、Mock、Fixture 或未调用的新目录。
- [ ] 正常、失败、恢复、并发、取消、幂等、安全和故障注入证据齐全。
- [ ] 真实依赖按要求运行；环境缺失被标记 Blocked，而非使用本地替代品关闭。
- [ ] Evidence 包含 Commit、环境版本、配置、Artifact Hash 和重现命令。
- [ ] 未运行完整 CI/E2E/Fault/Migration/Security/Load/DR 时没有宣称通过。

## 架构不变量

- [ ] Single Controller 是唯一产品控制器。
- [ ] 每个任务都有 Plan，direct answer 不绕过 Plan/Trace/Budget/Outcome。
- [ ] PlanVersion 激活后不可变；Replan 创建新版本。
- [ ] Retry、Replan、Recovery、Reconciliation 有不同 Owner 和状态。
- [ ] PostgreSQL Domain Fact 与 LangGraph Checkpoint 分离并可对账。
- [ ] Knowledge、Memory、Trace、Audit、Queue Receipt 不冒充彼此事实。
- [ ] 模型只产生 Proposal。
- [ ] Tool UNKNOWN 不盲目 Retry。
- [ ] Security、Approval、Audit、Idempotency 和 Secret Gate 不可绕过。
- [ ] Frontend 只消费 Authorized Projection / AvailableAction。

## Legacy 迁移

- [ ] 所有旧 Agent、Model、Retrieval、Tool、API、Frontend 执行入口有完整 Inventory。
- [ ] 每个兼容入口真实接入版本 Adapter 或被明确禁用/删除。
- [ ] 每个兼容 Flag 有可执行状态机、Owner、Audit、Rollback 和删除日期。
- [ ] 所有 Legacy Allowlist 有静态与动态 Guard、测试和移除条件。
- [ ] 旧数据库数据完成 Backfill/Cutover/Verification。
- [ ] 旧 API 只通过版本化 Adapter 兼容，不永久代理新架构。
- [ ] 旧 GeneralAgent 默认路径退出。
- [ ] 直接 Provider SDK 调用归零。
- [ ] 直接 Tool 执行旁路归零。
- [ ] 无必要 Legacy Alias 删除。

## Contract Bundle

- [ ] 十一模块跨 Owner Contract 在 Registry 中 100% 覆盖。
- [ ] 每个 Contract 有唯一 Owner、Schema、Canonical Hash 和版本策略。
- [ ] 每个 Contract 有 Producer Fixture 与 Consumer Fixture。
- [ ] 当前真实 Backend Producer/Consumer 已采用 Canonical Contract 或期限 Adapter。
- [ ] Web/Desktop 类型由 Schema 生成或自动验证一致。
- [ ] 重复 Envelope/Security/Failure/Receipt/Projection/DTO 定义已清理。
- [ ] Unknown Major/Enum、Tamper、Backward/Forward Compatibility 测试通过。

## 数据与基础设施

- [x] Alembic Upgrade/Downgrade、既有库接管、在线 DDL、drift 与 forward-fix 策略验证。
- [x] PostgreSQL 事务、约束、并发、隔离、连接丢失和恢复验证。
- [x] Outbox/Inbox 领域同事务、Duplicate、Gap、Redelivery、Hash Conflict 和 Crash 验证。
- [x] 真实 RabbitMQ Confirm、Reconnect、DLQ、Replay、Backpressure 和 Partition 验证。
- [x] Idempotency Claim 并发、冲突、过期、续租和结果丢失验证。
- [x] Lease/Fencing 拒绝晚到结果和旧 Worker 提交。
- [x] 真实 S3/MinIO Hash、Commit、Visibility、Delete、Restore、Legal Hold 验证。
- [ ] 真实 LangGraph PostgreSQL Checkpointer Restart/Resume/Generation/Schema Upgrade 验证。
- [ ] Backup/Restore、PITR（环境支持时）、Projection Replay 和 Recovery Reconcile 验证。
- [ ] Health/Readiness/Metrics/Operator Runbook 可用。

## Web / Desktop

- [ ] Web 使用 `apps/web/src/product/**` 新 Contract 和 Store。
- [ ] Desktop 使用版本化 Product Bridge。
- [ ] SSE Duplicate、Disconnect、Cursor Expire、Resync 验证。
- [ ] 多 Interrupt、Approve、Deny、Cancel、Reconcile UI 验证。
- [ ] UNKNOWN Effect 不展示普通 Retry。
- [ ] Provisional Content 与 Publication 分离。
- [ ] Citation、Artifact、Quality、Admin 独立授权。
- [ ] Web Browser E2E、Desktop Smoke、Build、Lint 通过。

## Runtime 与故障

- [ ] Deterministic Single-Step Plan 真实闭环。
- [ ] Dynamic DAG ReadySet/Dispatch/Send/Reducer/Join 真实闭环。
- [ ] Replan Barrier 和新 PlanVersion 验证。
- [ ] Native Interrupt/Resume/Cancel/Deadline 验证。
- [ ] Tool Approval/Effect/UNKNOWN/Reconciliation/Compensation 验证。
- [ ] Security Epoch 在等待期变化时旧授权失效。
- [ ] Crash、Duplicate、Out-of-order、Response Lost、Lease Loss 注入通过。
- [ ] Delete、Privacy Delete、Legal Hold、Restore 通过。

## Knowledge、Memory 与质量

- [ ] SourceSpan、KnowledgeVersion、Snapshot、Index Cutover 完成。
- [ ] Standard/Local/Deep/Agentic Profile 同集运行。
- [ ] EvidenceLedger、CitationLineage、Claim Binding 完成。
- [ ] Corrective Retrieval 与 Agent Core Replan 分离。
- [ ] ContextPack、Memory Governance、Privacy Delete 完成。
- [ ] Reflexion 只产生 Candidate，经过治理后复用。
- [ ] RAG Core Five 全部按版本化输入测量或如实 Blocked。
- [ ] Critical Slice、Citation/Safety、Cost/Latency Gate 完成。

## 最终证据与归档

- [ ] Requirement Ledger 的 Mandatory 项 100% 有 Code/Test/Trace/Eval/Evidence。
- [ ] Fixed Dataset 和 Case Set Hash 被跟踪。
- [ ] Benchmark Comparison 是 COMPARABLE 或如实 INCOMPARABLE。
- [ ] Release Gate 不把 BLOCKED/UNAVAILABLE/ERROR 写成 PASS。
- [ ] Production Readiness 只按真实证据更新。
- [ ] 完整 CI、E2E、Fault、Migration、Security、Load、DR 的运行情况披露。
- [ ] Program 文件和证据归档到 `docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/`。
- [ ] `.agent/programs/` 恢复 no-active。

## 当前未证明

```text
PHASE01-04 complete after correction
fixed benchmark measured pass
Agentic GraphRAG stable superiority
production-grade recovery
production security and operations
production ready
```

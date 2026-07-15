# Program Closure Checklist

program: zuno-canonical-architecture-runtime-realization-v1
state: active
current_phase: PHASE02

## Phase 状态

- [x] PHASE01 Current Baseline and Requirement Ledger
- [ ] PHASE02 Legacy Runtime Compatibility and Cutover Map
- [ ] PHASE03 Executable Cross-module Contract Bundle
- [ ] PHASE04 PostgreSQL Domain and Transaction Foundation
- [ ] PHASE05 Security Control Plane
- [ ] PHASE06 Observability Minimum Black Box
- [ ] PHASE07 Model Gateway Runtime
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

- [ ] 所有旧 Agent、Model、Retrieval、Tool、API、Frontend 执行入口有 Inventory。
- [ ] 每个兼容 Flag 有 Owner、状态、Rollback 和删除日期。
- [ ] 所有 Legacy Allowlist 有测试和移除条件。
- [ ] 旧数据库数据完成 Backfill/Cutover/Verification。
- [ ] 旧 API 只通过版本化 Adapter 兼容，不永久代理新架构。
- [ ] 旧 GeneralAgent 默认路径退出。
- [ ] 直接 Provider SDK 调用归零。
- [ ] 直接 Tool 执行旁路归零。
- [ ] 无必要 Legacy Alias 删除。

## 数据与基础设施

- [ ] Alembic Upgrade/Downgrade 或恢复策略验证。
- [ ] PostgreSQL 事务、约束、并发和隔离验证。
- [ ] Outbox/Inbox Duplicate、Gap、Redelivery 验证。
- [ ] Lease/Fencing 拒绝晚到结果。
- [ ] Object Store Hash、Commit、Delete、Restore 验证。
- [ ] Checkpointer Restart/Resume/Generation Reconcile 验证。
- [ ] Backup/Restore 与 Projection Rebuild 验证。

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

- [ ] Requirement Ledger 的 Mandatory 项有 Code/Test/Trace/Eval/Evidence。
- [ ] Fixed Dataset 和 Case Set Hash 被跟踪。
- [ ] Benchmark Comparison 是 COMPARABLE 或如实 INCOMPARABLE。
- [ ] Release Gate 不把 BLOCKED/UNAVAILABLE/ERROR 写成 PASS。
- [ ] Production Readiness 只按真实证据更新。
- [ ] 完整 CI、E2E、Fault、Migration、Security、Load、DR 的运行情况披露。
- [ ] Program 文件和证据归档到 `docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/`。
- [ ] `.agent/programs/` 恢复 no-active。

## 当前未证明

```text
fixed benchmark measured pass
Agentic GraphRAG stable superiority
production-grade recovery
production security and operations
production ready
```

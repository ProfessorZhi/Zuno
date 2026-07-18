# Production Readiness

status: implementation_available_measurement_blocked

本文件只维护状态事实源，不承担完整目标架构设计。完整产品与运行架构以 `docs/architecture/architecture.md` 为准。

## Current

Zuno 当前前台定位是 Lean Complete Agentic GraphRAG Product：本地优先、短期可闭环、可演示、可评测、可恢复的企业知识库 Agent 产品。

已具备的本地实现基线包括：

- Product & API：AgentChat、workspace、knowledge/file、message、model/tool DTO 和部分 task/event surface。
- Product Runtime Batch：`ARCH-PRODUCT-001` 到 `ARCH-PRODUCT-080` 已达到 `implementation_available`，统一 Web/Desktop/External API Contract、Product 不成为第二 Controller、Command Journal、CommandReceipt、幂等冲突、Projection/AuthorizedView/SSE/Cursor、Interrupt/Signal/Approval/UNKNOWN Effect、RunOutcome、Upload/Parse/Index/Searchable、Artifact/Publication/Delivery/Render/Read、全链路授权、ActionToken、Sanitization、Sandbox、Desktop typed IPC、External API replay protection、Delete/Correction/Retention、SLO 和 Target-to-Current evidence gate 均可机器验证；这只代表 Product Surface runtime batch 需求收口，不代表 PHASE05 或全 Program 关闭。
- Input & Knowledge：文本类文档 ingestion、local object store、durable ingestion store、chunk/index、retrieval、GraphRAG、evidence-span hardening surface 和真实 text PDF SourceSpan vertical slice。
- Input Runtime Batch：`ARCH-ING-001` 到 `ARCH-ING-080` 已达到 `implementation_available`，SourceObject 不可变保存、对象提交校验、ParseJob 生命周期、ParserWorker succeeded / blocked 路径、SourceSpan provenance、handoff envelope、queue/outbox/reconciler、缓存、格式保真、删除 receipt、legal hold、容量、安全 profile、Trace/API 和 Target-to-Current evidence gate 均可机器验证；这只代表 Input / Document Ingestion runtime batch 需求收口，不代表 PHASE11、PHASE04 或全 Program 关闭。
- Agent Core：GeneralAgent single loop、Model Gateway surface、统一 runtime service、Strategy / Plan-and-Execute / ReAct step execution、Reflection / Replan / Grounded Synthesis 和 Memory pre/post commit baseline。
- Agent Runtime Batch：`ARCH-AGENT-001` 到 `ARCH-AGENT-080` 已达到 `implementation_available`，Single Controller、Plan/ReAct/Reflection/Replan/Reflexion 分层、Runtime State 序列化恢复、Budget/Deadline、统一入口 Contract、Interrupt/Resume、Ref-only Graph State、RuntimeEvent/Trace、DAG、PlanVersion/GoalVersion、Step/Action/BranchResult、Effect UNKNOWN/Reconcile、Final Gate/Publication/RunOutcome、Failure/Budget/Recovery/ResultValidity/Outbox/Reconciler 和明确时间语义均可机器验证；这只代表 Agent Core runtime batch 需求收口，不代表 PHASE08 或全 Program 关闭。
- Model Gateway Runtime Batch：`ARCH-MODEL-001` 到 `ARCH-MODEL-088` 已达到 `implementation_available`，统一 Gateway 调用入口、Role/Operation 分离、不可变 Binding、Dispatch 前 Budget Gate、Call/Attempt 独立状态、单一 selected response、Structured Output 本地校验、Repair 确定性记录、Provider/Gateway/Product Streaming 分层、Stream Chunk 顺序去重校验、Timeout UNKNOWN/Reconcile、Retry/Fallback/Repair/Escalation/Replan Proposal 控制动作分离、Gateway 不激活 PlanVersion 或修改 RunOutcome、Embedding/Rerank/Vision/Transcription/Classification/Judge operation result contract、Judge 不作为唯一质量证明、Context Compression lineage/constraint/conflict/distortion-risk 保留、Memory/Security/Tool 输出只形成 candidate/proposal、Usage/Pricing/Quota/CAS 边界、Provider Health 窗口证据、Circuit key 隔离、Capability degrade/stale/revoke 生命周期、Operation-specific Adapter Conformance 与 SDK/API/Model Mapping 变化重验、未知 Provider signal fail-closed、Gateway Config Snapshot 内容寻址、Config Activation Validation/Replay/Canary/CAS/Rollback gate、Call 固定 Config Snapshot、Provider/Model 生命周期、Emergency Disable 和 Retirement 历史保留、Admission 层级容量、租户公平/Reserved Capacity/防饥饿、排队请求 Deadline/Security/Budget/Config 绑定、Overload Backpressure/Load Shedding 不绕过 Security/Validation/Usage/Audit/Budget gate、三类 Cache 分离、Result Cache 默认关闭且按租户和版本隔离、Cache Hit Reuse Receipt、Revocation/Deletion/Model Retirement/Validity 变化失效 Cache、版本化 Operational Command、高风险 Command Authorization/Approval/Expected Generation/Audit、独立 Retention Binding、Tombstone/Visibility Revocation/Physical Cleanup/Verification 删除顺序、Legal Hold、SLI/SLO 维度、Readiness 证据门禁、Adapter/API/SDK rollout、Provider API Sunset、Experiment gate/assignment、Shadow Call/Result、ResultValidity 事件、稳定 Failure Code、Suggested Control Action、Domain Event、Projection/Source Fact、Ownership、Versioned Envelope、Storage Layering、Compatibility Facade、Migration Integrity、Unknown quarantine、Fault Recovery 和 Current Evidence Gate 边界均可机器验证；这只代表 Model Gateway 模块本批需求收口，不代表 PHASE07 或全 Program 关闭。
- Capability & Tool：capability registry/control plane、tool adapters、MCP/tool surfaces、approval/resume/idempotency trace baseline。
- Capability Runtime Batch：`ARCH-CAP-001` 到 `ARCH-CAP-080` 已达到 `implementation_available`，Capability/Skill/Tool/Provider taxonomy、模型 proposal-only、CrossModuleEnvelope、unknown fail-closed/quarantine、SkillVersion immutability、discovery/load/resource/policy/supply-chain/revocation、CapabilityDefinition/Version/Binding/Conformance/FailureDomain/ConnectorPack、Availability Snapshot/Entry、Selection/Fallback、exact version pinning、inventory revalidation、result validity/reuse、security constraint/trust/audit ownership、domain/object/projection persistence boundary、transaction/outbox/CAS/recovery/fencing、generic adapter families、structured manifest、draft-only discovery、custom extension、UNKNOWN side-effect retry boundary、structured trace/event 和 Current Evidence Gate 均可机器验证；这只代表 Capability / Skill 模块本批需求收口，不代表 PHASE14 或全 Program 关闭。
- Tool Runtime Batch：`ARCH-TOOL-001` 到 `ARCH-TOOL-080` 已达到 `implementation_available`，ToolDefinition ownership、Planner projection boundary、Gateway execution path、immutable ToolVersion、Installation/Activation split、Exposure/Execute split、ActionProposal producer guard、PreparedToolAction aggregate、canonical hash、TargetResourceSet、EffectProfile、secret-free prepared action、approval/security/audit/claim/dispatch ordering、Attempt/Receipt/Effect/Reconciliation/Compensation/Cancellation 状态机、output firewall、CLI/OpenAPI/SDK/MCP/Browser/Async adapter governance、resource conflict、replan barrier、timeout/deadline、failure namespace、outbox/domain fact transaction、secret lease、sandbox fail-closed、capacity gate ordering、canary/drain/retired history/ObjectRef/legal hold/SLO/allowlist/readiness evidence 均可机器验证；这只代表 Tool Runtime 模块本批需求收口，不代表 PHASE15 或全 Program 关闭。
- Security Runtime Batch：`ARCH-SEC-001` 到 `ARCH-SEC-060` 已达到 `implementation_available`，Principal/WorkloadIdentity、tenant/workspace isolation、OrgUnit/Membership/DelegatedAdminScope、UI permission mapping、ActionSet、explicit deny/default deny、Grant lineage/revocation、Agent/Task/Session grant intersection、PolicyVersion/PAP/PDP/PEP/PIP/simulation/shadow、AuthorizationDecision/explanation/Epoch、input/output detection、classification/redaction/information flow/declassification/action intent、Memory/Multimodal/Knowledge/Citation/Model gates、PreparedToolAction hash、Approval replay protection、execute-time epoch review、UNKNOWN Effect reconciliation、MCP audience/token/On-Behalf-Of/CredentialVersionRef、SecretLease、Sandbox/Network/SSRF、SupplyChain/Break-glass/Incident、安全事实 outbox/audit/recovery/storage/checkpoint/product projection/eval/release/readiness evidence 均可机器验证；这只代表 Security 模块本批需求收口，不代表 PHASE05 或全 Program 关闭。
- Memory Runtime Batch：`ARCH-MEM-001` 到 `ARCH-MEM-060` 已达到 `implementation_available`，Working/Session/Long-term lifecycle、Episodic/Semantic/Procedural taxonomy、projection boundary、ContextPackVersion immutable read view、Session Summary/raw split、Candidate/Governance、MemoryVersion/source trace、retrieval scope/ACL/security ordering、compression/fidelity/tool payload/protected set/budget/token validation、rehydration、Reflexion/Procedural promotion、consolidation/freshness/conflict/state machines、projection publication/index receipt、idempotent commit/checkpoint/CAS/UNKNOWN reconcile、privacy delete/legal hold、安全边界、model proposal、model routing/upgrade、trace/outcome/eval、PostgreSQL/ObjectRef/rebuildable projection/CrossModuleEnvelope/readiness evidence 均可机器验证；这只代表 Memory 模块本批需求收口，不代表 PHASE13 或全 Program 关闭。
- Knowledge Runtime Batch：`ARCH-KNOW-001` 到 `ARCH-KNOW-030` 已达到 `implementation_available`，Agent Core retrieval decision boundary、EvidenceRequirement、snapshot/security/budget pinning、KnowledgeVersion acceptance、fixed retrieval graph、dynamic RetrievalPlan/RetrievalRound、多 retriever idempotent reducer、result validation、fusion/RRF/rerank/model slot、graph SourceSpan backlink、EvidenceLedger/Frontier、authority/temporal/conflict/citation eligibility、corrective retrieval、retry/correct/replan separation、stop/budget/cancellation/recovery/version lifecycle、deletion propagation、typed event、eval comparability、quality release gate 和 config separation 均可机器验证；这只代表 Knowledge 模块本批需求收口，不代表 PHASE12 或全 Program 关闭。
- XMOD Runtime Batch：`ARCH-XMOD-001` 到 `ARCH-XMOD-010` 已达到 `implementation_available`，共享 Contract 唯一 Owner、Producer/Consumer/Storage/Failure Owner 覆盖、Effective Epoch/Generation/Deadline、Receipt 不冒充领域成功、PreparedAction 四方拆分、Mandatory Audit Backpressure、Index Publish/Visibility 协议、Version/Enum compatibility、Failure Prefix 去重和 ADR/merge audit evidence 均可机器验证；这只代表 Wave 1 Cross-module Contract 治理批次收口，不代表 PHASE03 或全 Program 关闭。
- Governance & Observability：local trace/eval helpers、EnterpriseRAG paired eval runner、failure bucket diagnostics、profile completeness diagnostics 和 release gate output surface。
- Observability Runtime Batch：`ARCH-OBS-001` 到 `ARCH-OBS-024`、`ARCH-OBS-RAG-001` 到 `ARCH-OBS-RAG-020` 已达到 `implementation_available`，Trace Context/Tree、Envelope Versioning、Dedup、Ordering、Lifecycle、Agent/Model/Retrieval/Tool Trace、Security Redaction、Immutable Audit、Sampling、External Sink、Retention/Legal Hold、Eval Dataset/Case、Eval Recovery、Judge Policy、Failure Bucket、Benchmark Comparability、Profile Completeness、Release Gate、Measurement Status、Evidence Registry、Projection Rebuild、Quality Proven、RAG Core Five、Route/Graph/Source/Fusion/Rerank/Agentic Loop Trace、Evaluation Slice、Agent Efficiency、Quality-constrained Efficiency、Cost/Latency Attribution、Core Five Release Gate 和 Reproducible Evidence 均可机器验证；这只代表 Observability / Eval 模块本批需求收口，不代表 PHASE06 或全 Program 关闭。
- Local Infrastructure：SQLite/SQLModel、local object store、config、database/storage surfaces。
- PHASE04 P04-T04：PostgreSQL Idempotency Claim Service 已达到 `implementation available`，包含 tenant-scoped canonical hash、owner/generation/expiry fencing、并发单赢家、heartbeat、abort、进程退出后的 effect reconciliation 与 result replay；它不等于领域成功，也不代表 PHASE04 已关闭。
- PHASE04 P04-T05：PostgreSQL Lease/Fencing Worker Coordinator 已达到 `implementation available`，使用数据库时钟、epoch/fencing token、heartbeat、显式 handoff 与同事务 fenced commit，并通过进程崩溃、暂停、cancel race 和 TCP network partition；它不等于领域结果成功，也不代表 PHASE04 已关闭。
- PHASE04 P04-T01：默认数据库路径已达到 `implementation available`，应用由唯一 `PostgresRuntime` 提供 sync/async SQLModel Session Factory，DAO 写入由 Domain UoW 统一提交，并通过真实 PostgreSQL 的跨 Repository 回滚、tenant 隔离、timeout、取消、deadlock/serialization retry boundary、pool exhaustion 与 connection-loss recovery；它不代表 PHASE04 已关闭。
- PHASE04 P04-T02：PostgreSQL Schema 迁移已达到 `implementation available`，使用唯一 Alembic revision chain 和冻结显式 baseline，覆盖 31 张领域表与 24 张基础设施表的 ownership/drift、空库往返、既有库接管、重复迁移、迁移锁、在线 index、渐进约束验证、持久 backfill 与 forward-fix；它不代表领域数据已 cutover，也不代表 PHASE04 已关闭。
- PHASE04 P04-T03：Transactional Outbox/Inbox 与真实 RabbitMQ transport 已达到 `implementation available`，Product 领域事实与 Outbox、Inbox 与 Memory 领域事实分别同事务提交，覆盖 confirm、ACK/NACK、redelivery、duplicate、不同 hash quarantine、ordering watermark、retry/backoff、DLQ/replay、backlog、broker restart 与 network partition；Queue receipt 不等于领域成功，也不代表 PHASE04 已关闭。
- PHASE04 P04-T06 MinIO / Official Checkpointer 子范围：真实 S3-compatible Object Store 已达到 `implementation available`，覆盖 staging/multipart/hash/commit/visibility、PostgreSQL Manifest、commit 后失联对账、只读 committed gate、delete/restore、authorization、retention/legal hold、lifecycle、storage restart 与篡改 quarantine；官方 `langgraph.checkpoint.postgres.PostgresSaver` 已由 Coordinator Decision 批准并完成真实 PostgreSQL setup、多代 put、restart restore、thread isolation、writes、delta channel history、delete cleanup、infra generation 对账和 stale generation reject；Object 或 Checkpoint receipt 不等于领域成功，P04-T06 仍缺 graph-level interrupt/resume、official backup/restore、retention/prune、Product Projection Replay 和 combined-service fault 证据。
- PHASE04 P04-T07 Operator 子范围：PostgreSQL/RabbitMQ/MinIO 的 health、readiness、capacity、backlog、trace correlation、failure owner/retry owner/recovery owner 和结构化 operator snapshot 已达到 `implementation available`；该 telemetry 不产生 Eval verdict，也不代表官方 Checkpointer、PITR、完整 Projection Replay 或 PHASE04 已关闭。
- PHASE04 P04-T07 Capacity Admission 子范围：`ARCH-INFRA-031/032/033` 已达到 `implementation available`，PostgreSQL `infra_capacity_admissions` / `infra_capacity_reservations` 提供 drain flag、generation、atomic reservation、owner-fenced release 和 capacity exhaustion backpressure；它不证明所有 Product、Agent、Model 或 Tool runtime 已接入，也不关闭 PHASE04。
- PHASE04 P04-T07 Mandatory Audit 子范围：`ARCH-INFRA-054/055` 已达到 `implementation available`，PostgreSQL `infra_audit_channels` / `infra_mandatory_audit_events` 提供 durable audit receipt、effect 前 durable audit gate、fail-closed audit capacity mode，以及 effect observed 后 capacity 释放；它不证明所有 Tool、Product、Agent、Model 或 Security runtime 已接入，也不关闭 PHASE04。
- PHASE04 P04-T07 Cutover Snapshot 子范围：`ARCH-INFRA-048/049` 已达到 `implementation available`，PostgreSQL `infra_cutover_targets` / `infra_cutover_snapshots` / `infra_active_snapshot_refs` 提供 Generation/CAS cutover activation、active snapshot reference 和 retirement guard；它不证明完整 Product recovery cutover、PITR、RecoverySet 或 official Checkpointer restore，也不关闭 PHASE04。
- PHASE04 P04-T07 Recovery Watermark 子范围：`ARCH-INFRA-022/052` 已达到 `implementation available`，PostgreSQL `infra_recovery_watermarks` / `infra_recovery_sets` / `infra_recovery_set_members` 提供权威与派生组件 watermark 记录、RecoverySet 对齐检查、mismatch fail-closed 和 verification hash；它不证明 PITR、完整 Product Projection Replay 或 official Checkpointer restore，也不关闭 PHASE04。
- PHASE04 P04-T07 Secret Rotation / Tenant Hit 子范围：`ARCH-INFRA-035/058` 已达到 `implementation available`，PostgreSQL `infra_secret_versions` / `infra_secret_rotation_heads` / `infra_secret_leases` 提供 generation-fenced secret version activation、lease receipt 和 rollback，`infra_cross_tenant_hits` 提供跨租户命中的 fail-closed/quarantine 持久证据；它不证明生产 KMS、真实 secret material custody、PITR 或 official Checkpointer restore，也不关闭 PHASE04。
- PHASE04 P04-T07 PITR Alignment 子范围：`ARCH-INFRA-029` 已达到 `implementation_available`，`tools/scripts/verify_phase04_pitr_alignment.py` 使用临时真实 PostgreSQL primary/recovery 容器、WAL archive、`pg_basebackup` 和 recovery target time，证明 DB/Object/Checkpoint/Index RecoverySet 在 PITR 后保持对齐，target time 之后的 derived index watermark 不会混入恢复结果；它不证明 official Checkpointer restore、完整 Product Projection Replay 或 PHASE04 closure。
- PHASE04 P04-T07 DR Profile 子范围：`docs/governance/infrastructure-dr-profile.yaml` 已达到 `implementation available`，明确 PostgreSQL、Object Manifest/MinIO、RabbitMQ Outbox/Inbox、official Checkpointer、Product Projection Replay 和 PITR 的 RPO/RTO/Owner/Recovery Owner、验证命令、evidence ref 与 cutover fail-closed policy；official Checkpointer 仍 blocked，完整 Projection Replay 仍是 Phase-level blocker。
- PHASE04 P04-T07 Infrastructure Capability Profile 子范围：`InfrastructureCapabilityProfileV1` 和 `DataServiceCapabilityV1` 已达到 `implementation available`，profile frozen、显式 versioned、canonical hash 校验，Developer CI 与 Server Product 共用 typed contract，并声明每个 Data Service 的 config hash、supported/unsupported semantics 和 authoritative/rebuildable 边界；它不代表 official Checkpointer、PITR、完整 RecoverySet 或企业 index adapter 已完成。
- PHASE04 P04-T07 Backup/Service Boundary 子范围：`ARCH-INFRA-026/041` 已达到 `implementation available`，Backup Scope/RPO/Encryption/Verify profile 和 PostgreSQL/RabbitMQ/Object/Checkpoint typed service boundary 均可机器验证；它不证明生产 encrypted backup、PITR、完整 RecoverySet 或 official Checkpointer restore。
- PHASE04 P04-T07 Checkpoint Boundary / Version 子范围：`ARCH-INFRA-021/023` 已达到 `implementation available`，`agent_runtime_checkpoints` 与 `infra_checkpoints` 的 owner/receipt 边界、`Checkpoint Commit != Domain Commit`、以及 CHECKPOINT adapter/schema unknown version fail-closed 均可机器验证；它不证明 official LangGraph PostgreSQL Checkpointer runtime 已安装或可恢复。
- PHASE04 P04-T07 Restore/Cutover Completion Gate 子范围：`ARCH-INFRA-027/028/053` 已达到 `implementation available`，backup completed、restore isolated before cutover 和 recovery cutover explicit allow 均由 fail-closed gate 保护；它不证明完整 Backup/Restore/PITR、RecoverySet 或 official Checkpointer restore。
- PHASE04 P04-T07 Infrastructure Docs Governance 子范围：`ARCH-INFRA-001/002` 已达到 `implementation available`，Infrastructure 文档的 Current/Target/Future/Explicitly Not Selected 分层、唯一正式 Target 文档、Agent 镜像、architecture canonical 四文件集合与 entrypoint verifier 均可机器验证；它不证明任何 runtime adapter 或恢复闭环。
- PHASE04 P04-T07 Infrastructure / Domain Boundary 子范围：基础设施 receipt 边界已达到 `implementation available`，Queue ACK、RabbitMQ delivery、Object Commit、Idempotency Claim、Object Manifest visibility 和 operator telemetry 均被 verifier 固定为不能解释成领域成功；领域终局仍由 Product、Input、Knowledge、Agent Core、Memory、Tool 等 owner 持有。
- PHASE04 P04-T07 Reconciler Supervision Boundary 子范围：`ARCH-INFRA-039` 已达到 `implementation available`，IdempotencyWorkerSupervisor 的 owner/generation/expiry fencing、reconcile/no-reexecution，以及 LeaseWorkerCoordinator 的 heartbeat、同事务 fenced commit、crash handoff 和 PostgreSQL partition fail-closed 均有机器证据；它不证明所有产品 Reconciler 已接入。
- PHASE04 P04-T07 Infrastructure Typed Port 子范围：Local/Developer CI 与 Server Product 已共用同一 `InfrastructureCapabilityProfileV1` / `DataServiceCapabilityV1` typed port surface，并覆盖 PostgreSQL、RabbitMQ、Object、Checkpoint、Vector、Graph、Lexical、Cache、Secret 和 Telemetry service kind；unknown service kind fail closed，但 official Checkpointer 等 target adapter 仍未完成。
- PHASE04 P04-T07 Tenant Isolation Profile 子范围：`TenantIsolationProfileV1` 已达到 `implementation available`，Infrastructure Capability Profile 中每个 service kind 都有 tenant scope、默认 target、强隔离选项、cross-tenant action 和 evidence ref；运行时 hit gate 由 Secret Rotation / Tenant Hit 子范围补证。
- PHASE04 P04-T07 Tenant Physical Constraints 子范围：`ARCH-INFRA-034` 已达到 `implementation available`，PostgreSQL、RabbitMQ、Object ref/MinIO 和 Operator telemetry 的当前证据把 tenant scope 放入物理键、协议 header、object target/auth hook 或 snapshot 约束；它不证明 official Checkpointer，运行时 cross-tenant hit quarantine/fail-closed 由 `ARCH-INFRA-058` gate 补证。
- PHASE04 P04-T07 Upgrade Compatibility Profile 子范围：`UpgradeCompatibilityProfileV1` 已达到 `implementation available`，Infrastructure Capability Profile 中每个 service kind 都有显式 adapter/schema version、read/write/rollback compatible versions、unknown-version fail-closed action 和 canonical content hash；它不证明 live rolling upgrade、official Checkpointer integration 或完整 recovery replay。
- PHASE04 P04-T07 Adapter Conformance Profile 子范围：`AdapterConformanceProfileV1` 已达到 `implementation available`，Developer CI 与 Server Product 对每个 service kind 共用 conformance suite version、supported/unsupported semantics、required test refs 和 evidence ref，并对 unsupported local semantic fail-fast；它不证明所有未来 enterprise adapter 已实现。
- PHASE04 P04-T07 Release Provenance Manifest 子范围：`ReleaseManifestV1` 已达到 `implementation available`，本地真实 PostgreSQL/RabbitMQ/MinIO 的 source commit、运行中 image id bundle、Compose network/port refs、config hash、migration versions、adapter versions、compatibility evidence 与 provenance refs 可机器验证；它不证明 production application image release、外部 SBOM/signing、official Checkpointer 或完整 recovery replay。
- PHASE04 P04-T07 Redis Optional Boundary 子范围：`DataServiceCapabilityV1` 中 Redis/CACHE boundary 已达到 `implementation available`，Redis 只作为 optional acceleration cache，非权威、可从来源重建，且不进入 PHASE04 required real services 或 release adapter provenance；它不证明 Redis HA、failover、rate-limit acceleration 或 enterprise deployment。
- PHASE04 P04-T07 Derived Index Boundary 子范围：`DataServiceCapabilityV1` 中 VECTOR/Milvus、GRAPH/Neo4j 和 LEXICAL/BM25/Search boundary 已达到 `implementation available`，三者均为 versioned、non-authoritative、rebuildable from source，且不进入 PHASE04 required release adapter provenance；它不证明这些 server adapter、visibility receipt、acceptance gate 或 rebuild drill 已实现。
- PHASE04 P04-T07 Contract Ownership Boundary 子范围：`ARCH-INFRA-046/047/056` 已达到 `implementation available`，Index write/receipt/visibility 与 Knowledge acceptance 分层、IndexManifest/Acceptance 归领域 Owner、PreparedToolAction/ActionProposal/SecurityApproval/AuditPersistence owner 不重叠均可机器验证；它不证明 index adapter runtime、Tool effect runtime 或 audit durable-before-effect runtime 已完成。

## Short-term Closure Gap

P0：

- Agentic GraphRAG fixed benchmark 跑通并达到 baseline gate。
- 所有真实模型调用统一进入 Model Runtime / Gateway。
- 统一 Agent Core 真实闭环：Strategy、Plan-and-Execute、ReAct、Observation、Reflection、Replan、Reflexion、Memory 和 Retrieval 进入同一条可执行、可恢复、可测量链路。
- Corrective Agentic GraphRAG：`RETRIEVE_MORE -> replan -> execute_step` 真实回路、EvidenceLedger 和 failure bucket corrective action 可观测。
- Agent run trace 持久化并可查看。

P1：

- task / planner / retrieval / approval 状态本地持久化。
- 至少一个真实 text PDF parser 已跑通 source span citation；扫描/OCR PDF 仍返回 needs_ocr，不 fake index。
- 2-3 个真实 Tool 完成 approval / timeout / trace 闭环。
- Memory ContextPack 在真实 AgentChat 中可观测。
- Reflexion candidate -> review -> approved -> future ContextPack reuse。
- Skill metadata -> instruction -> resource 的渐进式加载 trace。

P2：

- 前端 E2E、项目演示脚本和可复现启动方式。

## Measurement Blocked

Agentic GraphRAG 当前不能写成 quality completed。

```text
implementation available
measurement blocked
quality not yet proven
```

blocked 原因：

- PHASE13 sample-8 已运行 EnterpriseRAG paired runner，但本地 profile runner 因 embedding model/base_url 未配置而输出 `blocked_not_measured`，`measured_case_count=0`。
- PHASE13 sample-80 仍因仓库没有 tracked fixed 80-case set 而 blocked。
- release gate 现在只在 `standard_rag`、`deep_graphrag` 和 `agentic_graphrag` 都完成同一 fixed case set 时写 `fixed_benchmark`；profile 不完整时输出 `profile_completeness.blocked_reason`。

证据入口：

- `docs/evidence/unified-agent-runtime-phase13-release-gate.md`
- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/closure-summary.md`

必须保留的质量门：

```text
Agentic Recall@5 >= standard_rag
Evidence Text Available@5 >= 0.60
Source Doc Citation Accuracy >= 0.85
Citation Accuracy >= 0.30
Answer Correctness >= standard_rag
Unsupported Claim Rate 不得恶化
```

blocked、prepared、runtime observed 和 measured 必须严格区分。缺 trace 字段时输出 `unavailable_due_to_missing_trace_fields`，不得编造 failure bucket。

## Completed

近期可作为 completed 的内容只限已经由代码、测试、trace/eval 或 verifier 支撑的本地实现基线和文档/guardrail 收口。

历史 program 完成事实保留在：

- `docs/history/programs/README.md`

历史完成不等于当前 quality gate 已通过。

## Future Optional

以下内容是可选未来扩展，不是短期 blocker：

- Redis 高级缓存、Kafka、Kubernetes、Service Mesh 和多区域部署。
- Managed PostgreSQL / Managed Queue / Managed Object Store 是部署形态选择，不是当前本地实现完成证据。
- 外部 Milvus / Neo4j 集群和分布式 graph/vector index 的企业级部署。
- 复杂 SSO / DLP / Vault、Firecracker。
- 大规模在线评测平台和企业运维门户。
- 大量 parser/provider 并行接入、OCR/VLM enrichment 平台化。
- Single Controller 下多 Agent Role 协作是未来可兼容方向；产品级自治 Multi-Agent runtime 仍是更长期 Future Optional。

PostgreSQL、RabbitMQ 和 MinIO / S3-compatible Object Store 的 canonical integration path 已有真实本地 Docker 证据并达到 `implementation available`；SQLite、本地对象存储和本地队列仍只作为 Developer/CI adapter 保留。官方 LangGraph PostgreSQL Checkpointer 与完整恢复闭环尚未完成，因此 PHASE04 和整个产品仍不能声明完成或 production ready。

# Production Readiness

status: implementation_available_measurement_blocked

本文件只维护状态事实源，不承担完整目标架构设计。完整产品与运行架构以 `docs/architecture/architecture.md` 为准。

## Current

Zuno 当前前台定位是 Lean Complete Agentic GraphRAG Product：本地优先、短期可闭环、可演示、可评测、可恢复的企业知识库 Agent 产品。

已具备的本地实现基线包括：

- Product & API：AgentChat、workspace、knowledge/file、message、model/tool DTO 和部分 task/event surface。
- Input & Knowledge：文本类文档 ingestion、local object store、durable ingestion store、chunk/index、retrieval、GraphRAG、evidence-span hardening surface 和真实 text PDF SourceSpan vertical slice。
- Agent Core：GeneralAgent single loop、Model Gateway surface、统一 runtime service、Strategy / Plan-and-Execute / ReAct step execution、Reflection / Replan / Grounded Synthesis 和 Memory pre/post commit baseline。
- Capability & Tool：capability registry/control plane、tool adapters、MCP/tool surfaces、approval/resume/idempotency trace baseline。
- Governance & Observability：local trace/eval helpers、EnterpriseRAG paired eval runner、failure bucket diagnostics、profile completeness diagnostics 和 release gate output surface。
- Local Infrastructure：SQLite/SQLModel、local object store、config、database/storage surfaces。
- PHASE04 P04-T04：PostgreSQL Idempotency Claim Service 已达到 `implementation available`，包含 tenant-scoped canonical hash、owner/generation/expiry fencing、并发单赢家、heartbeat、abort、进程退出后的 effect reconciliation 与 result replay；它不等于领域成功，也不代表 PHASE04 已关闭。
- PHASE04 P04-T05：PostgreSQL Lease/Fencing Worker Coordinator 已达到 `implementation available`，使用数据库时钟、epoch/fencing token、heartbeat、显式 handoff 与同事务 fenced commit，并通过进程崩溃、暂停、cancel race 和 TCP network partition；它不等于领域结果成功，也不代表 PHASE04 已关闭。
- PHASE04 P04-T01：默认数据库路径已达到 `implementation available`，应用由唯一 `PostgresRuntime` 提供 sync/async SQLModel Session Factory，DAO 写入由 Domain UoW 统一提交，并通过真实 PostgreSQL 的跨 Repository 回滚、tenant 隔离、timeout、取消、deadlock/serialization retry boundary、pool exhaustion 与 connection-loss recovery；它不代表 PHASE04 已关闭。
- PHASE04 P04-T02：PostgreSQL Schema 迁移已达到 `implementation available`，使用唯一 Alembic revision chain 和冻结显式 baseline，覆盖 31 张领域表与 10 张基础设施表的 ownership/drift、空库往返、既有库接管、重复迁移、迁移锁、在线 index、渐进约束验证、持久 backfill 与 forward-fix；它不代表领域数据已 cutover，也不代表 PHASE04 已关闭。
- PHASE04 P04-T03：Transactional Outbox/Inbox 与真实 RabbitMQ transport 已达到 `implementation available`，Product 领域事实与 Outbox、Inbox 与 Memory 领域事实分别同事务提交，覆盖 confirm、ACK/NACK、redelivery、duplicate、不同 hash quarantine、ordering watermark、retry/backoff、DLQ/replay、backlog、broker restart 与 network partition；Queue receipt 不等于领域成功，也不代表 PHASE04 已关闭。
- PHASE04 P04-T06 MinIO 子范围：真实 S3-compatible Object Store 已达到 `implementation available`，覆盖 staging/multipart/hash/commit/visibility、PostgreSQL Manifest、commit 后失联对账、只读 committed gate、delete/restore、authorization、retention/legal hold、lifecycle、storage restart 与篡改 quarantine；Object receipt 不等于领域成功，P04-T06 仍被官方 LangGraph PostgreSQL Checkpointer 关键依赖阻塞。
- PHASE04 P04-T07 Operator 子范围：PostgreSQL/RabbitMQ/MinIO 的 health、readiness、capacity、backlog、trace correlation、failure owner/retry owner/recovery owner 和结构化 operator snapshot 已达到 `implementation available`；该 telemetry 不产生 Eval verdict，也不代表官方 Checkpointer、PITR、完整 Projection Replay 或 PHASE04 已关闭。
- PHASE04 P04-T07 DR Profile 子范围：`docs/governance/infrastructure-dr-profile.yaml` 已达到 `implementation available`，明确 PostgreSQL、Object Manifest/MinIO、RabbitMQ Outbox/Inbox、official Checkpointer、Product Projection Replay 和 PITR 的 RPO/RTO/Owner/Recovery Owner、验证命令、evidence ref 与 cutover fail-closed policy；它不证明完整恢复演练，official Checkpointer 仍 blocked，PITR 与 Projection Replay 仍是 `target_not_current`。
- PHASE04 P04-T07 Infrastructure Capability Profile 子范围：`InfrastructureCapabilityProfileV1` 和 `DataServiceCapabilityV1` 已达到 `implementation available`，profile frozen、显式 versioned、canonical hash 校验，Developer CI 与 Server Product 共用 typed contract，并声明每个 Data Service 的 config hash、supported/unsupported semantics 和 authoritative/rebuildable 边界；它不代表 official Checkpointer、PITR、完整 RecoverySet 或企业 index adapter 已完成。
- PHASE04 P04-T07 Infrastructure / Domain Boundary 子范围：基础设施 receipt 边界已达到 `implementation available`，Queue ACK、RabbitMQ delivery、Object Commit、Idempotency Claim、Object Manifest visibility 和 operator telemetry 均被 verifier 固定为不能解释成领域成功；领域终局仍由 Product、Input、Knowledge、Agent Core、Memory、Tool 等 owner 持有。
- PHASE04 P04-T07 Infrastructure Typed Port 子范围：Local/Developer CI 与 Server Product 已共用同一 `InfrastructureCapabilityProfileV1` / `DataServiceCapabilityV1` typed port surface，并覆盖 PostgreSQL、RabbitMQ、Object、Checkpoint、Vector、Graph、Lexical、Cache、Secret 和 Telemetry service kind；unknown service kind fail closed，但 official Checkpointer 等 target adapter 仍未完成。
- PHASE04 P04-T07 Tenant Isolation Profile 子范围：`TenantIsolationProfileV1` 已达到 `implementation available`，Infrastructure Capability Profile 中每个 service kind 都有 tenant scope、默认 target、强隔离选项、cross-tenant action 和 evidence ref；它不证明 `ARCH-INFRA-058` 的全服务运行时 cross-tenant hit quarantine/fail-closed。
- PHASE04 P04-T07 Tenant Physical Constraints 子范围：`ARCH-INFRA-034` 已达到 `implementation available`，PostgreSQL、RabbitMQ、Object ref/MinIO 和 Operator telemetry 的当前证据把 tenant scope 放入物理键、协议 header、object target/auth hook 或 snapshot 约束；它不证明 official Checkpointer 或 `ARCH-INFRA-058` 全服务 cross-tenant hit quarantine/fail-closed。
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

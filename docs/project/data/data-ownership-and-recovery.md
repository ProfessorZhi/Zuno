# Data Ownership & Recovery：事实在哪里、如何一致？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Domain、Runtime、Knowledge、Tool、Security 和 Eval 各自保存什么，部分失败如何恢复？
owner: Data / Infrastructure Contract
replaces: old module/database/consistency appendices (Superseded)

## Part A — Architecture Narrative

数据架构首先回答“谁有权说某件事是真的”，然后才回答“这件事存在哪个数据库”。Domain Owner
保存当前业务事实和版本；Knowledge、Runtime、Memory、Tool 和 Eval 保存各自可重建或可审计的
投影、控制状态、上下文、外部效果或评测结果。一个 Provider 的 ACK、checkpoint 或 index write
不能替代 Domain commit。

例如 Domain transaction 已成功但 checkpoint 或 queue publish 失败时，恢复必须从已提交 Domain
generation 重新构造控制状态，并用 operation id 检查是否已发生外部效果；反过来 checkpoint 显示
完成而 Domain commit 缺失时，不能把业务标成成功。共享 PostgreSQL Cluster 可以是 Target 起点，
但逻辑 Ownership 必须先于物理 database-per-service。

这套设计的代价是版本、幂等键、Outbox/Inbox 和 reconciliation 增加了工程工作；收益是跨服务
部分失败不会被伪装成成功。若模块化单体和独立 worker 能提供相同的审计、恢复和安全语义，不保留
额外物理存储或分布式事务框架。

## Part B — Detailed Architecture Specification

### Storage and reconciliation contract

每个 Job/Command/Effect 使用稳定 identity、输入版本、幂等键、attempt、lease、timeout、cancellation
和 receipt。System of Record、Projection、Runtime Control、Cache/Memory、Object Artifact、Queue
必须明确 Owner 与重建方式；Queue ACK、Index write、Checkpoint 和 HTTP 2xx 不能证明 Domain success。
恢复顺序是读取最后合法 DomainGeneration、检查 provider operation ID、reconcile outbox/inbox，
再 resume/retry/replan/manual review。物理 DB split 需要独立 availability、scaling、security 或
lifecycle 证据。

## Ownership map

| Owner | authoritative data | projections/inputs |
|---|---|---|
| Platform Domain | Matter、DocumentVersion、accepted Claim/Evidence/Finding、HumanDecision、WorkProduct、authorization facts | proposals、references、receipts |
| Agent Runtime | AgentRun、Plan、Step、RuntimeGeneration、checkpoint、interrupt、budget | Domain snapshots、Knowledge candidates、Tool receipts |
| Knowledge | source/parse/index/retrieval state、EvidenceCandidate、CitationLineage、graph/vector projections | Domain DocumentVersion/ACL |
| Tool/Sandbox | ToolAttempt、EffectReceipt、Provider Operation ID、Reconciliation | PreparedAction、Security decision、secret lease |
| Security | policy、grant、security epoch、decision/audit authority | principal/resource facts |
| Eval/Observability | trace、metric、dataset、eval run/result、release gate | redacted references to every owner |

## Physical policy

V1 allows one PostgreSQL cluster with schemas/tables owned by services. Physical database split is a later decision requiring independent availability, scaling, security or lifecycle evidence. Private tables are never joined across services; use HTTP, event, reference, snapshot or receipt.

## Store classification

| 类别 | Part-A 语义 | 典型 Owner/Provider |
|---|---|---|
| System of Record | Canonical Domain/transaction facts and versions | PostgreSQL / Domain Owner |
| Derived Projection | lexical、dense、graph、citation and retrieval projection | Elasticsearch、Milvus、Neo4j 或等价 Provider |
| Runtime Control | Plan、Step、checkpoint、resume、generation | LangGraph Checkpointer/Runtime Store |
| Cache / Context | 可过期、可删除、可重建的 Memory/Cache | Redis、OpenViking 或等价 Provider |
| Object Artifact | 原始文档和版本化文件 | MinIO 或等价 Object Store |
| Queue / Delivery | Job delivery、retry、DLQ、backpressure | RabbitMQ、Redis 或其他 Provider |

Projection、Cache、Queue 和 Checkpoint 都不能成为 Canonical Business Truth。当前仓库出现某个
Provider 只证明代码或配置表面，不证明历史项目或生产主链路使用它。

## Recovery

```text
Local transaction
  + idempotency key
  + transactional outbox/inbox when needed
  + queue delivery
  + provider receipt / operation id
  + reconciliation
```

Queue ACK、checkpoint commit、HTTP 2xx、object commit 和 index write receipt only prove their own boundary. A domain commit must be verified by Domain Owner. If Domain Generation > Checkpoint Generation, rebuild control state from Domain; if Checkpoint > Domain, quarantine/retry from last legal generation.

队列 Job 需要 JobId、幂等键、attempt、lease、timeout、cancellation、retry、DLQ、backpressure 和
reconciliation；队列不是 Business Truth，也不能通过重复投递直接生成第二个业务 Effect。

## Current / Target / Gap

- Current：PostgreSQL migrations、RabbitMQ outbox/worker、runtime tables and checkpoint adapters exist in repository; actual distributed deployment remains UNKNOWN。
- Target：logical ownership first, explicit reconciliation, no default 2PC/Event Sourcing/Saga。
- Gap：cross-service transaction traces, crash tests, schema compatibility, outbox/inbox and backup/restore evidence。

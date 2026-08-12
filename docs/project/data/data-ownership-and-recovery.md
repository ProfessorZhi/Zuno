# Data Ownership & Recovery：事实在哪里、如何一致？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Domain、Runtime、Knowledge、Tool、Security 和 Eval 各自保存什么，部分失败如何恢复？
owner: Data / Infrastructure Contract
replaces: old module/database/consistency appendices (Superseded)

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

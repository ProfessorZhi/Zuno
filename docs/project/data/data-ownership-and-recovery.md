# Data Ownership & Recovery：事实在哪里、如何一致？

status: normative-target
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

## Current / Target / Gap

- Current：PostgreSQL migrations、RabbitMQ outbox/worker、runtime tables and checkpoint adapters exist in repository; actual distributed deployment remains UNKNOWN。
- Target：logical ownership first, explicit reconciliation, no default 2PC/Event Sourcing/Saga。
- Gap：cross-service transaction traces, crash tests, schema compatibility, outbox/inbox and backup/restore evidence。

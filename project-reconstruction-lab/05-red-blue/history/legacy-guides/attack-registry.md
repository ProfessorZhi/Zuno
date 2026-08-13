# Attack Registry

| ID | Claim | Red Question | Required Evidence | Current State |
|---|---|---|---|---|
| RT-001 | Zuno 需要独立存在 | WorkBuddy + Legal Backend 是否足够？ | A/B/C Benchmark | UNDER_ATTACK |
| RT-002 | Domain Kernel 必须独立 | 普通 JSON + PostgreSQL 是否同样有效？ | Domain mutation/review test | UNDER_ATTACK |
| RT-003 | GraphRAG 有必要 | Hybrid RAG 是否已足够？ | Kill Graph Benchmark | UNDER_ATTACK |
| RT-004 | Multi-Agent 有必要 | Single Agent + parallel tools 是否足够？ | Task completion/cost comparison | UNDER_ATTACK |
| RT-005 | Memory Engine 有必要 | Matter DB + Checkpoint 是否足够？ | Reuse/staleness benchmark | UNDER_ATTACK |
| RT-006 | Microservice 边界合理 | 为什么不是 Worker/Library/同一服务？ | Scaling/failure/security evidence | ACCEPTED_TARGET / OPEN_BOUNDARY |
| RT-007 | Python-only 合理 | Java/Spring 是否降低长期成本？ | Workload/team/schema comparison | ACCEPTED_TARGET / HYPOTHESIS |

任何 Claim 没有 Evidence 前都不进入 `PRODUCTION_PROVEN`。

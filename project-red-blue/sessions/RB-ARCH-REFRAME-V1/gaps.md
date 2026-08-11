# RB-ARCH-REFRAME-V1 Gap Clusters

## CLUSTER-001

Gap IDs: GAP-REFRAME-001, GAP-REFRAME-002
Questions: Q001, Q002, Q003
Failed Claim: Python-only 不需要性能和维护边界。
Root Cause: 没有 CPU/GPU/IO workload profile、队列 SLO、跨语言 RPC 成本和长周期维护数据。
Gap Types: ARCHITECTURE_GAP, PERFORMANCE_GAP
Current Evidence: Python 3.12、FastAPI、Docker Python image、LangGraph/PyTorch/RAG dependencies；未发现 Java/Spring。
Required Research: worker benchmark、latency/cost、类型/Contract/观测一致性与外部 Java integration test。
Suggested Blue Route: KEEP_PYTHON_ONLY；重计算独立 worker/native backend。
Status: RESEARCH_REQUIRED

## CLUSTER-002

Gap IDs: GAP-REFRAME-003, GAP-REFRAME-004, GAP-REFRAME-005, GAP-REFRAME-006, GAP-REFRAME-007, GAP-REFRAME-008, GAP-REFRAME-009, GAP-REFRAME-010, GAP-REFRAME-011
Questions: Q004, Q005, Q006, Q007, Q008, Q009, Q010, Q011, Q012, Q013, Q014
Failed Claim: 每个逻辑能力或 Agent 都必须独立微服务。
Root Cause: 没有把 scaling、failure、security、deployment、data ownership 和 lifecycle 映射到候选边界。
Gap Types: SERVICE_BOUNDARY_GAP, OVERENGINEERING_GAP, SECURITY_GAP, RUNTIME_GAP
Current Evidence: 当前是 backend + worker；用户固定 Microservice Target；候选 5 服务与 worker profiles 尚未实现/运行。
Required Research: per-service contract/fault/scale/security spikes；profile-vs-service comparison。
Suggested Blue Route: 5 network-facing services；Legal Intelligence/Model/Eval 保持 provider/worker，满足独立边界才拆。
Status: RESEARCH_REQUIRED

## CLUSTER-003

Gap IDs: GAP-REFRAME-012, GAP-REFRAME-013
Questions: Q015, Q016
Failed Claim: 微服务数据必须立即 Database-per-service，或 Domain/Runtime 可以共享一个事实源。
Root Cause: physical isolation 与 logical ownership、generation/reconcile 尚未由新 taxonomy 统一。
Gap Types: OWNERSHIP_GAP, DEPLOYMENT_GAP
Current Evidence: PostgreSQL migrations、runtime tables、shared compose database；没有新服务的 schema ownership proof。
Required Research: local transaction + outbox/inbox + idempotency + reconcile；schema isolation and migration plan。
Suggested Blue Route: shared PostgreSQL cluster, strict logical ownership, API/event only；later physical split by evidence。
Status: RESEARCH_REQUIRED

## CLUSTER-004

Gap IDs: GAP-REFRAME-014, GAP-REFRAME-015, GAP-REFRAME-016
Questions: Q017, Q018, Q019, Q020
Failed Claim: gRPC/Event/Kafka/Kubernetes 或用户数天然决定微服务架构。
Root Cause: 没有 protocol latency/error matrix、retry storm、backpressure、deployment profile 和真实容量。
Gap Types: COMMUNICATION_GAP, OPERATIONAL_GAP, OVERENGINEERING_GAP
Current Evidence: RabbitMQ worker、Docker Compose、容量仍为 Target assumption。
Required Research: workload-based protocol and deployment benchmarks。
Suggested Blue Route: HTTP sync / queue long-run / MCP external；Compose → managed container/K8s only with evidence。
Status: RESEARCH_REQUIRED

## CLUSTER-005

Gap IDs: GAP-REFRAME-017, GAP-REFRAME-018
Questions: Q021, Q022, Q024
Failed Claim: 11 modules can remain alongside new Product/Domain/Service taxonomy without competing truth.
Root Cause: Entry points, verifier, QA links and ownership registry still hardcode old module set.
Gap Types: DOC_GOVERNANCE_GAP, OWNERSHIP_GAP
Current Evidence: existing architecture directory contract and scripts explicitly require 11 module docs.
Required Research: canonical taxonomy migration, superseded archive disposition, link and verifier audit.
Suggested Blue Route: new taxonomy is sole canonical source; old module bodies become superseded history/redirects.
Status: USER_GATE

## CLUSTER-006

Gap IDs: GAP-REFRAME-019
Questions: Q023
Failed Claim: Target Microservice Architecture is already Current.
Root Cause: Compose has one backend image, one queue worker image, one frontend plus infrastructure; no independent Domain/Runtime/Knowledge/Tool business services.
Gap Types: CURRENT_EVIDENCE_GAP
Current Evidence: infra/docker/docker-compose.yml, Dockerfile, `zuno.main:app`, queue runner.
Required Research: implementation program, service images, deployment traces, fault tests and service SLO evidence.
Suggested Blue Route: mark Target only; production readiness unchanged.
Status: USER_GATE

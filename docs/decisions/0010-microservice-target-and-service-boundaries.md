# ADR-0010：Microservice Target 与服务边界

- 状态：`accepted-target`
- 日期：2026-08-13
- 基线：`0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f`
- 关联：`ADR-0003`、`ADR-0005`、`ADR-0007`、`project-red-blue/sessions/RB-ARCH-REFRAME-V1/`

## Context

本轮固定 Microservice Architecture 为 Target Constraint，但不接受 `11 Logical Modules = 11 Services`。服务边界必须由至少一个强理由支持：Independent Scaling、Failure Isolation、Security/Resource Isolation、Independent Deployment、Distinct Availability、Distinct Data Ownership 或独立 Operational Lifecycle。

## Decision

Target 候选为五个 network-facing Python services：

1. `edge-api`：认证、路由、限流、SSE 和外部 API/MCP delivery；不拥有业务事实。
2. `platform-domain-service`：Tenant/User/Workspace/Matter/DocumentVersion、accepted Claim/Evidence/Finding、HumanDecision/WorkProduct、Review 和 authorization facts；拥有 Domain PostgreSQL 事务事实。
3. `agent-runtime-service`：AgentRun、Plan、Step、checkpoint、resume、HITL、replan、budget、Coordinator、role profiles 和 ephemeral workers；拥有 Runtime Control State。
4. `knowledge-service`：source/ingestion、parse/index/embed/rerank/graph projection、retrieval API、RetrievalRound、EvidenceCandidate 和 Citation Lineage；重处理由 worker profiles 完成。
5. `tool-sandbox-service`：MCP/API/CLI adapters、Sandbox、secret/network/filesystem policy、ToolAttempt、EffectReceipt、Provider Operation ID 和 Reconciliation。

V1 不单独拆：

- Legal Intelligence：Capability Contract + providers，运行于 Agent/Knowledge workers；
- Model Gateway：Agent/Knowledge provider layer；
- Memory：Domain/Runtime context strategy and projection；
- Multi-Agent specialist：同一 Agent Runtime Service 的 profile/worker；
- Eval/Observability：独立 batch/trace worker 与存储生命周期，不增加同步业务 CRUD service。

服务与 Worker 分离：同一 service 可以有 API/control process 与独立 worker pool；同一 Python image 不代表同一服务；单节点 Developer Compose 可以合并部署，但生产 Target 必须可独立配置、扩缩容、隔离故障和审计。

## Communication

- HTTP：CRUD、query、小命令和可调试同步 Contract。
- Durable queue：Agent Run、Ingestion、Embedding、Graph Build、Eval、Sandbox Job。
- MCP/API：外部 Host 和企业系统。
- gRPC：仅在高吞吐内部调用 benchmark 证明收益后引入。

每个异步 Job 都要求 Job Identity、Idempotency Key、Attempt、Timeout、Cancellation、Retry、Dead-letter、Backpressure 和 Reconciliation。Queue 不是业务事实源。

## Data Boundary

V1 允许共享 PostgreSQL Cluster，但每个服务有明确 schema/table ownership，禁止跨服务 JOIN 私有表；跨边界只用 API、Event、Reference、Snapshot 或 Receipt。Domain State 和 LangGraph Checkpoint 是两个事实域，按 Generation/Receipt/Idempotency/Reconciliation 对账。

物理 Database-per-service、Kafka、Saga Framework、2PC、Kubernetes、service mesh 不是本 ADR 的默认条件；独立 availability/scaling/security/lifecycle 证据成立后才可拆或引入。

## Why not library / worker

纯 library 不能提供独立 security/resource/failure boundary；纯 worker 不能提供 Domain/Runtime/Knowledge/Tool 的稳定跨 Host API。反过来，Legal Capability、Model Gateway、Agent profile 和 Eval batch 没有独立边界时，不应伪装为 service。

## Consequences

正面：隔离长任务、重检索、Sandbox 与事务型 Domain；允许 WorkBuddy 等 Host 通过 API/MCP；不把逻辑模块、服务、进程和团队强行一一对应。

负面：增加 network latency、serialization、schema compatibility、retry storm、distributed tracing、secret/config distribution、deployment coordination 和 local development 成本。必须以 failure/scale/operation evidence 证明值得承担。

## Reversal / Refinement Criteria

服务数量可以合并或拆分；只有当 boundary 的 scale、failure、security、deployment、data ownership 或 lifecycle 证据变化时才更新。Microservice Target 本身不因当前没有完整实现而撤销，但“5 个服务”仍是 Candidate，不是 Current。

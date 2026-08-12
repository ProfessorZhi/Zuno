# Architecture Candidates

本页是 Target 候选登记表，不是正式架构事实。正式 Survived 设计必须同步到 `docs/project/architecture/`、专题文档和 ADR。

| Candidate | Why it might exist | Simplest alternative | Current State | Required Proof |
|---|---|---|---|---|
| Legal Domain Kernel | 业务事实、证据、版本和人工决策需要稳定 Owner | JSON + PostgreSQL | UNDER_ATTACK | Domain mutation/review/staleness tests |
| Domain-aware Runtime | Planner/Completion 直接使用领域条件 | WorkBuddy Tool JSON / ordinary workflow | UNDER_ATTACK | C vs B quality and efficiency benchmark |
| Conditional Graph Retrieval | 跨文档、关系型证据可能需要 Graph | Hybrid RAG | UNDER_ATTACK | Kill Graph Benchmark |
| Composable Multi-Agent | 专业角色、并行和权限隔离 | Single Agent + workers | PROPOSED | task/cost/failure comparison |
| Python-only | AI/NLP ecosystem 和团队复杂度 | Java + Python | ACCEPTED_TARGET | workload/schema/deployment rationale |
| Microservice Target | 长任务、重检索、Sandbox failure/resource isolation | Modular Monolith + Workers | ACCEPTED_TARGET | service boundary evidence |
| OpenViking Memory Provider | 分层 Context/Memory 接入 | PostgreSQL + Checkpoint | HISTORICAL_USER_CONFIRMED / TARGET_OPEN | historical artifact and provider conformance |

## Boundary

逻辑能力、进程、服务、容器、数据库和团队不是一一映射。任何“一个 Agent 一个服务”的方案默认拒绝，除非有独立部署、安全、SLA 或资源池证据。

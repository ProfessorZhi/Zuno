# Architecture Candidates

本页是 Target 候选登记表，不是正式架构事实。正式 Survived 设计必须同步到 `docs/architecture/`、专题文档和 ADR。

## PROJECT-ARCHITECTURE-RECONSTRUCTION-V1 输入边界

本表由十类 Canonical Facts、当前仓库证据和既有 ADR 驱动。它不把历史技术现实、当前
代码表面与 Target 候选合并；每个候选都必须回到真实问题、最小替代方案和可复现的证据。

本轮固定两个输入约束：

- `Python-only` 是后端 Target Constraint，不等于历史项目已经 Python-only，也不免除性能和维护成本审查；
- `Microservice Architecture` 是部署 Target Constraint，不等于 `11 modules = 11 services`，也不预先批准五个服务。

## 评审顺序

```text
事实深度 → 真实问题 → Domain Contract → Runtime/Knowledge Contract
→ Logical Capability → Physical Service/Worker → Data/Security/Eval
→ Red → Blue → Counter Attack → Decision
```

在本 Program 中，`ACCEPTED_TARGET` 只表示 Owner Constraint 或已通过前一轮的目标方向；
不表示 Current、Measured 或 Production Proven。服务数量、Domain-aware Runtime 和
所有条件性能力仍需本轮重新审查。

| Candidate | Why it might exist | Simplest alternative | Current State | Required Proof |
|---|---|---|---|---|
| Legal Domain Kernel | 业务事实、证据、版本和人工决策需要稳定 Owner | JSON + PostgreSQL | UNDER_ATTACK | Domain mutation/review/staleness tests |
| Domain-aware Runtime | Planner/Completion 直接使用版本化 Domain Conditions、EvidenceRequirement、staleness 和 Review gate | WorkBuddy Tool JSON / ordinary workflow / Host + Legal Backend | UNDER_ATTACK | C vs B quality and efficiency benchmark；必须证明收益不是普通 Backend Workflow 可实现 |
| Conditional Graph Retrieval | 跨文档、关系型证据可能需要 Graph | Hybrid RAG | UNDER_ATTACK | Kill Graph Benchmark |
| Composable Multi-Agent | 专业角色、并行和权限隔离 | Single Agent + workers | PROPOSED | task/cost/failure comparison |
| Python-only | AI/NLP ecosystem 和团队复杂度 | Java + Python | ACCEPTED_TARGET | workload/schema/deployment rationale |
| Microservice Target | 长任务、重检索、Sandbox failure/resource isolation | Modular Monolith + Workers | ACCEPTED_TARGET | service boundary evidence |
| OpenViking Memory Provider | 分层 Context/Memory 接入 | PostgreSQL + Checkpoint | HISTORICAL_USER_CONFIRMED / TARGET_OPEN | historical artifact and provider conformance |

## Boundary

逻辑能力、进程、服务、容器、数据库和团队不是一一映射。任何“一个 Agent 一个服务”的方案默认拒绝，除非有独立部署、安全、SLA 或资源池证据。

## 本轮最小交付

1. 用 Fact Readiness Gate 检查产品问题链是否足以支持架构推导；
2. 为 Legal Domain、Runtime、Knowledge、Multi-Agent、Memory 和 Service Boundary 建立最小候选；
3. 对 WorkBuddy Host + Legal Backend、普通 Workflow、Hybrid RAG、Single Agent + parallel tools、Modular Monolith + Workers 执行 Kill Test；
4. 对每个 surviving 候选登记 Owner、状态、失败、恢复、幂等、Security、Observability、Test、替代和删除条件；
5. 用户 Gate 前只生成 ADR/Canonical Sync 候选，不生成实现任务。

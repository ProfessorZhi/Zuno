# Zuno 总体 Target 架构

updated: 2026-08-13
status: normative-target-architecture-reframe-v1
document_role: cross-cutting integration source
canonical_taxonomy: `docs/project/product/`, `domain/`, `agents/`, `knowledge/`, `services/`, `data/`, `security/`, `eval/`, `deployment/`
current_state_source: `docs/status/production-readiness.md` and `docs/evidence/`
decision_sources: `docs/decisions/0008-legal-domain-kernel-and-host-boundary.md`, `0009-python-only-backend.md`, `0010-microservice-target-and-service-boundaries.md`, `0011-architecture-document-taxonomy.md`

> 本文只回答跨领域问题：产品、Domain、Agent、Knowledge、Service、Data、Security、Eval 和 Deployment 如何连成一个目标系统。每个专题的 Canonical Question、Owner、Contract 和详细状态只在对应专题文档定义；本文不创建第二套状态机。

## 0. 这次重构改变了什么

上一阶段的 `11 Logical Modules + 1 Architecture` 是历史 Target 组织方式，不是 Zuno 的永久边界。本轮固定 Python-only 后端和 Microservice Deployment Target，但重新攻击服务数量、物理部署、Multi-Agent、运行时和文档 taxonomy。

新架构采用三层：

```text
Product / Domain
    ↓ 业务语义、Canonical State、Review 和 Human Decision
Logical Capability Architecture
    ↓ Agent、Knowledge、Capability、Tool、Security、Eval
Physical Service / Deployment Architecture
    ↓ Python services、workers、databases、queue、object/index providers
```

Logical capability 不等于 service，service 不等于 process，process 不等于 container，container 不等于 team。任何物理拆分都必须回答 `Why service? Why not library? Why not worker? Who owns state? How does it recover?`。

## 1. 产品与领域核心

Zuno Target Product 是面向司法与专业法律工作的 **Legal Case Intelligence & Agent Platform**。核心原则是：

```text
Business Semantics Stable
Computation Pluggable
Agents Composable
```

产品流程以复杂案件分析为例：

```text
Create Matter
  → Upload Evidence / DocumentVersion
  → Knowledge ingestion and evidence retrieval
  → Agent Runtime Coordinator
  → Research / Evidence / Dispute role profiles
  → Legal Capability Provider proposals
  → Domain Owner validation and version commit
  → Finding / HumanDecision
  → WorkProduct
  → optional Tool Effect + Audit
```

Domain State 表示法律业务世界的权威状态；Runtime State 表示一次执行进行到哪里；Knowledge Projection 表示如何找到证据；Memory 表示可复用上下文；Tool Effect 表示外部世界发生了什么。五者不能互相冒充。

阅读产品与领域规范：

- [`product-architecture.md`](../product/product-architecture.md)：用户任务、Host、Review 和 WorkProduct。
- [`legal-domain-model.md`](../domain/legal-domain-model.md)：Domain Object、Canonical Owner 和 Proposal 边界。
- [`domain-state-lifecycle.md`](../domain/domain-state-lifecycle.md)：版本、stale、依赖、审批和恢复。

## 2. Python-only Target

Python-only 是 Target Constraint，不是 Current 生产证明。理由是工作负载和边界的一致性：

- FastAPI/Pydantic、SQLAlchemy/SQLModel、LangGraph、PyTorch、Transformers、RAG/NLP Providers 共用 Python Contract、类型和测试工具；
- 控制层通常是 IO-bound 或 external-service-bound，网络、数据库、模型 API 和索引引擎承担主要等待；
- CPU-heavy OCR、解析、embedding、rerank、graph build 和 batch eval 不得占用 FastAPI request thread，必须进入独立 worker 或 native-backed engine；
- 外部 Java/Spring 系统通过 HTTP、gRPC candidate、MCP/API 或消息 Contract 集成，不把第二后端语言引入 Zuno；
- Python-only 的成本是 GIL、CPU 任务、依赖体积、运行时类型约束和长期维护，需要 Worker、Pydantic schema、静态检查、故障注入和 workload benchmark 约束。

Java/Spring 的企业生态、强类型、JVM 并发和人才池是有效反对理由，但不足以单独改变 Target；只有跨语言 RPC、组织维护、性能和安全证据显示 Python-only 的总成本更高，才进入逆转评审。

## 3. 五个 Network-facing Python Services

```text
External surfaces / WorkBuddy / Firm systems / Court systems / MCP clients
                              ↓
                         edge-api
                              ↓
     ┌────────────────────────┼────────────────────────┐
     ↓                        ↓                        ↓
platform-domain        agent-runtime              knowledge
     │                        │                        │
     └───────────────┬────────┴───────────────┬────────┘
                     ↓                        ↓
              tool-sandbox              worker profiles
```

| 服务 | 独立理由 | Canonical Owner | 不负责 |
|---|---|---|---|
| `edge-api` | 外部认证、路由、SSE、限流和协议适配；生产入口可独立扩缩容 | API delivery/correlation receipt | Domain、Runtime、Tool 和 Eval 事实 |
| `platform-domain-service` | 事务型业务状态、授权事实和 Review，与长任务和重计算有不同 failure/availability/security | Tenant/User/Workspace/Matter/DocumentVersion、accepted Claim/Evidence/Finding、HumanDecision/WorkProduct、Review、authorization facts | LangGraph、OCR、Sandbox、检索算法 |
| `agent-runtime-service` | 长运行、checkpoint/resume、HITL、replan、budget、parallel branch 和 model calls 有独立生命周期 | AgentRun、Plan、Step、Runtime Control、Checkpoint、Delegation Proposal | 普通 CRUD、最终 Domain Commit、Tool Effect |
| `knowledge-service` | OCR/parse/index/embed/rerank/graph build 与 retrieval API 资源异构 | Source/ingestion、Index/Projection、RetrievalRound、EvidenceCandidate、Citation Lineage | accepted Finding、权限事实和人工决定 |
| `tool-sandbox-service` | Secret、filesystem/network policy、Sandbox 和 external effect 需要强 security/resource/failure isolation | ToolAttempt、EffectReceipt、Provider Operation ID、Reconciliation | Agent Plan、Domain Fact、模型编排 |

这是五个服务的 Target Candidate，不是 Current。服务可由同一个 Python 镜像构建，但服务 Contract、配置、资源池、队列和部署边界必须独立可测试。

## 4. 逻辑能力如何落到服务

以下能力不自动变成服务：

| 逻辑能力 | V1 物理形态 | 拆成服务的证据 |
|---|---|---|
| Legal Intelligence | Agent/Knowledge worker 中的 Capability Provider；本地算法、LLM、fine-tuned model、OSS、API、MCP 可替换 | 独立 GPU/模型、许可证、SLA、权限或发布生命周期 |
| Model Gateway | Agent Runtime/Knowledge provider layer | 多产品共享 quota/secret、独立模型 serving、路由 SLA 或成本边界 |
| Memory | Domain/Runtime 的上下文策略和存储投影 | 独立租户隔离、召回规模、删除生命周期或扩缩容证据 |
| Multi-Agent | Agent Runtime 内的 Coordinator、profiles、ephemeral workers | 独立 Agent 的 SLA、security boundary、resource pool 或发布周期 |
| Eval / Observability | Eval batch worker、trace/audit sink 和 release gate storage | 独立离线吞吐与生命周期；不要求同步 CRUD service |
| GraphRAG | Knowledge provider + graph/index worker | Query-class Kill Test 和独立 graph build/serve 资源边界 |

更详细的 Agent 和 Knowledge 边界见 [`agent-platform.md`](../agents/agent-platform.md)、[`multi-agent-runtime.md`](../agents/multi-agent-runtime.md) 和 [`knowledge-evidence-architecture.md`](../knowledge/knowledge-evidence-architecture.md)。

## 5. FastAPI 与 LangGraph 的硬边界

```text
FastAPI / HTTP Application Interface
  Auth, Matter/Review CRUD, Upload, Agent Config,
  Run Submit, Run Status, Control Command, SSE/WebSocket

LangGraph / Runtime Orchestration Provider
  Agent Run, long-running workflow, checkpoint,
  resume, HITL interrupt, dynamic branch, reducer, replan
```

LangGraph 只进入 `agent-runtime-service`。它不创建 Case、不更新 Permission、不列出 User、不直接写 Domain Store。Plain Python workflow、state machine、Pi 或 Host Runtime 仍可替换 LangGraph；保留 Runtime Contract，不把框架类型扩散到 Domain/Service API。

## 6. 同步、异步与队列

| 场景 | 默认通信 | 原因 |
|---|---|---|
| CRUD、查询、小型命令 | HTTP/JSON Contract | 可观测、易调试、外部互操作 |
| Agent Run、Ingestion、Graph Build、Embedding、Eval、Sandbox Job | durable queue | 长运行、重资源、取消、重试、backpressure 和 DLQ |
| 外部 Host/WorkBuddy/企业系统 | MCP/API/HTTP | 兼容边界和部署主权 |
| 高吞吐内部调用 | gRPC candidate | 只有 latency/serialization evidence 成立才采用 |

Queue 不是 Business Truth。每个 Job 必须有 Job Identity、Idempotency Key、Attempt、Timeout、Cancellation、Retry Policy、Dead-letter、Backpressure 和 Reconciliation；RabbitMQ/Redis/Kafka 都是 Provider 候选，不由架构文字锁死。

## 7. Domain State 与 Runtime State

```text
platform-domain PostgreSQL
  Matter / DocumentVersion / Claim / Fact / Evidence /
  Conflict / Dispute / Finding / HumanDecision / WorkProduct /
  Approval / authorization facts / version / provenance / audit reference

agent-runtime store / LangGraph Checkpointer
  Node / Branch / Pending Work / Reducer / Interrupt /
  Checkpoint / Resume Position / Runtime Generation
```

恢复必须处理 partial failure：

1. Domain DB 已提交 Effect Success，Checkpoint 停在执行前：读取 EffectReceipt/Idempotency，禁止重复副作用。
2. Checkpoint 显示 Node 完成，Domain Transaction 未提交：回退到最后合法 DomainGeneration，不能假装业务完成。
3. Knowledge 返回 EvidenceCandidate，Domain Owner 未接受：只能进入 Proposal/Review，不能生成 FindingVersion。
4. HumanDecision 改变 Canonical State：旧 Finding/Plan 依据版本重新验证，必要时创建新 Run。

数据和一致性规范见 [`data-ownership-and-recovery.md`](../data/data-ownership-and-recovery.md)。

## 8. Deployment Profiles

```text
Developer:   Compose；同镜像可运行五服务和最小 worker，重依赖可按 profile 启用
Staging:     多服务、多 worker、真实队列/对象存储/索引，验证合同、故障和观测
Production:  HA/滚动升级/独立扩缩容/安全隔离；是否 Kubernetes 由证据决定
```

Microservice Target 不自动要求 Kubernetes、Kafka、service mesh、Database-per-service、Event Sourcing 或 Saga Framework。共享 PostgreSQL Cluster 可以作为 V1 物理基础设施，但按 schema/table ownership 隔离，禁止跨服务 JOIN 私有表；物理数据库拆分需要独立 availability、scaling、security 或 lifecycle 证据。

## 9. Current / Target / History

| 状态 | 事实 |
|---|---|
| Current | `pyproject.toml` 为 Python 3.12；Docker 使用 Python 3.12；`zuno.main:app` 是 FastAPI 入口；Compose 有 backend、worker、frontend 应用容器与基础设施；存在 PostgreSQL migrations；仓库没有 Java/Spring 匹配证据 |
| Target | Python-only、五个 network-facing services、独立 worker profiles、Domain/Runtime State 分离、HTTP/queue/MCP 分层、Developer/Staging/Production profiles |
| Hypothesis | Python 总成本、每个服务的扩缩容/失败/安全收益、Multi-Agent 质量/效率、Kubernetes、物理 DB split 和 service count |
| Future | Persistent Agent Team、物理 Database-per-service、Kubernetes、Event Sourcing、Saga 或更细粒度 Provider Service；只有新的证据和 ADR 才能进入 Target |
| History | 旧 `docs/project/modules/01..11` 作为上一阶段设计材料；被新 taxonomy 标记 Superseded，不再是 Canonical Target |
| UNKNOWN | 实际线上服务数、真实用户/容量、SLO、团队 Ownership、Java 外部系统、生产部署和当前质量 |

## 10. Canonical Reading Order

```text
Product reader:   docs/README.md → architecture.md → product → domain
Agent engineer:   architecture → domain → agents → services → data/security
Knowledge engineer: domain → knowledge → agents → eval
Backend engineer: domain → services → data → security → deployment
SRE:              services → data → deployment → eval/observability
```

Canonical 专题入口：[`service-architecture.md`](../services/service-architecture.md)、[`security-architecture.md`](../security/security-architecture.md)、[`legal-eval-and-benchmark.md`](../eval/legal-eval-and-benchmark.md)、[`microservice-deployment.md`](../deployment/microservice-deployment.md)。完整 taxonomy 还包括 [`product-architecture.md`](../product/product-architecture.md)、[`legal-domain-model.md`](../domain/legal-domain-model.md)、[`domain-state-lifecycle.md`](../domain/domain-state-lifecycle.md)、[`agent-platform.md`](../agents/agent-platform.md)、[`multi-agent-runtime.md`](../agents/multi-agent-runtime.md)、[`knowledge-evidence-architecture.md`](../knowledge/knowledge-evidence-architecture.md) 和 [`data-ownership-and-recovery.md`](../data/data-ownership-and-recovery.md)。

新 taxonomy 的唯一入口和迁移规则见 [`docs/project/README.md`](../README.md)、[`docs/decisions/0011-architecture-document-taxonomy.md`](../../decisions/0011-architecture-document-taxonomy.md)。`architecture-views.md` 与 `architecture.html` 只展示本架构，不拥有第二套事实。

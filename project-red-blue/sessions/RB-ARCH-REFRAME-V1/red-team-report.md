# ARCHITECTURE-REFRAME-V1 红蓝架构报告

## 结论

本轮接受用户给定的两个 Target Constraint：后端 Python-only、部署目标 Microservice Architecture。红队没有接受“Python-only = 性能无边界”或“Microservice = 11 模块/11 服务”；复杂度证明责任转移到服务边界、worker 类型、数据 Ownership、协议、部署和验证证据。

当前 HEAD 的真实形态仍是：Python 3.12、FastAPI 单后端镜像、RabbitMQ ingestion/RAG worker、Vue/Electron client，以及 PostgreSQL/Redis/RabbitMQ/Neo4j/Milvus/MinIO 等 Compose 依赖。没有 Java/Spring 代码证据，也没有独立 Platform/Domain、Agent Runtime、Knowledge、Tool/Sandbox 业务服务的 Current 证据。Target ≠ Current，Production Readiness 不变。

## Python-only 的最强反对理由与结论

最强攻击是 Java/Spring 在企业事务、安全、强类型、JVM 并发和人才池上成熟，且 Python 有 GIL、CPU 性能和长期维护风险。Blue 只有在边界明确时幸存：

- FastAPI/Pydantic 负责 HTTP、Contract 和短请求；
- Agent、Ingestion、Graph/Embedding、Eval、Sandbox 都能进入独立 worker/failure domain；
- CPU-heavy 不在线程中硬跑，交给独立 worker、PyTorch/CUDA/ONNX 或已有 native engine；
- 外部 Java 客户通过 HTTP/gRPC/MCP/API 集成，不把第二语言引入 Zuno 后端；
- Python-only 的收益是同一套类型/Schema、LangGraph、PyTorch、Transformers、RAG/NLP Provider、测试和观测语义，减少 cross-language RPC/DTO/失败语义复制；这仍需性能和维护 Benchmark。

结论：`KEEP_PYTHON_ONLY`，但目标表述是“Python 控制面 + native-backed/independent workers”，不是“Python 单进程吞吐足够”。

## 最终服务候选

| Target deployable | Why service | Why not library/worker only | Owned facts | Non-goal |
|---|---|---|---|---|
| `edge-api` | 外部认证、路由、SSE、限流和 API/MCP surface 有独立 ingress 边界 | Developer 可与 Platform 同镜像；生产入口仍可独立扩缩容 | API delivery receipt、request correlation | 不拥有 Domain/Runtime state |
| `platform-domain-service` | 事务型 Canonical business/domain state、权限和 Review 的 availability/security 与长任务不同 | 必须可被多个 Host/Runtime/Worker 访问；不能被 Agent worker 直接写库 | Tenant/User/Workspace/Matter/DocumentVersion、accepted Claim/Evidence/Finding、HumanDecision/WorkProduct、Review、authorization facts | 不运行 LangGraph、OCR、Sandbox |
| `agent-runtime-service` | 长运行、checkpoint/resume、HITL、replan、budget、parallel branch 有独立 scaling/failure lifecycle | 需要 submit/status/control API 与 runner pool；不只是请求内 library | AgentRun、Plan、Step、Runtime Control/Checkpoint、Delegation proposal | 不做普通 CRUD、Domain commit 或 Tool effect |
| `knowledge-service` | OCR/parse/index/embed/rerank/graph build 与 retrieval API 资源异构 | 保留 query API 与独立 ingestion/index/graph worker pools；不为每个算法拆服务 | Source/Document ingestion state、Index/Projection、RetrievalRound、EvidenceCandidate/Citation lineage | 不提交最终 Finding 或权限事实 |
| `tool-sandbox-service` | Sandbox、secret、network/filesystem policy 和 external effect 需要独立安全/资源/failure domain | Runtime 只能提交 PreparedAction；执行必须隔离 | ToolAttempt、EffectReceipt、Provider Operation ID、Reconciliation | 不拥有 Agent plan 或 Domain fact |

### 不独立成服务的候选

- Legal Intelligence：Contract + local/LLM/fine-tuned/OSS/API/MCP Provider，默认在 Agent/Knowledge worker 内；GPU、许可证、SLA 或独立发布证据成立才拆。
- Model Gateway：Provider layer，默认与 Agent Runtime/Knowledge 同服务边界；多产品共享 quota/secret/model serving 证据成立才拆。
- Memory：逻辑能力与 Domain/Runtime 数据策略，不是默认服务；Domain state 不能被 Memory 取代。
- Eval/Observability：独立 Eval/Trace worker 与存储生命周期，V1 不增加同步 CRUD 服务；业务只提交 job/receipt。
- 每个 Specialist Agent：同一 Agent Runtime Service 的 profile/worker，不是一服务一 Agent。

因此 Target 是“五个 network-facing Python services + 明确 worker profiles”，不是 11 services。具体数量仍是 Target Candidate，必须由 service/fault/scale/security evidence 升级。

## FastAPI、LangGraph、Domain/Runtime State

```text
FastAPI = HTTP/API/Application Interface
  Auth / Matter / Review / Upload / Agent Config / Run Submit / Run Status / SSE

LangGraph = Agent orchestration provider inside Agent Runtime Service
  Long-running Run / checkpoint / resume / HITL / dynamic branch / replan

PostgreSQL Domain State = business truth
  Matter / Case profile / Fact / Event / Evidence / Dispute / Finding /
  HumanDecision / WorkProduct / Approval / Effect reference

Runtime Store / LangGraph Checkpointer = control truth
  Node / Branch / Pending Work / Graph State / Resume Position
```

两者通过 `DomainGeneration`、`CheckpointGeneration`、`EffectReceipt`、Idempotency Key 和 Reconciliation 对账；Checkpoint 不能成为 Case Fact，LangGraph 不能承载普通 CRUD。

## Multi-Agent 最终模型

允许从 L0 Single Agent、L1 Role Pipeline、L2 Ephemeral Worker、L3 Specialized Domain Agent 到 L4 Persistent Team，但默认物理模型是同一 `agent-runtime-service` 中的 Coordinator + role profiles + ephemeral workers。所有 Agent 共享 Legal Domain Kernel、Capability Contracts、Knowledge Scope、Security 和 Eval；差异来自 Role、Instruction/Skill、Knowledge Scope、Capability Binding、Tool Permission、Memory/Model/Delegation Policy。只有独立 SLA、security boundary、resource pool、deployment 或 release lifecycle 才拆成服务。

## 新 Canonical Architecture Taxonomy

```text
docs/project/
├─ facts/                         # 历史与当前事实：What happened?
├─ architecture/                 # 只有四个文件：总体关系与图展示
├─ product/product-architecture.md
├─ domain/legal-domain-model.md
├─ domain/domain-state-lifecycle.md
├─ agents/agent-platform.md
├─ agents/multi-agent-runtime.md
├─ knowledge/knowledge-evidence-architecture.md
├─ services/service-architecture.md
├─ data/data-ownership-and-recovery.md
├─ security/security-architecture.md
├─ eval/legal-eval-and-benchmark.md
└─ deployment/microservice-deployment.md
```

每份文档只回答一个 Canonical Question：Product（用户工作是什么）、Domain（业务世界是什么）、Agents（如何计划/协作/执行）、Knowledge（如何形成证据）、Services（逻辑能力如何形成部署单元）、Data（事实在哪里/谁拥有/如何恢复）、Security（谁能做什么）、Eval（如何证明）、Deployment（如何运行/扩容）。旧 11 Module 文档被标记 Superseded/History；新 taxonomy 是唯一 Target Source。architecture/ 仍只有四个文件，专题不塞回其中。

## Current / Target / History

| 状态 | 本轮结论 |
|---|---|
| Current | Python 3.12/FastAPI；backend + worker + frontend Compose 应用容器；PostgreSQL/Redis/RabbitMQ/Neo4j/Milvus/MinIO 依赖；55 migrations；无 Java/Spring repo match |
| Target | Python-only + Microservice；五个 network-facing services；worker profiles；shared PostgreSQL cluster with logical ownership；HTTP/queue/MCP protocol split；Compose/Staging/Production profiles |
| Hypothesis | 服务数、每个 boundary 的 scale/failure/security 收益、Python 维护/性能收益、C/B agent runtime收益、K8s/物理 DB split |
| History | 11 Module + 1 Architecture 作为上一阶段设计与审计材料，不再是新的 Canonical Target |

## Open Evidence Gaps

1. 没有真实部署证据证明五服务 Target 已运行。
2. 没有 workload profile 证明 CPU/GPU/IO SLO、队列容量和 Python worker 规模。
3. 没有 service-level fault injection、network retry、backpressure、schema compatibility 或 reconciliation trace。
4. 没有服务边界对应的团队/值班/独立发布证据。
5. 没有 Multi-Agent 与 profile/worker/service 变体的公平 Benchmark。
6. 没有新 taxonomy 完成后的全部旧链接和 verifier 迁移结果。

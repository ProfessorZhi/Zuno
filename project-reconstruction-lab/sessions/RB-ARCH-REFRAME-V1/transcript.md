# RB-ARCH-REFRAME-V1 Red/Blue Transcript

本记录只保存可审计的攻击、回答和证据边界，不保存隐藏思维链。Microservice 与 Python-only 是本轮 Target Constraint；红队攻击的是其理由、服务数量和边界。

## Q001

Attack Area: PYTHON_ONLY
Claim Under Test: Target 可以固定为 Python-only。
Red Attack: Java/Spring 的企业生态、强类型、并发和长期维护是否足以否定 Python？
Blue Answer: 不能仅凭生态否定。Zuno 的控制层、FastAPI/Pydantic Contract、LangGraph、PyTorch/Transformers、RAG/NLP Provider 都共享 Python 类型和运行时；保留 Python-only 可减少跨语言 DTO、RPC、观测和失败语义重复，但不是“AI 都用 Python”的口号。
Disposition: KEEP_PYTHON_ONLY_TARGET
Evidence: pyproject.toml; infra/docker/Dockerfile; no Java/Spring match in repository
Scorecard Ref: Q001
Gap Candidate Refs: GAP-REFRAME-001

## Q002

Attack Area: PYTHON_ONLY
Claim Under Test: Python-only 长期维护风险可接受。
Red Attack: GIL、CPU 性能、人才池和企业客户既有 Java 栈怎么办？
Blue Answer: Python 只承担控制/API/IO 编排；CPU-heavy 解析、OCR、embedding、rerank 进入独立 worker 或成熟 native backend。外部企业 Java 集成通过 HTTP/gRPC/MCP/API，不把 Java 引入 Zuno 后端。长期维护仍需类型、Contract、lint、测试和运行证据。
Disposition: KEEP_WITH_EXPLICIT_BOUNDARY
Evidence: workload inventory; pyproject; Docker command; deployment target docs
Scorecard Ref: Q002
Gap Candidate Refs: GAP-REFRAME-001, GAP-REFRAME-002

## Q003

Attack Area: PYTHON_ONLY
Claim Under Test: “Python 性能够用”足够作为架构理由。
Red Attack: CPU-bound、IO-bound、GPU-bound、external-service-bound 是否已区分？
Blue Answer: 不能用笼统性能声明。FastAPI 负责短请求和 IO；Agent/ingestion/eval/sandbox 进入独立 worker；PyTorch/CUDA/ONNX/数据库引擎承担重计算。需以 latency、queue backlog、CPU/GPU、cost 和 failure isolation 证据校准。
Disposition: KEEP_PYTHON_WITH_WORKER_BOUNDARY
Evidence: infra/docker/docker-compose.yml; queue runner; pyproject dependencies
Scorecard Ref: Q003
Gap Candidate Refs: GAP-REFRAME-002

## Q004

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Python-only Target 等于一个 Python 微服务。
Red Attack: 为什么不继续单体？
Blue Answer: Target 固定 Microservice，但不固定数量。强理由来自 Agent 长任务、Knowledge CPU/GPU/IO、Sandbox 安全隔离、Platform 事务、Eval 批处理的异构 workload 和 failure domain，而不是用户数或企业感。
Disposition: KEEP_MICROSERVICE_TARGET
Evidence: user Target Constraint; current compose has backend and worker; docs architecture reframe report
Scorecard Ref: Q004
Gap Candidate Refs: GAP-REFRAME-003

## Q005

Attack Area: SERVICE_BOUNDARY
Claim Under Test: 11 个逻辑模块必须变成 11 个服务。
Red Attack: 这是最直接的旧架构偷换。
Blue Answer: 删除该映射。Logical Domain、Capability、Worker、Service、Process、Team 和数据库不是同一层。最终采用 5 个 network-facing Python services，加独立 worker profiles；服务数由 scaling、failure、security、deployment、data ownership 证明。
Disposition: DELETE_11_TO_11_MAPPING
Evidence: current compose; old architecture governance; user Target Constraint
Scorecard Ref: Q005
Gap Candidate Refs: GAP-REFRAME-003, GAP-REFRAME-004

## Q006

Attack Area: SERVICE_BOUNDARY
Claim Under Test: API Gateway 是必须的独立服务。
Red Attack: 如果只有一个外部入口，Gateway 是否只是多一跳？
Blue Answer: 保留为 edge-api/BFF Target，因为认证、路由、SSE、限流和外部协议隔离有独立边界；在单节点 Profile 可以与 Platform Domain 同镜像部署，但逻辑 Contract 和服务可独立扩容。
Disposition: KEEP_AS_DEPLOYABLE_EDGE
Evidence: docs/README.md frontend/backend boundary; src/backend/zuno/main.py
Scorecard Ref: Q006
Gap Candidate Refs: GAP-REFRAME-004

## Q007

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Platform / Domain Service 应独立。
Red Attack: 为什么不能放入 Agent Runtime 或 Knowledge？
Blue Answer: 它拥有 PostgreSQL Canonical Business/Domain State、Matter、Evidence accepted version、Finding、HumanDecision、WorkProduct、Review 和权限事实；与长运行、CPU/GPU、沙箱故障域不同，保留独立事务与部署边界。
Disposition: KEEP_PLATFORM_DOMAIN
Evidence: domain ownership design; current platform database and product services
Scorecard Ref: Q007
Gap Candidate Refs: GAP-REFRAME-005

## Q008

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Agent Runtime Service 应独立。
Red Attack: Agent Run 是否只是普通 API 请求或一个 Library？
Blue Answer: 长运行、checkpoint、resume、HITL、replan、parallel branch、budget 和 model calls 形成独立 failure/scaling/lifecycle；FastAPI 只负责 submit/status/control，LangGraph 只在该服务内承担 orchestration，不能承载 CRUD。
Disposition: KEEP_AGENT_RUNTIME
Evidence: src/backend/zuno/agent/runtime; LangGraph deps; current runtime docs
Scorecard Ref: Q008
Gap Candidate Refs: GAP-REFRAME-005, GAP-REFRAME-006

## Q009

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Knowledge Service 应独立。
Red Attack: Ingestion、Retrieval、Graph、Embedding 是否只是同一个 Python package？
Blue Answer: 逻辑上可共用 package，但物理上需要独立 worker pool：OCR/parse、embedding/rerank、index/graph build 和 retrieval API 的资源与延迟不同。V1 以一个 Knowledge service + worker profiles 表示，禁止把每种算法拆成服务。
Disposition: KEEP_KNOWLEDGE_PLUS_WORKERS
Evidence: queue runner ParseWorker/IndexWorker/GraphWorker; Milvus/Neo4j/MinIO dependencies
Scorecard Ref: Q009
Gap Candidate Refs: GAP-REFRAME-006, GAP-REFRAME-007

## Q010

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Tool / Sandbox Service 应独立。
Red Attack: MCP/API/CLI adapter 是否可以放在 Runtime 里？
Blue Answer: 普通 Tool adapter 可以是 library；但 Sandbox、filesystem/network policy、secret scope、effect receipt 和 side-effect reconciliation 需要独立 security/resource/failure boundary。Runtime 提交 PreparedAction，Tool/Sandbox 执行并返回 Receipt。
Disposition: KEEP_TOOL_SANDBOX
Evidence: src/backend/zuno/platform/services/sandbox; docs/project/modules/08/09 at baseline
Scorecard Ref: Q010
Gap Candidate Refs: GAP-REFRAME-008

## Q011

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Legal Intelligence 必须是独立微服务。
Red Attack: Event extraction、conflict、Fact–Article、applicability 是否值得网络化？
Blue Answer: 默认不拆。它们是 Domain Capability Contracts + providers，可以在 Agent/Knowledge workers 内运行；只有模型/GPU、许可证、独立发布、权限或 SLA 形成独立 boundary 才提升为 service。
Disposition: MERGE_AS_CAPABILITY_PROVIDERS
Evidence: RB-KERNEL-V3 legal capability matrix; no legal service in current code
Scorecard Ref: Q011
Gap Candidate Refs: GAP-REFRAME-007, GAP-REFRAME-009

## Q012

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Model Gateway 必须独立服务。
Red Attack: Model routing、quota、fallback 是否需要 network hop？
Blue Answer: V1 合并到 Agent Runtime/Knowledge provider layer；tenant-wide quota、secret boundary、独立模型 serving 或多产品共享形成证据后再拆。Provider Contract 保留，不锁物理部署。
Disposition: MERGE_PROVIDER_LAYER
Evidence: pyproject model dependencies; current backend entrypoint; ADR 0007 reuse-first
Scorecard Ref: Q012
Gap Candidate Refs: GAP-REFRAME-009

## Q013

Attack Area: SERVICE_BOUNDARY
Claim Under Test: Eval/Observability 必须是同步业务服务。
Red Attack: Trace、benchmark、release gate 是否会拖慢产品请求？
Blue Answer: 业务 API 只发 trace/eval job and receipt；Eval/benchmark 是独立 batch worker，Observability ingestion 可由平台基础设施接收。独立 worker 具备生命周期隔离，不要求 V1 再造一个 CRUD service。
Disposition: KEEP_AS_WORKER_NOT_API_SERVICE
Evidence: docs/status/production-readiness.md; current eval baseline; queue architecture
Scorecard Ref: Q013
Gap Candidate Refs: GAP-REFRAME-010

## Q014

Attack Area: AGENT_RUNTIME
Claim Under Test: Multi-Agent 应一 Agent 一服务。
Red Attack: Coordinator、Evidence、Dispute、Research、Reviewer 如何部署？
Blue Answer: 默认同一 Agent Runtime Service 中的 profiles/workers，共享 Domain Kernel、Capabilities、Knowledge Scope、Security、Eval；只有独立 SLA、权限、资源池或发布周期才拆。
Disposition: MERGE_AGENT_PROFILES
Evidence: user Target Constraint; RB-KERNEL-V3 multi-agent red team
Scorecard Ref: Q014
Gap Candidate Refs: GAP-REFRAME-005, GAP-REFRAME-011

## Q015

Attack Area: DATA_OWNERSHIP
Claim Under Test: PostgreSQL 与 LangGraph checkpoint 可共用一个事实源。
Red Attack: 这样不是更简单吗？
Blue Answer: 不能混为一谈。Platform Domain PostgreSQL 保存 Case/Fact/Evidence/Finding/Review/Effect business state；Runtime store/checkpointer 保存 node/branch/pending work/resume position。两者通过 version/generation/receipt reconcile。
Disposition: KEEP_STATE_SEPARATION
Evidence: current runtime graph; infra/db migrations; ADR 0005
Scorecard Ref: Q015
Gap Candidate Refs: GAP-REFRAME-012

## Q016

Attack Area: DATA_OWNERSHIP
Claim Under Test: Database-per-service 是微服务教条。
Red Attack: shared PostgreSQL cluster 是否违反服务边界？
Blue Answer: V1 采用 shared PostgreSQL cluster + schema/table ownership + API/event boundary；禁止跨服务私有表 JOIN。物理库隔离只有在独立 availability/scaling/security/lifecycle 有证据时才做。
Disposition: KEEP_LOGICAL_OWNERSHIP_FIRST
Evidence: infra/db migrations; docs/governance ownership baseline
Scorecard Ref: Q016
Gap Candidate Refs: GAP-REFRAME-013

## Q017

Attack Area: COMMUNICATION
Claim Under Test: 所有服务调用都应 gRPC 或都应 Event。
Red Attack: 统一协议是否更“架构化”？
Blue Answer: 不统一。CRUD/query/small command 用 HTTP；long-running/ingestion/graph/eval/sandbox 用 queue；外部 interoperability 用 MCP/API；gRPC 只作为高吞吐内部候选。每种调用都要有 idempotency/timeout/cancellation contract。
Disposition: KEEP_PROTOCOL_BY_WORKLOAD
Evidence: current FastAPI + RabbitMQ worker; user Target Constraint
Scorecard Ref: Q017
Gap Candidate Refs: GAP-REFRAME-014

## Q018

Attack Area: COMMUNICATION
Claim Under Test: 微服务一定比模块化单体更快。
Red Attack: network latency、serialization、retry storm、tracing 和 local development cost 怎么办？
Blue Answer: 不做性能绝对声明。同步路径保持短且少；大任务异步；trace propagation、schema version、backpressure、DLQ 和 reconciliation 是成本。可在 Developer Profile 用同镜像/Compose 运行，不把生产服务边界等同本地进程数。
Disposition: KEEP_WITH_COST_REGISTER
Evidence: service architecture target; current compose
Scorecard Ref: Q018
Gap Candidate Refs: GAP-REFRAME-014, GAP-REFRAME-015

## Q019

Attack Area: DEPLOYMENT
Claim Under Test: Microservice Target 自动要求 Kubernetes。
Red Attack: 是否因为微服务就引入 K8s、Kafka 和 service mesh？
Blue Answer: 不自动。Developer 使用 Compose，Staging 使用 multi-service profile，Production 只在 HA/rolling/autoscaling/operator evidence 成立后选择 managed container/Kubernetes。队列、数据库、网格均保持 provider/adapter。
Disposition: DEFER_KUBERNETES_AND_KAFKA
Evidence: infra/docker; docs/status/production-readiness.md
Scorecard Ref: Q019
Gap Candidate Refs: GAP-REFRAME-016

## Q020

Attack Area: DEPLOYMENT
Claim Under Test: 用户规模足以推出服务数量。
Red Attack: 3,000–8,000 注册用户是否就是拆分理由？
Blue Answer: 不是。理由是 workload heterogeneity：Platform transaction、Agent long-running、Knowledge CPU/GPU/IO、Sandbox security、Eval batch。容量数字仍是 Target assumption，不是 Current evidence。
Disposition: DELETE_USER_COUNT_ARGUMENT
Evidence: user capacity assumptions; current delivery facts UNKNOWN
Scorecard Ref: Q020
Gap Candidate Refs: GAP-REFRAME-003, GAP-REFRAME-016

## Q021

Attack Area: DOC_TAXONOMY
Claim Under Test: 11 Module + 1 Architecture 仍是唯一合理文档结构。
Red Attack: 11 是上一阶段拆分，为什么成为永久约束？
Blue Answer: 不应永久保留。正式 taxonomy 按问题组织：Product、Domain、Agents、Knowledge、Services、Data、Security、Eval、Deployment；旧模块进入 Superseded/History，不再作为 Canonical Source。
Disposition: REPLACE_TAXONOMY
Evidence: docs/project/architecture governance; user Target Constraint
Scorecard Ref: Q021
Gap Candidate Refs: GAP-REFRAME-017

## Q022

Attack Area: DOC_TAXONOMY
Claim Under Test: 新目录只要搬文件就能避免重复事实。
Red Attack: Product/Domain/Service/Data 各写一遍 Fact 状态怎么办？
Blue Answer: 每个 canonical doc 必须声明问题、Owner、Canonical Facts、输入输出、依赖和被替代文档；Domain owns business state，Runtime owns control state，Knowledge owns retrieval projections，Tool owns effects，Eval owns eval facts。其他文档只引用。
Disposition: KEEP_OWNERSHIP_REGISTRY
Evidence: ADR 0003/0007; new taxonomy design
Scorecard Ref: Q022
Gap Candidate Refs: GAP-REFRAME-018

## Q023

Attack Area: CURRENT_EVIDENCE
Claim Under Test: 当前仓库已经是真微服务架构。
Red Attack: Compose 有多少业务服务？
Blue Answer: HEAD 的 Compose 有 backend、worker、frontend 三个应用容器，其他是基础设施；backend 与 worker 使用同一镜像，业务服务没有独立 domain/runtime/knowledge/tool API。Target Microservice 尚未成为 Current。
Disposition: REJECT_CURRENT_MICROSERVICE_CLAIM
Evidence: infra/docker/docker-compose.yml; Dockerfile; zuno.main:app; queue.runner
Scorecard Ref: Q023
Gap Candidate Refs: GAP-REFRAME-019

## Q024

Attack Area: CURRENT_EVIDENCE
Claim Under Test: New taxonomy 已经取代旧文档。
Red Attack: 未更新入口、verifier、QA links 时是否形成两套真相？
Blue Answer: 现在只是 Target/Worktree 设计；必须同步 docs README、AGENT routing、system.yaml、verifiers/tests、old module disposition，并保留 history trace。完成前不能宣称迁移完成。
Disposition: EVIDENCE_GATE
Evidence: current hard-coded verifier inventory; docs governance
Scorecard Ref: Q024
Gap Candidate Refs: GAP-REFRAME-017, GAP-REFRAME-018

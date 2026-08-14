<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: ARCH-REFRAME-V1
execution_mode: AUTOMATED
status: ARCHIVED
base_sha: 0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_SESSION_COMPRESSION
source_session: RB-ARCH-REFRAME-V1
# ARCHITECTURE_INTERVIEW — ARCH-REFRAME-V1

本文件是正式 Red / Blue 对抗记录的单文件归档。它保留当时的核心问题、回答、Review/Score、决策和收口结果；不拥有今天的 Current Facts、Target Architecture 或实现授权。

## Session Manifest: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/manifest.yaml`

session_id: "RB-ARCH-REFRAME-V1"
workflow: "03-red-blue-optimization"
mode: "FULL_REVIEW"
scope: "PYTHON_ONLY_MICROSERVICE_ARCHITECTURE_REFRAME"
project_package_version: "ZUNO-MAIN@0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
target_role: "principal software architect / microservice and agent platform architect"
question_budget: 24
actual_question_count: 24
stop_reason: "QUESTION_BUDGET_REACHED_AFTER_SERVICE_BOUNDARY_FALSIFICATION"
zuno_base_sha: "0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
defense_base_sha: "0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
post_sync_sha: a8c167a
resume_version: "V1_PUBLIC_REPOSITORY_EVIDENCE"
project_fact_version: "docs/project/facts@0c07cfd"
campaign_id: "ZUNO-ARCHITECTURE-REFRAME-V1"
round_id: "RB-ARCH-REFRAME-V1"
parent_session_id: "RB-KERNEL-V3"
baseline_session_id: "RB-KERNEL-V3"
campaign_scope: "PYTHON_ONLY_MICROSERVICE_ARCHITECTURE_REFRAME"
campaign_phase: "ADVERSARIAL_ESCALATION"
red_kernel_version: "v3.1"
judge_policy_version: "v1"
source_scope:
  - "Zuno main @ 0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
  - "AGENTS.md, .agent/system.yaml, .agent/programs/current.md"
  - "docs/README.md, docs/project/**, docs/decisions/**, docs/status/**, docs/governance/**, docs/verification/**"
  - "project-reconstruction-lab/**, src/backend/**, infra/**, tests/**, tools/scripts/**"
started_at: "2026-08-12T23:30:00+08:00"
completed_at: "2026-08-13T02:30:00+08:00"
status: "COMPLETED"
user_gate_resolution: "APPROVED_WITH_AMENDMENTS"
resolution_status: "CANONICAL_SYNC_COMPLETE"
canonical_sync_sha: "a8c167a"
mutation_retest: "COMPLETED"
mutation_retest_result: "PASS_WITH_OPEN_EVIDENCE_GAPS"

## Questions / Transcript: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/transcript.md`

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

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/scorecard.md`

# RB-ARCH-REFRAME-V1 Scorecard

## 逐题记录

| Question ID | Attack Area | Answer Defensibility (0-5) | Architecture / Project Fitness (0-5) | Severity | Gap Type | Evidence Missing | Stop Status |
|---|---|---:|---:|---|---|---|---|
| Q001 | PYTHON_ONLY | 4 | 4 | P1 | ARCHITECTURE_GAP | cross-language cost benchmark | EVIDENCE_REQUIRED |
| Q002 | PYTHON_ONLY | 4 | 4 | P1 | PERFORMANCE_GAP | worker CPU/GPU measurements | EVIDENCE_REQUIRED |
| Q003 | PYTHON_ONLY | 4 | 4 | P1 | PERFORMANCE_GAP | workload profile and queue SLO | EVIDENCE_REQUIRED |
| Q004 | SERVICE_BOUNDARY | 4 | 4 | P0 | TARGET_CONSTRAINT | service boundary evidence | EVIDENCE_REQUIRED |
| Q005 | SERVICE_BOUNDARY | 5 | 5 | P0 | OVERENGINEERING_GAP | migration taxonomy proof | PASS |
| Q006 | SERVICE_BOUNDARY | 4 | 4 | P1 | SERVICE_BOUNDARY_GAP | edge scaling evidence | EVIDENCE_REQUIRED |
| Q007 | SERVICE_BOUNDARY | 4 | 5 | P0 | OWNERSHIP_GAP | domain write trace | EVIDENCE_REQUIRED |
| Q008 | SERVICE_BOUNDARY | 4 | 5 | P0 | RUNTIME_GAP | long-run service trace | EVIDENCE_REQUIRED |
| Q009 | SERVICE_BOUNDARY | 4 | 4 | P0 | SERVICE_BOUNDARY_GAP | knowledge worker SLO | EVIDENCE_REQUIRED |
| Q010 | SERVICE_BOUNDARY | 4 | 5 | P0 | SECURITY_GAP | sandbox isolation evidence | EVIDENCE_REQUIRED |
| Q011 | SERVICE_BOUNDARY | 5 | 4 | P1 | OVERENGINEERING_GAP | legal capability resource evidence | EVIDENCE_REQUIRED |
| Q012 | SERVICE_BOUNDARY | 4 | 4 | P1 | OVERENGINEERING_GAP | model gateway sharing evidence | EVIDENCE_REQUIRED |
| Q013 | SERVICE_BOUNDARY | 4 | 4 | P1 | OVERENGINEERING_GAP | eval worker lifecycle evidence | EVIDENCE_REQUIRED |
| Q014 | AGENT_RUNTIME | 5 | 4 | P0 | OVERENGINEERING_GAP | agent profile vs service test | EVIDENCE_REQUIRED |
| Q015 | DATA_OWNERSHIP | 5 | 5 | P0 | OWNERSHIP_GAP | domain/runtime reconcile trace | EVIDENCE_REQUIRED |
| Q016 | DATA_OWNERSHIP | 4 | 4 | P1 | DEPLOYMENT_GAP | schema isolation evidence | EVIDENCE_REQUIRED |
| Q017 | COMMUNICATION | 4 | 4 | P1 | COMMUNICATION_GAP | protocol latency/error matrix | EVIDENCE_REQUIRED |
| Q018 | COMMUNICATION | 4 | 3 | P1 | OPERATIONAL_GAP | tracing/retry cost | EVIDENCE_REQUIRED |
| Q019 | DEPLOYMENT | 5 | 4 | P1 | OVERENGINEERING_GAP | deployment profile evidence | EVIDENCE_REQUIRED |
| Q020 | DEPLOYMENT | 5 | 4 | P1 | OVERENGINEERING_GAP | real capacity/workload data | KNOWN_GAP |
| Q021 | DOC_TAXONOMY | 5 | 5 | P0 | DOC_GOVERNANCE_GAP | taxonomy migration | EVIDENCE_REQUIRED |
| Q022 | DOC_TAXONOMY | 5 | 5 | P0 | OWNERSHIP_GAP | canonical registry verifier | EVIDENCE_REQUIRED |
| Q023 | CURRENT_EVIDENCE | 5 | 1 | P0 | CURRENT_EVIDENCE_GAP | deployed service evidence | KNOWN_GAP |
| Q024 | CURRENT_EVIDENCE | 5 | 2 | P0 | DOC_GOVERNANCE_GAP | final verifier and link audit | EVIDENCE_REQUIRED |

## Campaign Quality Profile

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | p0_count | p1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| PYTHON_ONLY | 3 | 4.00 | 4.00 | 0 | 3 | 0 | 0.00 |
| SERVICE_BOUNDARY | 10 | 4.40 | 4.40 | 6 | 4 | 0 | 0.00 |
| AGENT_RUNTIME | 1 | 5.00 | 4.00 | 1 | 0 | 0 | 0.00 |
| DATA_OWNERSHIP | 2 | 4.50 | 4.50 | 1 | 1 | 0 | 0.00 |
| COMMUNICATION | 2 | 4.00 | 3.50 | 0 | 2 | 0 | 0.00 |
| DEPLOYMENT | 2 | 5.00 | 4.00 | 0 | 2 | 0 | 0.00 |
| DOC_TAXONOMY | 2 | 5.00 | 5.00 | 2 | 0 | 0 | 0.00 |
| CURRENT_EVIDENCE | 2 | 5.00 | 1.50 | 2 | 0 | 0 | 0.00 |

question_count: 24
avg_answer_defensibility: 4.54
avg_architecture_project_fitness: 4.00
p0_count: 12
p1_count: 12
unsupported_count: 0
unsupported_rate: 0.00

## Campaign Summary

coverage_status: COMPLETE_FOR_REFRAME_SCOPE
p0_total: 11
p1_total: 13
reopened_gap_count: 0
decision: PYTHON_ONLY_AND_MICROSERVICE_TARGET_SURVIVE; SERVICE_COUNT_AND_TAXONOMY_REFRAMED

## Baseline Delta

- Python-only 与 Microservice 从“候选”变成用户确认的 Target Constraint；红队只保留边界、成本和证据攻击。
- 11 Logical Modules 不再是永久 Canonical Architecture；服务数量收敛为 5 个 network-facing Python services + worker profiles 的 Target 候选。
- Multi-Agent 保持开放，但 Agent profile 不自动等于微服务；Legal Intelligence、Model Gateway、Eval/Observability 等候选服务被压缩为 Provider/Worker，除非出现独立边界证据。

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/red-team-report.md`

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

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/gaps.md`

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

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/blue-change-set.md`

# RB-ARCH-REFRAME-V1 Blue Change Set

## CHANGE-001

Source Cluster IDs: CLUSTER-001, CLUSTER-002, CLUSTER-003, CLUSTER-004
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/decisions/0009-python-only-backend.md; docs/decisions/0010-microservice-target-and-service-boundaries.md; docs/project/architecture/architecture.md; docs/project/services/service-architecture.md; docs/project/deployment/microservice-deployment.md
Applied Commit SHA: a8c167a
Validation Run: architecture reframe, link, governance, red-blue and focused pytest suite passed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: Python-only and Microservice remain Target constraints; five network-facing services are the current Target candidate; workers, protocols, K8s and physical DB splits remain evidence-gated.

## CHANGE-002

Source Cluster IDs: CLUSTER-005, CLUSTER-006
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/project/README.md; docs/project/architecture/README.md; docs/project/architecture/architecture-views.md; docs/project/architecture/architecture.html; docs/project/product/; docs/project/domain/; docs/project/agents/; docs/project/knowledge/; docs/project/services/; docs/project/data/; docs/project/security/; docs/project/eval/; docs/project/deployment/; .agent/system.yaml; AGENTS.md
Applied Commit SHA: a8c167a
Validation Run: architecture reframe, link, governance, red-blue and focused pytest suite passed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: replace 11 Module + 1 Architecture as canonical taxonomy; old module documents are explicitly Superseded/History and no longer own current Target facts.

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-ARCH-REFRAME-V1/retest.md`

# RB-ARCH-REFRAME-V1 Retest

## RETEST-001

上一轮 Gap: GAP-REFRAME-017, GAP-REFRAME-018, GAP-REFRAME-019
Change IDs: CHANGE-001, CHANGE-002
Mutation Variable: 将正式入口从 11 Module + 1 Architecture 改为 Product/Domain/Agents/Knowledge/Services/Data/Security/Eval/Deployment taxonomy，并把五服务 Target 与 Current 单体+worker事实分离。
Result: PASS
Observation: 新 taxonomy、五服务 Target、Python-only/LangGraph/FastAPI 边界和旧入口迁移已同步；服务数、性能、质量、安全与生产部署仍需独立 Evidence。

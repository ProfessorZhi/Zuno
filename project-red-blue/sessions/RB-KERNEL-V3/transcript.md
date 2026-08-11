# RB-KERNEL-V3 Red Team Transcript

本记录是公开证据审计，不保存隐藏思维链。每题只记录攻击命题、可审计回答、反证状态与下一步证据。

## Q001

Attack Area: HOST_SUBSTITUTION
Claim Under Test: WorkBuddy + 法律知识库 + Skills + MCP/API 已足以覆盖 Zuno 的完整价值。
Red Attack: 官方资料已公开 WorkBuddy 的专家、Skills、MCP 与任务执行能力；为什么还需要独立 Host？
Blue Answer: 不能证明需要独立 Host。Host 应默认外置；只有 Canonical 法律状态、证据依赖、人工决定和可验证执行不能通过稳定 API 维持时，才有升级理由。
Disposition: SURVIVES_ONLY_AS_BACKEND_CONTRACT
Evidence: official platform matrix; docs/project/architecture/architecture.md; repository code inventory
Scorecard Ref: Q001
Gap Candidate Refs: GAP-V3-001

## Q002

Attack Area: HOST_SUBSTITUTION
Claim Under Test: Zuno Native Runtime 是必要组件。
Red Attack: 一个普通 Backend Workflow、Temporal/Celery 或 WorkBuddy Tool 是否已经足够？
Blue Answer: 当前没有证据证明 Native Runtime 必要。Legal Backend + 普通异步工作流是默认最小方案；Native Runtime 只能作为 C 变体，等待公平 Benchmark。
Disposition: DEFER_NATIVE_RUNTIME
Evidence: docs/decisions/0007-reuse-first-provider-boundary.md; docs/project/modules/06-agent-core-planning-control.md
Scorecard Ref: Q002
Gap Candidate Refs: GAP-V3-001, GAP-V3-002

## Q003

Attack Area: HOST_SUBSTITUTION
Claim Under Test: Domain-aware Runtime 相比 Tool-level integration 有已知质量/效率收益。
Red Attack: 是否只是把 orchestration 从 Tool 内搬到 Runtime？
Blue Answer: 是一个有效的杀伤性解释。first-class domain input/output 只有在跨运行复用、依赖失效、证据门控或人工决定确实减少重推理/错误时才产生可测收益；目前只是 Hypothesis。
Disposition: HYPOTHESIS_NOT_PROVEN
Evidence: docs/status/production-readiness.md; no legal-domain runtime code or trace at BASE_SHA
Scorecard Ref: Q003
Gap Candidate Refs: GAP-V3-002, GAP-V3-003

## Q004

Attack Area: HOST_SUBSTITUTION
Claim Under Test: WorkBuddy 不具备足够的企业安全能力。
Red Attack: 能否用“不安全”作为 Zuno 独立存在的理由？
Blue Answer: 不能。公开企业资料存在权限、控制、审计、专有部署等能力描述；其精确合同和证据未知。Zuno 的可辩护差异只能是目标性的 Security Verifiability + Deployment Sovereignty。
Disposition: DELETE_UNSUPPORTED_ATTACK
Evidence: WorkBuddy public enterprise pages; docs/project/modules/09-security.md
Scorecard Ref: Q004
Gap Candidate Refs: GAP-V3-004

## Q005

Attack Area: DOMAIN_KERNEL_MINIMALITY
Claim Under Test: 全部候选法律对象都必须成为 Canonical Domain Object。
Red Attack: Matter、Case、Party、DocumentVersion、Claim、Fact、Event、Evidence、Conflict、Dispute、LegalIssue、StatuteVersion、LegalElement、ApplicableLaw、SimilarCase、Finding、HumanDecision、WorkProduct 是否构成对象膨胀？
Blue Answer: 是。最小根对象暂保留 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct；Case 可作为场景别名/配置，其他对象先作为 typed proposal、projection 或 capability output，除非身份、版本、Owner 和审查需求被证明。
Disposition: SIMPLIFY_DOMAIN_KERNEL
Evidence: module ownership docs; no matching legal classes in src/backend/zuno at BASE_SHA
Scorecard Ref: Q005
Gap Candidate Refs: GAP-V3-003

## Q006

Attack Area: DOMAIN_KERNEL_MINIMALITY
Claim Under Test: 普通 JSON + PostgreSQL 与正式 Domain Model 等价且更简单。
Red Attack: 如果只需返回 JSON，为什么要 Canonical Owner、版本和状态？
Blue Answer: 对一次性问答，普通 JSON 足够；对跨文档、跨运行、人工修订和审计，JSON 只有在补齐稳定 Identity、Version、Provenance、Ownership、Mutation Authority、Staleness、Dependency、Review、Audit 后才形成 Domain Contract。复杂度由复用场景证明，而非名称证明。
Disposition: CONDITIONAL_KEEP
Evidence: docs/decisions/0007; docs/project/modules/01,03,06,09
Scorecard Ref: Q006
Gap Candidate Refs: GAP-V3-003, GAP-V3-005

## Q007

Attack Area: DOMAIN_KERNEL_MINIMALITY
Claim Under Test: Legal Domain State 就是 Memory 的更正式叫法。
Red Attack: Matter Fact 是否可以直接作为长期 Memory？
Blue Answer: 不可以。Domain State 表示业务世界的当前可审计状态和主张版本；Memory 表示可复用上下文/经验，可能被压缩、过期、删除或召回。Fact/Evidence/Finding 不能因为可复用就变成 Memory。
Disposition: KEEP_BOUNDARY_SIMPLIFIED
Evidence: docs/project/modules/05-memory-context.md; docs/project/architecture/architecture.md
Scorecard Ref: Q007
Gap Candidate Refs: GAP-V3-005

## Q008

Attack Area: DOMAIN_LIFECYCLE
Claim Under Test: New Evidence 到来后需要 Event Sourcing 或全量重算。
Red Attack: Evidence → Fact/Conflict/Dispute/ApplicableLaw/Finding 的失效和新 Run 如何实现？
Blue Answer: Postgres 保存当前事实及不可变版本；新 Evidence 写入后按依赖边界标记受影响 Fact/Finding 为 STALE 或 REVIEW_REQUIRED，冲突/适用性等派生结果按策略重新评估，必要时 enqueue 新 Run。默认不引入 Event Sourcing，也不在同一事务中盲目全量重算。
Disposition: SIMPLIFY_TO_VERSIONED_POSTGRES
Evidence: docs/project/modules/06-agent-core-planning-control.md; docs/status/production-readiness.md
Scorecard Ref: Q008
Gap Candidate Refs: GAP-V3-005, GAP-V3-006

## Q009

Attack Area: DOMAIN_LIFECYCLE
Claim Under Test: Canonical Domain Owner 是必要的，而不是 API 网关的包装。
Red Attack: 普通 Backend 是否可以把 Tool JSON 直接写库？
Blue Answer: 低风险原型可以；正式法律事实不能。Provider/Agent 输出必须是 Proposal/Candidate，Owner 做 Schema、Evidence、Permission、Version 和状态转换，才能避免模型或工具直接宣布事实。
Disposition: CONDITIONAL_KEEP
Evidence: docs/project/modules/07-capability-skill.md; docs/project/modules/01-product-surface.md
Scorecard Ref: Q009
Gap Candidate Refs: GAP-V3-005

## Q010

Attack Area: CURRENT_REALITY
Claim Under Test: Zuno 已经拥有 Legal Domain Kernel。
Red Attack: BASE_SHA 的代码、Migration、Trace 或 Eval 在哪里证明 Matter/Fact/Conflict/FindingVersion？
Blue Answer: 未找到可证明完整法律 Kernel 的实现。代码可见的是通用 ingestion/document/retrieval/agent/evidence 结构与目标文档；法律对象与变更闭环仍是 Target/Hypothesis。
Disposition: REJECT_CURRENT_CLAIM
Evidence: repository-current-inventory.md; docs/status/production-readiness.md
Scorecard Ref: Q010
Gap Candidate Refs: GAP-V3-003, GAP-V3-007

## Q011

Attack Area: CURRENT_REALITY
Claim Under Test: 当前 Runtime 已具备 Domain State first-class input/output。
Red Attack: LangGraph checkpoint、AgentRun 与 legal business fact 是否已有可运行对账证据？
Blue Answer: 文档定义了分离边界，但缺少法律 Domain State 的实现与 E2E trace；因此不能将 Target Contract 表述为 Current。
Disposition: REJECT_CURRENT_CLAIM
Evidence: docs/evidence/current-runtime-baseline.md; no legal domain classes at BASE_SHA
Scorecard Ref: Q011
Gap Candidate Refs: GAP-V3-007

## Q012

Attack Area: RETRIEVAL
Claim Under Test: GraphRAG 是法律系统的默认必要能力。
Red Attack: Fixed Hybrid 是否已经能覆盖多数任务？
Blue Answer: 不能先验断言 Graph 优越。Exact statute、semantic similarity 可由 lexical/dense/hybrid 解决；跨文档证据链、Fact→Element→Statute、事件关系才是 Graph 的条件候选。
Disposition: DELETE_ALWAYS_ON_GRAPH
Evidence: docs/decisions/0006; docs/project/modules/03-knowledge-agentic-graphrag.md
Scorecard Ref: Q012
Gap Candidate Refs: GAP-V3-008

## Q013

Attack Area: RETRIEVAL
Claim Under Test: Agentic RAG without Graph 与 Conditional Legal Graph 必须采用复杂图控制。
Red Attack: Graph 构建、更新和错误传播成本是否可能超过收益？
Blue Answer: 是，必须测 Recall@K、nDCG、Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Latency、Token、Cost；没有 Kill Graph Test，Graph 只保留 Provider 候选。
Disposition: DEFER_GRAPH_PROVIDER
Evidence: project-red-blue/09-open-source-review.md; docs/project/modules/10-observability-eval.md
Scorecard Ref: Q013
Gap Candidate Refs: GAP-V3-008, GAP-V3-009

## Q014

Attack Area: MULTI_AGENT
Claim Under Test: Persistent Multi-Agent Team 是必要默认值。
Red Attack: 一个强 Agent + parallel tools 或 L2 ephemeral worker 是否足够？
Blue Answer: 优先 L0 single controller、L1 role pipeline、L2 ephemeral worker、L3 specialized capability；持久 Agent Team 和 autonomous society 删除为默认目标，除非任务并发、权限和结果优势可复现。
Disposition: DELETE_PERSISTENT_TEAM_DEFAULT
Evidence: docs/project/modules/03; docs/project/modules/06; docs/status/production-readiness.md
Scorecard Ref: Q014
Gap Candidate Refs: GAP-V3-010

## Q015

Attack Area: MEMORY
Claim Under Test: 独立 Long-term Memory 是复杂法律任务的必要基础设施。
Red Attack: Matter DB + Runtime Checkpoint 是否已经足够？
Blue Answer: 对 Matter context 和执行恢复，通常先用 Domain Store + Checkpoint；Memory 只在可测地改善跨任务召回且不污染权威状态时启用，Working/Session 优先，Long-term 进入 Future/Conditional。
Disposition: SIMPLIFY_MEMORY_OPTIONAL
Evidence: docs/project/modules/05-memory-context.md; docs/project/modules/06-agent-core-planning-control.md
Scorecard Ref: Q015
Gap Candidate Refs: GAP-V3-011

## Q016

Attack Area: RUNTIME
Claim Under Test: LangGraph 或自研 Runtime 是不可替换核心。
Red Attack: Plain Python、Async Workflow、State Machine、WorkBuddy Runtime、Pi 或 LangGraph 是否都可以作为 provider？
Blue Answer: 可以。LangGraph 仅在 durable execution、checkpoint、interrupt/resume、parallel/reducer、replan、HITL 等需求被任务证明时保留；Legal Domain Fact 不能放入其 checkpoint。
Disposition: EXTERNALIZE_RUNTIME_PROVIDER
Evidence: official LangGraph persistence/interrupt docs; docs/project/modules/06
Scorecard Ref: Q016
Gap Candidate Refs: GAP-V3-002, GAP-V3-012

## Q017

Attack Area: TOOL_RUNTIME
Claim Under Test: Zuno 必须自建 Tool Runtime 才能安全执行。
Red Attack: MCP/API/CLI/现有 Sandbox 加一个薄 Adapter 是否已足够？
Blue Answer: 对 capability execution，普通 MCP/API/CLI/异步作业是优先路径；Zuno 只保留授权、幂等、Receipt、审计和对账 Contract。自研 Runtime 不作为默认产品边界。
Disposition: SIMPLIFY_TOOL_PLANE
Evidence: docs/project/modules/08-tool-runtime.md; docs/project/modules/09-security.md
Scorecard Ref: Q017
Gap Candidate Refs: GAP-V3-012

## Q018

Attack Area: DEPLOYMENT
Claim Under Test: 3,000–8,000 注册用户足以证明十一微服务。
Red Attack: Modular Monolith + independently scalable workers 是否足够？
Blue Answer: 用户数本身不构成微服务证据。先按 API/Domain、Agent long-running、ingestion/index、sandbox、eval 的 workload heterogeneity 划分 worker；只有 scaling/failure/deploy/security/team ownership 数据证明后再拆。
Disposition: DELETE_MICROSERVICE_DEFAULT
Evidence: docs/project/modules/11-infrastructure.md; capacity assumptions in user brief are not Current
Scorecard Ref: Q018
Gap Candidate Refs: GAP-V3-013

## Q019

Attack Area: SECURITY
Claim Under Test: Zuno 因为开源和自部署而天然更安全。
Red Attack: 能否把 source visibility 等同于安全？
Blue Answer: 不能。安全差异应是可验证性与部署主权的 Target/Hypothesis，需 SBOM、签名产物、离线网络测试、secret/tool/model/domain trace、sandbox 与供应链证据。
Disposition: DELETE_UNSUPPORTED_SECURITY_CLAIM
Evidence: docs/project/modules/09-security.md; official WorkBuddy enterprise pages
Scorecard Ref: Q019
Gap Candidate Refs: GAP-V3-004, GAP-V3-014

## Q020

Attack Area: SECURITY
Claim Under Test: WorkBuddy 的公开部署方式可以被推定为不安全。
Red Attack: 没有官方证据时能否做该断言？
Blue Answer: 不能。WorkBuddy 的确切租户、网络、审计和模型路由合同保持 UNKNOWN；应设计相同 Security Benchmark，而非做品牌推断。
Disposition: DELETE_UNSUPPORTED_ATTACK
Evidence: official WorkBuddy public pages and service/privacy terms
Scorecard Ref: Q020
Gap Candidate Refs: GAP-V3-004, GAP-V3-014

## Q021

Attack Area: LEGAL_CAPABILITY
Claim Under Test: 论文算法应直接写进各个 Agent。
Red Attack: JIA、Fact–Article、冲突检测、法条预测是否需要 Agent 内嵌代码？
Blue Answer: 不应。能力定义为 `EVENT_EXTRACTION`、`EVENT_ALIGNMENT`、`CONFLICT_DETECTION`、`FACT_ARTICLE_MAPPING`、`SIMILAR_CASE_RETRIEVAL`、`LEGAL_APPLICABILITY`、`EVIDENCE_REASONING`；provider 只交付 Proposal/Candidate/Reference/Receipt。
Disposition: KEEP_CAPABILITY_PROVIDER_BOUNDARY
Evidence: legal-ai-capability-matrix.md; docs/project/modules/07-capability-skill.md
Scorecard Ref: Q021
Gap Candidate Refs: GAP-V3-015

## Q022

Attack Area: LEGAL_CAPABILITY
Claim Under Test: 公开论文/仓库即可证明商业可复用和 Zuno 质量领先。
Red Attack: 是否逐项检查 code/data/model/license/reproduction？
Blue Answer: 未证明。InternLM-Law 代码仓库有 Apache-2.0，但模型权重/数据需要单独核查；LawBench 是评测，不是集成；JIA、Fact–Article、Statute、LJPCheck 的代码/数据商业授权保持 UNKNOWN。
Disposition: DEFER_INTEGRATION
Evidence: legal-ai-capability-matrix.md; official repository LICENSE files
Scorecard Ref: Q022
Gap Candidate Refs: GAP-V3-015, GAP-V3-016

## Q023

Attack Area: BENCHMARK
Claim Under Test: Zuno 在同模型/语料/工具/预算下已经优于 WorkBuddy、Dify 或 generic setup。
Red Attack: 是否有 A/B/C 的复杂法律任务结果？
Blue Answer: 没有。只能冻结 Benchmark A WorkBuddy generic、B WorkBuddy + Zuno capabilities、C Zuno native runtime；指标必须含 evidence/citation/unsupported/conflict/fact-article/applicability/reviewer acceptance 以及 latency/token/cost/model calls/reuse。
Disposition: REJECT_CURRENT_SUPERIORITY
Evidence: docs/status/production-readiness.md; current eval baseline
Scorecard Ref: Q023
Gap Candidate Refs: GAP-V3-017

## Q024

Attack Area: MINIMUM_ARCHITECTURE
Claim Under Test: Full Legal-native Agent Platform 是当前最小充分架构。
Red Attack: 如果 WorkBuddy + Legal Backend 已足够，Zuno Runtime/Graph/Memory/Microservices 如何处置？
Blue Answer: 最小充分方案 A/B 都优先于 C。A 是 WorkBuddy Host + legal scopes/skills + MCP/API capability backend；B 增加 Canonical Domain Store、evidence/review contracts 和轻量 worker；C 只有当 C>B 的收益被重复证明时才启用 native runtime。
Disposition: ADOPT_MINIMAL_B_DEFER_C
Evidence: all V3 artifacts; docs/decisions/0008 when synchronized
Scorecard Ref: Q024
Gap Candidate Refs: GAP-V3-001, GAP-V3-002, GAP-V3-017

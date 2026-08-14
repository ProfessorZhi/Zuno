<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: KERNEL-V3
execution_mode: AUTOMATED
status: ARCHIVED
base_sha: 0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_SESSION_COMPRESSION
source_session: RB-KERNEL-V3
# ARCHITECTURE_INTERVIEW — KERNEL-V3

本文件是正式 Red / Blue 对抗记录的单文件归档。它保留当时的核心问题、回答、Review/Score、决策和收口结果；不拥有今天的 Current Facts、Target Architecture 或实现授权。

## Session Manifest: `project-reconstruction-lab/sessions/RB-KERNEL-V3/manifest.yaml`

session_id: "RB-KERNEL-V3"
workflow: "03-red-blue-optimization"
mode: "FULL_REVIEW"
scope: "DOMAIN_NATIVE_AGENT_PLATFORM_COMPETITIVE_FALSIFICATION"
project_package_version: "ZUNO-MAIN@0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
target_role: "principal software architect / red team architecture auditor"
question_budget: 24
actual_question_count: 24
stop_reason: "QUESTION_BUDGET_REACHED_AFTER_COMPETITIVE_FALSIFICATION"
zuno_base_sha: "0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
defense_base_sha: "0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
post_sync_sha: a8c167a
resume_version: "V3_PUBLIC_EVIDENCE_ONLY"
project_fact_version: "docs/project/facts@0c07cfd"
campaign_id: "ZUNO-RED-KERNEL-V3"
round_id: "RB-KERNEL-V3"
parent_session_id: "RB-ARCH-001"
baseline_session_id: "RB-ARCH-001"
campaign_scope: "DOMAIN_NATIVE_AGENT_PLATFORM_COMPETITIVE_FALSIFICATION"
campaign_phase: "ADVERSARIAL_ESCALATION"
red_kernel_version: "v3"
judge_policy_version: "v3"
source_scope:
  - "Zuno main @ 0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f"
  - "AGENTS.md, .agent/system.yaml, .agent/programs/current.md"
  - "docs/project/**, docs/decisions/**, docs/status/**, docs/evidence/**, docs/governance/**"
  - "project-reconstruction-lab/**"
  - "src/backend/zuno/**, tests/**, pyproject.toml"
  - "Tencent WorkBuddy official public pages accessed 2026-08-12"
  - "Dify, Pi, LangGraph and RAGFlow official documentation/repositories accessed 2026-08-12"
  - "JIA, Fact-Article Correspondence, Statute Prediction, LawBench, LJPCheck and InternLM-Law primary sources accessed 2026-08-12"
started_at: "2026-08-12T19:00:00+08:00"
completed_at: "2026-08-12T23:00:00+08:00"
status: "COMPLETED"
user_gate_resolution: "APPROVED_WITH_AMENDMENTS"
resolution_status: "CANONICAL_SYNC_COMPLETE"
canonical_sync_sha: "a8c167a"
mutation_retest: "COMPLETED"
mutation_retest_result: "PASS_WITH_OPEN_EVIDENCE_GAPS"

## Questions / Transcript: `project-reconstruction-lab/sessions/RB-KERNEL-V3/transcript.md`

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
Evidence: project-reconstruction-lab/legacy/numbered/09-open-source-review.md; docs/project/modules/10-observability-eval.md
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

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-KERNEL-V3/scorecard.md`

# RB-KERNEL-V3 Scorecard

## 逐题记录

| Question ID | Attack Area | Answer Defensibility (0-5) | Architecture / Project Fitness (0-5) | Severity | Gap Type | Evidence Missing | Stop Status |
|---|---|---:|---:|---|---|---|---|
| Q001 | HOST_SUBSTITUTION | 4 | 2 | P0 | BUILD_BUY_GAP | WorkBuddy contract fit spike | KNOWN_GAP |
| Q002 | HOST_SUBSTITUTION | 4 | 2 | P0 | OVERENGINEERING_GAP | A/B/C runtime benchmark | KNOWN_GAP |
| Q003 | HOST_SUBSTITUTION | 4 | 3 | P1 | MEASUREMENT_GAP | state reuse and re-reasoning measurements | EVIDENCE_REQUIRED |
| Q004 | HOST_SUBSTITUTION | 5 | 4 | P1 | UNSUPPORTED_CLAIM | exact WorkBuddy enterprise contract | PASS |
| Q005 | DOMAIN_KERNEL_MINIMALITY | 4 | 4 | P1 | OVERENGINEERING_GAP | canonical object decision record | EVIDENCE_REQUIRED |
| Q006 | DOMAIN_KERNEL_MINIMALITY | 4 | 4 | P1 | ARCHITECTURE_GAP | cross-run/legal task spike | EVIDENCE_REQUIRED |
| Q007 | DOMAIN_KERNEL_MINIMALITY | 5 | 4 | P2 | DOC_CLARIFY | no Current implementation | PASS |
| Q008 | DOMAIN_LIFECYCLE | 4 | 4 | P1 | ARCHITECTURE_GAP | dependency invalidation trace | EVIDENCE_REQUIRED |
| Q009 | DOMAIN_LIFECYCLE | 4 | 4 | P1 | SECURITY_GAP | proposal-to-owner write trace | EVIDENCE_REQUIRED |
| Q010 | CURRENT_REALITY | 5 | 1 | P0 | CURRENT_EVIDENCE_GAP | legal kernel code/migration/trace | KNOWN_GAP |
| Q011 | CURRENT_REALITY | 5 | 1 | P0 | CURRENT_EVIDENCE_GAP | legal domain/checkpoint E2E | KNOWN_GAP |
| Q012 | RETRIEVAL | 4 | 4 | P1 | BUILD_BUY_GAP | kill graph benchmark | EVIDENCE_REQUIRED |
| Q013 | RETRIEVAL | 4 | 4 | P1 | MEASUREMENT_GAP | graph cost/error buckets | EVIDENCE_REQUIRED |
| Q014 | MULTI_AGENT | 4 | 4 | P1 | OVERENGINEERING_GAP | L0-L3 comparison | EVIDENCE_REQUIRED |
| Q015 | MEMORY | 4 | 4 | P1 | OVERENGINEERING_GAP | memory ablation | EVIDENCE_REQUIRED |
| Q016 | RUNTIME | 4 | 4 | P0 | BUILD_BUY_GAP | runtime substitution spike | EVIDENCE_REQUIRED |
| Q017 | TOOL_RUNTIME | 4 | 4 | P1 | BUILD_BUY_GAP | MCP/API adapter and effect trace | EVIDENCE_REQUIRED |
| Q018 | DEPLOYMENT | 5 | 4 | P1 | OVERENGINEERING_GAP | workload/failure/scaling evidence | KNOWN_GAP |
| Q019 | SECURITY | 5 | 3 | P1 | SECURITY_GAP | attested security benchmark | EVIDENCE_REQUIRED |
| Q020 | SECURITY | 5 | 4 | P1 | UNSUPPORTED_CLAIM | WorkBuddy deployment evidence | KNOWN_GAP |
| Q021 | LEGAL_CAPABILITY | 4 | 4 | P1 | ARCHITECTURE_GAP | provider conformance spike | EVIDENCE_REQUIRED |
| Q022 | LEGAL_CAPABILITY | 5 | 4 | P0 | LICENSE_GAP | data/model/code license matrix | KNOWN_GAP |
| Q023 | BENCHMARK | 5 | 1 | P0 | MEASUREMENT_GAP | executed A/B/C results | KNOWN_GAP |
| Q024 | MINIMUM_ARCHITECTURE | 4 | 4 | P0 | BUILD_BUY_GAP | replacement cost and C>B result | KNOWN_GAP |

## Campaign Quality Profile

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | p0_count | p1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| HOST_SUBSTITUTION | 4 | 4.25 | 2.75 | 2 | 2 | 2 | 0.50 |
| DOMAIN_KERNEL_MINIMALITY | 3 | 4.33 | 4.00 | 0 | 3 | 0 | 0.00 |
| DOMAIN_LIFECYCLE | 2 | 4.00 | 4.00 | 0 | 2 | 0 | 0.00 |
| CURRENT_REALITY | 2 | 5.00 | 1.00 | 2 | 0 | 0 | 0.00 |
| RETRIEVAL | 2 | 4.00 | 4.00 | 0 | 2 | 0 | 0.00 |
| MULTI_AGENT | 1 | 4.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| MEMORY | 1 | 4.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| RUNTIME | 1 | 4.00 | 4.00 | 1 | 0 | 0 | 0.00 |
| TOOL_RUNTIME | 1 | 4.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| DEPLOYMENT | 1 | 5.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| SECURITY | 2 | 5.00 | 3.50 | 0 | 2 | 2 | 1.00 |
| LEGAL_CAPABILITY | 2 | 4.50 | 4.00 | 1 | 1 | 0 | 0.00 |
| BENCHMARK | 1 | 5.00 | 1.00 | 1 | 0 | 0 | 0.00 |
| MINIMUM_ARCHITECTURE | 1 | 4.00 | 4.00 | 1 | 0 | 0 | 0.00 |

question_count: 24
avg_answer_defensibility: 4.38
avg_architecture_project_fitness: 3.33
p0_count: 8
p1_count: 16
unsupported_count: 4
unsupported_rate: 0.17

## Campaign Summary

coverage_status: COMPLETE_FOR_V3_SCOPE
p0_total: 8
p1_total: 16
reopened_gap_count: 0
decision: MINIMAL_DOMAIN_BACKEND_SURVIVES; NATIVE_RUNTIME_NOT_PROVEN

## Baseline Delta

- RB-ARCH-001 的 Build-vs-Buy gap 在 V3 被拆成 Host、Domain Backend、Runtime Provider、Retrieval、Memory、Tool、Deployment 七个独立杀伤面。
- V3 首次把 WorkBuddy 作为公平 A/B/C benchmark 的 Host 变体，并把针对 WorkBuddy 的安全负面断言从攻击选项中删除为无证据断言。
- V3 没有把法律对象列表、GraphRAG、Multi-Agent、Memory、Runtime 或微服务升级为 Current；所有未运行的收益保持 Hypothesis。

---

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-KERNEL-V3/red-team-report.md`

# RED-KERNEL-V3 红队报告

## 结论先行

本轮没有证明 Zuno 需要独立的完整 Agent Host 或自研 Agent Runtime。最强的可被保留命题更窄：在跨文档、跨运行、需要人工修订、证据依赖失效和审计的法律任务中，可能需要一个法律业务状态后端；这个后端可以由 WorkBuddy、Dify、Pi 或其他 Host 通过 MCP/API 调用。

这不是 Zuno 当前能力优于 WorkBuddy 的结论。BASE_SHA 上没有足够的法律 Domain Kernel 代码、Migration、运行 Trace 或 Eval；质量、效率、安全和生产性均保持 Hypothesis/UNKNOWN。仓库侦察记录见 `project-reconstruction-lab/sources/repository-current-inventory.md`。

## 最强的十个反对理由

1. WorkBuddy 已公开横向 Agent、Skills、MCP 和任务执行能力；独立 Host 的增量价值没有证明。
2. WorkBuddy + 普通 MCP/API Legal Backend 可能覆盖 Domain-aware Runtime 的大部分收益；Runtime 可能只是搬运 orchestration。
3. Zuno 当前代码没有可证明的完整 Matter/Fact/Conflict/FindingVersion 法律状态闭环，Target 不能冒充 Current。
4. 全部候选法律对象会制造 identity、version、owner、dependency 和 migration 负担；多数对象应先是 projection 或 provider proposal。
5. New Evidence 的 stale/re-evaluation 可以用 PostgreSQL 当前事实、版本和依赖引用加异步工作流处理，不需要 Event Sourcing。
6. Exact statute 和语义检索可能由 lexical/dense/hybrid 解决；GraphRAG 的额外成本和错误传播尚未被 Kill Test 抵消。
7. Single Controller + parallel tools 或 ephemeral worker 可能足够；Persistent Multi-Agent Team 没有质量/效率证据。
8. Matter DB + checkpoint 可能覆盖工作上下文和恢复；独立 Long-term Memory 不应成为硬依赖。
9. MCP/API/CLI/现有 Sandbox 加授权、幂等、Receipt 和审计适配器可能足够；自研 Tool Runtime 没有独立必要性。
10. 数千用户的假设不能推出十一微服务；工作负载异构才是拆分理由，必须先证明模块化单体 + worker 不足。

## Domain Model 的最小定义

Domain Model 是软件对法律业务世界的正式、可审计表示，不是 LLM Model、Prompt、Knowledge Base、Memory、Skill、Tool、GraphRAG 或 LangGraph State。

V3 只保留以下最小 Canonical 候选：

| 层级 | 对象 | 规则 |
|---|---|---|
| 根与来源 | `Matter`、`DocumentVersion` | `Case` 是场景别名或 Profile，除非司法案件身份带来独立权限/生命周期，不能再造一个根对象 |
| 主张与证据 | `Claim`、`Evidence` | Claim 是待验证主张；Evidence 有来源、版本、引用位置和权限 |
| 结论与人工权威 | `Finding`、`HumanDecision`、`WorkProduct` | Finding 是受证据约束的工作结论；HumanDecision 是人工权威；WorkProduct 是发布物 |

`Party`、`Fact`、`Event`、`Conflict`、`Dispute`、`LegalIssue`、`StatuteVersion`、`LegalElement`、`ApplicableLaw`、`SimilarCase` 不删除其业务含义，但在没有稳定身份、版本、Owner、审查和跨运行复用证据前，只作为 typed proposal、retrieval projection、derived view 或 Capability Provider 输出。

每一个进入 Canonical Store 的对象必须回答：Identity、Version、Provenance、State、Ownership、Mutation Authority、Staleness、Dependency、Review、Audit。Provider 或 Agent 只能产生 `Proposal`、`Candidate`、`Observation`、`Reference`、`Receipt`，不能直接写 `FactVersion`、`ConflictVersion` 或 `FindingVersion`。

## New Evidence 的最小传播协议

```text
EvidenceVersion committed
  -> find dependent Claim / derived object
  -> mark affected Fact/Finding STALE or REVIEW_REQUIRED
  -> enqueue bounded re-evaluation when policy says so
  -> create new proposal/run
  -> Canonical Owner + human gate commit a new version
```

这不是自动全量重算，也不是默认 Event Sourcing。PostgreSQL 可以保存当前业务事实、不可变版本、依赖引用和审计记录；Checkpoint 只保存控制流恢复位置。恢复时以两者对账结果决定继续、补偿、阻塞或重评估。

## KEEP / SIMPLIFY / EXTERNALIZE / DEFER / DELETE

| 动作 | 保留内容 |
|---|---|
| KEEP | 最小 Canonical Domain State；Proposal → Owner → Version → Review；Evidence provenance；Security/approval/idempotency/audit；Legal Capability Contract；A/B/C 与安全 Benchmark |
| SIMPLIFY | Domain Object 集合；Postgres 当前事实+版本；Memory 先 Working/Session；模块化单体 + 独立 worker；普通 MCP/API Tool Adapter |
| EXTERNALIZE | Agent Host、模型、向量/混合/图检索、OCR/解析、Sandbox、LangGraph/Pi/WorkBuddy Runtime、法律算法 Provider |
| DEFER | Native Domain-aware Runtime；Persistent Multi-Agent；Always-on GraphRAG；Long-term Memory；微服务；Event Sourcing；自研 Tool Runtime |
| DELETE | 针对 WorkBuddy 的安全负面断言、闭源天然不安全、开源天然安全、GraphRAG 必优于 Hybrid、Multi-Agent 必优于 Single Agent、当前已领先或 production ready 等无证据陈述 |

## 三个最小充分架构

| 方案 | 概念/组件 | 新代码与运维成本 | 质量假设 | 替换成本 |
|---|---|---|---|---|
| A：WorkBuddy Host | WorkBuddy + Legal Knowledge Scopes + Skills + MCP/API capabilities；必要时一个事实存储 | 最低；Host 合同和数据边界需要核验 | 通用 Host 已覆盖单次/低状态任务；法律 Backend 价值未验证 | 最低，Host 可换 |
| B：Legal Backend | A + 最小 Canonical Domain Store + Evidence/Review API + typed capability providers + 轻量 async worker | 中等；仍不拥有 Native Runtime | 跨文档、跨运行、人工复核和 stale 传播可能改善质量/返工 | 中等；Host 与 Runtime 解耦 |
| C：Conditional Native Runtime | B + 可替换 Runtime Provider；Domain State 作为 typed input/output；不是 LangGraph checkpoint | 最高；只有 Benchmark 证明收益才承担 | C > B 才支持 first-class runtime；C ≈ B 时删除 C | 最高，应延后到可逆 Spike |

推荐顺序：先 A 做 Kill Zuno；若 Domain State/证据/审查无法稳定由 A 承载，进入 B；只有 C 在相同模型、语料、工具、提示、时间和 Token 预算下重复优于 B，才允许保留 C。

## 公平 Benchmark A/B/C

| 变体 | 固定条件 | 唯一变量 |
|---|---|---|
| A | 同一 Base Model、原始语料、外部工具、法律 Prompt/Skills、Token/时间预算 | WorkBuddy Generic Legal Agent |
| B | 同 A | WorkBuddy 调用 Zuno Legal Capabilities：event.extract/align、conflict.detect、fact_article.match、evidence.retrieve、similar_case.search、legal_applicability |
| C | 同 A/B；Capabilities 与输出格式相同 | Zuno Native Runtime + first-class Domain State、Evidence Requirement、Domain-aware Planning、Staleness、HITL |

必须按任务切片：cross-document analysis、multi-evidence reasoning、dispute identification、Fact–Article mapping、evidence sufficiency、legal applicability、similar case、long-running matter update。指标不能只用 LLM Judge：

- 质量：Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict/Dispute F1、Fact–Article F1、Applicability Accuracy、Reviewer Acceptance、Task Completion。
- 效率：Latency、Token、Cost、Model Calls、Retrieval Rounds、Tool Calls、Domain State Reuse Rate、重复提取率、重试/重规划率。

解释规则：`C > B > A` 才同时支持 Legal Intelligence 与 Native Runtime；`C ≈ B > A` 只支持 Legal Backend，Host 可作为主要宿主；`C ≈ B ≈ A` 删除对应自研复杂度。

## Graph / Multi-Agent / Memory Kill Tests

- Graph：Fixed Vector、Fixed Hybrid、Always Graph、Agentic RAG without Graph、Conditional Legal Graph；按 Exact Statute、Similar Case、Claim→Evidence、Fact→LegalElement→Statute、cross-document chain 等 query class 测试 Recall@K、nDCG、证据充分性、引用正确性、Unsupported Claim、Latency/Token/Cost。
- Multi-Agent：L0 Single Agent、L1 Role Pipeline、L2 Ephemeral Worker、L3 Specialized Domain Agent、L4 Persistent Team；先比较 L0-L2，禁止把多个 Agent 等同多套法律代码。
- Memory：Single-run Context、Matter DB + Checkpoint、Working/Session Memory、Long-term Memory；只有跨任务复用收益超过污染、权限和维护成本才升级。

## 安全可验证性假设

不对 WorkBuddy 做安全负面断言。Zuno 只有一个待验证差异假设：更容易提供 Source-level Audit、Build Reproducibility、SBOM、Signed Artifact、Network Egress Audit、Secret/Model/Tool/Domain/Human Decision Trace、Sandbox Boundary Test。必须执行 no-egress、allowlist、secret leakage、cross-tenant、prompt injection + tool、sandbox escape、revoked permission、stale credential、duplicate side effect 等测试；在产生 attestation 前不能写成安全优势。

## 进入正式 Target 的结论

本轮允许进入正式 Target 的是“最小 Legal Domain Kernel + Host-agnostic Legal Backend + 可替换 Provider + Benchmark Gate”。Native Domain-aware Runtime 只进入 `DEFERRED / HYPOTHESIS`，不进入默认 Current 或不可替换架构。该边界由 ADR 0008 记录，若后续 C>B 未成立，ADR 的 reversal criteria 要求删除 C。

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-KERNEL-V3/gaps.md`

# RB-KERNEL-V3 Gap Clusters

本轮结论不是“复杂架构正确”，而是把可删复杂度和仍值得验证的最小契约分开。所有 Gap 仍需代码、Migration、Trace、Eval、Spike 或用户证据关闭。

## CLUSTER-001

Gap IDs: GAP-V3-001, GAP-V3-002
Questions: Q001, Q002, Q003, Q024
Failed Claim: Zuno 必须拥有独立完整 Host 和 Native Runtime。
Root Cause: WorkBuddy + MCP/API Legal Backend 的能力边界和 C>B 的证据尚未测试。
Gap Types: BUILD_BUY_GAP, OVERENGINEERING_GAP, MEASUREMENT_GAP
Current Evidence: WorkBuddy 官方资料公开横向 Agent 能力；Zuno 当前没有法律 Domain Runtime 运行证据。
Required Research: 同模型/语料/工具/预算的 A/B/C；Host API contract fit；替换成本。
Suggested Blue Route: 先采用 Host + Backend；Native Runtime 只作为可逆 Provider。
Status: RESEARCH_REQUIRED

## CLUSTER-002

Gap IDs: GAP-V3-003, GAP-V3-005, GAP-V3-006
Questions: Q005, Q006, Q007, Q008, Q009
Failed Claim: 全部法律对象、Event Sourcing 和复杂 Domain State 都是必要的。
Root Cause: 业务对象的跨运行身份、版本、依赖失效和人工审查需求没有最小案例证据。
Gap Types: OVERENGINEERING_GAP, ARCHITECTURE_GAP, SECURITY_GAP
Current Evidence: 现有代码有通用 DocumentVersion/Claim/Evidence 结构；法律对象闭环未实现。
Required Research: 两个跨文档、带新证据和人工修订的真实案例；Postgres 版本化 spike。
Suggested Blue Route: 最小 Kernel + typed proposal + dependency invalidation；不默认 Event Sourcing。
Status: RESEARCH_REQUIRED

## CLUSTER-003

Gap IDs: GAP-V3-007
Questions: Q010, Q011
Failed Claim: Zuno 当前已有可宣称的 Legal Domain Kernel 和 first-class Domain Runtime。
Root Cause: Target 文档超前于代码、Migration、E2E Trace 和 Eval。
Gap Types: CURRENT_EVIDENCE_GAP
Current Evidence: BASE_SHA 未发现完整法律 Domain 类/表/运行闭环；Production Readiness 为 NOT_ESTABLISHED。
Required Research: 明确 implementation Program 后，才可建立 legal state code/trace/eval。
Suggested Blue Route: 正式文档标 Target/Hypothesis；不变更 Current status。
Status: USER_GATE

## CLUSTER-004

Gap IDs: GAP-V3-008, GAP-V3-009
Questions: Q012, Q013
Failed Claim: GraphRAG 默认优于 Hybrid RAG。
Root Cause: 没有按 query class 的 Kill Graph Test 和成本/错误传播数据。
Gap Types: BUILD_BUY_GAP, MEASUREMENT_GAP
Current Evidence: ADR 0006 已把 Graph 定义为 conditional，但没有本轮运行结果。
Required Research: Vector/Hybrid/Always Graph/Agentic no Graph/Conditional Graph 五路对照。
Suggested Blue Route: Graph 仅作为 Conditional Provider。
Status: RESEARCH_REQUIRED

## CLUSTER-005

Gap IDs: GAP-V3-010, GAP-V3-011, GAP-V3-012, GAP-V3-013
Questions: Q014, Q015, Q016, Q017, Q018
Failed Claim: Persistent Multi-Agent、独立 Memory、自研 Tool Runtime、十一微服务是默认必要条件。
Root Cause: 没有 L0-L3、Matter DB+Checkpoint、MCP/API Adapter、Modular Monolith+Workers 的对照证据。
Gap Types: OVERENGINEERING_GAP, BUILD_BUY_GAP
Current Evidence: 文档已描述部分边界；规模与真实 workload 仍 UNKNOWN，容量假设不是 Current。
Required Research: 逐项 kill test；保留可替换接口而不是预先部署复杂组件。
Suggested Blue Route: L0-L2 优先、Memory optional、MCP/API adapter、模块化单体+worker。
Status: RESEARCH_REQUIRED

## CLUSTER-006

Gap IDs: GAP-V3-004, GAP-V3-014
Questions: Q004, Q019, Q020
Failed Claim: Zuno 通过开源天然更安全，或 WorkBuddy 因闭源天然不安全。
Root Cause: 没有任何一方的同口径安全 Benchmark 和 attestation。
Gap Types: SECURITY_GAP, UNSUPPORTED_CLAIM
Current Evidence: WorkBuddy 公开企业能力存在；Zuno Security Verifiability 仍是 Target。
Required Research: no-egress、allowlist、secret、tenant、sandbox、injection、revocation、idempotency、SBOM、签名产物。
Suggested Blue Route: 以可验证性/部署主权为 Hypothesis，不做品牌攻击。
Status: RESEARCH_REQUIRED

## CLUSTER-007

Gap IDs: GAP-V3-015, GAP-V3-016
Questions: Q021, Q022
Failed Claim: 论文算法可直接写进 Agent，公开仓库即可商业复用。
Root Cause: Capability Contract、provider conformance 和 code/data/model license 还未完成。
Gap Types: ARCHITECTURE_GAP, LICENSE_GAP
Current Evidence: 公开论文和 InternLM-Law/LawBench 资料已记录；多数研究代码/数据授权 UNKNOWN。
Required Research: commit lock、输入输出 schema、复现、许可证与商用法律审查。
Suggested Blue Route: provider only returns proposals; no unreviewed source copy。
Status: RESEARCH_REQUIRED

## CLUSTER-008

Gap IDs: GAP-V3-017
Questions: Q023, Q024
Failed Claim: Zuno 当前已证明在法律质量、效率或生产性上优于通用 Host。
Root Cause: 没有 A/B/C 执行结果，也没有法律任务的 baseline、reviewer acceptance 或成本数据。
Gap Types: MEASUREMENT_GAP, CURRENT_EVIDENCE_GAP
Current Evidence: production readiness 与 eval baseline 明确保持未证明。
Required Research: 固定模型/语料/工具/提示预算/时间预算后执行 benchmark，并报告失败与成本。
Suggested Blue Route: 只把 benchmark protocol 进入 Target，不写 superiority。
Status: USER_GATE

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-KERNEL-V3/blue-change-set.md`

# RB-KERNEL-V3 Blue Change Set

本文件记录红队后允许进入正式架构的最小变更。创建时尚未同步 Canonical 文档；Commit SHA 在验证后回填。

## CHANGE-001

Source Cluster IDs: CLUSTER-001, CLUSTER-002, CLUSTER-003
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/decisions/0008-legal-domain-kernel-and-host-boundary.md; docs/project/architecture/architecture.md
Applied Commit SHA: a8c167a
Validation Run: architecture/document/module verifier suite passed; no Runtime implementation performed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: 保留最小 Legal Domain Kernel 作为可审计业务状态契约；不把完整法律对象列表或 Native Runtime 当作 Current。默认 Host + Legal Backend，Native Runtime 只保留可逆 benchmark 变体。

## CHANGE-002

Source Cluster IDs: CLUSTER-004, CLUSTER-005, CLUSTER-006, CLUSTER-007, CLUSTER-008
User Gate: APPROVED
Sync Status: APPLIED
Canonical Paths: docs/project/modules/01-product-surface.md; docs/project/modules/03-knowledge-agentic-graphrag.md; docs/project/modules/05-memory-context.md; docs/project/modules/06-agent-core-planning-control.md; docs/project/modules/07-capability-skill.md; docs/project/modules/08-tool-runtime.md; docs/project/modules/09-security.md; docs/project/modules/10-observability-eval.md; docs/project/modules/11-infrastructure.md
Applied Commit SHA: d264dbd
Validation Run: architecture/document/module verifier suite passed; no Runtime implementation performed
Validation Not Run: full CI and production service/eval evidence
Retest IDs: RETEST-001

Decision: Graph、Persistent Multi-Agent、Long-term Memory、自研 Tool Runtime、微服务拆分、安全优越性和法律质量优越性均不得作为无证据默认；改为 conditional/optional/deferred，并冻结 A/B/C 及安全评测协议。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-KERNEL-V3/retest.md`

# RB-KERNEL-V3 Retest

## RETEST-001

上一轮 Gap: GAP-V3-001, GAP-V3-002, GAP-V3-003, GAP-V3-017
Change IDs: CHANGE-001, CHANGE-002
Mutation Variable: 把“独立 Native Runtime 必须存在”改为“Host + Legal Backend 默认；Native Runtime 只在 C>B Benchmark 后启用”，并把 Legal Domain Kernel 缩减为最小可审计状态契约。
Result: PASS
Observation: Canonical 文档、ADR、入口和 verifier 已同步；红队 Claim 只在 Target/Hypothesis 边界内幸存，质量、效率、安全和 Production Readiness 仍保持开放证据缺口。
Evidence: RB-KERNEL-V3 transcript Q001-Q024; baseline SHA 0c07cfd69e4fcf76d5be53c0f7dce38171abfc8f

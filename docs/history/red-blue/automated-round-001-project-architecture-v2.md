<!-- Archive metadata: normalized without rewriting the historical record. -->
series: ARCHITECTURE_INTERVIEW
round_id: 001
execution_mode: AUTOMATED
status: ARCHIVED
base_sha: 1155d696fa0dcc08a7682f3c873c345cfccf016a
archive_commit: RECORDED_IN_FINAL_HANDOFF
architecture_revision_commit: NOT_CHANGED_IN_THIS_TASK
round_format: LEGACY_SESSION_COMPRESSION
source_session: RB-WORKFLOW-V2-001
# ARCHITECTURE_INTERVIEW — 001

本文件是正式 Red / Blue 对抗记录的单文件归档。它保留当时的核心问题、回答、Review/Score、决策和收口结果；不拥有今天的 Current Facts、Target Architecture 或实现授权。

## Session Manifest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/manifest.yaml`

session_id: "RB-WORKFLOW-V2-001"
workflow: "03-red-blue-optimization"
mode: "FULL_REVIEW"
scope: "PROJECT_ARCHITECTURE_100Q_V2"
project_package_version: "ZUNO-MAIN@1155d696fa0dcc08a7682f3c873c345cfccf016a"
target_role: "principal architect / distributed systems / legal AI / staff interviewer"
question_budget: 100
actual_question_count: 100
stop_reason: "QUESTION_BUDGET_REACHED_AFTER_SCORED_BLUE_REVIEW"
zuno_base_sha: "1155d696fa0dcc08a7682f3c873c345cfccf016a"
defense_base_sha: "1155d696fa0dcc08a7682f3c873c345cfccf016a"
post_sync_sha: null
resume_version: "PROJECT-FACTS-V1@4b960408f0693a42edd9a1a89accb98ac49d1edc"
project_fact_version: "docs/project/facts@4b960408f0693a42edd9a1a89accb98ac49d1edc"
internship_work_sha: "UNKNOWN"
interview_notes_sha: "UNKNOWN"
campaign_id: "ZUNO-RED-BLUE-WORKFLOW-V2"
round_id: "ROUND-001"
parent_session_id: "RB-ARCH-001"
baseline_session_id: "RB-ARCH-001"
campaign_scope: "PROJECT_ARCHITECTURE_100Q_V2"
campaign_phase: "FULL_REVIEW"
red_kernel_version: "v2.0"
judge_policy_version: "v2.0"
protocol_version: "ZUNO-RED-BLUE-WORKFLOW-V2"
category_distribution:
  A: 10
  B: 10
  C: 15
  D: 15
  E: 10
  F: 10
  G: 10
  H: 8
  I: 7
  J: 5
novelty_status: "NOT_ASSESSED"
source_scope:
  - "Zuno main @ 1155d696fa0dcc08a7682f3c873c345cfccf016a"
  - "docs/project/facts/**"
  - "docs/project/architecture/**"
  - "docs/project/{product,domain,agents,knowledge,services,data,security,eval,deployment}/**"
  - "docs/decisions/0006-0011*.md"
  - "project-reconstruction-lab/**"
  - "AGENTS.md, .agent/system.yaml, .agent/programs/current.md"
started_at: "2026-08-12T00:00:00+08:00"
completed_at: "2026-08-12T00:00:00+08:00"
status: "COMPLETED"
user_gate_resolution: "PENDING"
resolution_status: "ROUND_REVIEW_PENDING"
canonical_sync_status: "NOT_APPLIED"
counter_attack_status: "WAITING_FOR_USER_GATE"

## Questions / Transcript: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/transcript.md`

# RB-WORKFLOW-V2-001 Transcript

本记录是当前 `main` 基线上的 V2 百问 Round。它只保存可见问题、Blue 回答、Red 批评、修订和评分，不保存隐藏思维链。Historical/Current/Target 必须分开；`UNKNOWN` 是合法答案。

## Q001

Round ID: ROUND-001
Category: A
Question: 法院侧原始任务到底是什么？请从收到的材料、人工处理步骤、最慢或最易错步骤、系统输出和人工复核点还原一条链；如果当前没有直接证据，为什么仍然能冻结 Legal Domain？
Attack Intent: 防止从技术组件倒推业务需求。
Target Component: Product / Legal Domain
Assumption Being Attacked: 历史法院工作流已经被确认。
Severity: P0
Expected Answer Depth: Historical fact、UNKNOWN、Target 分层。
Evidence Required: 用户回忆、旧 QA、Demo、任务记录或客户材料。
Kill Condition: Blue 用“法律材料复杂”代替真实工作流，且没有 Fact Gap。
Blue Answer: 当前只能确认智慧法院相关项目存在 Demo、法院侧测试和 Pilot；原始 As-Is Workflow 仍 UNKNOWN。Target 先冻结“材料→DocumentVersion→Evidence Candidate→人工审核”的可追溯边界，不把它写成历史已实现。
State Boundary: Historical=UNKNOWN；Current=事实文档和仓库部分证据；Target=可审计法律工作流候选。
Problem: 缺少业务起点；Decision: FACT_RECOVERY_QUEUE；Why: 领域对象必须由真实任务约束。
Ownership: Facts Owner 记录证据，Domain Owner 只维护 Target Contract；State Transition: UNKNOWN→USER_CONFIRMED/ARTIFACT 或保持 UNKNOWN。
Failure: 错误业务假设会造成错误 Domain；Retry: 重新访谈/查 Artifact；Recovery: 回退候选对象；Idempotency: Evidence ID 去重。
Security: 不把客户材料复制进公开仓库；Observability: 记录 Evidence ID 和 Scope。
Alternative: 先做通用问答；Tradeoff: 可快速 Demo 但无法证明领域差异。
Test / Benchmark: Fact Readiness Gate；Evidence: docs/project/facts/requirements-and-workflows.md。
Remaining Gap: GAP-V2-001
Red Critique: 回答守住了事实边界，但没有业务任务证据。
Blue Revision: 将真实法院链路列为下一轮 Fact Recovery 的前置输入。
Final Red Assessment: 未关闭 P0，架构只能作为候选。
Score: 2/5
Architecture Fitness: 3/5
Scorecard Ref: Q001
Gap Candidate Refs: GAP-V2-001

## Q002

Round ID: ROUND-001
Category: A
Question: “回答质量需要提高”具体对应事实错误、漏召回、引用不准、答案不完整、响应慢还是人工不接受？如果不能区分，为什么可以选择 GraphRAG、Memory 或 Multi-Agent？
Attack Intent: 攻击未定义的质量目标。
Target Component: Product / Eval
Assumption Being Attacked: 客户反馈已经足够指导技术选型。
Severity: P0
Expected Answer Depth: Feedback classification、指标和未知项。
Evidence Required: QA、反馈记录、错误样本或评测协议。
Kill Condition: Blue 把“质量”直接等同于更多检索或更多 Agent。
Blue Answer: 当前确认的是客户要求继续提高回答质量，根因 UNKNOWN。Target 必须先按 Parser、Retrieval、Evidence、Reasoning、Citation、Completeness、Latency 和 Reviewer Acceptance 分类，再做消融；没有分类前 Graph/Memory/Multi-Agent 都只能 DEFER。
State Boundary: Historical=反馈已确认、根因 UNKNOWN；Current=Quality not_yet_proven；Target=分层 Legal Eval。
Problem: 反馈不可诊断；Decision=DEFER_COMPLEXITY；Why=先定位错误再引入组件。
Ownership: Eval Owner 维护指标，Facts Owner 维护历史反馈；State Transition: Feedback→Error Class→Benchmark Case。
Failure: 错误归因；Retry: 重放固定 QA；Recovery: 回到最小 Hybrid/Single Agent baseline；Idempotency: Dataset Version。
Security: 反馈样本按权限脱敏；Observability: 保存错误类型和原始引用。
Alternative: 只看 LLM Judge；Tradeoff: 便宜但无法定位证据错误。
Test / Benchmark: L1–L5 Eval、A/B/C；Evidence: docs/project/facts/data-and-evaluation-history.md。
Remaining Gap: GAP-V2-002
Red Critique: 有正确的停手原则，但缺真实错误分布。
Blue Revision: 将错误分类协议列为先于 Graph/Memory 的 Eval Task。
Final Red Assessment: P0 保持开放。
Score: 2/5
Architecture Fitness: 3/5
Scorecard Ref: Q002
Gap Candidate Refs: GAP-V2-002

## Q003

Round ID: ROUND-001
Category: A
Question: 产品的最小成功结果是什么：节省人工阅读时间、提高 Evidence Sufficiency、减少 Unsupported Claim、提高 Reviewer Acceptance，还是完成某种法院表单？谁有权接受？
Attack Intent: 防止把技术完成当产品价值。
Target Component: Product / Human Review
Assumption Being Attacked: Agent Answer 本身就是交付物。
Severity: P1
Expected Answer Depth: WorkProduct、验收者、指标。
Evidence Required: 业务验收记录或用户确认。
Kill Condition: 只有“模型回答得更好”而没有任务级结果。
Blue Answer: 当前没有正式验收指标，Production Readiness 仍 NOT_ESTABLISHED。Target 将 WorkProduct、Evidence/Citation、Reviewer Decision 和 Task Completion 分开，验收必须由业务/Reviewer Contract 定义；不能把模型输出直接当成功。
State Boundary: Historical=UNKNOWN；Current=Eval framework exists as design；Target=Reviewer-gated WorkProduct。
Problem: 价值未定义；Decision=KEEP_REVIEW_GATE；Why=高风险法律输出需要人类权威。
Ownership: Product/Domain Owner 定义 WorkProduct，Reviewer 负责决定；State Transition: Draft→Review→Accepted/Rejected。
Failure: 输出不完整或证据不足；Retry: 追加 Evidence/重新分析；Recovery: 保留未通过状态；Idempotency: WorkProduct Version。
Security: Reviewer 权限和 Matter scope；Observability: 记录 decision、evidence 和版本。
Alternative: 直接 Chat Answer；Tradeoff: 更快但不可审计。
Test / Benchmark: Reviewer Acceptance、Unsupported Claim Rate；Evidence: docs/project/eval/legal-eval-and-benchmark.md。
Remaining Gap: GAP-V2-002
Red Critique: Target 闭环清楚，历史验收者仍未知。
Blue Revision: 不把 Target 指标升级为历史结果。
Final Red Assessment: 设计方向可保留，历史 P1 未关闭。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q003
Gap Candidate Refs: GAP-V2-002

## Q004

Round ID: ROUND-001
Category: A
Question: 为什么 Domain 根对象优先是 Matter，而不是 Case？如果同一案件需要多个工作空间、权限边界、版本和交付物，哪个身份是 Canonical？
Attack Intent: 攻击对象命名和身份漂移。
Target Component: Legal Domain Kernel
Assumption Being Attacked: Case/Matter 可以随意互换。
Severity: P1
Expected Answer Depth: Identity、Scope、Ownership。
Evidence Required: 真实业务身份和权限需求。
Kill Condition: 两者都做 Canonical，但没有独立 Identity/Lifecycle 证据。
Blue Answer: Target 默认 Matter 是法律工作和权限边界，Case 是 Profile/别名；只有跨运行独立身份、生命周期、权限或审计需求被证明确实存在，Case 才升级为 Canonical。
State Boundary: Historical=对象命名 UNKNOWN；Current=通用模型表面；Target=Matter-first minimal kernel。
Problem: 对象膨胀；Decision=SIMPLIFY；Why=减少无证据状态机。
Ownership: Platform/Domain Service；State Transition: Matter Created→Active→Closed/Archived。
Failure: Case/Matter 双写冲突；Retry: 通过 Domain Owner 重建映射；Recovery: 以 Matter ID 和版本恢复；Idempotency: 外部 Case Ref 唯一约束。
Security: Matter 是权限隔离边界；Observability: identity mapping trace。
Alternative: Case 与 Matter 双根；Tradeoff: 语义更丰富但增加一致性成本。
Test / Benchmark: Identity/permission/version tests；Evidence: docs/project/domain/legal-domain-model.md。
Remaining Gap: GAP-V2-003
Red Critique: 最小化原则成立，但需要真实权限场景。
Blue Revision: 把 Case 升级条件写成 reversal criterion。
Final Red Assessment: Target 可保留，历史未知。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q004
Gap Candidate Refs: GAP-V2-003

## Q005

Round ID: ROUND-001
Category: A
Question: Claim、Evidence、Finding、HumanDecision、WorkProduct 中哪些必须是 Canonical，哪些可以是 Proposal 或 Projection？如果模型直接写 Finding 会发生什么？
Attack Intent: 攻击 Domain Model 对象膨胀和写权限。
Target Component: Domain State
Assumption Being Attacked: 所有抽取结果都是真实事实。
Severity: P0
Expected Answer Depth: Canonical Owner、mutation authority、review。
Evidence Required: Contract、mutation test、review trace。
Kill Condition: Provider 或 Agent 可以绕过 Owner 写正式 Finding。
Blue Answer: Target 最小 Canonical 候选为 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct；Agent/Provider 只能返回 Proposal/Candidate/Observation/Reference/Receipt，Domain Owner 验证 provenance、权限、版本和 review 后提交正式版本。
State Boundary: Historical=未证明完整 Kernel；Current=通用代码表面；Target=Proposal→Validation→Version→Review。
Problem: 非权威结果污染业务状态；Decision=KEEP_OWNER_GATE；Why=法律结论需审计和人工权威。
Ownership: Platform/Domain Owner；State Transition: Candidate→Accepted/Rejected→Versioned。
Failure: 错误 Proposal；Retry: 重新生成候选但不重复提交；Recovery: 依据版本回滚；Idempotency: Proposal ID/Source Version。
Security: Owner permission、Matter scope；Observability: provenance、review 和 mutation trace。
Alternative: JSON + PostgreSQL 无 Contract；Tradeoff: 更少代码但边界不可审计。
Test / Benchmark: mutation/review/staleness E2E；Evidence: ADR-0008、domain model。
Remaining Gap: GAP-V2-003
Red Critique: 规范闭环清楚，但 Current 证据不存在。
Blue Revision: 将完整 Kernel 保持 UNDER_ATTACK。
Final Red Assessment: Target 设计成立，Current P0 未关闭。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q005
Gap Candidate Refs: GAP-V2-003, GAP-V2-022

## Q006

Round ID: ROUND-001
Category: A
Question: Evidence、Chunk、Citation 和 DocumentVersion 的关系是什么？为什么检索返回的 Chunk 不能直接成为 Evidence？
Attack Intent: 攻击 Retrieval Projection 与业务证据混淆。
Target Component: Knowledge / Domain
Assumption Being Attacked: Top-K 文本就是可采信证据。
Severity: P1
Expected Answer Depth: provenance、source span、permission、acceptance。
Evidence Required: Evidence Contract 和 citation trace。
Kill Condition: 任何向量命中都可直接支持 Finding。
Blue Answer: Chunk 是索引投影，Citation 是引用定位，DocumentVersion 是来源版本，Evidence 是经过权限、来源、版本和业务接受的证据；Knowledge 只给 EvidenceCandidate，Domain Owner 才提交 EvidenceVersion。
State Boundary: Historical=UNKNOWN；Current=检索代码表面；Target=Chunk→Candidate→Accepted Evidence。
Problem: 检索命中被过度信任；Decision=KEEP_EVIDENCE_GATE；Why=证据充分性不能由相似度单独决定。
Ownership: Knowledge owns projection；Domain owns accepted Evidence；State Transition: Indexed→Candidate→Accepted/Rejected。
Failure: stale index/错片段；Retry: 重新定位 source span；Recovery: 从 DocumentVersion 重建 projection；Idempotency: source version + span key。
Security: 召回前权限过滤；Observability: retrieval round、source span、citation lineage。
Alternative: 直接把 Chunk 写入 prompt；Tradeoff: 简单但无法审计。
Test / Benchmark: Gold Evidence Recall、Citation Correctness；Evidence: ADR-0006、knowledge docs。
Remaining Gap: GAP-V2-009
Red Critique: 边界明确，指标尚未运行。
Blue Revision: 将 Evidence Sufficiency 作为 Gate 而非相似度阈值。
Final Red Assessment: Target survived；Evidence measurement open。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q006
Gap Candidate Refs: GAP-V2-009, GAP-V2-022

## Q007

Round ID: ROUND-001
Category: A
Question: 新 Evidence 到来时，哪些事实或 Finding 被标记 stale？如何避免全量重算和静默沿用旧结论？
Attack Intent: 攻击版本与依赖传播。
Target Component: Domain State Lifecycle
Assumption Being Attacked: 写入新材料即可自动解决新鲜度。
Severity: P0
Expected Answer Depth: dependency graph、state transition、bounded reevaluation。
Evidence Required: stale propagation test/trace。
Kill Condition: 没有 dependency、stale、review 或 re-run 语义。
Blue Answer: Target 保存 accepted object 的依赖版本；新 EvidenceVersion 只标记受影响 Claim/Finding 为 STALE 或 REVIEW_REQUIRED，按策略 bounded re-evaluate，必要时创建新 Run/Proposal，不能假装旧 Finding 仍然有效。
State Boundary: Historical=未确认；Current=stale contract 文档；Target=versioned dependency lifecycle。
Problem: 旧结论失效传播；Decision=KEEP_DEPENDENCY_STATE；Why=跨运行可靠性来自版本而非 Prompt。
Ownership: Domain Owner 维护状态，Runtime 触发分析；State Transition: VALID→STALE→REVIEWED/REPLACED。
Failure: propagation job 中断；Retry: idempotent dependency scan；Recovery: 从 canonical dependency table 重建 affected set；Idempotency: EvidenceVersion + dependent ID。
Security: 只处理有权限的 Matter；Observability: stale reason、generation、run linkage。
Alternative: 每次重新读取全部材料；Tradeoff: 简单但昂贵且不透明。
Test / Benchmark: stale/re-evaluation fault tests；Evidence: domain-state-lifecycle.md。
Remaining Gap: GAP-V2-003, GAP-V2-007
Red Critique: Target 有因果链，Current 没有运行证明。
Blue Revision: 把“新证据触发重分析”从自动保证改为 policy-triggered Target。
Final Red Assessment: P0 Current gap remains。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q007
Gap Candidate Refs: GAP-V2-003, GAP-V2-007

## Q008

Round ID: ROUND-001
Category: A
Question: 如果 WorkBuddy 或其他 Host 已能返回结构化 JSON，Zuno 还需要保存 Domain State 吗？跨 Run、人工修改、stale 传播和审计分别需要什么持久化？
Attack Intent: 直接攻击 Zuno 独立存在必要性。
Target Component: Host Boundary / Domain Backend
Assumption Being Attacked: Tool JSON 不能承载任何领域状态。
Severity: P0
Expected Answer Depth: Kill Runtime/Domain Test、最小后端边界。
Evidence Required: A/B/C benchmark 和业务跨运行案例。
Kill Condition: B 能用普通 Tool JSON 完整满足任务且无复用/审计损失。
Blue Answer: 对一次性低状态任务，WorkBuddy + Tool JSON 可能足够；只有跨 Run 的版本、review、stale dependency、权限和 WorkProduct 需要稳定 Owner 时，才保留最小 Legal Backend。Native Runtime 不因此自动保留。
State Boundary: Historical=产品真实复杂度仍部分 UNKNOWN；Current=Target only；Target=Host-agnostic minimal backend hypothesis。
Problem: 独立产品必要性未证；Decision=UNDER_ATTACK；Why=把差异压缩到 Domain Contract。
Ownership: Domain Backend owns accepted state；Host owns interaction；State Transition: Tool Proposal→Backend validation。
Failure: Host 重试或 Backend 不可用；Retry: idempotent proposal submission；Recovery: Backend version/receipt reconcile；Idempotency: proposal key。
Security: Backend 决定 Matter permission，Host 不能扩大 scope；Observability: Host/Backend correlation trace。
Alternative: WorkBuddy-only；Tradeoff: 低成本但跨运行审计可能不足。
Test / Benchmark: Kill Zuno、Kill Runtime、A/B/C；Evidence: ADR-0008。
Remaining Gap: GAP-V2-004
Red Critique: 这是诚实的缩减，但尚未有任务级数据证明 Backend 必要。
Blue Revision: Native Runtime 继续 DEFER，Backend 仅保留为可证伪假设。
Final Red Assessment: P0 未关闭，禁止宣传独立 Host 优势。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q008
Gap Candidate Refs: GAP-V2-004

## Q009

Round ID: ROUND-001
Category: A
Question: 如果法院只需要文档问答而不是跨月案件维护，Matter、Finding、Memory 和复杂 Review 是否都应进入 V1？
Attack Intent: 攻击把长期 Target 全量前置。
Target Component: Product Scope
Assumption Being Attacked: 所有领域对象都由产品类型决定。
Severity: P1
Expected Answer Depth: Scope-down、最小充分架构。
Evidence Required: 真实工作流和 Pilot scope。
Kill Condition: Blue 无法删除不必要状态。
Blue Answer: 不应全量前置。一次性问答可先保留 DocumentVersion、EvidenceCandidate/Citation、Answer Review 和最小 Task；Matter/Finding/Memory/stale 只有跨运行任务需要时才进入 V1 Target。
State Boundary: Historical=V1真实范围 UNKNOWN；Current=设计文档；Target=profiled scope。
Problem: Domain 对象过早冻结；Decision=SCOPE_DOWN；Why=按任务复杂度引入状态。
Ownership: Product/Domain Owner；State Transition: profile selects contract subset。
Failure: 后续扩展缺少迁移；Retry: additive versioned contract；Recovery: 从 source/evidence rebuild；Idempotency: task profile ID。
Security: scope-specific permissions；Observability: profile and feature usage。
Alternative: 全量 Domain Kernel；Tradeoff: 未来扩展快但首期复杂。
Test / Benchmark: minimal workflow vs full domain cost/quality；Evidence: requirements facts UNKNOWN。
Remaining Gap: GAP-V2-001, GAP-V2-005
Red Critique: 具有必要的 scope discipline，仍依赖历史任务恢复。
Blue Revision: 将 V1 object set 设为候选，不作为历史事实。
Final Red Assessment: Target fitness acceptable。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q009
Gap Candidate Refs: GAP-V2-001, GAP-V2-005

## Q010

Round ID: ROUND-001
Category: A
Question: 如果 A/B/C 结果是 C≈B>A，Zuno Native Runtime 应该保留吗？如果 C≈B≈A，哪个复杂度必须删除？
Attack Intent: 检查架构能否接受失败结果。
Target Component: Product Thesis / Runtime
Assumption Being Attacked: 自研 Runtime 必须成功。
Severity: P0
Expected Answer Depth: Reversal criteria、删除路径。
Evidence Required: 预注册 benchmark。
Kill Condition: Blue 无法承诺删除 Native Runtime。
Blue Answer: C≈B>A 时保留 Legal Backend、削薄或删除 Native Runtime；C≈B≈A 时删除没有增益的 Domain/Runtime 复杂度；只有 C 在相同模型、语料、工具和预算下有可归因增益才保留。
State Boundary: Historical=无质量结论；Current=Benchmark design only；Target=可逆架构假设。
Problem: 设计锁定风险；Decision=KEEP_REVERSAL_CRITERIA；Why=复杂度引入者举证。
Ownership: Eval Owner 计算结果，Architecture Owner 执行 ADR reversal；State Transition: Hypothesis→Measured→Keep/Delete。
Failure: benchmark 偏差；Retry: preregistered repeat on held-out slice；Recovery: revert provider/contract。
Idempotency: same benchmark seed, corpus, model, tool and budget。
Security: 同一安全条件；Observability: model/token/tool budget and trace。
Alternative: 只比较最终 Judge；Tradeoff: 简单但无法归因。
Test / Benchmark: A/B/C protocol；Evidence: ADR-0008、eval docs。
Remaining Gap: GAP-V2-004, GAP-V2-020
Red Critique: 删除承诺成立，当前无数据。
Blue Revision: 把 Native Runtime 状态保持 DEFERRED/HYPOTHESIS。
Final Red Assessment: 通过原则攻击，未通过价值证明。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q010
Gap Candidate Refs: GAP-V2-004, GAP-V2-020

## Q011

Round ID: ROUND-001
Category: B
Question: Legal Domain Kernel 为什么不是“几个 JSON Schema 加 PostgreSQL 表”？如果普通 JSON + PostgreSQL 能通过版本、来源、审查、stale 和 audit 测试，Kernel 是否应被删除？
Attack Intent: Kill Domain Kernel。
Target Component: Legal Domain Kernel
Assumption Being Attacked: “Kernel”名称本身创造价值。
Severity: P0
Expected Answer Depth: Canonical Contract、删除条件、测试。
Evidence Required: domain mutation/review/staleness tests。
Kill Condition: 简化方案在同一任务和审计指标上等价。
Blue Answer: Kernel 不是新数据库，而是稳定的业务 Contract、Owner、mutation authority、dependency 和 review 语义；若普通 JSON + PostgreSQL 能同样验证这些边界，则删除“独立 Kernel”品牌，只保留最小 Contract/Owner。
State Boundary: Historical=UNKNOWN；Current=通用模型表面；Target=可缩减 Domain Contract。
Problem: 概念包装风险；Decision=UNDER_ATTACK；Why=行为而非命名决定存在资格。
Ownership: Domain Owner；State Transition: Proposal→Validation→Version。
Failure: schema drift/绕过写入；Retry: contract validation；Recovery: versioned records；Idempotency: mutation key。
Security: permission and review preconditions；Observability: mutation audit。
Alternative: plain JSON/PG；Tradeoff: 可能足够，需对照验证。
Test / Benchmark: Kill Domain Kernel；Evidence: ADR-0008。
Remaining Gap: GAP-V2-005, GAP-V2-022
Red Critique: 允许自己被删除是正确姿态，但测试尚未实现。
Blue Revision: 将 Kernel 的 surviving claim 缩小为 Contract + Owner，而非专属存储。
Final Red Assessment: 复杂度尚未获证。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q011
Gap Candidate Refs: GAP-V2-005, GAP-V2-022

## Q012

Round ID: ROUND-001
Category: B
Question: “Business Semantics Stable, Computation Pluggable, Agents Composable”如何防止业务语义被 Skill、Prompt 或 Provider 悄悄改变？
Attack Intent: 攻击原则的可执行性。
Target Component: Contracts / Governance
Assumption Being Attacked: 口号可以防止语义漂移。
Severity: P1
Expected Answer Depth: Contract ownership、provider boundary、tests。
Evidence Required: schema/contract conformance。
Kill Condition: Provider 可以直接写 Fact 或改变状态机。
Blue Answer: 业务语义由 Domain Owner、Schema、版本、权限、Review 和状态转移定义；Provider 只能返回 Proposal/Candidate/Observation/Receipt，Agent profile 只能绑定 Skill/Capability/Knowledge/Permission，不拥有 Canonical 状态机。
State Boundary: Historical=未证明；Current=Target docs；Target=contract enforcement。
Problem: provider 语义漂移；Decision=KEEP_CONTRACT_BOUNDARY；Why=替换实现而不替换业务真相。
Ownership: Domain Owner owns contract；State Transition: provider output→validated proposal。
Failure: incompatible provider；Retry: provider fallback or reject；Recovery: old version/provider；Idempotency: contract version + provider operation ID。
Security: provider cannot grant permission；Observability: provider/version/schema trace。
Alternative: Agent prompt convention；Tradeoff: 快但不可审计。
Test / Benchmark: provider conformance and schema tests；Evidence: ADR-0007/0008。
Remaining Gap: GAP-V2-022
Red Critique: 机制完整，Current enforcement evidence absent。
Blue Revision: 把 contract conformance 设为 Build/Provider Gate。
Final Red Assessment: Target survived conditionally。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q012
Gap Candidate Refs: GAP-V2-022

## Q013

Round ID: ROUND-001
Category: B
Question: 一个组件何时有资格成为独立 Service，而不是 Library 或 Worker？请给出不可被“用户数很多”替代的判据。
Attack Intent: 建立 Necessary Complexity Gate。
Target Component: Service Architecture
Assumption Being Attacked: 服务化等于成熟。
Severity: P0
Expected Answer Depth: boundary evidence。
Evidence Required: scaling/failure/security/lifecycle evidence。
Kill Condition: 只能回答“未来扩展”。
Blue Answer: 至少需要 Independent Scaling、Failure Isolation、Security/Resource Isolation、Independent Deployment、Distinct Availability、Distinct Data Ownership 或独立 Operational Lifecycle 之一，并说明为何 Worker/Library 不足。
State Boundary: Historical=实际服务数 UNKNOWN；Current=backend+worker evidence；Target=Microservice boundary candidates。
Problem: 服务数量膨胀；Decision=KEEP_GATE；Why=物理边界必须有运行理由。
Ownership: Service Owner；State Transition: candidate→evidence→service/defer。
Failure: network/partial failure；Retry: contract-aware；Recovery: reconcile/rollback；Idempotency: request/job identity。
Security: boundary-specific policy；Observability: distributed trace and SLO。
Alternative: modular monolith + workers；Tradeoff: lower ops cost。
Test / Benchmark: service boundary review；Evidence: ADR-0010。
Remaining Gap: GAP-V2-018
Red Critique: 判据清楚，但尚未逐服务有数据。
Blue Revision: 五服务保持 Candidate，不是批准清单。
Final Red Assessment: Gate survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q013
Gap Candidate Refs: GAP-V2-018

## Q014

Round ID: ROUND-001
Category: B
Question: 如果 Logical Capability、Process、Service、Container 和 Team 不是一一映射，Canonical 文档如何防止每个层次又定义一套 Domain State？
Attack Intent: 攻击文档和 ownership 重复。
Target Component: Documentation / Ownership
Assumption Being Attacked: 目录拆分自动带来清晰边界。
Severity: P0
Expected Answer Depth: taxonomy、owner registry、verifier。
Evidence Required: canonical ownership registry and verifier。
Kill Condition: 多份文档定义不同 Fact 状态机。
Blue Answer: Domain、Lifecycle、Runtime、Knowledge、Service、Data、Security、Eval 各自声明唯一 Canonical Question 和 Owner；跨边界只引用 Proposal/Observation/Snapshot/Receipt；Verifier 检查唯一 owner、架构目录四文件和旧模块 Superseded。
State Boundary: Historical=文档治理已部分验证；Current=verifier evidence；Target=single-owner taxonomy。
Problem: 文档事实分叉；Decision=KEEP_CANONICAL_OWNER；Why=读者和实现需一个权威源。
Ownership: docs/project Owner Registry；State Transition: document candidate→ADR→canonical。
Failure: stale duplicate doc；Retry: link/ownership audit；Recovery: supersede duplicate；Idempotency: canonical path。
Security: ownership changes review；Observability: verifier output。
Alternative: 仅靠 README；Tradeoff: 易漂移。
Test / Benchmark: architecture/document verifiers；Evidence: ADR-0011、current validators。
Remaining Gap: GAP-V2-022
Red Critique: 当前治理验证存在，但 V2 Round 记录不自动写 Canonical。
Blue Revision: 增加 Canonical Write Gate traceability。
Final Red Assessment: P0 mitigated at process level。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q014
Gap Candidate Refs: GAP-V2-022

## Q015

Round ID: ROUND-001
Category: B
Question: 为什么 Domain State 不是 Memory？如果 Memory 里长期保存了一个事实性结论，系统如何防止它被当成权威业务事实？
Attack Intent: 攻击 Memory/Domain 边界。
Target Component: Domain / Memory
Assumption Being Attacked: 上下文复用等于事实保存。
Severity: P0
Expected Answer Depth: authority、scope、staleness、write policy。
Evidence Required: memory write/quarantine tests。
Kill Condition: Memory Provider 可以提交 FactVersion/FindingVersion。
Blue Answer: Domain State 是业务世界的权威版本；Memory 是可过期、可压缩、可删除的上下文/经验。Memory 只能产生 MemoryCandidate，经 scope、authority、provenance、conflict 和 policy 检查；不能替代 Evidence/Finding。
State Boundary: Historical=用户确认参与 Memory/OpenViking，具体事实语义仍部分 UNKNOWN；Current=仓库未证明 OpenViking；Target=Memory governance boundary。
Problem: Memory 污染 Domain；Decision=KEEP_SEPARATION；Why=可复用不等于权威。
Ownership: Memory policy owner vs Domain owner；State Transition: candidate→accepted memory projection, never domain commit。
Failure: stale/poisoned memory；Retry: quarantine/re-evaluate；Recovery: delete projection/rebuild from source；Idempotency: memory candidate key。
Security: scope/tenant/data class；Observability: provenance and write decision。
Alternative: 把事实都塞 Matter DB；Tradeoff: 少一个 Provider 但缺通用上下文治理。
Test / Benchmark: memory pollution, permission, reuse ablation；Evidence: ADR-0008、facts/team-and-ownership.md。
Remaining Gap: GAP-V2-011, GAP-V2-012
Red Critique: 边界合理，历史 OpenViking 角色和 Current 仍需证据。
Blue Revision: OpenViking 只登记为历史参与和 Target Provider candidate。
Final Red Assessment: Target survives; historical gap remains。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q015
Gap Candidate Refs: GAP-V2-011, GAP-V2-012

## Q016

Round ID: ROUND-001
Category: B
Question: 为什么 Domain State 不属于 LangGraph checkpoint？如果 checkpoint 显示 Node 已完成但 Domain Transaction 未提交，恢复时以谁为准？
Attack Intent: 攻击框架状态与业务状态混淆。
Target Component: Runtime / Data
Assumption Being Attacked: 一个 State Store 更简单。
Severity: P0
Expected Answer Depth: reconciliation、generation、recovery。
Evidence Required: crash/reconcile trace。
Kill Condition: 以 checkpoint “Node complete”直接宣称业务完成。
Blue Answer: LangGraph checkpoint 只保存 graph control state；Domain Store 由 Canonical Owner 保存业务事实。恢复时以合法 DomainGeneration、事务提交和 EffectReceipt 对账；Node complete 但 Domain 未提交只能重试/补交，不能假装完成。
State Boundary: Historical=Current reconciliation 未证明；Current=graph/checkpoint code surface；Target=two-state reconciliation contract。
Problem: partial commit；Decision=KEEP_STATE_SEPARATION；Why=框架 checkpoint 不是业务事实。
Ownership: Runtime owns control; Domain owns business; State Transition: checkpoint→reconcile→commit/retry。
Failure: checkpoint/domain mismatch；Retry: idempotent commit/reconcile；Recovery: last valid generation；Idempotency: run/step/domain generation key。
Security: Domain commit rechecks permission；Observability: generation/correlation/receipt trace。
Alternative: checkpoint as source of truth；Tradeoff: simpler but corruptible。
Test / Benchmark: fault injection at both write points；Evidence: architecture.md、ADR-0008。
Remaining Gap: GAP-V2-007, GAP-V2-013
Red Critique: 机制答案完整，但没有 Current fault test。
Blue Revision: 把 reconcile trace 列为 P0 implementation evidence。
Final Red Assessment: Architecture principle survives, implementation not proven。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q016
Gap Candidate Refs: GAP-V2-007, GAP-V2-013

## Q017

Round ID: ROUND-001
Category: B
Question: Skill、Capability、Tool、Knowledge、Memory 和 Domain State 各自回答什么问题？为什么把 Case Fact 写成 long-term Memory 会造成错误？
Attack Intent: 攻击概念边界。
Target Component: Agent Contract
Assumption Being Attacked: 所有上下文都可统一叫 Memory/Tool。
Severity: P1
Expected Answer Depth: stable definitions、owner。
Evidence Required: canonical agent docs。
Kill Condition: 同一对象在不同文档中角色漂移。
Blue Answer: Skill=HOW；Capability=WHAT；Tool=HOW executed；Knowledge=可检索信息；Memory=可复用上下文/经验；Domain State=业务世界当前事实。Case Fact 需要版本、权威、依赖和审计，不能因被复用就降成 Memory。
State Boundary: Historical=概念使用部分未知；Current=Target docs；Target=contract vocabulary。
Problem: 语义混淆；Decision=KEEP_BOUNDARY；Why=权限、生命周期和审计不同。
Ownership: each owner document；State Transition: provider output typed by contract。
Failure: wrong scope/authority；Retry: schema validation；Recovery: migrate projection not fact；Idempotency: typed object/version。
Security: Domain permissions vs Memory scopes；Observability: type/provenance。
Alternative: unified context object；Tradeoff: fewer concepts but hidden semantics。
Test / Benchmark: contract lint and boundary review；Evidence: agent-platform.md。
Remaining Gap: GAP-V2-005, GAP-V2-011
Red Critique: 解释清楚，仍需实现级 schema verifier。
Blue Revision: 把边界纳入 Complexity Card 和 Contract Gate。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q017
Gap Candidate Refs: GAP-V2-005, GAP-V2-011

## Q018

Round ID: ROUND-001
Category: B
Question: 如果 WorkBuddy + Legal Backend 已能完成 Domain Conditions、Evidence Gate、staleness 和人工复核，Native Domain-aware Runtime 还剩什么不可替代的能力？
Attack Intent: Kill Native Runtime。
Target Component: Domain-aware Runtime
Assumption Being Attacked: first-class input/output 必须由 Zuno Runtime 提供。
Severity: P0
Expected Answer Depth: causal benchmark、delete condition。
Evidence Required: B/C controlled comparison。
Kill Condition: C 与 B 等价且普通 Backend 可承担全部语义。
Blue Answer: 若 B 已提供版本化 Domain Contract、EvidenceRequirement、stale dependency、Review Gate 和 reconcile，Native Runtime 不保留；只有 C 在同预算下因 first-class contract 产生可归因质量/效率收益，才进入 Target。
State Boundary: Historical=无比较实验；Current=Hypothesis；Target=Native Runtime deferred。
Problem: orchestration relocation 可能被误称产品差异；Decision=DEFER_NATIVE_RUNTIME；Why: 只有可归因质量或效率增益才足以承担 Native Runtime 成本。
Ownership: Eval establishes evidence; Runtime owner executes only after gate。
State Transition: A/B/C hypothesis→measured→keep/delete。
Failure: benchmark confounder；Retry: held-out repeated runs；Recovery: use Host+Backend。
Idempotency: same corpus/model/tool/budget；Security: equal controls。
Observability: model calls, retrieval, tool calls, reuse, latency, cost；Alternative: WorkBuddy Host + Backend。
Test / Benchmark: Kill Runtime / A-B-C；Evidence: ADR-0008；Tradeoff: Host+Backend 更易替换，但可能牺牲 first-class orchestration 的局部便利。
Remaining Gap: GAP-V2-004, GAP-V2-020
Red Critique: 明确承诺删除，但 C 尚未测量。
Blue Revision: Native Runtime 维持 DEFERRED，不写 Current。
Final Red Assessment: P0 remains open。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q018
Gap Candidate Refs: GAP-V2-004, GAP-V2-020

## Q019

Round ID: ROUND-001
Category: B
Question: 为什么 `ACCEPTED_TARGET` 不能直接等于 `SURVIVED`？一个 Target 设计需要经过哪些 Red、Blue、Counter 和 Evidence 阶段？
Attack Intent: 防止状态偷换。
Target Component: Architecture Governance
Assumption Being Attacked: ADR 接受即证明。
Severity: P1
Expected Answer Depth: state model、write gate。
Evidence Required: Round trace、ADR、benchmark。
Kill Condition: accepted-target 文档被当成 Current/Measured。
Blue Answer: `ACCEPTED_TARGET` 表示 Owner/用户在目标层接受方向；`SURVIVED` 需要 Red/Blue/Counter 仍成立；`MEASURED` 需要可复现测试/Eval；`PRODUCTION_PROVEN` 还需运行证据。Canonical Write Gate 必须保留 Debate Trace。
State Boundary: Current/Target/Future 独立；History 归档；状态不是证据强度。
Problem: 文档过度承诺；Decision=KEEP_STATE_MODEL。
Ownership: Architecture Governance；State Transition: Proposed→Under Attack→Survived/Rejected→Accepted Target→Measured。
Failure: stale claim；Retry: reopen next round；Recovery: supersede doc/ADR。
Idempotency: decision ID and round ID；Security: user gate audit；Observability: commit and verifier。
Alternative: README status only；Tradeoff: easier but non-auditable。
Test / Benchmark: V2 verifier and canonical gate；Evidence: state-model.md。
Remaining Gap: GAP-V2-022
Red Critique: 流程清晰，可执行性由 verifier 保证。
Blue Revision: 新 Round 的每题保留 decision and evidence refs。
Final Red Assessment: Process design survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q019
Gap Candidate Refs: GAP-V2-022

## Q020

Round ID: ROUND-001
Category: B
Question: Architecture Part A、Part B、Part C 为什么要分阶段？如果 Part A 的 Problem/Domain/Ownership 不稳定，为什么可以直接写 API、表和 Service topology？
Attack Intent: 防止过早落到实现细节。
Target Component: Architecture Process
Assumption Being Attacked: 先列组件再补理由。
Severity: P1
Expected Answer Depth: phase gate、dependency。
Evidence Required: reconstruction workflow and user gate。
Kill Condition: Part C 反向决定历史 Problem/Domain。
Blue Answer: Part A 先锁 Problem、Product Context、Domain、Canonical State、Ownership 和失败边界；Part B 再审 Runtime/Knowledge/Security/Data/Service；Part C 只有 Accepted Target 后写 API、Schema、Migration、Tests。未稳定的上层不能被实现细节反推。
State Boundary: Historical facts separate; Target candidates phase-gated。
Problem: implementation-led architecture；Decision=KEEP_PART_GATES。
Ownership: Architecture Owner；State Transition: A stable→B attacked→C gated。
Failure: late domain change；Retry: reopen B/C；Recovery: Expand/Migrate/Verify/Contract。
Idempotency: versioned contract and ADR；Security: schema/API changes stop condition；Observability: gate checklist。
Alternative: one big architecture doc；Tradeoff: faster but conflates levels。
Test / Benchmark: doc gate and change review；Evidence: round-protocol-v2.md。
Remaining Gap: GAP-V2-005, GAP-V2-022
Red Critique: 分层合理，尚未形成完整 Part A record。
Blue Revision: Round-001 先输出候选和 Gap，不改 Canonical Architecture。
Final Red Assessment: Process survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q020
Gap Candidate Refs: GAP-V2-005, GAP-V2-022

## Q021

Round ID: ROUND-001
Category: C
Question: 为什么每个 Agent Run 都需要 Plan？对确定性的单步“检索→回答”，Plan 是否只是额外状态？
Attack Intent: 攻击 Planner 默认存在。
Target Component: Agent Runtime
Assumption Being Attacked: 所有任务都要动态规划。
Severity: P1
Expected Answer Depth: task class、scope down、cost。
Evidence Required: task routing and benchmark。
Kill Condition: 单步任务也强制复杂 Plan 且无收益。
Blue Answer: 不需要强制。确定性单步任务可走 Direct/Fixed Workflow；Plan 只在多步、并行、预算、审批、重试、HITL 或 replan 需要显式控制时创建。Plan 本身是 Runtime Control State，不是 Domain Fact。
State Boundary: Historical=实际 Planner 范围 UNKNOWN；Current=Agent graph surface；Target=profiled planning。
Problem: planner overhead；Decision=SIMPLIFY；Why=按任务复杂度选择。
Ownership: Runtime owns Plan；State Transition: direct task or PlanVersion。
Failure: wrong plan；Retry: bounded replan；Recovery: last valid PlanVersion；Idempotency: run/plan generation。
Security: policy snapshot before execution；Observability: plan cost and completion reason。
Alternative: always ReAct/always DAG；Tradeoff: flexibility vs cost。
Test / Benchmark: fixed single-step vs planned workflow。
Evidence: agent-platform.md；Remaining Gap: GAP-V2-006
Red Critique: 能删除默认 Planner，符合必要复杂度。
Blue Revision: 将 Direct Path 加入 Runtime Target candidate。
Final Red Assessment: Target fitness good; Current unknown。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q021
Gap Candidate Refs: GAP-V2-006

## Q022

Round ID: ROUND-001
Category: C
Question: Deterministic Single-Step Plan、Dynamic DAG 和 ReAct 分别解决什么不同问题？如果三者都能调用 Tool，为什么不只保留一个？
Attack Intent: 攻击功能重叠。
Target Component: Planning
Assumption Being Attacked: 机制越多越强。
Severity: P1
Expected Answer Depth: mechanism separation and selection policy。
Evidence Required: task matrix。
Kill Condition: 无法给出触发条件。
Blue Answer: Single-Step 解决固定一次动作；DAG 解决已知依赖和并行；ReAct 解决观察后动态选择。选择由 Task Contract/complexity policy 决定，不能把三者叠加成默认路径。
State Boundary: Current=无证据显示全部生产使用；Target=policy-dispatched execution modes。
Problem: execution mode explosion；Decision=MERGE_AS_POLICY；Why=保留能力但减少默认路径。
Ownership: Runtime policy；State Transition: TaskClass→mode→Step states。
Failure: mode mismatch；Retry: bounded fallback/replan；Recovery: checkpoint mode/version；Idempotency: step key。
Security: each mode same approval gate；Observability: mode and transition。
Alternative: only ReAct；Tradeoff: simpler but less deterministic。
Test / Benchmark: mode ablation on task classes。
Evidence: multi-agent-runtime.md；Remaining Gap: GAP-V2-006
Red Critique: 需要真实任务分类和成本数据。
Blue Revision: 把三种机制作为 Conditional Runtime Capability。
Final Red Assessment: conditional survive。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q022
Gap Candidate Refs: GAP-V2-006

## Q023

Round ID: ROUND-001
Category: C
Question: Dynamic DAG 的并行分支如何声明 Join 条件？如果一个分支失败、超时或产生互相冲突的 Proposal，Coordinator 能否错误地继续完成？
Attack Intent: 攻击并行和完成条件。
Target Component: Agent Runtime
Assumption Being Attacked: 所有 branch 完成就等于任务完成。
Severity: P0
Expected Answer Depth: reducer/join/evidence gate。
Evidence Required: branch failure and join tests。
Kill Condition: Join 只按节点数，不检查 domain/evidence condition。
Blue Answer: Join 必须绑定 PlanVersion、branch result、required/optional semantics、EvidenceRequirement 和 Domain Condition；失败/冲突分支进入 BLOCKED/REPLAN/REVIEW，不能仅因其他分支完成就发布 Finding。
State Boundary: Runtime branch state 与 Domain proposal 分离。
Problem: false completion；Decision=KEEP_DOMAIN_AWARE_COMPLETION_CONTRACT。
Ownership: Runtime joins control; Domain Owner validates business completion。
State Transition: Pending→Succeeded/Failed/Conflict→Join Gate→Complete/Blocked。
Failure: partial branch; Retry: branch-local idempotent retry; Recovery: checkpoint+domain snapshot; Idempotency: branch attempt key。
Security: branch permissions fixed by policy snapshot；Observability: join reason and missing evidence。
Alternative: all-or-nothing task；Tradeoff: simple but loses partial progress。
Test / Benchmark: failure injection, evidence-gate tests。
Evidence: agent-platform.md；Remaining Gap: GAP-V2-006, GAP-V2-007
Red Critique: Target answer addresses false completion but Current missing。
Blue Revision: completion Gate remains Hypothesis until trace exists。
Final Red Assessment: P0 implementation gap。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q023
Gap Candidate Refs: GAP-V2-006, GAP-V2-007

## Q024

Round ID: ROUND-001
Category: C
Question: PlanVersion 为什么不可变？当新 Evidence 使旧 Finding stale 时，旧 Plan 是修补、复制还是新建版本？
Attack Intent: 攻击计划变更与历史可追溯性。
Target Component: Plan / Replan
Assumption Being Attacked: 直接修改当前 Plan 更简单。
Severity: P0
Expected Answer Depth: versioning、barrier、audit。
Evidence Required: plan epoch/replan trace。
Kill Condition: 旧执行记录无法解释当时依据。
Blue Answer: PlanVersion 不可变，replan 创建新版本并声明 barrier、已完成/需重做步骤、DomainGeneration 和 Evidence snapshot；不能静默修改旧 Plan，否则无法审计和恢复。
State Boundary: Historical=未证明；Current=Target contract；Target=immutable PlanVersion + replan barrier。
Problem: execution history rewrite；Decision=KEEP_VERSIONING。
Ownership: Runtime；State Transition: PlanV1→Barrier→PlanV2。
Failure: concurrent replan；Retry: compare-and-swap epoch；Recovery: last valid version；Idempotency: plan generation。
Security: policy snapshot must be rechecked；Observability: version diff and reason。
Alternative: mutable JSON plan；Tradeoff: less schema but no replay certainty。
Test / Benchmark: epoch conflict/fault test。
Evidence: multi-agent-runtime.md；Remaining Gap: GAP-V2-006, GAP-V2-007
Red Critique: 设计闭环，未证明 Current。
Blue Revision: 新版 Plan 只作为 Target。
Final Red Assessment: Target survives conditionally。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q024
Gap Candidate Refs: GAP-V2-006, GAP-V2-007

## Q025

Round ID: ROUND-001
Category: C
Question: Agent Run 在 Planner 已提交 PlanVersion、PostgreSQL 已写 Run，但 LangGraph Checkpoint 写失败时，恢复顺序是什么？
Attack Intent: 攻击控制状态双写。
Target Component: Runtime / Data
Assumption Being Attacked: Framework checkpoint 总能作为恢复锚点。
Severity: P0
Expected Answer Depth: reconciliation sequence。
Evidence Required: injected failure trace。
Kill Condition: 重启后重复创建 Run 或跳过未执行步骤。
Blue Answer: Domain Run/Plan 是已提交业务控制事实；Checkpoint 缺失时从 Run/Plan version、step records、idempotency records 和 DomainGeneration 重建/补写 runtime checkpoint，不能重复创建业务 Run。
State Boundary: Domain control records vs framework checkpoint。
Problem: checkpoint write loss；Decision=KEEP_RECONCILIATION；Why=外部框架不是唯一事实源。
Ownership: Runtime Service owns Run/Plan; checkpointer is derived control persistence。
State Transition: Run submitted→checkpoint missing→rebuild→resume/blocked。
Failure: partial persist；Retry: checkpoint write; Recovery: deterministic reconstruction; Idempotency: Run ID/PlanVersion。
Security: resume rechecks policy epoch；Observability: recovery reason and generation。
Alternative: fail permanently；Tradeoff: safer but loses work。
Test / Benchmark: checkpoint failure injection。
Evidence: ADR-0008/0010；Remaining Gap: GAP-V2-007, GAP-V2-013
Red Critique: 有恢复方向，但没有具体 storage contract。
Blue Revision: 将 checkpoint 与 Domain Run reconciliation 作为 P0 Gap。
Final Red Assessment: P0 remains open。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q025
Gap Candidate Refs: GAP-V2-007, GAP-V2-013

## Q026

Round ID: ROUND-001
Category: C
Question: Coordinator、Evidence Agent、Dispute Agent 和 Reviewer Agent 为什么是 Agent，而不是 Skill、Capability 或普通 Worker？
Attack Intent: 防止 Agent 数量由角色名驱动。
Target Component: Multi-Agent
Assumption Being Attacked: 专业角色天然需要独立 Agent。
Severity: P1
Expected Answer Depth: independent context/permission/model/lifecycle/eval。
Evidence Required: task ablation and role contract。
Kill Condition: 角色没有独立上下文、权限、资源或评测边界。
Blue Answer: 默认先是同一 Runtime 中的 role profile、Skill 或 ephemeral worker；只有独立 Context、Permission、Model Policy、Knowledge Scope、Resource Pool、Lifecycle 或 Eval Contract 才升级 Agent。
State Boundary: Historical=角色拓扑 UNKNOWN；Current=target profiles；Target=levelled agent model。
Problem: role/service inflation；Decision=SIMPLIFY_TO_PROFILE；Why=共享 Domain/Capability。
Ownership: Runtime profile registry；State Transition: profile→worker/agent only with evidence。
Failure: delegation mismatch；Retry: bounded worker retry；Recovery: coordinator checkpoint。
Security: profile permission downscope；Observability: delegation lineage。
Alternative: persistent team；Tradeoff: flexibility vs cost。
Test / Benchmark: single agent + parallel tools vs L2/L3。
Evidence: multi-agent-runtime.md；Remaining Gap: GAP-V2-006。
Red Critique: 可以降级为 Profile，保留条件明确。
Blue Revision: L4/L5 持久团队不作为默认。
Final Red Assessment: 条件性保留。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q026
Gap Candidate Refs: GAP-V2-006

## Q027

Round ID: ROUND-001
Category: C
Question: 两个 Agent 共享同一个 Matter 时，如何防止一个 Agent 看到另一个 Agent 未授权的 Memory、Evidence 或 Tool？
Attack Intent: 攻击共享 Domain State 的权限边界。
Target Component: Multi-Agent / Security
Assumption Being Attacked: 共享 Matter 自动等于共享全部上下文。
Severity: P0
Expected Answer Depth: scope intersection and preflight。
Evidence Required: cross-agent authorization trace。
Kill Condition: Matter ID 是唯一权限判断。
Blue Answer: Matter 是必要但不充分的边界；每次 ContextPack、Evidence retrieval、Memory injection 和 Tool execution 都计算 Tenant/Workspace/Matter/User/Agent/Task/Connection/epoch 交集，拒绝未授权内容。
State Boundary: Historical=未证明；Current=Target security；Target=pre-retrieval/pre-execution enforcement。
Problem: lateral disclosure；Decision=KEEP_DOWN_SCOPE。
Ownership: Security owns decision facts，Domain owns Matter；State Transition: candidate→authorized/rejected。
Failure: stale grant；Retry: re-evaluate epoch；Recovery: quarantine output。
Security: deny by default；Observability: authorization decision trace。
Alternative: shared prompt；Tradeoff: easy but unsafe。
Test / Benchmark: cross-tenant/cross-agent access and revocation。
Evidence: security-architecture.md；Remaining Gap: GAP-V2-015。
Red Critique: Target 对权限有要求，Current 未验证。
Blue Revision: 将 Context Assembly Security Test 设为 P0。
Final Red Assessment: 设计保留，证据开放。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q027
Gap Candidate Refs: GAP-V2-015

## Q028

Round ID: ROUND-001
Category: C
Question: 多 Agent 并行时，哪些步骤可以共享 Evidence Retrieval，哪些必须独立执行？共享结果如何防止一个角色的错误污染全部角色？
Attack Intent: 攻击并行复用和污染传播。
Target Component: Runtime / Knowledge
Assumption Being Attacked: 共享 Context 越多越高效。
Severity: P1
Expected Answer Depth: immutable snapshot、role scope、provenance。
Evidence Required: reuse trace and error isolation test。
Kill Condition: mutable共享上下文无版本和来源。
Blue Answer: 可共享的是有版本、权限和来源的 Evidence Snapshot/Candidate；角色推断、未审查 Memory 和 Proposal 不直接共享。共享引用而非可变结论，角色仍需独立证据门。
State Boundary: Retrieval projection vs domain acceptance。
Problem: contamination；Decision=KEEP_IMMUTABLE_SNAPSHOT。
Ownership: Knowledge owns snapshot provenance；Domain owns accepted fact。
State Transition: retrieval→snapshot→role proposal。
Failure: wrong retrieval；Retry: role-local retrieval；Recovery: invalidate snapshot。
Security: snapshot scope checked per consumer；Observability: reuse/reference lineage。
Alternative: independent full retrieval；Tradeoff: cost higher but isolation stronger。
Test / Benchmark: reuse rate vs unsupported claims。
Evidence: knowledge-evidence-architecture.md；Remaining Gap: GAP-V2-009。
Red Critique: 复用与隔离的取舍可测。
Blue Revision: 将 reuse rate 作为效率而非质量替代指标。
Final Red Assessment: 条件性通过。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q028
Gap Candidate Refs: GAP-V2-009

## Q029

Round ID: ROUND-001
Category: C
Question: Reviewer Agent 是否真的需要自主规划和工具权限？如果它只检查 Evidence Sufficiency，为什么不是确定性 Validator？
Attack Intent: 删除无必要 Reviewer Agent。
Target Component: Reviewer Agent
Assumption Being Attacked: 角色名决定 Agent。
Severity: P1
Expected Answer Depth: deterministic boundary and human review。
Evidence Required: reviewer task examples and error analysis。
Kill Condition: Validator 已能完成全部检查且 Agent 无增益。
Blue Answer: Schema、引用存在性和权限可由确定性 Validator 完成；只有需要语义判断、冲突解释或复核建议时才使用 Reviewer profile，且不能替代 HumanDecision。
State Boundary: Historical=Reviewer Agent 未确认；Current=Target candidate；Target=validator-first review。
Problem: LLM overuse；Decision=SIMPLIFY。
Ownership: Eval/Domain policy；State Transition: deterministic checks→optional semantic proposal→human decision。
Failure: false pass；Retry: human escalation；Recovery: block WorkProduct。
Security: read-only by default；Observability: check and model contribution。
Alternative: always Agent；Tradeoff: more flexible but costlier。
Test / Benchmark: validator-only vs reviewer-assisted acceptance。
Evidence: eval docs；Remaining Gap: GAP-V2-020。
Red Critique: 删除条件明确。
Blue Revision: Reviewer Agent 不是默认服务。
Final Red Assessment: Simplification survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q029
Gap Candidate Refs: GAP-V2-020

## Q030

Round ID: ROUND-001
Category: C
Question: Agent 的 Reflection 如果不改变 Plan、EvidenceRequirement 或下一步动作，为什么不删除？
Attack Intent: 攻击 Reflection 术语化。
Target Component: Reflection
Assumption Being Attacked: 更多自我批评等于更高质量。
Severity: P1
Expected Answer Depth: observable mutation and ablation。
Evidence Required: reflection ablation with cost/quality。
Kill Condition: 只增加 Token/Latency，不改变错误率或行动。
Blue Answer: Reflection 只有在产生可审计的 Action、Evidence Gap、Plan Revision 或 Abstain 结果时才保留；否则删除为无效思考步骤。收益必须用固定任务消融验证。
State Boundary: Historical=未确认；Current=Target mechanism；Target=measurable reflection。
Problem: token waste；Decision=DEFER_UNTIL_ABLATION。
Ownership: Runtime policy/Eval；State Transition: step result→reflection decision→action/no-op。
Failure: self-confirmation bias；Retry: bounded independent check；Recovery: return to prior valid state。
Security: reflection cannot grant permission；Observability: delta and cost。
Alternative: deterministic checklist；Tradeoff: less flexible but reproducible。
Test / Benchmark: with/without reflection。
Evidence: eval contract；Remaining Gap: GAP-V2-006。
Red Critique: 有明确删除条件。
Blue Revision: Reflection 保持 Hypothesis。
Final Red Assessment: 未证明必要。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q030
Gap Candidate Refs: GAP-V2-006

## Q031

Round ID: ROUND-001
Category: C
Question: Replan 如何判断是新证据导致的必要变化，而不是模型随机改变计划？
Attack Intent: 攻击非确定性 Replan。
Target Component: Replan
Assumption Being Attacked: 模型可以随时重规划。
Severity: P0
Expected Answer Depth: trigger, evidence delta, version barrier。
Evidence Required: replan trace with trigger。
Kill Condition: 无 Trigger、旧新 Plan 差异和审核条件。
Blue Answer: Replan 必须有 Trigger（新 Evidence、Tool failure、stale、budget、permission 或 human decision），绑定 DomainGeneration/PlanVersion，并经过 bounded policy；随机换计划不能直接覆盖旧版本。
State Boundary: Runtime control references Domain snapshot；Target only。
Problem: oscillating plan；Decision=KEEP_TRIGGERED_REPLAN。
Ownership: Runtime policy；State Transition: valid plan→trigger→barrier→new plan。
Failure: endless loop；Retry: bounded attempts and escalate。
Recovery: last valid plan；Idempotency: trigger fingerprint。
Security: permission epoch recheck；Observability: trigger/diff/attempt。
Alternative: fixed workflow；Tradeoff: less adaptive。
Test / Benchmark: replan loop/fault tests。
Evidence: agent-platform.md；Remaining Gap: GAP-V2-006, GAP-V2-007。
Red Critique: 触发条件比“模型想改”强，但未实现。
Blue Revision: Replan loop 作为 P0 test。
Final Red Assessment: Target conditionally survives。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q031
Gap Candidate Refs: GAP-V2-006, GAP-V2-007

## Q032

Round ID: ROUND-001
Category: C
Question: Agent Budget 到底限制 Token、模型调用、Tool Calls、Retrieval Rounds、时间还是外部副作用？不同预算耗尽时状态如何落盘？
Attack Intent: 攻击模糊 Budget。
Target Component: Runtime Budget
Assumption Being Attacked: 一个数字足够控制成本。
Severity: P1
Expected Answer Depth: dimensions and terminal states。
Evidence Required: budget receipt/trace。
Kill Condition: 超预算后仍发布未审查结果或无限重试。
Blue Answer: Budget 是分维度 Contract：time、model calls、tokens、retrieval/tool calls、cost 和 effect allowance；耗尽进入 BUDGET_EXCEEDED/NEEDS_REVIEW，保存 partial state，不能静默降级为成功。
State Boundary: Runtime Budget Snapshot vs Domain state。
Problem: runaway cost/unsafe effect；Decision=KEEP_MULTIDIMENSION_BUDGET。
Ownership: Runtime policy；State Transition: Running→BudgetExceeded→Resume/Abort/Review。
Failure: provider reports late usage；Retry: reconcile usage receipt；Recovery: bounded resume with new approval。
Security: budget cannot expand permissions；Observability: per-step usage。
Alternative: token-only；Tradeoff: misses tool/time risk。
Test / Benchmark: budget fault injection。
Evidence: agent-platform.md；Remaining Gap: GAP-V2-014。
Red Critique: 状态和预算维度清楚，暂无运行证据。
Blue Revision: 将 Usage Receipt 与 Effect Allowance 分开。
Final Red Assessment: Target survives。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q032
Gap Candidate Refs: GAP-V2-014

## Q033

Round ID: ROUND-001
Category: C
Question: HITL Interrupt 恢复时，人工决定绑定的是哪个 Matter、Finding、PlanVersion 和 Security Epoch？
Attack Intent: 攻击人工审批恢复漂移。
Target Component: HITL
Assumption Being Attacked: 一个 approval_id 就足够恢复。
Severity: P0
Expected Answer Depth: binding and stale approval。
Evidence Required: approval resume trace。
Kill Condition: 审批后 Domain/permission 已变更仍执行旧动作。
Blue Answer: Approval 必须绑定 Matter/Task、PreparedAction、PlanVersion、DomainGeneration、ToolVersion、parameters hash 和 Security Epoch；恢复前重新验证，任何版本或权限变化都需重新审批。
State Boundary: HumanDecision ≠ Security Approval ≠ Runtime interrupt。
Problem: stale approval；Decision=KEEP_BOUND_APPROVAL。
Ownership: Security owns effect approval; Domain owns legal review; Runtime owns interrupt。
State Transition: INTERRUPTED→Approved/Rejected/Stale→Resume/Review。
Failure: stale or duplicate approval；Retry: re-approve；Recovery: cancel prepared action。
Security: deny on epoch mismatch；Observability: decision lineage。
Alternative: approval_id only；Tradeoff: simpler but unsafe。
Test / Benchmark: revoked permission and changed parameters。
Evidence: security architecture；Remaining Gap: GAP-V2-015, GAP-V2-016。
Red Critique: 关键绑定明确。
Blue Revision: 双审批不合并。
Final Red Assessment: Target survives; implementation P0。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q033
Gap Candidate Refs: GAP-V2-015, GAP-V2-016

## Q034

Round ID: ROUND-001
Category: C
Question: 一个 Agent 是否可以直接调用 Legal Capability Provider 并把结果写入 Domain？如果不能，谁执行 Proposal→Validation？
Attack Intent: 攻击 Capability 与 Domain Owner 边界。
Target Component: Legal Capability
Assumption Being Attacked: 专业算法输出即法律事实。
Severity: P0
Expected Answer Depth: provider contract and owner mutation。
Evidence Required: provider conformance/mutation trace。
Kill Condition: Agent/Provider 直写 FactVersion/ConflictVersion。
Blue Answer: Provider 只能输出 typed Proposal/Candidate/Observation/Reference/Receipt；Domain Owner 执行 schema、provenance、permission、dependency、review 和 version validation。Agent 只提交 proposal，不拥有 mutation authority。
State Boundary: capability output vs domain canonical state。
Problem: unverified legal fact；Decision=KEEP_PROVIDER_BOUNDARY。
Ownership: Capability provider computes; Domain Owner commits。
State Transition: provider candidate→validated/rejected→version。
Failure: malformed or unsupported proposal；Retry: provider-local or human review；Recovery: no canonical write。
Security: provider scoped access；Observability: provider/model/version trace。
Alternative: hard-code algorithms in Agent；Tradeoff: fast but duplicated and untestable。
Test / Benchmark: conformance and mutation denial。
Evidence: ADR-0007/0008；Remaining Gap: GAP-V2-022。
Red Critique: 这是核心保护边界，但没有 Current 证据。
Blue Revision: Provider conformance Gate。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q034
Gap Candidate Refs: GAP-V2-022

## Q035

Round ID: ROUND-001
Category: C
Question: 为什么 LangGraph 需要承担 durable workflow，而不是 Plain Python、Celery 或普通状态机？请给出实际触发条件和删除条件。
Attack Intent: Kill LangGraph。
Target Component: LangGraph
Assumption Being Attacked: 框架名称就是 Runtime 必要性。
Severity: P1
Expected Answer Depth: provider comparison and trigger。
Evidence Required: durable execution/HITL/replan benchmark or trace。
Kill Condition: 任务只有 Retrieve→Model→Tool→Answer，且无 checkpoint/interrupt/resume/branch/reducer。
Blue Answer: LangGraph 仅在 durable execution、checkpoint、interrupt/resume、parallel/reducer、HITL 或 replan 被任务证明需要时保留；简单流可用 Plain Python/State Machine。LangGraph 不拥有 Domain State。
State Boundary: Current has LangGraph surface; Target provider candidate。
Problem: orchestration overdesign；Decision=DEFER_PROVIDER_LOCK。
Ownership: Runtime owns orchestration contract；provider is replaceable。
State Transition: workflow run/checkpoint only。
Failure: provider checkpoint mismatch；Retry/recovery via reconciliation。
Security: framework cannot bypass gates；Observability: provider/version trace。
Alternative: Plain Python/Celery/State Machine；Tradeoff: less built-in durable semantics。
Test / Benchmark: runtime provider spike and fault tests。
Evidence: ADR-0008；Remaining Gap: GAP-V2-013, GAP-V2-020。
Red Critique: 有删除条件，当前没有实际 task profile。
Blue Revision: 不把 LangGraph 写成永久核心。
Final Red Assessment: Conditional defer。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q035
Gap Candidate Refs: GAP-V2-013, GAP-V2-020

## Q036

Round ID: ROUND-001
Category: D
Question: Exact Statute 查询、语义 FAQ、Similar Case、Claim→Evidence、Fact→LegalElement→Statute 和跨文档证据链为什么要使用同一种 Retrieval？
Attack Intent: 攻击统一检索路径。
Target Component: Knowledge / Retrieval
Assumption Being Attacked: Vector Search 适合所有法律问题。
Severity: P1
Expected Answer Depth: query class routing。
Evidence Required: query-class benchmark。
Kill Condition: 无 Query Class，始终 Graph 或始终 Dense。
Blue Answer: Retrieval 应按 Task/Claim/EvidenceRequirement/QueryClass 选择 lexical、dense、hybrid、rerank、graph 或 corrective；Exact Statute 可能 lexical/version 优先，跨关系证据才候选 Graph。
State Boundary: Historical=检索实际路径部分 UNKNOWN；Current=多 provider surface；Target=conditional retrieval policy。
Problem: wrong retriever；Decision=KEEP_CONDITIONAL_ROUTING。
Ownership: Knowledge Owner；State Transition: query classification→retrieval round→candidate/evidence。
Failure: misclassification；Retry: fallback hybrid/corrective；Recovery: preserve query/candidates。
Security: filter before retrieval；Observability: query class/provider/latency。
Alternative: fixed vector/hybrid；Tradeoff: simpler but task mismatch。
Test / Benchmark: Recall@K, nDCG, citation and latency by class。
Evidence: ADR-0006；Remaining Gap: GAP-V2-009。
Red Critique: 没有宣称 Graph 天然优越，保留条件性。
Blue Revision: query class 必须进入 Eval dataset。
Final Red Assessment: Target survives pending benchmark。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q036
Gap Candidate Refs: GAP-V2-009, GAP-V2-020

## Q037

Round ID: ROUND-001
Category: D
Question: GraphRAG 的 Graph 中哪些节点和边是 Canonical Domain State，哪些只是 Retrieval Projection？错误 Event/Conflict 边如何纠正？
Attack Intent: 攻击 Graph 与业务事实混淆。
Target Component: Graph Retrieval
Assumption Being Attacked: 图里的边天然是真实关系。
Severity: P0
Expected Answer Depth: projection/provenance/rebuild。
Evidence Required: graph projection contract and correction trace。
Kill Condition: Neo4j/Graph index 可以直接提交 Conflict/Finding。
Blue Answer: Graph 默认是 Derived Projection，节点边带 source/version/provenance/confidence；Domain State 只由 Owner 接受。错误边可删除/重建 projection，不能直接修改 Canonical Fact。
State Boundary: Graph=derived index；Domain=accepted state。
Problem: graph hallucination/staleness；Decision=CONDITIONAL_GRAPH_PROVIDER。
Ownership: Knowledge builds projection; Domain accepts facts。
State Transition: source→projection candidate→retrieval observation；not canonical commit。
Failure: extraction error/index stale；Retry: versioned rebuild；Recovery: rebuild from DocumentVersion/accepted state。
Security: graph query scoped to Matter/tenant；Observability: edge provenance and build version。
Alternative: relational joins/hybrid；Tradeoff: less multi-hop but simpler。
Test / Benchmark: graph error rate, evidence sufficiency, rebuild test。
Evidence: knowledge/domain docs；Remaining Gap: GAP-V2-009, GAP-V2-010。
Red Critique: Graph 权威边界清晰。
Blue Revision: Neo4j 保持 provider candidate，不默认 Canonical。
Final Red Assessment: Target survives only conditionally。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q037
Gap Candidate Refs: GAP-V2-009, GAP-V2-010

## Q038

Round ID: ROUND-001
Category: D
Question: 如果 Hybrid RAG 在大多数 Query Class 上与 Graph 相同或更好，Graph Provider 的删除条件是什么？
Attack Intent: Kill Graph。
Target Component: GraphRAG
Assumption Being Attacked: 研究趋势等于项目收益。
Severity: P1
Expected Answer Depth: preregistered threshold and deletion path。
Evidence Required: kill graph benchmark。
Kill Condition: Graph 无 Recall/Evidence/Reviewer/Cost tradeoff 的净收益。
Blue Answer: Graph 必须在关系型、跨文档、多证据 Query Class 上预注册阈值；若没有质量收益，或收益不足以覆盖 Build/Latency/Token/维护成本，则降为可选 Provider 或删除，不保留 Always-on。
State Boundary: Target/Hypothesis only；Current quality not proven。
Problem: graph cost；Decision=DEFER_CONDITIONAL。
Ownership: Eval decides evidence；Knowledge removes provider。
State Transition: candidate→benchmark→conditional/delete。
Failure: biased benchmark；Retry: held-out hard cases and independent review。
Recovery: hybrid/vector fallback。
Security: same evidence/permission conditions；Observability: provider cost/latency。
Alternative: Fixed Hybrid；Tradeoff: less graph expressivity, lower ops cost。
Test / Benchmark: Graph Kill Test。
Evidence: ADR-0008/0006；Remaining Gap: GAP-V2-010, GAP-V2-020。
Red Critique: 删除条件足够明确，阈值仍需预注册。
Blue Revision: 先做 benchmark，不改生产路径。
Final Red Assessment: Graph not yet justified。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q038
Gap Candidate Refs: GAP-V2-010, GAP-V2-020

## Q039

Round ID: ROUND-001
Category: D
Question: Cross-document Evidence Chain 如何定义“足够”？只要找到三篇相关文档，还是必须覆盖每个 Claim 的 source span、版本和权限？
Attack Intent: 攻击 Evidence Sufficiency 模糊化。
Target Component: Evidence Retrieval
Assumption Being Attacked: 文档数量代表证据充分。
Severity: P0
Expected Answer Depth: claim coverage and citation integrity。
Evidence Required: gold evidence and citation evaluation。
Kill Condition: 无 Claim/EvidenceRequirement mapping，仍发布结论。
Blue Answer: Sufficiency 由 Claim/Requirement 覆盖、source span、DocumentVersion、权限、独立来源和冲突披露定义；文档数量只能是候选信号，不能替代支持链。
State Boundary: Candidate evidence vs accepted evidence vs Finding。
Problem: unsupported conclusion；Decision=KEEP_EVIDENCE_GATE。
Ownership: Domain/Eval contract；State Transition: requirement→candidate→accepted/insufficient。
Failure: missing/contradictory sources；Retry: targeted retrieval or abstain；Recovery: block Finding。
Security: evidence filtered before context；Observability: claim coverage and citation lineage。
Alternative: top-k docs；Tradeoff: cheaper but unsafe。
Test / Benchmark: Evidence Sufficiency, Claim Coverage, Citation Correctness。
Evidence: eval/knowledge docs；Remaining Gap: GAP-V2-009, GAP-V2-020。
Red Critique: 质量定义比 Recall 更贴近法律任务。
Blue Revision: Unsupported Claim 必须是 release metric。
Final Red Assessment: Target survives; measurement open。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q039
Gap Candidate Refs: GAP-V2-009, GAP-V2-020

## Q040

Round ID: ROUND-001
Category: D
Question: DocumentVersion 更新后，旧 Chunk、Embedding、BM25、Graph 和 Citation 如何标记 stale？能否混用不同版本的证据？
Attack Intent: 攻击索引版本一致性。
Target Component: Knowledge Indexes
Assumption Being Attacked: 索引更新是最终一致就足够。
Severity: P0
Expected Answer Depth: version binding and serving policy。
Evidence Required: index version and stale serving tests。
Kill Condition: 旧版本命中被静默引用为当前事实。
Blue Answer: 所有 Projection 绑定 DocumentVersion/IndexVersion；更新后旧投影可服务历史任务但不能无标记支持当前 Finding，Citation 必须记录版本；重建中进入 stale/limited 状态，按 policy abstain 或回退原文。
State Boundary: source version vs projection version vs accepted evidence。
Problem: version mixing；Decision=KEEP_VERSION_BINDING。
Ownership: Knowledge owns indexes; Domain owns accepted citation。
State Transition: indexed→stale→rebuild/available。
Failure: partial rebuild；Retry: idempotent job；Recovery: source/object storage rebuild。
Security: version does not bypass permissions；Observability: index generation and stale reason。
Alternative: overwrite in place；Tradeoff: simple but loses audit。
Test / Benchmark: stale index fault injection。
Evidence: knowledge/data docs；Remaining Gap: GAP-V2-009, GAP-V2-013。
Red Critique: 可以解释一致性，但 Current 尚未证明。
Blue Revision: 禁止静默混版。
Final Red Assessment: Target survives conditionally。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q040
Gap Candidate Refs: GAP-V2-009, GAP-V2-013

## Q041

Round ID: ROUND-001
Category: D
Question: Agentic Retrieval 何时允许第二轮检索？Evidence Gap 是谁定义的，如何避免 Agent 为了“更充分”无限搜索？
Attack Intent: 攻击 Agentic RAG 无界循环。
Target Component: Agentic Retrieval
Assumption Being Attacked: 更多检索总能提高答案。
Severity: P1
Expected Answer Depth: EvidenceRequirement, budget, stop/abstain。
Evidence Required: retrieval round trace and stop distribution。
Kill Condition: 没有 Gap、Budget、Stop Reason 或成本记录。
Blue Answer: 第二轮由未满足 EvidenceRequirement、冲突、低置信 citation 或 reviewer policy 触发，受 Retrieval Budget/Time/Token 限制；若仍不足则 ABSTAIN/REVIEW，不无限搜索。
State Boundary: RetrievalRound control state vs Evidence accepted state。
Problem: search loop/cost；Decision=KEEP_BOUNDED_AGENTIC_RETRIEVAL。
Ownership: Knowledge policy/Eval；State Transition: round→gap→next/stop。
Failure: repeated query；Retry: deduplicated query and provider fallback。
Recovery: keep prior evidence and stop reason；Idempotency: round fingerprint。
Security: same scope each round；Observability: round count/stop reason/cost。
Alternative: fixed one-shot hybrid；Tradeoff: lower cost, may miss evidence。
Test / Benchmark: latency/cost vs evidence sufficiency。
Evidence: knowledge/eval docs；Remaining Gap: GAP-V2-010, GAP-V2-020。
Red Critique: 需要真实 stop 分布，不是设计宣言。
Blue Revision: Stop Reason 纳入 Eval Contract。
Final Red Assessment: Target conditionally survives。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q041
Gap Candidate Refs: GAP-V2-010, GAP-V2-020

## Q042

Round ID: ROUND-001
Category: D
Question: Reranker 选择错误证据时，系统如何区分 Retriever 漏召回、Reranker 排序错误和 Generator 忽略证据？
Attack Intent: 攻击只测最终答案。
Target Component: Retrieval Eval
Assumption Being Attacked: 最终 Answer Score 能定位根因。
Severity: P1
Expected Answer Depth: layered eval and trace。
Evidence Required: stage-level dataset/trace。
Kill Condition: 只有一个 end-to-end score。
Blue Answer: Eval 分层保存 candidate recall、rerank nDCG、Evidence Sufficiency、citation mapping、claim support 和 final unsupported rate；每轮 trace 关联 stage 输出，才可定位责任。
State Boundary: candidate/index vs model reasoning vs accepted finding。
Problem: diagnosis blind spot；Decision=KEEP_LAYERED_EVAL。
Ownership: Eval Owner；State Transition: raw→retrieval→rerank→evidence→answer。
Failure: missing stage trace；Retry: replay fixed input；Recovery: fallback baseline。
Security: eval data scope；Observability: stage metrics and IDs。
Alternative: LLM Judge only；Tradeoff: low cost but opaque。
Test / Benchmark: staged error attribution。
Evidence: legal-eval docs；Remaining Gap: GAP-V2-020。
Red Critique: 分层指标有用，仍未测。
Blue Revision: 禁止只报最终 Judge。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q042
Gap Candidate Refs: GAP-V2-020

## Q043

Round ID: ROUND-001
Category: D
Question: Knowledge Scope 由用户选择后，为什么不能 retrieve everything？Task、Claim、EvidenceRequirement 和权限分别怎样约束查询？
Attack Intent: 攻击知识库全量召回和越权。
Target Component: Knowledge Scope
Assumption Being Attacked: 用户选 Scope 等于授权全部内容。
Severity: P0
Expected Answer Depth: policy intersection and query class。
Evidence Required: pre-retrieval filtering test。
Kill Condition: Scope selection绕过 tenant/matter/document permissions。
Blue Answer: Scope 只是候选范围，实际查询仍取 Task、Claim、EvidenceRequirement、Tenant/Workspace/Matter/User/Agent policy 的交集；过滤要在索引召回前完成，不能依赖 Prompt 删除。
State Boundary: Knowledge retrieval view vs Security decision。
Problem: data leakage/noisy retrieval；Decision=KEEP_SCOPE_INTERSECTION。
Ownership: Security grants, Knowledge applies filters。
State Transition: requested scope→authorized scope→retrieval round。
Failure: stale grant/index；Retry: re-evaluate epoch；Recovery: discard unauthorized candidates。
Security: deny by default；Observability: filter reasons and scope hash。
Alternative: one legal_kb；Tradeoff: simpler but leaks/noisy。
Test / Benchmark: cross-tenant and permission retrieval。
Evidence: security/knowledge docs；Remaining Gap: GAP-V2-015。
Red Critique: 权限前置是关键。
Blue Revision: Scope selected ≠ retrieve everything 写入 Gate。
Final Red Assessment: Target survives pending test。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q043
Gap Candidate Refs: GAP-V2-015

## Q044

Round ID: ROUND-001
Category: D
Question: 类案检索的“相似”是语义相似、法条相似、争议结构相似、事实模式相似还是结果相似？混在一个向量空间会造成什么？
Attack Intent: 攻击 Similar Case 单一 embedding。
Target Component: Similar Case Retrieval
Assumption Being Attacked: 相似度没有任务语义。
Severity: P1
Expected Answer Depth: query class/features and evaluation。
Evidence Required: labeled similar-case task set。
Kill Condition: 没有相似定义和人工相关性协议。
Blue Answer: Similar Case 必须声明 Query Class/相似维度，可能组合事实、争议、法条、程序和结果；向量只是候选，最终需 provenance、版本和人工/标注相关性评估。
State Boundary: SimilarCase candidate/projection vs Domain Finding。
Problem: misleading precedent；Decision=KEEP_TASK_TYPED_RETRIEVAL。
Ownership: Knowledge/Eval；State Transition: query→candidates→reviewed references。
Failure: spurious similarity；Retry: hybrid/rerank；Recovery: disclose limitation。
Security: scope and jurisdiction filter；Observability: feature/query class。
Alternative: single dense index；Tradeoff: cheap but ambiguous。
Test / Benchmark: nDCG, citation/reviewer acceptance by class。
Evidence: knowledge/eval docs；Remaining Gap: GAP-V2-020。
Red Critique: 需要实际标签，不可凭术语。
Blue Revision: Similar Case 保持 Candidate。
Final Red Assessment: 条件性保留。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q044
Gap Candidate Refs: GAP-V2-020

## Q045

Round ID: ROUND-001
Category: D
Question: Legal Capability 的 Event Extraction、Alignment、Conflict Detection、Fact–Article Mapping 为什么不直接嵌入每个 Agent？
Attack Intent: 攻击能力复用边界。
Target Component: Legal Intelligence
Assumption Being Attacked: Agent 私有代码更快。
Severity: P1
Expected Answer Depth: capability contract/provider replacement。
Evidence Required: duplicated-code or provider conformance evidence。
Kill Condition: 每个 Agent 重复一套法律算法且无法统一评测。
Blue Answer: 稳定的是 Capability Contract，算法实现可本地、LLM、fine-tuned model、OSS、API/MCP；Agent 负责选择和解释，不复制专业逻辑，Provider 不能直接写 Canonical state。
State Boundary: provider proposal vs domain version。
Problem: duplication/provider lock-in；Decision=KEEP_CAPABILITY_CONTRACT。
Ownership: Legal Intelligence contract/Domain owner；State Transition: input→proposal→validation。
Failure: provider disagreement；Retry: alternate provider/human review；Recovery: no commit until accepted。
Security: scoped inputs and output provenance；Observability: provider/version/quality。
Alternative: per-agent code；Tradeoff: local simplicity but drift。
Test / Benchmark: provider equivalence and task quality。
Evidence: ADR-0008/0007；Remaining Gap: GAP-V2-022。
Red Critique: Contract 层价值清楚，历史研究转化仍未知。
Blue Revision: 研究代码需 License/Fit Gate。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q045
Gap Candidate Refs: GAP-V2-022, GAP-V2-023

## Q046

Round ID: ROUND-001
Category: D
Question: 如果某个法律研究论文只有 GitHub 代码、没有 LICENSE，是否可以复制进 Zuno？
Attack Intent: 攻击研究成果商业复用假设。
Target Component: Research Transfer
Assumption Being Attacked: Public GitHub 等于可商用。
Severity: P0
Expected Answer Depth: license/isolated provider path。
Evidence Required: official repo/license and legal review。
Kill Condition: 没有 License 审查仍复制源码/模型。
Blue Answer: 不能自动复制。Public Context 只支持能力候选；无 LICENSE 标记 LICENSE_UNKNOWN，不能进入正式产品。可先独立 Spike/协议适配，经过 License、模型权重、数据和商业使用审查后决定。
State Boundary: PUBLIC_CONTEXT ≠ Commercial Permission ≠ Current integration。
Problem: legal/supply-chain risk；Decision=KEEP_LICENSE_GATE。
Ownership: Legal/Security/Build-Buy review；State Transition: unknown→reviewed→adopt/replace/reject。
Failure: license incompatibility；Retry: alternative implementation/provider；Recovery: remove isolated adapter。
Security: SBOM and artifact provenance；Observability: version/license record。
Alternative: build clean-room contract；Tradeoff: cost higher but safer。
Test / Benchmark: provider fit + license checklist。
Evidence: reuse-first ADR；Remaining Gap: GAP-V2-023。
Red Critique: 不能把论文写成 Current。
Blue Revision: LICENSE_UNKNOWN 是硬门槛。
Final Red Assessment: Policy survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q046
Gap Candidate Refs: GAP-V2-023

## Q047

Round ID: ROUND-001
Category: D
Question: OpenViking 历史上用户参与过 Memory/Context 接入，为什么这不证明当前仓库仍使用它，也不证明它拥有 Legal Fact？
Attack Intent: 攻击 Historical/Current/Target 污染。
Target Component: OpenViking Provider
Assumption Being Attacked: 用户经历等于当前依赖。
Severity: P0
Expected Answer Depth: fact state and provider boundary。
Evidence Required: old artifact/current dependency/conformance。
Kill Condition: 用户历史确认被写成当前生产组件或 Domain Owner。
Blue Answer: 用户确认只支持 Historical USER_CONFIRMED 范围；当前仓库未发现实现/依赖，故 Current UNKNOWN/未发现；Target 仍需 Provider Fit。OpenViking 可拥有 Memory/Context projection，不能拥有 Legal Domain State。
State Boundary: Historical user fact / Current repo evidence / Target provider separate。
Problem: experience inflation；Decision=KEEP_BOUNDARY。
Ownership: Facts Owner vs Memory policy vs Domain Owner。
State Transition: historical fact stays fact; provider candidate→fit review。
Failure: provider unavailable；Retry/fallback PostgreSQL/context strategy；Recovery: rebuild projection。
Security: provider must obey scope/secret policy；Observability: adapter/version trace。
Alternative: Matter DB + checkpoint；Tradeoff: fewer dependencies but possibly less context governance。
Test / Benchmark: memory reuse/contamination/permission ablation。
Evidence: facts/technology-reality.md；Remaining Gap: GAP-V2-011, GAP-V2-012。
Red Critique: 证据状态严格。
Blue Revision: OpenViking remains historical + target-open。
Final Red Assessment: Target and fact boundary survive。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q047
Gap Candidate Refs: GAP-V2-011, GAP-V2-012

## Q048

Round ID: ROUND-001
Category: D
Question: Memory 的 Working、Session、Matter-context、User 和 Organization scope 如何避免把一个 Matter 的事实泄漏到另一个 Matter？
Attack Intent: 攻击 Memory Scope。
Target Component: Memory
Assumption Being Attacked: 长期记忆默认可全局召回。
Severity: P0
Expected Answer Depth: scope/authority/temporal validity/revocation。
Evidence Required: cross-scope fault test。
Kill Condition: Memory key 或 embedding 相似度是唯一隔离条件。
Blue Answer: Scope、Authority、Matter/tenant binding、Temporal Validity、Data Classification 和 Security Epoch 组成召回前过滤；Working/Session 默认短命，Matter/User/Org 需要明确写入 policy 和删除/撤销。
State Boundary: Memory projection vs Domain Fact。
Problem: cross-matter contamination；Decision=KEEP_SCOPE_GOVERNANCE。
Ownership: Memory policy/Security；State Transition: candidate→authorized scope→context pack/expire。
Failure: wrong scope or stale grant；Retry: quarantine/revalidate；Recovery: delete/rebuild projection。
Security: deny-by-default and pre-retrieval filtering；Observability: scope and authority trace。
Alternative: one vector memory；Tradeoff: simple but unsafe。
Test / Benchmark: leakage, revocation, stale memory, reuse quality。
Evidence: agent/domain/security docs；Remaining Gap: GAP-V2-011, GAP-V2-015。
Red Critique: Target完整但 Current未知。
Blue Revision: Long-term Memory not default。
Final Red Assessment: conditional survive。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q048
Gap Candidate Refs: GAP-V2-011, GAP-V2-015

## Q049

Round ID: ROUND-001
Category: D
Question: Matter DB + Runtime Checkpoint 已能保存上下文时，OpenViking/独立 Memory Engine 的增量价值如何测？
Attack Intent: Kill Memory Engine。
Target Component: Memory Provider
Assumption Being Attacked: 分层 Memory 天然更好。
Severity: P1
Expected Answer Depth: ablation and deletion condition。
Evidence Required: memory benchmark。
Kill Condition: Provider 不提高 Context Reuse/质量，或收益低于成本和风险。
Blue Answer: 比较 Matter DB + Checkpoint、Session retrieval、OpenViking provider，在相同任务/模型/预算下测 context reuse、answer quality、staleness、污染、延迟和成本；无净收益则删除/外部化。
State Boundary: Provider only projection；Domain facts separate。
Problem: provider complexity；Decision=DEFER_PROVIDER_ADOPT。
Ownership: Eval decides; Memory policy stays Zuno。
State Transition: candidate→benchmark→adopt/delete。
Failure: memory pollution；Retry/quarantine；Recovery: rebuild from source/accepted memory。
Security: same scope controls；Observability: reuse and source trace。
Alternative: PostgreSQL + checkpoint；Tradeoff: lower complexity。
Test / Benchmark: memory ablation。
Evidence: ADR-0008；Remaining Gap: GAP-V2-011, GAP-V2-020。
Red Critique: 测量对象完整，仍无数据。
Blue Revision: OpenViking is not locked。
Final Red Assessment: Memory engine not justified yet。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q049
Gap Candidate Refs: GAP-V2-011, GAP-V2-020

## Q050

Round ID: ROUND-001
Category: D
Question: 如果 Graph、Memory 和 Multi-Agent 都能提高最终答案，如何判断收益来自哪一个，而不是更多 Token、更多 Retrieval 或不同 Prompt？
Attack Intent: 攻击归因混淆。
Target Component: Legal Eval
Assumption Being Attacked: 叠加实验可以证明每个组件。
Severity: P0
Expected Answer Depth: controlled factorial/ablation design。
Evidence Required: preregistered A/B/C and ablation plan。
Kill Condition: 变体同时改变模型、语料、预算、工具或 Prompt。
Blue Answer: 固定 base model、raw corpus、tools、comparable prompt/skills、token/time budget；按 A/B/C 和单变量消融记录 Evidence/Citation/Unsupported/Task/Latency/Cost/Calls/Reuse，不能用总 Judge score 归因。
State Boundary: Hypothesis only；no current quality claim。
Problem: causal ambiguity；Decision=KEEP_CONTROLLED_EVAL。
Ownership: Eval Owner；State Transition: hypothesis→registered→measured→decision。
Failure: confounded benchmark；Retry: independent slice/repeat。
Security: same data/permission profile；Observability: all budgets and calls。
Alternative: demo comparison；Tradeoff: cheap but invalid。
Test / Benchmark: A/B/C + Graph/Memory/Multi-Agent ablation。
Evidence: eval docs/ADR-0008；Remaining Gap: GAP-V2-020。
Red Critique: 归因要求充分，实验尚未执行。
Blue Revision: 复杂度只有通过归因才可保留。
Final Red Assessment: Evaluation gate survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q050
Gap Candidate Refs: GAP-V2-020

## Q051

Round ID: ROUND-001
Category: E
Question: PostgreSQL、Object Storage、Vector Index、Graph Projection、Cache 和 Runtime Checkpoint 分别保存什么？哪些可以重建，哪些是 System of Record？
Attack Intent: 攻击多数据库多事实源。
Target Component: Data Architecture
Assumption Being Attacked: 每个存储都可以保留最终结果。
Severity: P0
Expected Answer Depth: storage role matrix and rebuild input。
Evidence Required: data ownership registry/restore test。
Kill Condition: Neo4j/Milvus/Redis/Checkpoint 任一直接成为 Canonical Domain Truth。
Blue Answer: PostgreSQL 保存 Domain/accepted business state；Object Storage 保存原始文档/不可变来源；Vector/Graph/ES 是 derived projection；Redis 是 cache/lease candidate；Checkpoint 是 Runtime control state。Projection/cache/checkpoint 可从 versioned source/contract rebuild。
State Boundary: SoR vs projection/cache/runtime/object。
Problem: source conflict；Decision=KEEP_ROLE_SEPARATION。
Ownership: Domain/Data/Knowledge/Runtime owners separate。
State Transition: source→projection; domain transaction→outbox; runtime checkpoint→reconcile。
Failure: index/cache loss；Retry: rebuild/repopulate；Recovery: restore source and canonical DB。
Idempotency: version/generation keys；Security: each store inherits scope and retention。
Observability: source/projection generation and restore logs。
Alternative: one PostgreSQL for all；Tradeoff: simple but resource/security boundaries weaker。
Test / Benchmark: restore derived indexes and state reconciliation。
Evidence: architecture/data docs；Remaining Gap: GAP-V2-013。
Red Critique: Role separation clear, actual backup/restore unknown。
Blue Revision: physical stores remain provider candidates until evidence。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q051
Gap Candidate Refs: GAP-V2-013

## Q052

Round ID: ROUND-001
Category: E
Question: PostgreSQL 事务提交了 Finding，但 Outbox 写入失败时，能否发布 WorkProduct？如何恢复 DB/Queue 双写？
Attack Intent: 攻击事务与消息一致性。
Target Component: Domain / Outbox
Assumption Being Attacked: DB commit 和消息 publish 天然一致。
Severity: P0
Expected Answer Depth: local transaction/outbox/reconcile。
Evidence Required: outbox fault injection。
Kill Condition: 业务提交成功但没有可重发记录，或 Queue 成功被当事实。
Blue Answer: Domain fact 与 Outbox 必须在同一本地事务；Outbox 写失败则事务回滚，不能发布完成。Publisher 可重试，Consumer 以 event_id/idempotency/domain version 幂等；已有提交但消息未知时由 reconciler 扫描 Outbox/receipt。
State Boundary: Queue is delivery, DB is business truth。
Problem: dual write；Decision=KEEP_OUTBOX_IF_NEEDED。
Ownership: Domain owns transaction, infrastructure publishes。
State Transition: transaction→outbox pending→published/failed/retry。
Failure: publish timeout/duplicate；Retry: safe resend；Recovery: reconcile pending/unknown。
Security: event scope and secret isolation；Observability: event/attempt/receipt。
Alternative: direct publish/2PC；Tradeoff: 2PC heavier and not default。
Test / Benchmark: DB success/publish failure matrix。
Evidence: ADR-0010/data docs；Remaining Gap: GAP-V2-013, GAP-V2-017。
Red Critique: 不默认 2PC，恢复语义具体。
Blue Revision: Outbox only where cross-boundary event required。
Final Red Assessment: Target survives conditional on implementation。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q052
Gap Candidate Refs: GAP-V2-013, GAP-V2-017

## Q053

Round ID: ROUND-001
Category: E
Question: 两个 Agent 同时接受基于同一 EvidenceVersion 的互相冲突 Finding，Domain Owner 如何防止最后写入者覆盖前者？
Attack Intent: 攻击并发业务写。
Target Component: Domain Concurrency
Assumption Being Attacked: PostgreSQL last-write-wins 足够。
Severity: P0
Expected Answer Depth: optimistic concurrency/version conflict/review。
Evidence Required: concurrent mutation test。
Kill Condition: 无 generation/compare-and-swap/Conflict proposal。
Blue Answer: Proposal 带 DomainGeneration、source/evidence versions 和 expected current version；提交使用 optimistic concurrency/transaction，冲突产生 ConflictProposal 或 Review Required，不允许静默覆盖。
State Boundary: Proposal concurrency vs accepted Domain State。
Problem: lost update；Decision=KEEP_VERSIONED_MUTATION。
Ownership: Domain Owner；State Transition: proposal→accepted or version conflict→review。
Failure: concurrent commit；Retry: regenerate against new snapshot；Recovery: retain both provenance branches。
Idempotency: proposal/operation key；Security: same permission at commit。
Observability: conflict and generation trace。
Alternative: last-write-wins；Tradeoff: simpler but corrupts review history。
Test / Benchmark: concurrent proposal fault test。
Evidence: domain lifecycle/ADR-0008；Remaining Gap: GAP-V2-007, GAP-V2-022。
Red Critique: 必须区分 Domain Conflict 与分布式锁。
Blue Revision: Conflict 是业务候选，不自动成立。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q053
Gap Candidate Refs: GAP-V2-007, GAP-V2-022

## Q054

Round ID: ROUND-001
Category: E
Question: DocumentVersion、EvidenceVersion、FindingVersion 和 WorkProductVersion 为什么不可变？如果用户要修改，保存 patch 还是新版本？
Attack Intent: 攻击可审计性和可变实体。
Target Component: Versioning
Assumption Being Attacked: 直接 UPDATE 最简单。
Severity: P1
Expected Answer Depth: version/provenance/audit。
Evidence Required: version/mutation contract。
Kill Condition: 旧结论依据被覆盖后无法回放。
Blue Answer: 影响审计和依赖的对象采用不可变版本；用户修订生成新版本/新 HumanDecision，保留 parent/version/provenance，当前视图指向最新合法版本；Patch 可作为辅助，不取代版本。
State Boundary: current projection vs immutable versions。
Problem: history loss；Decision=KEEP_VERSIONED_FACTS。
Ownership: Domain Owner；State Transition: draft→version→review/publish/supersede。
Failure: partial version write；Retry transaction/idempotency key；Recovery previous version。
Security: access/version retention；Observability: actor/reason/source version。
Alternative: mutable rows with audit log；Tradeoff: fewer rows but harder dependency semantics。
Test / Benchmark: version replay/stale propagation。
Evidence: domain-state-lifecycle.md；Remaining Gap: GAP-V2-007。
Red Critique: 需要明确哪些对象可以压缩。
Blue Revision: Cache/projection 可覆盖，Canonical versions 不覆盖。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q054
Gap Candidate Refs: GAP-V2-007

## Q055

Round ID: ROUND-001
Category: E
Question: 共享 PostgreSQL Cluster 如何实现 Logical Ownership？如果 Knowledge Service 需要读取 Domain 的 Matter 权限，能否直接 JOIN 私有表？
Attack Intent: 攻击 shared DB 与服务边界。
Target Component: Service Data Ownership
Assumption Being Attacked: 共享集群等于共享表。
Severity: P0
Expected Answer Depth: schema/table owner/API boundary。
Evidence Required: schema registry and access test。
Kill Condition: 跨服务任意 JOIN 或直接写他人表。
Blue Answer: V1 可共享 Cluster，但按 schema/table owner、DB role、migration owner 和 API/event/reference 边界隔离；Knowledge 通过授权查询/Reference/Snapshot 获取必要范围，不直接 JOIN/写 Domain 私有表。
State Boundary: physical cluster vs logical ownership。
Problem: coupling/hidden writes；Decision=KEEP_LOGICAL_OWNERSHIP_FIRST。
Ownership: each service owner; Data Governance audits。
State Transition: request→authorized read/reference；only owner mutates。
Failure: service/API unavailable；Retry/cached scoped snapshot；Recovery no private table write。
Security: DB roles/row scope/secret separation；Observability: cross-boundary call trace。
Alternative: database-per-service；Tradeoff: stronger isolation, higher ops/migration cost。
Test / Benchmark: unauthorized SQL/write and contract tests。
Evidence: ADR-0010/data docs；Remaining Gap: GAP-V2-018。
Red Critique: shared physical DB can work only with enforced owner。
Blue Revision: database-per-service remains conditional。
Final Red Assessment: Target survives pending enforcement。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q055
Gap Candidate Refs: GAP-V2-018

## Q056

Round ID: ROUND-001
Category: E
Question: Redis 保存的是 Cache、Lease、Rate Limit 还是 Session？如果 Redis 清空，哪些功能降级，哪些 Canonical State 必须不受影响？
Attack Intent: 攻击 Redis 多用途和事实混淆。
Target Component: Redis
Assumption Being Attacked: Redis 可做通用状态库。
Severity: P1
Expected Answer Depth: role-specific recovery。
Evidence Required: cache/lease loss test。
Kill Condition: Redis 丢失会丢 Matter/Finding/Approval 或无法恢复。
Blue Answer: Redis 只能按明确角色使用：cache/lease/rate limit/ephemeral session candidate；Domain/Review/Effect/Plan facts 不依赖 Redis 唯一保存。清空后可重建 cache，lease 通过 DB/job state 对账，短期拒绝重复副作用。
State Boundary: ephemeral vs canonical。
Problem: hidden state；Decision=ROLE_LIMIT_REDIS。
Ownership: relevant service; Domain remains PostgreSQL。
State Transition: cache miss/reacquire lease/requeue。
Failure: eviction/partition；Retry with bounded backoff；Recovery from canonical/job store。
Security: no unrestricted secrets/PII in cache；Observability: hit/miss/lease takeover。
Alternative: PostgreSQL advisory locks/in-memory；Tradeoff: lower infra but weaker scale/TTL。
Test / Benchmark: Redis loss and duplicate job test。
Evidence: architecture/data docs；Remaining Gap: GAP-V2-013, GAP-V2-017。
Red Critique: Redis role未被预设为必需。
Blue Revision: provider replaceable。
Final Red Assessment: Conditional survive。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q056
Gap Candidate Refs: GAP-V2-013, GAP-V2-017

## Q057

Round ID: ROUND-001
Category: E
Question: Object Storage 中原始文档被覆盖、删除或不可用时，DocumentVersion 和 Evidence Citation 如何保持可审计？
Attack Intent: 攻击源数据可追溯性。
Target Component: Object Storage / Document
Assumption Being Attacked: 文件路径足够证明来源。
Severity: P0
Expected Answer Depth: immutable object/version/hash/retention。
Evidence Required: object versioning/restore evidence。
Kill Condition: Citation 只指向可变 URL，无法恢复原文。
Blue Answer: DocumentVersion 必须记录 content hash、object version/URI、ingestion/parser version、source span 和权限；对象不可变或有保留/备份策略。对象缺失时标记 Evidence unavailable，不伪造引用，等待恢复或人工复核。
State Boundary: object source vs accepted Evidence/Citation。
Problem: irreproducible evidence；Decision=KEEP_SOURCE_PROVENANCE。
Ownership: Domain owns DocumentVersion metadata; object provider stores bytes。
State Transition: upload→immutable version→parse/index→citation。
Failure: object loss/corruption；Retry restore/verify hash；Recovery backup or block Finding。
Idempotency: content hash/document version；Security: tenant isolation/retention。
Observability: hash, object version, restore and citation checks。
Alternative: mutable filesystem；Tradeoff: simple but non-auditable。
Test / Benchmark: delete/corrupt/restore citation test。
Evidence: domain/knowledge/security docs；Remaining Gap: GAP-V2-009, GAP-V2-015。
Red Critique: 证据链完整，备份策略仍 Target。
Blue Revision: Object Store not business truth。
Final Red Assessment: Target survives conditionally。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q057
Gap Candidate Refs: GAP-V2-009, GAP-V2-015

## Q058

Round ID: ROUND-001
Category: E
Question: 法律规则、StatuteVersion、LegalElement 和 ApplicableLaw 如果作为 Projection，更新法条后如何避免旧 Finding 仍使用过时适用法？
Attack Intent: 攻击法律版本和派生结论。
Target Component: Legal Applicability
Assumption Being Attacked: 法条文本检索即可解决版本。
Severity: P0
Expected Answer Depth: effective dates/dependency/stale/review。
Evidence Required: statute version and applicability test。
Kill Condition: 没有生效日期、jurisdiction、依赖和 stale 传播。
Blue Answer: 规则引用必须绑定 StatuteVersion、jurisdiction/effective time/source；ApplicableLaw/Finding 记录依赖版本，规则更新标记受影响结论 stale/review_required，必要时新 Run，不静默替换历史结论。
State Boundary: legal knowledge projection vs accepted Finding。
Problem: temporal legal error；Decision=KEEP_VERSIONED_LEGAL_DEPENDENCY。
Ownership: Knowledge maintains source projection; Domain owns finding version。
State Transition: rule update→affected→stale/re-evaluate→review。
Failure: incomplete impact scan；Retry bounded dependency scan；Recovery prior version + review。
Security: source/license/scope；Observability: rule version and dependent findings。
Alternative: current statute lookup only；Tradeoff: simpler but historically unsafe。
Test / Benchmark: temporal/jurisdiction cases。
Evidence: domain/eval docs；Remaining Gap: GAP-V2-007, GAP-V2-020。
Red Critique: 关键法律语义不能隐藏在 Prompt。
Blue Revision: 先保留为 Candidate/Derived View。
Final Red Assessment: Target conditionally survives。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q058
Gap Candidate Refs: GAP-V2-007, GAP-V2-020

## Q059

Round ID: ROUND-001
Category: E
Question: HumanDecision 改变 Finding 后，旧 Agent Run、Memory、Citation、WorkProduct 和缓存如何处理？
Attack Intent: 攻击人工反馈后的依赖传播。
Target Component: Domain/Runtime/Memory
Assumption Being Attacked: 人工改一行结论即可结束。
Severity: P0
Expected Answer Depth: version/stale/review/rebuild。
Evidence Required: human decision propagation trace。
Kill Condition: 旧上下文或 WorkProduct 继续对外发布。
Blue Answer: HumanDecision 创建新 Domain version 并记录 reason/actor；依赖 Finding/WorkProduct/Plan/Memory projection 标记 stale/review/rebuild，旧版本保留审计但不作为当前发布依据。
State Boundary: HumanDecision canonical vs runtime/memory projections。
Problem: feedback inconsistency；Decision=KEEP_DEPENDENCY_PROPAGATION。
Ownership: Domain Owner commits; Runtime/Memory reconcile。
State Transition: decision→dependent stale→recompute/review/publish。
Failure: propagation crash；Retry idempotent dependency scan；Recovery from version graph。
Security: reviewer permission and publication gate；Observability: decision lineage。
Alternative: overwrite current text；Tradeoff: simple but corrupts downstream。
Test / Benchmark: human revision fault test。
Evidence: domain lifecycle/data docs；Remaining Gap: GAP-V2-007, GAP-V2-013。
Red Critique: 不能让 Memory 偷偷保留旧事实。
Blue Revision: Memory receives only approved projection according to policy。
Final Red Assessment: Target survives; implementation gap。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q059
Gap Candidate Refs: GAP-V2-007, GAP-V2-013

## Q060

Round ID: ROUND-001
Category: E
Question: 如果采用 Event Sourcing 能完整记录变化，为什么当前不默认采用？PostgreSQL 当前版本加审计在哪些条件下不够？
Attack Intent: Kill Event Sourcing。
Target Component: Persistence
Assumption Being Attacked: 高风险领域天然需要 Event Sourcing。
Severity: P1
Expected Answer Depth: necessity/reversal criteria。
Evidence Required: audit/replay/scale requirement。
Kill Condition: Blue 只说“业界常用”或无法说明 PostgreSQL 方案缺什么。
Blue Answer: 当前版本+不可变版本+依赖+审计已能满足目标 Contract，不默认引入 Event Sourcing 的额外 replay/schema/ops 成本；只有需要完整事件重放、监管不可变日志、复杂 temporal query 或现方案无法审计时重开 ADR。
State Boundary: audit history vs event-sourced business truth。
Problem: premature persistence complexity；Decision=DEFER_EVENT_SOURCING。
Ownership: Data/Domain Owner；State Transition: versioned current/previous/audit。
Failure: audit corruption；Retry/recovery from backup; idempotency event/version key。
Security: immutable audit access；Observability: mutation history。
Alternative: PostgreSQL versions + audit/outbox；Tradeoff: lower ops complexity。
Test / Benchmark: audit/replay requirement spike。
Evidence: ADR-0008/0010；Remaining Gap: GAP-V2-018。
Red Critique: 能接受未来逆转，而不是教条删除。
Blue Revision: Event Sourcing remains Future/conditional。
Final Red Assessment: Defer survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q060
Gap Candidate Refs: GAP-V2-018

## Q061

Round ID: ROUND-001
Category: F
Question: Tool Catalog 中“可见工具”“可授权工具”“可执行工具”分别是什么？为什么 Agent 看到 Tool Schema 不代表可以调用？
Attack Intent: 攻击 Tool discovery 与 permission 混淆。
Target Component: Tool Runtime / Security
Assumption Being Attacked: Schema visibility equals authority。
Severity: P0
Expected Answer Depth: candidate vs authorized vs executable sets。
Evidence Required: tool onboarding/grant/selection trace。
Kill Condition: Model 仅凭工具描述即可执行副作用。
Blue Answer: Catalog visibility 是描述；Authorized Candidate Set 由安装、Grant、Tenant/Workspace/User/Agent/Task/Connection/epoch 交集形成；Executable Set 还需版本、health、quota、compatibility、approval 和 effect preflight。
State Boundary: Tool metadata vs authorization/effect。
Problem: privilege escalation；Decision=KEEP_TWO_SET_POLICY。
Ownership: Security owns authorization; Tool owns execution。
State Transition: visible→authorized candidate→executable→attempt/receipt。
Failure: revoked/health/compat mismatch；Retry recalculate or refuse；Recovery no side effect unless receipt。
Security: deny-by-default, secret scoping；Observability: decision lineage。
Alternative: tools all available；Tradeoff: simple but unsafe。
Test / Benchmark: revoked permission, incompatible version, hidden secret tests。
Evidence: security/tool docs；Remaining Gap: GAP-V2-015, GAP-V2-016。
Red Critique: 权限和可执行性分离正确。
Blue Revision: Tool selection must consume Security decision, not prompt only。
Final Red Assessment: Target survives pending trace。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q061
Gap Candidate Refs: GAP-V2-015, GAP-V2-016

## Q062

Round ID: ROUND-001
Category: F
Question: Tool Calling Strategy 解决的是调用时机、工具选择、参数生成、失败重试、Observation 回注还是权限？如何避免把一个名字当成完整能力？
Attack Intent: 恢复并审计个人/历史贡献边界，同时攻击概念模糊。
Target Component: Tool Calling Strategy
Assumption Being Attacked: Tool Strategy 是一个单一模块。
Severity: P1
Expected Answer Depth: historical fact boundary and target contract。
Evidence Required: user confirmation, code/task artifact, trace。
Kill Condition: Blue 把用户参与自动扩展为全部 Tool Runtime。
Blue Answer: 历史上用户确认参与 Tool Calling Strategy，但具体改动仍需恢复；Target 将 selection、schema/argument validation、permission/approval、execution、observation、retry/reconcile 拆开，个人贡献不能据此扩张。
State Boundary: Historical USER_CONFIRMED broad / detail UNKNOWN；Target contract detailed。
Problem: ownership inflation and unsafe coupling；Decision=FACT_RECOVERY + CONTRACT_SPLIT。
Ownership: Facts Owner records personal scope; Security/Tool owners target contracts。
State Transition: candidate action→validated/prepared→approved→attempt→receipt/unknown。
Failure: wrong tool/args/timeout；Retry bounded and idempotent；Recovery reconcile unknown effect。
Security: selection cannot grant permission；Observability: strategy decision/trace。
Alternative: model direct tool call；Tradeoff: simpler but no governance。
Test / Benchmark: tool selection/argument/effect fault matrix。
Evidence: facts/team-and-ownership.md；Remaining Gap: GAP-V2-024。
Red Critique: 没有虚构个人文件或 API。
Blue Revision: 个人贡献留在 Fact Recovery Queue。
Final Red Assessment: Architecture/Fact boundary survives。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q062
Gap Candidate Refs: GAP-V2-024

## Q063

Round ID: ROUND-001
Category: F
Question: Tool 参数由模型生成时，Schema Validation 通过是否足以执行？参数中包含目标、资源、权限和不可逆副作用时还需什么？
Attack Intent: 攻击结构合法与业务安全混淆。
Target Component: Tool Effect
Assumption Being Attacked: JSON Schema 是全部安全控制。
Severity: P0
Expected Answer Depth: semantic validation, approval, effect class。
Evidence Required: prepared action/preflight test。
Kill Condition: schema-valid malicious destination can execute。
Blue Answer: Schema 只验证形状；还需 semantic/domain validation、resource scope、secret/network policy、effect classification、approval、budget、idempotency 和 execution-time preflight。
State Boundary: Proposal/PreparedAction vs EffectReceipt。
Problem: unsafe valid args；Decision=KEEP_EFFECT_GATE。
Ownership: Tool/Security/Domain as relevant；State Transition: generated→validated→prepared→approved→executed/blocked。
Failure: destination/permission changed；Retry re-preflight；Recovery block or reconcile unknown。
Security: least privilege and untrusted content isolation；Observability: parameter hash/redaction/decision。
Alternative: schema-only; Tradeoff: fast but unsafe。
Test / Benchmark: injection, revoked grant, wrong resource, secret leakage。
Evidence: security/tool docs；Remaining Gap: GAP-V2-015, GAP-V2-016。
Red Critique: 形状和权威边界分得正确。
Blue Revision: Schema never authorizes effect。
Final Red Assessment: Target survives conditionally。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q063
Gap Candidate Refs: GAP-V2-015, GAP-V2-016

## Q064

Round ID: ROUND-001
Category: F
Question: Tool 调用超时但外部系统可能已成功时，为什么不能立即 retry？需要保存哪些 Receipt、Provider Operation ID 和 Unknown Effect？
Attack Intent: 攻击不可逆副作用的重复执行。
Target Component: Effect Reconciliation
Assumption Being Attacked: timeout equals failure。
Severity: P0
Expected Answer Depth: unknown outcome/reconcile/idempotency。
Evidence Required: effect fault test and provider API behavior。
Kill Condition: timeout always blind retry or marks failed without reconciliation。
Blue Answer: Timeout 进入 UNKNOWN_EFFECT；保存 ToolAttempt、idempotency key、request hash、provider operation ID（若有）、响应/超时和 policy。优先查询 provider 状态或人工对账；只有确定未执行或 provider 幂等时 retry。
State Boundary: EffectReceipt/Unknown Effect vs Domain WorkProduct。
Problem: duplicate irreversible action；Decision=KEEP_RECONCILIATION。
Ownership: Tool Sandbox owns effect receipt; Domain/Runtime reference it。
State Transition: prepared→attempt→success/failure/unknown→reconcile→closed/retry。
Failure: provider unavailable；Retry query with backoff；Recovery manual reconciliation/compensation only if supported。
Security: effect scope and secret audit；Observability: operation/correlation trace。
Alternative: blind retry；Tradeoff: simpler but dangerous。
Test / Benchmark: timeout-after-commit and duplicate side-effect test。
Evidence: ADR-0010/security docs；Remaining Gap: GAP-V2-016, GAP-V2-017。
Red Critique: 这是 P0，不能靠模型判断。
Blue Revision: Tool Runtime target retains receipt/reconcile even if adapter is externalized。
Final Red Assessment: Contract survives; implementation unproven。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q064
Gap Candidate Refs: GAP-V2-016, GAP-V2-017

## Q065

Round ID: ROUND-001
Category: F
Question: MCP/API/CLI 的 ToolVersion 发生变化时，旧 Plan 或 PreparedAction 能否继续执行？
Attack Intent: 攻击 Tool Contract/版本漂移。
Target Component: Tool Versioning
Assumption Being Attacked: 名称相同即可兼容。
Severity: P1
Expected Answer Depth: version compatibility and approval binding。
Evidence Required: version contract and compatibility tests。
Kill Condition: 旧参数直接发送到新 Tool，或版本变化不触发审批。
Blue Answer: PreparedAction 绑定 Tool Identity/Version、schema hash、parameter hash 和 security epoch；不兼容则拒绝/重新准备，兼容升级也按 policy 重新 preflight；旧 receipt 可回查但不伪造新版本成功。
State Boundary: Tool metadata/version vs effect receipt。
Problem: version drift；Decision=KEEP_VERSION_BINDING。
Ownership: Tool provider contract; Security approves execution。
State Transition: plan tool ref→compat check→prepared/invalidated。
Failure: provider update；Retry replan/reprepare；Recovery old version or block。
Security: approval bound to version；Observability: version/hash。
Alternative: latest alias；Tradeoff: easy but unsafe/reproducibility loss。
Test / Benchmark: incompatible schema and rollback。
Evidence: tool/security docs；Remaining Gap: GAP-V2-016。
Red Critique: 版本绑定避免了隐式升级。
Blue Revision: Tool alias 不能绕过 version policy。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q065
Gap Candidate Refs: GAP-V2-016

## Q066

Round ID: ROUND-001
Category: F
Question: Sandbox 为什么必须是独立安全/资源边界？哪些 Tool 只需要薄 Adapter，哪些操作必须隔离进程或服务？
Attack Intent: 攻击 Tool Runtime 一刀切服务化或一刀切内嵌。
Target Component: Tool Sandbox
Assumption Being Attacked: 所有 Tool 风险相同。
Severity: P0
Expected Answer Depth: effect/resource classification。
Evidence Required: tool effect inventory and boundary tests。
Kill Condition: arbitrary filesystem/network/secret access occurs in Agent process。
Blue Answer: 只读、无副作用、受控 API 可用薄 Adapter；Python/CLI、filesystem、network、secret、不可逆外部 effect 需要独立 process/resource/security boundary，最小权限和 receipt/reconcile。
State Boundary: adapter proposal vs sandbox effect。
Problem: code execution/data exfiltration；Decision=KEEP_SANDBOX_BOUNDARY。
Ownership: Sandbox Service owns execution isolation; Security policy owner controls grants。
State Transition: prepared→sandbox admitted→running→receipt/blocked。
Failure: escape/timeout/resource exhaustion；Retry only safe/idempotent；Recovery kill/clean/reconcile。
Security: network allowlist, secret scope, filesystem boundary；Observability: syscall/network/effect trace。
Alternative: in-process adapter；Tradeoff: lower latency but high blast radius。
Test / Benchmark: sandbox escape, egress, secret leakage, resource limits。
Evidence: security/service docs；Remaining Gap: GAP-V2-015, GAP-V2-017。
Red Critique: 合并回 Agent 不能只讲网络跳数。
Blue Revision: Tool adapters and Sandbox boundary separated。
Final Red Assessment: Target survives if tested。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q066
Gap Candidate Refs: GAP-V2-015, GAP-V2-017

## Q067

Round ID: ROUND-001
Category: F
Question: Prompt Injection 出现在法院 PDF、Memory、检索结果或 Tool Observation 中时，哪一层把它标成 Untrusted Content？
Attack Intent: 攻击信任边界和 Observation 回注。
Target Component: Security / Agent Context
Assumption Being Attacked: Model 能自行识别不可信指令。
Severity: P0
Expected Answer Depth: taint/trust labels/policy boundary。
Evidence Required: injection + tool fault test。
Kill Condition: 文档内容可改变 Tool permission、destination 或 approval。
Blue Answer: Source Document、Memory Candidate、Retrieval Candidate 和 Observation 默认 Untrusted；Context assembly 保留 provenance/taint，Security/Policy 层决定是否可作为事实/行动依据，模型文本不能授予权限。
State Boundary: content vs instruction/policy。
Problem: indirect prompt injection；Decision=KEEP_TAINT_BOUNDARY。
Ownership: Security owns trust policy; Knowledge/Tool carry provenance。
State Transition: untrusted input→analyzed candidate→validated proposal only。
Failure: taint dropped；Retry reject/review；Recovery invalidate output/receipt。
Security: least privilege, approval, no secret echo；Observability: taint/flow trace。
Alternative: prompt disclaimer；Tradeoff: low engineering cost but weak。
Test / Benchmark: prompt injection + tool, secret leakage, malicious PDF。
Evidence: security architecture；Remaining Gap: GAP-V2-015。
Red Critique: 只能靠 Prompt 的方案被杀死。
Blue Revision: Trust label becomes contract field。
Final Red Assessment: Target survives pending test。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q067
Gap Candidate Refs: GAP-V2-015

## Q068

Round ID: ROUND-001
Category: F
Question: 外部 Tool 成功后 Domain 状态提交失败，或 Domain 已写成功但 Effect Receipt 丢失，恢复时谁负责对账？
Attack Intent: 攻击 Tool/Domain 分布式事务。
Target Component: Tool/Domain Recovery
Assumption Being Attacked: Tool 成功和业务提交可以原子化。
Severity: P0
Expected Answer Depth: local transaction + receipt + reconciliation。
Evidence Required: partial failure matrix。
Kill Condition: 任何一侧成功都被忽略，导致重复或幻觉完成。
Blue Answer: 外部 Effect 不用 2PC 默认解决；Tool 保存 receipt/provider operation ID，Domain 保存 pending/accepted effect reference；Reconciler 查询并对账，未知状态阻断不可逆重试；Domain 不能因 checkpoint 完成而跳过 Receipt。
State Boundary: external world effect vs Domain effect acceptance。
Problem: distributed partial failure；Decision=KEEP_RECEIPT_RECONCILIATION。
Ownership: Tool owns effect truth/receipt; Domain owns business acceptance。
State Transition: pending→external unknown/success→reconciled→domain accepted/review。
Failure: network/DB/checkpoint partial；Retry queries/reconcile; Recovery manual if unknown。
Security: effect approval recheck；Observability: operation/correlation/receipt。
Alternative: Saga/2PC by default；Tradeoff: frameworks add cost and not all providers support。
Test / Benchmark: both-order fault injection。
Evidence: data/service ADR；Remaining Gap: GAP-V2-016, GAP-V2-017。
Red Critique: 恢复主权清楚，缺实际 receipt。
Blue Revision: 先实现 Contract/trace，再决定 framework。
Final Red Assessment: Target survives conditionally。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q068
Gap Candidate Refs: GAP-V2-016, GAP-V2-017

## Q069

Round ID: ROUND-001
Category: F
Question: Tool Runtime 如果已经包含 MCP、API、CLI、Sandbox、Network Policy、Secrets、Approval、Idempotency 和 Reconciliation，为什么不把它简单放回 Agent Service？
Attack Intent: 反向攻击伪简单合并。
Target Component: Tool Sandbox Service
Assumption Being Attacked: 少一个服务必然更好。
Severity: P1
Expected Answer Depth: boundary cost comparison。
Evidence Required: security/resource/failure evidence。
Kill Condition: 合并后仍有同等安全、资源和恢复隔离且网络成本占主导。
Blue Answer: 普通 adapters 可以回到 Runtime；Sandbox/effect/secret/network 仍需独立边界，除非证明合并后的隔离、资源、故障、权限、审计和恢复不劣且网络开销显著。服务边界不是功能清单而是风险边界。
State Boundary: Runtime control vs external effect。
Problem: false simplicity；Decision=KEEP_OR_MERGE_BY_EVIDENCE。
Ownership: Tool Service effect; Runtime plan。
State Transition: prepared action→execution receipt。
Failure: shared crash/security blast radius；Retry/recovery as above。
Security: process/network/secret boundary；Observability: distributed effect trace。
Alternative: in-process library；Tradeoff: lower latency, larger blast radius。
Test / Benchmark: isolation and latency comparison。
Evidence: ADR-0010；Remaining Gap: GAP-V2-018。
Red Critique: 需要实际 resource profile 证明拆分。
Blue Revision: service count remains open within Microservice constraint。
Final Red Assessment: Gate survives; five services not final。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q069
Gap Candidate Refs: GAP-V2-018

## Q070

Round ID: ROUND-001
Category: F
Question: Secret 由 Tool 需要时注入，模型、Prompt、Trace、Memory、Error Log 和 Sandbox 是否可能看到？最小 Secret Access Trace 是什么？
Attack Intent: 攻击 Secret 传播。
Target Component: Security / Tool
Assumption Being Attacked: secret manager 存在等于 secret 安全。
Severity: P0
Expected Answer Depth: secret scoping/redaction/access audit。
Evidence Required: secret leakage test and access trace。
Kill Condition: secret appears in model context/log/memory or broad process env。
Blue Answer: Secret 只在执行前按 Tool/Connection/Task scope 短时注入 Sandbox/adapter，模型和 Domain 不得读取；日志只记录 secret reference/hash/redaction，访问记录 actor/tool/version/connection/epoch/result。
State Boundary: secret control fact vs tool receipt。
Problem: exfiltration/overbroad access；Decision=KEEP_SECRET_SCOPE。
Ownership: Security/Secret Manager；Tool consumes least privilege。
State Transition: authorized→leased→used/revoked→destroyed/audited。
Failure: provider/log leak；Retry rotate/revoke and block；Recovery invalidate credentials and audit。
Security: no egress/default deny, local/offline profile；Observability: access trace without value。
Alternative: process-wide env；Tradeoff: easy but broad blast radius。
Test / Benchmark: secret leakage, stale credential, revoked permission。
Evidence: security docs；Remaining Gap: GAP-V2-015。
Red Critique: 设计清楚但没有 E2E 证据。
Blue Revision: Secret access is P0 Security Gate。
Final Red Assessment: Target survives pending evidence。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q070
Gap Candidate Refs: GAP-V2-015

## Q071

Round ID: ROUND-001
Category: G
Question: RabbitMQ/Queue Job 如果重复投递、Consumer 超时、Worker 重启或 ACK 丢失，Job Identity、Attempt、Lease、Retry 和 Dead Letter 如何定义？
Attack Intent: 攻击异步语义。
Target Component: Queue / Worker
Assumption Being Attacked: Queue delivery automatically ensures exactly once。
Severity: P0
Expected Answer Depth: at-least-once/idempotency/recovery。
Evidence Required: consumer duplicate/fault test and actual history。
Kill Condition: 以 exactly-once 口号掩盖重复执行。
Blue Answer: 默认按 at-least-once 设计；Job Identity/Idempotency Key、Attempt、Lease、Timeout、Cancellation、Retry/Backoff、DLQ 和 Reconciliation 由 Worker/Owner 处理，Queue 不是业务 Truth。
State Boundary: queue delivery vs Domain/Effect state。
Problem: duplicate/poison job；Decision=KEEP_EXPLICIT_JOB_SEMANTICS。
Ownership: job type owner; queue provider only delivers。
State Transition: submitted→leased→running→succeeded/failed/retry/DLQ/cancelled。
Failure: crash/ack loss；Retry after state/idempotency check；Recovery reconcile receipt/domain state。
Security: tenant/job scope and secret separation；Observability: job/attempt/lease trace。
Alternative: synchronous HTTP；Tradeoff: simpler but poor long-run/backpressure。
Test / Benchmark: duplicate side effect and worker takeover。
Evidence: ADR-0010；Remaining Gap: GAP-V2-017。
Red Critique: 没有把 RabbitMQ 历史使用写成事实。
Blue Revision: provider choice remains open。
Final Red Assessment: Target semantics survive。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q071
Gap Candidate Refs: GAP-V2-017, GAP-V2-024

## Q072

Round ID: ROUND-001
Category: G
Question: Job 失败后重试几次？哪些错误可重试，哪些必须立即 Block/Review？模型超时、权限撤销、Schema 错误和 Unknown Effect 能否共用策略？
Attack Intent: 攻击统一 Retry。
Target Component: Failure Policy
Assumption Being Attacked: 所有异常都 exponential backoff。
Severity: P0
Expected Answer Depth: error taxonomy and terminal state。
Evidence Required: failure taxonomy and retry policy tests。
Kill Condition: permission/schema/unknown effect 被盲目重试。
Blue Answer: Retry 按错误类型和副作用分类：transient provider/network 可有限重试；schema/permission/approval stale 进入 refused/review；unknown effect 先 reconcile；budget/validation/domain conflict 不直接重试。
State Boundary: runtime failure vs business/effect terminal state。
Ownership: component owner classifies; Security/Domain can veto。
State Transition: failed→retryable retry or blocked/refused/reconcile。
Failure: misclassification；Retry policy versioned and capped；Recovery manual/escalation when needed。
Security: revoked permission is terminal until new grant；Observability: reason and attempt。
Alternative: generic retry middleware；Tradeoff: less code but unsafe。
Test / Benchmark: error matrix/fault injection。
Evidence: service/data/security docs；Remaining Gap: GAP-V2-016, GAP-V2-017。
Red Critique: Retry is not one property。
Blue Revision: error classes part of contract。
Final Red Assessment: Target survives pending tests。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q072
Gap Candidate Refs: GAP-V2-016, GAP-V2-017

## Q073

Round ID: ROUND-001
Category: G
Question: Agent Runtime 重新启动后，如何确认已完成的 Domain Commit、Tool Effect、Knowledge Job 和 Human Approval，不重复执行？
Attack Intent: 攻击恢复锚点。
Target Component: Recovery
Assumption Being Attacked: Checkpoint resume position alone is sufficient。
Severity: P0
Expected Answer Depth: reconciliation order and receipts。
Evidence Required: restart recovery trace。
Kill Condition: 直接从最后节点重新执行所有副作用。
Blue Answer: 恢复先读取 Domain versions/Run/Plan、EffectReceipt/provider operation、Job idempotency、Approval/epoch，再与 checkpoint 对账；已完成 Effect 不重做，未提交 Domain 不假装成功，Unknown 进入 reconcile。
State Boundary: Domain/Effect/Job/Runtime control separately reconciled。
Problem: duplicate or phantom completion；Decision=KEEP_RECOVERY_RECONCILIATION。
Ownership: each state owner supplies evidence; Runtime coordinates。
State Transition: restart→snapshot/reconcile→resume/blocked/compensate。
Failure: partial stores unavailable；Retry reads/backoff; Recovery safe stop/manual。
Security: resume rechecks permissions/epoch；Observability: recovery decision。
Alternative: checkpoint-only；Tradeoff: simpler but unsafe。
Test / Benchmark: crash at every boundary。
Evidence: architecture/data ADR；Remaining Gap: GAP-V2-013, GAP-V2-017。
Red Critique: 这是一条必须实现的恢复链。
Blue Revision: 设为 Critical Gate。
Final Red Assessment: Target survives, Current P0。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q073
Gap Candidate Refs: GAP-V2-013, GAP-V2-017

## Q074

Round ID: ROUND-001
Category: G
Question: 新 Evidence 提交后触发 Agent Run，如果消息重复或 stale 扫描重复，如何保证只创建一个逻辑重分析 Run？
Attack Intent: 攻击事件触发幂等。
Target Component: Stale Trigger
Assumption Being Attacked: Queue duplicate is harmless。
Severity: P1
Expected Answer Depth: trigger fingerprint and domain generation。
Evidence Required: duplicate trigger test。
Kill Condition: 每次消息创建新 Run，造成成本和状态膨胀。
Blue Answer: Trigger 绑定 Matter、EvidenceVersion、affected dependency set、policy/profile version 和 trigger fingerprint；Domain/Runtime 用 unique idempotency key/CAS 合并重复请求，必要时保留不同 policy 的独立 Run。
State Boundary: event delivery vs logical Run identity。
Ownership: Domain lifecycle identifies affected set; Runtime creates run。
State Transition: evidence commit→affected/stale→dedup trigger→run。
Failure: scan race；Retry CAS/reconcile；Recovery inspect existing Run and generation。
Security: trigger uses current permission；Observability: trigger fingerprint and reuse。
Alternative: fire-and-forget every event；Tradeoff: simple but noisy/expensive。
Test / Benchmark: duplicate/out-of-order evidence events。
Evidence: domain lifecycle/agent docs；Remaining Gap: GAP-V2-007, GAP-V2-017。
Red Critique: 需要定义“不同 policy”边界，不能所有 trigger 合并。
Blue Revision: idempotency key includes policy/profile version。
Final Red Assessment: Target conditionally survives。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q074
Gap Candidate Refs: GAP-V2-007, GAP-V2-017

## Q075

Round ID: ROUND-001
Category: G
Question: 并行 Agent 产生互相冲突的 ConflictProposal 时，系统应选择一个、合并、创建 Conflict，还是交给 Human Review？
Attack Intent: 攻击自动合并法律冲突。
Target Component: Proposal Conflict
Assumption Being Attacked: Majority vote is truth。
Severity: P0
Expected Answer Depth: conflict semantics and review gate。
Evidence Required: conflict proposal/review example。
Kill Condition: 模型多数或最后写入者直接形成 ConflictVersion。
Blue Answer: 保留各 Proposal 和 provenance；Domain Owner 按 schema/evidence/permission/version 判断，无法确定时创建 Conflict/Review Required 候选，不自动把多数票变为正式法律事实。
State Boundary: ConflictProposal vs accepted ConflictVersion。
Ownership: Domain Owner/Human Reviewer；Runtime only coordinates。
State Transition: proposals→comparison→accepted/rejected/conflict review。
Failure: missing provenance；Retry provider or abstain；Recovery preserve alternatives。
Security: same Matter/tenant scope；Observability: proposal lineage and reviewer decision。
Alternative: highest score；Tradeoff: fast but opaque/unsafe。
Test / Benchmark: conflict precision/review acceptance。
Evidence: domain model/eval docs；Remaining Gap: GAP-V2-003, GAP-V2-020。
Red Critique: 法律冲突不能被 aggregation 隐藏。
Blue Revision: conflict remains candidate until review。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q075
Gap Candidate Refs: GAP-V2-003, GAP-V2-020

## Q076

Round ID: ROUND-001
Category: G
Question: Cancellation 发生在模型调用、检索、Sandbox 执行或外部 Effect 之后时，能否统一取消？已经发出的副作用怎么办？
Attack Intent: 攻击取消语义。
Target Component: Cancellation
Assumption Being Attacked: cancel flag stops everything。
Severity: P0
Expected Answer Depth: cooperative cancel/effect boundary/reconcile。
Evidence Required: cancellation fault matrix。
Kill Condition: Cancel 后仍宣称没有副作用，或直接强杀导致状态未知。
Blue Answer: Cancellation 按阶段处理：未开始任务可取消；模型/检索协作取消；Sandbox 可 terminate；已提交外部 Effect 不能假装取消，进入 receipt/reconcile/compensation（若 Provider 支持），Domain 保留状态。
State Boundary: control cancellation vs external world effect。
Ownership: Runtime controls; Tool reconciles external effect; Domain records outcome。
State Transition: running→cancel requested→cancelled/unknown/effect settled。
Failure: cancellation race；Retry status query; Recovery manual/reconcile。
Security: cancel permission and audit；Observability: cancellation point and effect status。
Alternative: hard kill process；Tradeoff: quick but unsafe unknowns。
Test / Benchmark: cancel at each side-effect phase。
Evidence: service/data docs；Remaining Gap: GAP-V2-016, GAP-V2-017。
Red Critique: “可取消”需要被分段而非总开关。
Blue Revision: cancellation is typed terminal/unknown state。
Final Red Assessment: Target survives pending fault test。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q076
Gap Candidate Refs: GAP-V2-016, GAP-V2-017

## Q077

Round ID: ROUND-001
Category: G
Question: Worker 拿到 Lease 后挂掉，另一个 Worker 接管前如何确认原 Worker 没有已经提交 Domain Fact 或 Effect？Lease 是锁还是过期租约？
Attack Intent: 攻击 Worker 接管和重复提交。
Target Component: Worker Lease
Assumption Being Attacked: Lease holder is permanent owner。
Severity: P0
Expected Answer Depth: lease expiry, CAS, receipt。
Evidence Required: lease parameter and takeover fault test。
Kill Condition: 新 Worker 仅按 lease timeout 重做副作用。
Blue Answer: Lease 是有期限的工作租约，不是事实所有权；接管先查 Domain generation、Attempt、idempotency record、EffectReceipt 和 provider operation status，再决定 resume/reconcile/block。
State Boundary: lease control vs canonical/effect state。
Ownership: worker scheduler controls lease; Domain/Tool owners decide completion。
State Transition: leased→expired→inspect→takeover/reconcile/block。
Failure: clock skew/partition；Retry with fencing token；Recovery safe takeover or manual。
Security: worker identity and scope；Observability: lease/fencing/attempt。
Alternative: process ownership/no lease；Tradeoff: simpler but no takeover safety。
Test / Benchmark: worker crash/clock/partition。
Evidence: architecture/data docs；Remaining Gap: GAP-V2-017。
Red Critique: fencing token尚需明确。
Blue Revision: Lease parameters are Gap, not historical fact。
Final Red Assessment: Target survives conditionally。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q077
Gap Candidate Refs: GAP-V2-017

## Q078

Round ID: ROUND-001
Category: G
Question: PostgreSQL 已提交业务事实但 Event Publish 失败时，为什么不能在事务内直接调用 MQ 来获得原子性？
Attack Intent: 攻击分布式事务误区。
Target Component: Outbox / Messaging
Assumption Being Attacked: in-transaction network call is atomic。
Severity: P1
Expected Answer Depth: local commit/outbox/retry。
Evidence Required: dual-write failure matrix。
Kill Condition: 直接调用 MQ 被描述成 atomic commit。
Blue Answer: 数据库事务不能把外部 MQ publish 自动纳入原子提交；默认用本地事务写事实和 Outbox，再异步发布；Consumer 幂等，Publisher 可重试，状态由 Outbox/Receipt 对账。
State Boundary: business commit vs message delivery。
Ownership: Domain writes outbox; infra delivers。
State Transition: domain+outbox committed→publish attempts→delivered/retry/dead。
Failure: publish fail/duplicate；Retry safe resend；Recovery scan outbox。
Security: message scope and tenant data；Observability: event IDs。
Alternative: 2PC；Tradeoff: heavy/unavailable with many providers。
Test / Benchmark: transaction/publish faults。
Evidence: ADR-0010；Remaining Gap: GAP-V2-013, GAP-V2-017。
Red Critique: 机制清晰，是否所有消息都需要 Outbox 仍应区分。
Blue Revision: 只对跨边界关键事件采用。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q078
Gap Candidate Refs: GAP-V2-013, GAP-V2-017

## Q079

Round ID: ROUND-001
Category: G
Question: 什么时候一个失败应当进入 `BLOCKED`，什么时候可返回部分 WorkProduct？部分结果如何标记，避免用户误以为完整结论？
Attack Intent: 攻击失败吞没和假成功。
Target Component: Run Outcome
Assumption Being Attacked: fallback answer is always better than refusal。
Severity: P0
Expected Answer Depth: terminal state and disclosure。
Evidence Required: partial completion policy and reviewer tests。
Kill Condition: 缺失关键 Evidence 时仍发布无标记完整结论。
Blue Answer: 必须按 TaskContract/EvidenceRequirement 区分 required/optional；required 缺失或安全/一致性未满足则 BLOCKED/ABSTAIN/REVIEW；optional 失败可生成 clearly partial WorkProduct，标注缺口、来源和未完成状态。
State Boundary: RunOutcome vs Finding/WorkProduct acceptance。
Ownership: Runtime reports outcome; Domain/Product publication gate decides。
State Transition: running→partial/blocked/complete→review/publish。
Failure: hidden missing evidence；Retry targeted gap or escalate。
Recovery: resume from valid state; no fake completion。
Security: partial output respects scope；Observability: completion reason/required gaps。
Alternative: best-effort answer；Tradeoff: user convenience vs legal risk。
Test / Benchmark: abstention precision/recall and reviewer acceptance。
Evidence: eval/agent docs；Remaining Gap: GAP-V2-020。
Red Critique: 这是法律产品的必要拒答边界。
Blue Revision: completion gate is explicit。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q079
Gap Candidate Refs: GAP-V2-020

## Q080

Round ID: ROUND-001
Category: G
Question: 如果模型 API、Vector DB、Graph DB、Object Store 和 PostgreSQL 同时存在超时，如何避免 Retry Storm 和级联故障？
Attack Intent: 攻击多 Provider 重试放大。
Target Component: Resilience
Assumption Being Attacked: 每层独立重试即可。
Severity: P1
Expected Answer Depth: retry budget/backpressure/circuit breaker/ownership。
Evidence Required: timeout/load fault test。
Kill Condition: 每层无限 exponential retry，或总预算不可观测。
Blue Answer: 重试由最接近错误的 Owner 分类并受全局 Run/Job Budget、deadline、backpressure、circuit/health 和 retry budget 约束；上层不能把已耗尽的调用再无限重试，必要时降级/blocked。
State Boundary: provider attempt vs Runtime/Job budget。
Ownership: each provider reports; Runtime coordinates deadline/budget。
State Transition: call→timeout→retryable/backoff/circuit/blocked。
Failure: correlated outage；Retry bounded jitter；Recovery queue drain/replay from idempotent job。
Security: resource/tenant quota；Observability: retry chain and amplification。
Alternative: no retry or per-layer retry；Tradeoff: availability vs storm risk。
Test / Benchmark: multi-provider outage injection。
Evidence: deployment/service docs；Remaining Gap: GAP-V2-017, GAP-V2-018。
Red Critique: 需要数字和配置才能落地。
Blue Revision: 配置和 SLO 延后到 implementation evidence。
Final Red Assessment: Target survives as design。
Score: 3/5
Architecture Fitness: 4/5
Scorecard Ref: Q080
Gap Candidate Refs: GAP-V2-017, GAP-V2-018

## Q081

Round ID: ROUND-001
Category: H
Question: 在 Microservice Target 已固定的前提下，为什么是 edge-api、Platform/Domain、Agent Runtime、Knowledge、Tool/Sandbox 五个候选，而不是 11 个服务或 3 个服务？
Attack Intent: 攻击服务数量偷换。
Target Component: Service Topology
Assumption Being Attacked: 五个服务已被证明。
Severity: P0
Expected Answer Depth: per-boundary evidence and open count。
Evidence Required: workload/failure/security/resource/lifecycle matrix。
Kill Condition: 服务数量由旧模块或“看起来完整”决定。
Blue Answer: 五个只是当前候选：edge 处理 northbound，Domain 事务，Runtime 长任务，Knowledge 重资源，Tool 安全副作用；每个边界仍需独立 scaling/failure/security/lifecycle 证据，可能合并或拆分，但不能回到 11=11。
State Boundary: Target constraint vs service candidate vs Current compose。
Ownership: Service Architecture owner；State Transition: capability→candidate→evidence→deployable boundary。
Failure: network/serialization/partial availability；Retry/reconcile contract；Security: boundary-specific。
Observability: distributed trace/SLO；Alternative: fewer services + workers；Tradeoff: ops vs isolation。
Test / Benchmark: service boundary scorecard and failure/load spikes。
Evidence: ADR-0010；Remaining Gap: GAP-V2-018。
Red Critique: 服务数量不能本轮直接定案。
Blue Revision: 五服务改名为 candidate topology。
Final Red Assessment: Target constraint survives; count open。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q081
Gap Candidate Refs: GAP-V2-018

## Q082

Round ID: ROUND-001
Category: H
Question: edge-api 如果只是认证、路由、SSE 和限流，为什么不能与 Platform/Domain 同一部署单元？独立部署的触发条件是什么？
Attack Intent: 攻击 Gateway 多一跳。
Target Component: edge-api
Assumption Being Attacked: API Gateway 必须独立服务。
Severity: P1
Expected Answer Depth: logical/physical separation。
Evidence Required: traffic/scaling/security lifecycle evidence。
Kill Condition: 没有独立边界，只有 network hop。
Blue Answer: edge 的逻辑 Contract 可保留，但物理上可以与 Domain 同镜像/单节点合并；只有 edge 流量、认证/协议安全、SSE 连接或发布生命周期需要独立扩缩容/隔离时才独立部署。
State Boundary: logical capability vs physical service。
Ownership: edge owns delivery/correlation, Domain owns facts。
State Transition: request→auth/routing→domain command/query。
Failure: edge unavailable; retry only safe commands; recovery traffic reroute。
Security: edge terminates auth but cannot authorize domain alone。
Observability: ingress/trace/SSE；Alternative: BFF in Domain；Tradeoff: lower latency/ops cost。
Test / Benchmark: connection/scaling/failure comparison。
Evidence: ADR-0010；Remaining Gap: GAP-V2-018。
Red Critique: logical ≠ physical 被正确保留。
Blue Revision: edge independent deployment remains conditional。
Final Red Assessment: Simplification candidate survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q082
Gap Candidate Refs: GAP-V2-018

## Q083

Round ID: ROUND-001
Category: H
Question: Knowledge Service 里的 OCR、Parsing、Embedding、Rerank、Graph Build 和 Retrieval API 是否需要分别成为服务？为什么 Worker Pool 可能足够？
Attack Intent: 攻击算法/Worker/Service 一一映射。
Target Component: Knowledge Service
Assumption Being Attacked: 每种重任务都要网络服务。
Severity: P1
Expected Answer Depth: resource profiles and deployment lifecycle。
Evidence Required: CPU/GPU/IO profile, queue SLO, failure isolation。
Kill Condition: 每个算法都独立部署但没有资源/生命周期差异。
Blue Answer: 逻辑上共用 Knowledge Contract；物理上可以按 CPU/GPU/IO、延迟和批处理分 worker pool；只有 Retrieval API 的独立 SLA、Graph Build 的资源/发布隔离或模型许可等证据成立才拆服务。
State Boundary: Knowledge owner vs worker/provider。
Ownership: Knowledge service owns projection contracts；workers execute jobs。
State Transition: ingestion job→projection generation→retrieval availability。
Failure: worker crash/index partial；Retry/rebuild from source；Security: scope inherited。
Observability: queue/CPU/GPU/index version；Alternative: one worker or modular monolith。
Test / Benchmark: workload profile and boundary spike。
Evidence: ADR-0010/knowledge docs；Remaining Gap: GAP-V2-018。
Red Critique: Worker-first meets necessary complexity。
Blue Revision: no algorithm microservices by default。
Final Red Assessment: Target survives conditionally。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q083
Gap Candidate Refs: GAP-V2-018

## Q084

Round ID: ROUND-001
Category: H
Question: 3,000–8,000 registered users是否足以证明微服务？如果只有 100 个用户，Agent/Knowledge/Sandbox 的异构 workload 仍可能需要独立边界吗？
Attack Intent: 杀死“用户数证明微服务”。
Target Component: Capacity / Services
Assumption Being Attacked: scale claims are user-count claims。
Severity: P1
Expected Answer Depth: workload heterogeneity vs volume。
Evidence Required: workload and failure/resource profile。
Kill Condition: 只用用户数量作拆分理由。
Blue Answer: 用户数不证明微服务；Agent 长运行、Knowledge CPU/GPU/IO、Sandbox 安全隔离、Platform 事务和 Eval batch 即使少用户也可能形成边界。反之若同一资源/失败/生命周期，仍可合并部署。
State Boundary: capacity assumptions are Target/UNKNOWN, not facts。
Ownership: Service/Deployment owner。
State Transition: workload profile→boundary candidate→measured deployment。
Failure: resource starvation/cascade；Retry/backpressure；Recovery isolate queues。
Security: Sandbox boundary independent of user count。
Observability: workload-specific SLO；Alternative: modular monolith + workers。
Test / Benchmark: workload isolation at low/high volume。
Evidence: ADR-0010/0011；Remaining Gap: GAP-V2-018。
Red Critique: 回答符合用户约束。
Blue Revision: 删除 capacity-based absolute claim。
Final Red Assessment: Principle survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q084
Gap Candidate Refs: GAP-V2-018

## Q085

Round ID: ROUND-001
Category: H
Question: Python-only 后端的最强反对理由是什么？如果某个 CPU/GPU workload 证明 Python 控制层和 Worker 总成本不可接受，何时允许引入 Java 或 Rust？
Attack Intent: 攻击 Python-only 绝对化。
Target Component: Language Policy
Assumption Being Attacked: AI ecosystem automatically beats Java。
Severity: P1
Expected Answer Depth: workload benchmark and reversal criteria。
Evidence Required: fixed workload/team/cost/security comparison。
Kill Condition: 没有证据仍将 Python-only 当永不可变。
Blue Answer: 反对理由包括 JVM 强类型/并发/生态、Python GIL/CPU/依赖/维护；当前保留 Python-only 是减少跨语言 Contract/RPC/观测复杂度。只有固定 workload/资源/团队条件下 Spike 证明总成本、可靠性、安全或性能不可接受才重开 ADR。
State Boundary: Target constraint ≠ historical language fact。
Ownership: Architecture/Team owner；State Transition: constraint→benchmark→retain/reverse。
Failure: Python worker saturation；Retry/backpressure/native backend；Recovery route heavy work to process/native engine。
Security: language choice not security proof；Observability: CPU/GPU/cost/SLO。
Alternative: Java service/Rust worker；Tradeoff: performance/type vs cross-language cost。
Test / Benchmark: cross-language workload spike。
Evidence: ADR-0009；Remaining Gap: GAP-V2-018, GAP-V2-020。
Red Critique: 这是可逆的而不是教条。
Blue Revision: external Java integration still allowed。
Final Red Assessment: Python target survives conditional evidence。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q085
Gap Candidate Refs: GAP-V2-018, GAP-V2-020

## Q086

Round ID: ROUND-001
Category: H
Question: Developer Compose、Staging Multi-service 和 Production HA 三种 Profile 分别证明什么？Compose 能否被称为 Production Ready？
Attack Intent: 攻击部署文档冒充运行证据。
Target Component: Deployment
Assumption Being Attacked: compose up equals production。
Severity: P0
Expected Answer Depth: profile boundary and evidence。
Evidence Required: deployment/e2e/fault/DR evidence。
Kill Condition: 仅有 Docker/Compose 就声称 Production Ready。
Blue Answer: Developer Profile 证明本地可启动；Staging 证明合同、队列、故障、观测和多服务协作；Production 还需 HA、滚动升级、备份/恢复、安全、负载、DR 和真实运行证据。当前 Production Readiness 为 NOT_ESTABLISHED。
State Boundary: deployment target vs current evidence。
Ownership: Deployment/SRE；State Transition: profile→verification→readiness evidence。
Failure: environment drift；Retry/fallback controlled；Recovery restore/rollback。
Security: secrets/network/artifact attestation；Observability: SLO/trace/log/metric。
Alternative: single node；Tradeoff: lower ops but no HA。
Test / Benchmark: profile-specific acceptance/fault tests。
Evidence: production-readiness.md；Remaining Gap: GAP-V2-018, GAP-V2-019。
Red Critique: 明确拒绝 Production Ready 误称。
Blue Revision: no production claim without evidence。
Final Red Assessment: Gate survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q086
Gap Candidate Refs: GAP-V2-018, GAP-V2-019

## Q087

Round ID: ROUND-001
Category: H
Question: 为什么不默认 Kubernetes、Kafka、Service Mesh、Database-per-service、Event Sourcing 和 Saga？每一项的触发证据分别是什么？
Attack Intent: 攻击“大厂基础设施”堆砌。
Target Component: Infrastructure
Assumption Being Attacked: platform complexity equals resilience。
Severity: P1
Expected Answer Depth: independent trigger and deletion/defer condition。
Evidence Required: scale/HA/throughput/security/lifecycle evidence。
Kill Condition: 用行业惯例替代具体 failure/resource/lifecycle 需求。
Blue Answer: K8s需 HA/rolling/autoscaling/operator；Kafka需吞吐/retention/replay/consumer topology；Mesh需治理/安全/观测收益；DB-per-service需独立 availability/scaling/security/lifecycle；Event Sourcing需 replay/audit；Saga需多本地事务补偿。当前都 DEFER。
State Boundary: Future provider choices not Current。
Ownership: Deployment/Data/Service owners。
State Transition: candidate→evidence→adopt/defer/delete。
Failure: each adds failure surface；Retry/recovery must be modeled before adopt。
Security: supply chain/secret/identity cost；Observability: operational burden measured。
Alternative: Docker/managed queue/shared PG/outbox/reconcile；Tradeoff: less capability, lower cost。
Test / Benchmark: capacity/failure/ops spike per candidate。
Evidence: ADR-0010；Remaining Gap: GAP-V2-018, GAP-V2-023。
Red Critique: 明确把成熟工具当候选而非必选。
Blue Revision: Complexity Card required for infrastructure additions。
Final Red Assessment: Defer policy survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q087
Gap Candidate Refs: GAP-V2-018, GAP-V2-023

## Q088

Round ID: ROUND-001
Category: H
Question: 服务间 HTTP、gRPC、MCP/API 和 Async Queue 如何选择？为什么“全部 gRPC”或“全部 Event”都不是架构原则？
Attack Intent: 攻击协议统一崇拜。
Target Component: Communication
Assumption Being Attacked: one protocol simplifies everything。
Severity: P1
Expected Answer Depth: interaction semantics。
Evidence Required: latency/serialization/failure/interop matrix。
Kill Condition: 协议选择不考虑同步性、长任务、外部兼容和重试。
Blue Answer: CRUD/查询/小命令默认 HTTP；长任务/重资源/取消/重试用 durable queue；外部 Host 用 MCP/API/HTTP；高吞吐内部结构化调用才评估 gRPC；Event 只在异步解耦/通知语义成立时使用。
State Boundary: communication receipt vs business truth。
Ownership: service contract owner；Queue is not truth。
State Transition: request/job/event with IDs and receipts。
Failure: timeout/partial/serialization；Retry per contract；Recovery reconcile。
Security: mTLS/auth/scope/provider policy；Observability: correlation across protocols。
Alternative: all HTTP；Tradeoff: simple but long jobs/streaming poor。
Test / Benchmark: protocol latency/error/ops cost matrix。
Evidence: ADR-0010；Remaining Gap: GAP-V2-018。
Red Critique: 默认协议有理由但不能锁死 gRPC。
Blue Revision: protocol remains provider/contract candidate。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 4/5
Scorecard Ref: Q088
Gap Candidate Refs: GAP-V2-018

## Q089

Round ID: ROUND-001
Category: I
Question: 法律系统的最小评测是否可以只用最终 LLM Judge Score？为什么必须分 Parser、Retrieval、Evidence、Citation、Finding、Reviewer 和 Task 层？
Attack Intent: 攻击单一质量指标。
Target Component: Legal Eval
Assumption Being Attacked: LLM Judge 是充分质量证据。
Severity: P0
Expected Answer Depth: layered metrics and error localization。
Evidence Required: fixed dataset/protocol。
Kill Condition: Judge 高分掩盖 unsupported/citation 错误。
Blue Answer: 不能。至少测 SourceSpan/Extraction、Recall/nDCG、Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Conflict/Fact–Article/Applicability、Reviewer Acceptance 和 Task Completion，并同时记录 Latency/Token/Cost/Calls。
State Boundary: Eval evidence vs Product/Domain truth。
Ownership: Eval Owner；Human Reviewer provides agreement/acceptance。
State Transition: dataset→run→raw result→analysis→release gate。
Failure: judge bias/data leakage；Retry independent slice/human review；Recovery block release。
Security: eval data access and redaction；Observability: reproducible run/artifact。
Alternative: final judge only；Tradeoff: cheap but non-diagnostic。
Test / Benchmark: A/B/C, Graph Kill, Memory/Multi-Agent ablation。
Evidence: legal-eval-and-benchmark.md；Remaining Gap: GAP-V2-020。
Red Critique: 指标链完整但没有运行结果。
Blue Revision: Quality remains not_yet_proven。
Final Red Assessment: Eval contract survives; proof open。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q089
Gap Candidate Refs: GAP-V2-020

## Q090

Round ID: ROUND-001
Category: I
Question: A/B/C Benchmark 如何保证 Same Model、Same Raw Corpus、Same Tools、Comparable Prompt、Same Token/Time Budget？
Attack Intent: 攻击不公平竞品实验。
Target Component: A/B/C Benchmark
Assumption Being Attacked: 变体名称相同就可比较。
Severity: P0
Expected Answer Depth: control variables and trace。
Evidence Required: preregistered configs, dataset hashes, run receipts。
Kill Condition: C 获得更多 Token/Tools/不同模型仍宣称优越。
Blue Answer: Benchmark 固定模型版本、原始语料/hash、外部工具、权限、Prompt/Skill 可比性、Token/Time/Cost budget 和数据切分；Trace 记录 calls/retrieval/tool/latency/cost/reuse，变更必须明确。
State Boundary: Hypothesis/Measured only。
Ownership: Eval Owner controls registration；Architecture Owner interprets。
State Transition: registered→run→raw result→reviewed decision。
Failure: confounder/missing trace；Retry invalidate run, not cherry-pick。
Security: equal deployment/data policy；Observability: config/artifact hashes。
Alternative: demo-to-demo；Tradeoff: fast but invalid causal claim。
Test / Benchmark: A/B/C protocol audit。
Evidence: ADR-0008/eval docs；Remaining Gap: GAP-V2-020。
Red Critique: 需要可审计配置而不只是说明。
Blue Revision: 未注册的结果不得进入 Decision。
Final Red Assessment: Benchmark gate survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q090
Gap Candidate Refs: GAP-V2-020

## Q091

Round ID: ROUND-001
Category: I
Question: Evidence Sufficiency、Citation Correctness 和 Unsupported Claim Rate 的分母是什么？如果系统选择 Abstain，任务完成率如何计算？
Attack Intent: 攻击指标定义和奖励拒答。
Target Component: Eval Contract
Assumption Being Attacked: 指标名本身可比较。
Severity: P1
Expected Answer Depth: annotation/protocol/abstention semantics。
Evidence Required: metric specification and gold labels。
Kill Condition: 分母、Gold Evidence 或 Abstain scoring 不明确。
Blue Answer: 每个指标必须声明样本单位、Gold Claim/Evidence/Citation、strict/partial matching 和权限范围；Abstain 在无证据任务可得分，但在有充分 Gold 的任务按未完成/安全拒答策略分开报告，不能把所有拒答当成功。
State Boundary: Eval facts are separate from Domain facts。
Ownership: Eval Owner and annotation governance。
State Transition: labeled dataset→run→metric calculation→release gate。
Failure: label disagreement；Retry adjudication/independent reviewer；Recovery version dataset。
Security: annotation access and PII；Observability: dataset/metric version。
Alternative: one Accuracy；Tradeoff: easier but hides safety/quality。
Test / Benchmark: metric contract unit tests and reviewer agreement。
Evidence: eval docs；Remaining Gap: GAP-V2-020。
Red Critique: 需要法院 QA/Gold protocol事实补强。
Blue Revision: 历史 QA 数量和标准保持 UNKNOWN。
Final Red Assessment: Target survives, Fact Gap remains。
Score: 3/5
Architecture Fitness: 5/5
Scorecard Ref: Q091
Gap Candidate Refs: GAP-V2-001, GAP-V2-020

## Q092

Round ID: ROUND-001
Category: I
Question: Graph、Memory、Multi-Agent 或 Reranker 的收益如果只在公开数据集上出现，为什么可以外推到法院真实任务？
Attack Intent: 攻击公开 Benchmark 外推。
Target Component: Eval Generalization
Assumption Being Attacked: Public dataset proxy equals customer workload。
Severity: P1
Expected Answer Depth: task transfer and limitation。
Evidence Required: court QA/representative task validation。
Kill Condition: 没有真实任务/用户复核仍宣称产品收益。
Blue Answer: 不能直接外推。公开数据只能作 PUBLIC_CONTEXT/方法验证；法院真实 QA、材料分布、错误成本和 Reviewer Acceptance 需要独立数据或用户授权验证。当前客户质量反馈根因和 QA 协议仍部分 UNKNOWN。
State Boundary: public research ≠ historical Zuno ≠ measured product。
Ownership: Facts/Eval Owner；User/Reviewer validates task relevance。
State Transition: public proxy→candidate→representative validation→decision。
Failure: distribution shift；Retry new slice/holdout；Recovery scope claim down。
Security: sensitive data handling；Observability: corpus provenance。
Alternative: public only；Tradeoff: accessible but weak relevance。
Test / Benchmark: representative court task benchmark when authorized。
Evidence: facts/data-and-evaluation-history.md；Remaining Gap: GAP-V2-001, GAP-V2-020。
Red Critique: 没有把论文成绩写成 Zuno 成绩。
Blue Revision: all claims scoped to dataset。
Final Red Assessment: Boundary survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q092
Gap Candidate Refs: GAP-V2-001, GAP-V2-020

## Q093

Round ID: ROUND-001
Category: I
Question: 一个新 Reranker/Legal Capability 在离线 Benchmark 上更好，谁批准 Artifact、Profile Version 和生产 adoption？如何回滚？
Attack Intent: 攻击 Eval 到发布的断链。
Target Component: Eval Release Gate
Assumption Being Attacked: benchmark win equals deploy permission。
Severity: P1
Expected Answer Depth: artifact provenance/release gate/rollback。
Evidence Required: signed artifact, shadow, adoption trace。
Kill Condition: Demo 或单次分数直接切换当前 Provider。
Blue Answer: Candidate Artifact 绑定代码/模型/数据/配置 hash、License/SBOM、Eval report 和 Security checks；Release Gate 批准 Profile Version，先 shadow/canary（若适用），adoption 可回滚到上一版本，未通过不影响当前。
State Boundary: Eval Artifact vs Runtime adoption vs Domain result。
Ownership: Eval release owner + Security + Runtime operator。
State Transition: candidate→evaluated→approved/rejected→adopted/rollback。
Failure: regressions/invalid artifact；Retry new candidate；Recovery previous profile/provider。
Security: signed artifact/supply chain；Observability: profile/version traces。
Alternative: hot swap config；Tradeoff: faster but irreproducible。
Test / Benchmark: release gate and rollback test。
Evidence: eval/security docs；Remaining Gap: GAP-V2-019, GAP-V2-023。
Red Critique: 发布证据不能由文档自动生成。
Blue Revision: adoption remains Target only。
Final Red Assessment: Target survives pending evidence。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q093
Gap Candidate Refs: GAP-V2-019, GAP-V2-023

## Q094

Round ID: ROUND-001
Category: I
Question: Observability 记录哪些 Trace 才能回答“答案错了是 Retrieval、Capability、Memory、Tool、Runtime 还是 Domain Review 的责任”？
Attack Intent: 攻击只记录最终文本。
Target Component: Observability
Assumption Being Attacked: 日志/LLM output 足够诊断。
Severity: P1
Expected Answer Depth: lineage/correlation/redaction/ownership。
Evidence Required: end-to-end trace contract。
Kill Condition: 无法从 Run 追到 source/version/provider/proposal/review/effect。
Blue Answer: Trace 需要 correlation/run/plan/step、model/provider/version/usage、retrieval rounds/candidates/citations、capability proposals、memory decisions、tool attempts/receipts、Domain mutations/reviews；隐藏思维链不保存，敏感值脱敏。
State Boundary: Trace evidence ≠ hidden chain-of-thought ≠ business fact。
Ownership: Observability stores trace; each owner emits contract fields。
State Transition: span lineage from request to WorkProduct/review/effect。
Failure: missing/late spans；Retry exporter; Recovery raw receipts/structured audit。
Security: redaction/access/retention；Observability: trace completeness metric。
Alternative: final answer log；Tradeoff: cheap but non-diagnostic。
Test / Benchmark: trace completeness and redaction tests。
Evidence: eval/security/architecture docs；Remaining Gap: GAP-V2-013, GAP-V2-019。
Red Critique: 需要明确 trace 不是存思维链。
Blue Revision: only visible rationale/structured reasons。
Final Red Assessment: Target survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q094
Gap Candidate Refs: GAP-V2-013, GAP-V2-019

## Q095

Round ID: ROUND-001
Category: I
Question: 评测发现 Domain-aware Runtime 与 WorkBuddy+Backend 无质量差异，但 C 延迟更高、成本更高时，是否仍可因为“架构更优雅”保留 C？
Attack Intent: Kill Native Runtime with efficiency evidence。
Target Component: Native Runtime
Assumption Being Attacked: semantic elegance beats measured cost。
Severity: P0
Expected Answer Depth: reversal and decision。
Evidence Required: controlled C vs B results。
Kill Condition: no quality gain and negative efficiency, yet Blue refuses deletion。
Blue Answer: 不应保留。若质量无增益且延迟/成本更差，删除或外部化 Native Runtime；若 C 在恢复、安全或治理上有独立、被验证且业务必须的收益，需单独量化并证明 B/普通 Workflow 不能满足。
State Boundary: Hypothesis→Measured decision。
Ownership: Eval/Architecture/User Gate。
State Transition: benchmark→decision→provider migration/delete。
Failure: migration compatibility；Retry B fallback；Recovery preserve Domain Contract。
Security: equal security controls plus measured difference。
Observability: cost/latency/retrieval/tool/domain reuse。
Alternative: B Host+Backend；Tradeoff: lower complexity。
Test / Benchmark: C vs B and provider exit spike。
Evidence: ADR-0008；Remaining Gap: GAP-V2-004, GAP-V2-020。
Red Critique: 这是必须接受的删除答案。
Blue Revision: C remains deferred until value evidence。
Final Red Assessment: Architecture falsifiability survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q095
Gap Candidate Refs: GAP-V2-004, GAP-V2-020

## Q096

Round ID: ROUND-001
Category: J
Question: 假设我是字节/阿里 Staff Engineer：为什么不是 WorkBuddy/Dify + Legal Backend？请用已知事实、Target Hypothesis 和必须执行的 Benchmark 分开回答。
Attack Intent: Big-Tech Host substitution attack。
Target Component: Product Positioning
Assumption Being Attacked: Zuno 必须拥有完整 Host。
Severity: P0
Expected Answer Depth: build/buy boundary and evidence humility。
Evidence Required: official host capability matrix, A/B/C benchmark, Legal Backend fit。
Kill Condition: 贬低竞品或把 Zuno 质量优势写成事实。
Blue Answer: WorkBuddy/Dify 可能作为 Host，Zuno 只保留需要跨运行、证据、版本、Review、stale 和审计的最小 Domain Backend；Native Runtime 只有 C>B 的可归因收益才保留。当前没有 Zuno 优于 Host 的质量/效率证据。
State Boundary: competitor facts/public evidence vs Zuno Target/Hypothesis。
Problem: Host 与 Domain Backend 的必要边界尚未由对照实验证明；Decision: DEFER_NATIVE_HOST_OWNERSHIP；Why: 先用 Legal Backend + 外部 Host 验证最小充分性；Retry: 重跑同预算 A/B/C；Recovery: 回退到 Host+Backend；Idempotency: 相同模型、语料、工具、预算和 case seed。
Ownership: Domain backend owns accepted state; Host owns interaction/runtime provider。
State Transition: Host task→proposal/API→validation/review/work product。
Failure: host/backend partial; retry idempotent; recovery receipts/versions。
Security: backend enforces scope; no negative security claims about Host。
Observability: host/backend correlation and benchmark metrics。
Alternative: WorkBuddy-only or full Zuno Host；Tradeoff: boundary vs build cost。
Test / Benchmark: Kill Zuno/Runtime and A/B/C。
Evidence: ADR-0008/0007；Remaining Gap: GAP-V2-004, GAP-V2-023。
Red Critique: 没有把 WorkBuddy/Dify 说成不安全或不够强。
Blue Revision: “Zuno value” remains falsifiable Legal Domain/Capability hypothesis。
Final Red Assessment: Positioning is defensible only as hypothesis。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q096
Gap Candidate Refs: GAP-V2-004, GAP-V2-023

## Q097

Round ID: ROUND-001
Category: J
Question: 假设我是 Principal Distributed Systems Engineer：Domain DB、Runtime Checkpoint、Queue、Tool Receipt 四者各自保存什么？请解释一次 Effect unknown 的恢复，而不是背组件名。
Attack Intent: 工程深度与状态所有权攻击。
Target Component: State/Recovery
Assumption Being Attacked: 组件列表等于架构理解。
Severity: P0
Expected Answer Depth: state model, failure, recovery, idempotency。
Evidence Required: fault-injection trace/contract。
Kill Condition: Checkpoint 或 Queue 被当业务事实，或 Unknown 被直接 retry。
Blue Answer: Domain DB 保存业务事实/版本；Checkpoint 保存 Graph control；Queue 保存 delivery/job attempt；Tool Receipt 保存外部 Effect outcome/operation ID。Effect unknown 先对账 provider/receipt，再决定 close/retry/review，不能盲重做。
State Boundary: four distinct state roles。
Problem: 多状态源可能产生部分提交；Decision: KEEP_STATE_SEPARATION；Why: 业务事实、控制状态、投递状态和外部效果不能互相冒充；Retry: 仅对可证明幂等的步骤重试；Recovery: 先以 Receipt/Provider Operation ID 对账；Idempotency: operation key 与 run/step 版本绑定。
Ownership: Domain/Runtime/Worker/Tool owners。
State Transition: submit→job→control→effect→receipt→domain acceptance。
Failure: partial commit/timeout；Retry idempotent/reconcile；Recovery generation/receipt。
Security: preflight and approval; Observability: end-to-end correlation。
Alternative: one state store；Tradeoff: fewer stores but unclear ownership。
Test / Benchmark: crash matrix at each boundary。
Evidence: architecture/data/service docs；Remaining Gap: GAP-V2-013, GAP-V2-017。
Red Critique: 这类问题不能用类名回答，当前还缺实现证据。
Blue Revision: 把状态回放列为 Critical Gate。
Final Red Assessment: Target reasoning strong; Current gap open。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q097
Gap Candidate Refs: GAP-V2-013, GAP-V2-017

## Q098

Round ID: ROUND-001
Category: J
Question: 假设我是 Hiring Manager：你本人到底做了什么？请不要把团队、框架、当前 Target 和个人实现混在一起；如果具体文件和 API 还不知道，应该如何回答？
Attack Intent: 个人贡献真实性攻击。
Target Component: Personal Ownership
Assumption Being Attacked: 参与平台等于负责平台。
Severity: P0
Expected Answer Depth: historical boundary and recovery plan。
Evidence Required: user confirmation, commits, task records, code/artifacts。
Kill Condition: 把团队 RAG/部署/架构写成个人负责，或用 Target 补齐。
Blue Answer: 当前可确认用户参与 Agent、Memory、OpenViking Memory/Context 接入和 Tool Calling Strategy；具体文件/API/bug/测试仍需 Fact Recovery。应区分 Personal、Team、Framework Provided、Other Team Work，不能把 LangGraph/OpenViking 能力或 Target service ownership写成个人成果。
State Boundary: USER_CONFIRMED broad scope / detail UNKNOWN；Target ≠ historical contribution。
Problem: 个人贡献边界仍缺代码级证据；Decision: KEEP_SCOPE_DOWN；Why: 只能把用户确认的 Agent/Memory/OpenViking/Tool Calling 范围写入事实；Retry: 用任务、提交、API 和具体场景回忆补证；Recovery: 无法确认则保持 UNKNOWN；Idempotency: 同一贡献声明必须可回链同一 Evidence ID。
Ownership: Facts Owner records; user is authority for personal memory。
State Transition: candidate recall→user confirmed/artifact→fact or UNKNOWN。
Failure: overclaim; Retry ask concrete scene/artifact; Recovery narrow resume claim。
Security: do not expose private repo/customer data；Observability: evidence IDs not invented metrics。
Alternative: impressive broad claim；Tradeoff: shorter but dishonest。
Test / Benchmark: commit/task/API/artifact cross-check。
Evidence: docs/project/facts/team-and-ownership.md；Remaining Gap: GAP-V2-024。
Red Critique: 诚实边界比包装更重要。
Blue Revision: personal claim stays limited until evidence。
Final Red Assessment: Fact Gate passes only at broad scope; P0 details open。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q098
Gap Candidate Refs: GAP-V2-024

## Q099

Round ID: ROUND-001
Category: J
Question: 把 LangGraph、Neo4j、Milvus、RabbitMQ、OpenViking、Dify 和 Kubernetes 全部删掉后，哪个最先证明不可删除？请按真实需求、失败模式、替代和证据排序，而不是按品牌排序。
Attack Intent: 全栈反事实压缩攻击。
Target Component: Technology Survival
Assumption Being Attacked: 技术清单代表产品能力。
Severity: P0
Expected Answer Depth: survival table and kill tests。
Evidence Required: component cards, workload/failure/security/eval evidence。
Kill Condition: 任意组件只因当前文档或简历名称被保留。
Blue Answer: 不能预设。优先证明 Domain Contract/Owner、Evidence/Citation integrity 和 Tool Effect reconciliation 这些语义资格；具体 Provider 按 Kill Test：LangGraph vs State Machine、Graph vs Hybrid、OpenViking vs DB+Checkpoint、Queue vs sync、K8s vs Compose/managed containers，未证明就 DEFER/DELETE。
State Boundary: historical usage/current code/Target candidate all separate。
Problem: 技术品牌清单不能证明组件必要；Decision: DEFER_PROVIDER_SELECTION；Why: 先保留 Canonical Contract，再按 Kill Test 选择 Provider；Retry: 失败时回退到更简单 Provider；Recovery: 保留契约和数据导出；Idempotency: 迁移任务使用组件级 operation key。
Ownership: Architecture/Eval/Service owners。
State Transition: component candidate→card→benchmark/spike→keep/refine/replace/delete。
Failure: deletion migration risk；Retry fallback provider；Recovery preserve canonical contracts。
Security: provider license/supply chain/egress evidence。
Observability: cost/latency/failure/quality and exit path。
Alternative: minimal host/backend/workers；Tradeoff: less capability but lower cost。
Test / Benchmark: technology survival table and kill tests。
Evidence: reuse-first and architecture ADRs；Remaining Gap: GAP-V2-018, GAP-V2-020, GAP-V2-023。
Red Critique: 没有用技术品牌直接赢辩论。
Blue Revision: 所有组件进入 Complexity Card。
Final Red Assessment: Necessary Complexity principle survives。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q099
Gap Candidate Refs: GAP-V2-018, GAP-V2-020, GAP-V2-023

## Q100

Round ID: ROUND-001
Category: J
Question: 本轮结束时，哪些 Claim 仍不能进入 Canonical Architecture？哪些必须进入 Fact Recovery Queue、Benchmark Queue 或 Implementation Evidence Queue？请明确下一轮最强攻击面。
Attack Intent: 检查能否主动收敛、拒绝过度承诺并形成下一轮。
Target Component: Round Governance
Assumption Being Attacked: 100 问完成等于架构通过。
Severity: P0
Expected Answer Depth: score/gate/gap/next round。
Evidence Required: full transcript/scorecard/gaps/decision board。
Kill Condition: 高分掩盖 P0，或直接 Canonical Sync。
Blue Answer: 本轮不自动通过；Native Runtime、Graph、Memory Provider、Multi-Agent topology、五服务 count 和历史复杂度仍需证据。Fact Queue 处理法院工作流、QA、个人代码、Incident；Benchmark Queue 处理 A/B/C、Graph/Memory/Agent；Implementation Evidence Queue 处理 state/reconcile/effect/security traces。下一轮优先攻击 Domain Backend 必要性、Tool Effect recovery、真实任务和 Service count。
State Boundary: Round result is Lab record; Canonical Sync pending User Gate。
Problem: 100 问完成不等于架构通过；Decision: KEEP_USER_GATE；Why: P0、事实缺口和未测量收益仍阻止 Canonical Sync；Retry: 下一轮只重测变化后的攻击面；Recovery: 不做 Canonical mutation；Idempotency: Round ID、Question ID 和 Gap ID 保持稳定。
Ownership: Red/Blue produce record; User Gate/Canonical Owner decide。
State Transition: Round→scored→gaps→counter attack→user gate→sync/defer。
Failure: unresolved P0/P1；Retry next round or fact recovery；Recovery no canonical mutation。
Security: critical gates remain open；Observability: score/gap lineage。
Alternative: declare success after 100 questions；Tradeoff: faster but unsafe。
Test / Benchmark: V2 verifier, scorecard/category totals, P0 gate。
Evidence: current facts/ADR/docs and this transcript；Remaining Gap: GAP-V2-001, GAP-V2-004, GAP-V2-013, GAP-V2-015, GAP-V2-017, GAP-V2-018, GAP-V2-020, GAP-V2-022, GAP-V2-024。
Red Critique: 100 问不能替代证据和 User Gate。
Blue Revision: Round status remains NOT_PASSED_PENDING_GATE。
Final Red Assessment: Round complete, architecture not approved。
Score: 4/5
Architecture Fitness: 5/5
Scorecard Ref: Q100
Gap Candidate Refs: GAP-V2-001, GAP-V2-004, GAP-V2-013, GAP-V2-015, GAP-V2-017, GAP-V2-018, GAP-V2-020, GAP-V2-022, GAP-V2-024

## Answers / Review / Score: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/scorecard.md`

# ROUND-001 Scorecard

本轮共有 100 题，Raw Score 最大 500。分数反映 Blue 防守质量，不代表架构已通过；本轮有 P0 Critical Gaps，状态必须为 `NOT_PASSED_PENDING_USER_GATE`。

## 逐题评分

| Question ID | Category | Answer (0-5) | Fitness (0-5) | Severity | Gap Refs |
|---|---|---:|---:|---|---|
| Q001 | A | 2 | 3 | P0 | GAP-V2-001 |
| Q002 | A | 2 | 3 | P0 | GAP-V2-002 |
| Q003 | A | 3 | 4 | P1 | GAP-V2-002 |
| Q004 | A | 3 | 4 | P1 | GAP-V2-003 |
| Q005 | A | 3 | 4 | P0 | GAP-V2-003, GAP-V2-022 |
| Q006 | A | 3 | 4 | P1 | GAP-V2-009, GAP-V2-022 |
| Q007 | A | 3 | 4 | P0 | GAP-V2-003, GAP-V2-007 |
| Q008 | A | 3 | 4 | P0 | GAP-V2-004 |
| Q009 | A | 3 | 4 | P1 | GAP-V2-001, GAP-V2-005 |
| Q010 | A | 3 | 4 | P0 | GAP-V2-004, GAP-V2-020 |
| Q011 | B | 3 | 4 | P0 | GAP-V2-005, GAP-V2-022 |
| Q012 | B | 3 | 4 | P1 | GAP-V2-022 |
| Q013 | B | 4 | 4 | P0 | GAP-V2-018 |
| Q014 | B | 4 | 5 | P0 | GAP-V2-022 |
| Q015 | B | 4 | 4 | P0 | GAP-V2-011, GAP-V2-012 |
| Q016 | B | 4 | 5 | P0 | GAP-V2-007, GAP-V2-013 |
| Q017 | B | 4 | 4 | P1 | GAP-V2-005, GAP-V2-011 |
| Q018 | B | 3 | 4 | P0 | GAP-V2-004, GAP-V2-020 |
| Q019 | B | 4 | 5 | P1 | GAP-V2-022 |
| Q020 | B | 4 | 4 | P1 | GAP-V2-005, GAP-V2-022 |
| Q021 | C | 3 | 4 | P1 | GAP-V2-006 |
| Q022 | C | 3 | 4 | P1 | GAP-V2-006 |
| Q023 | C | 3 | 4 | P0 | GAP-V2-006, GAP-V2-007 |
| Q024 | C | 4 | 4 | P0 | GAP-V2-006, GAP-V2-007 |
| Q025 | C | 3 | 5 | P0 | GAP-V2-007, GAP-V2-013 |
| Q026 | C | 4 | 4 | P1 | GAP-V2-006 |
| Q027 | C | 3 | 5 | P0 | GAP-V2-015 |
| Q028 | C | 3 | 4 | P1 | GAP-V2-009 |
| Q029 | C | 4 | 4 | P1 | GAP-V2-020 |
| Q030 | C | 3 | 4 | P1 | GAP-V2-006 |
| Q031 | C | 3 | 5 | P0 | GAP-V2-006, GAP-V2-007 |
| Q032 | C | 3 | 4 | P1 | GAP-V2-014 |
| Q033 | C | 4 | 5 | P0 | GAP-V2-015, GAP-V2-016 |
| Q034 | C | 4 | 5 | P0 | GAP-V2-022 |
| Q035 | C | 3 | 4 | P1 | GAP-V2-013, GAP-V2-020 |
| Q036 | D | 3 | 4 | P1 | GAP-V2-009, GAP-V2-020 |
| Q037 | D | 4 | 5 | P0 | GAP-V2-009, GAP-V2-010 |
| Q038 | D | 3 | 4 | P1 | GAP-V2-010, GAP-V2-020 |
| Q039 | D | 4 | 5 | P0 | GAP-V2-009, GAP-V2-020 |
| Q040 | D | 3 | 5 | P0 | GAP-V2-009, GAP-V2-013 |
| Q041 | D | 3 | 4 | P1 | GAP-V2-010, GAP-V2-020 |
| Q042 | D | 4 | 5 | P1 | GAP-V2-020 |
| Q043 | D | 4 | 5 | P0 | GAP-V2-015 |
| Q044 | D | 3 | 4 | P1 | GAP-V2-020 |
| Q045 | D | 4 | 5 | P1 | GAP-V2-022, GAP-V2-023 |
| Q046 | D | 4 | 5 | P0 | GAP-V2-023 |
| Q047 | D | 4 | 5 | P0 | GAP-V2-011, GAP-V2-012 |
| Q048 | D | 4 | 5 | P0 | GAP-V2-011, GAP-V2-015 |
| Q049 | D | 3 | 4 | P1 | GAP-V2-011, GAP-V2-020 |
| Q050 | D | 4 | 5 | P0 | GAP-V2-020 |
| Q051 | E | 4 | 5 | P0 | GAP-V2-013 |
| Q052 | E | 4 | 5 | P0 | GAP-V2-013, GAP-V2-017 |
| Q053 | E | 4 | 5 | P0 | GAP-V2-007, GAP-V2-022 |
| Q054 | E | 4 | 4 | P1 | GAP-V2-007 |
| Q055 | E | 4 | 5 | P0 | GAP-V2-018 |
| Q056 | E | 3 | 4 | P1 | GAP-V2-013, GAP-V2-017 |
| Q057 | E | 4 | 5 | P0 | GAP-V2-009, GAP-V2-015 |
| Q058 | E | 3 | 5 | P0 | GAP-V2-007, GAP-V2-020 |
| Q059 | E | 4 | 5 | P0 | GAP-V2-007, GAP-V2-013 |
| Q060 | E | 4 | 4 | P1 | GAP-V2-018 |
| Q061 | F | 4 | 5 | P0 | GAP-V2-015, GAP-V2-016 |
| Q062 | F | 3 | 5 | P1 | GAP-V2-024 |
| Q063 | F | 4 | 5 | P0 | GAP-V2-015, GAP-V2-016 |
| Q064 | F | 4 | 5 | P0 | GAP-V2-016, GAP-V2-017 |
| Q065 | F | 4 | 5 | P1 | GAP-V2-016 |
| Q066 | F | 4 | 5 | P0 | GAP-V2-015, GAP-V2-017 |
| Q067 | F | 4 | 5 | P0 | GAP-V2-015 |
| Q068 | F | 4 | 5 | P0 | GAP-V2-016, GAP-V2-017 |
| Q069 | F | 3 | 4 | P1 | GAP-V2-018 |
| Q070 | F | 4 | 5 | P0 | GAP-V2-015 |
| Q071 | G | 4 | 5 | P0 | GAP-V2-017, GAP-V2-024 |
| Q072 | G | 4 | 5 | P0 | GAP-V2-016, GAP-V2-017 |
| Q073 | G | 4 | 5 | P0 | GAP-V2-013, GAP-V2-017 |
| Q074 | G | 3 | 5 | P1 | GAP-V2-007, GAP-V2-017 |
| Q075 | G | 4 | 5 | P0 | GAP-V2-003, GAP-V2-020 |
| Q076 | G | 4 | 5 | P0 | GAP-V2-016, GAP-V2-017 |
| Q077 | G | 3 | 5 | P0 | GAP-V2-017 |
| Q078 | G | 4 | 5 | P1 | GAP-V2-013, GAP-V2-017 |
| Q079 | G | 4 | 5 | P0 | GAP-V2-020 |
| Q080 | G | 3 | 4 | P1 | GAP-V2-017, GAP-V2-018 |
| Q081 | H | 4 | 4 | P0 | GAP-V2-018 |
| Q082 | H | 4 | 4 | P1 | GAP-V2-018 |
| Q083 | H | 4 | 5 | P1 | GAP-V2-018 |
| Q084 | H | 4 | 5 | P1 | GAP-V2-018 |
| Q085 | H | 4 | 4 | P1 | GAP-V2-018, GAP-V2-020 |
| Q086 | H | 4 | 5 | P0 | GAP-V2-018, GAP-V2-019 |
| Q087 | H | 4 | 5 | P1 | GAP-V2-018, GAP-V2-023 |
| Q088 | H | 4 | 4 | P1 | GAP-V2-018 |
| Q089 | I | 4 | 5 | P0 | GAP-V2-020 |
| Q090 | I | 4 | 5 | P0 | GAP-V2-020 |
| Q091 | I | 3 | 5 | P1 | GAP-V2-001, GAP-V2-020 |
| Q092 | I | 4 | 5 | P1 | GAP-V2-001, GAP-V2-020 |
| Q093 | I | 4 | 5 | P1 | GAP-V2-019, GAP-V2-023 |
| Q094 | I | 4 | 5 | P1 | GAP-V2-013, GAP-V2-019 |
| Q095 | I | 4 | 5 | P0 | GAP-V2-004, GAP-V2-020 |
| Q096 | J | 4 | 5 | P0 | GAP-V2-004, GAP-V2-023 |
| Q097 | J | 4 | 5 | P0 | GAP-V2-013, GAP-V2-017 |
| Q098 | J | 4 | 5 | P0 | GAP-V2-024 |
| Q099 | J | 4 | 5 | P0 | GAP-V2-018, GAP-V2-020, GAP-V2-023 |
| Q100 | J | 4 | 5 | P0 | GAP-V2-001, GAP-V2-004, GAP-V2-013, GAP-V2-015, GAP-V2-017, GAP-V2-018, GAP-V2-020, GAP-V2-022, GAP-V2-024 |

## Category Score

| Category | Count | Answer Raw | Answer Score / 100 | Fitness Raw | Fitness Score / 100 |
|---|---:|---:|---:|---:|---:|
| A Product / Domain / Requirement | 10 | 28 | 56.0 | 38 | 76.0 |
| B Conceptual Architecture / Necessity | 10 | 37 | 74.0 | 43 | 86.0 |
| C Agent Runtime / Planning / Multi-Agent | 15 | 50 | 66.7 | 65 | 86.7 |
| D Knowledge / RAG / Graph / Memory | 15 | 54 | 72.0 | 70 | 93.3 |
| E Data / State / Database / Consistency | 10 | 38 | 76.0 | 47 | 94.0 |
| F Tool Runtime / Sandbox / Security | 10 | 38 | 76.0 | 49 | 98.0 |
| G Failure / Retry / Recovery / Idempotency | 10 | 37 | 74.0 | 49 | 98.0 |
| H Microservice / Scale / Deployment | 8 | 32 | 80.0 | 36 | 90.0 |
| I Observability / Eval / Benchmark | 7 | 27 | 77.1 | 35 | 100.0 |
| J Engineering Reality / Interview Attack | 5 | 20 | 80.0 | 25 | 100.0 |

## Round Total

```text
question_count: 100
answer_raw_score: 361 / 500
answer_normalized_score: 72.2 / 100
fitness_raw_score: 457 / 500
fitness_normalized_score: 91.4 / 100
p0_count: 58
p1_count: 42
unsupported_count: 0
unsupported_rate: 0.00
critical_gate: OPEN
decision: NOT_PASSED_PENDING_USER_GATE
```

高 Fitness 分数不能抵消 P0 Critical Gate。当前 Critical Open 包括：真实业务/QA事实、Domain/Runtime reconciliation、Tool Effect unknown outcome、Security enforcement、服务边界证据、A/B/C 与 Graph/Memory Benchmark、个人贡献细节和 Current Runtime Trace。

## Pass Gate

本轮不通过。原因不是 72.2 的回答分数低，而是存在未关闭 P0：Canonical State Ownership 的实现证据、不可逆副作用对账、安全/审批绕过测试、重复执行、跨服务一致性和 Evidence/Citation Integrity 尚未由运行证据关闭。

## Campaign Quality Profile

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | p0_count | p1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| PRODUCT_DOMAIN | 10 | 2.80 | 3.80 | 5 | 4 | 0 | 0.00 |
| CONCEPTUAL_ARCHITECTURE | 10 | 3.70 | 4.30 | 6 | 4 | 0 | 0.00 |
| AGENT_RUNTIME | 15 | 3.33 | 4.33 | 7 | 8 | 0 | 0.00 |
| KNOWLEDGE_RAG_MEMORY | 15 | 3.60 | 4.67 | 7 | 8 | 0 | 0.00 |
| DATA_STATE_CONSISTENCY | 10 | 3.80 | 4.70 | 7 | 3 | 0 | 0.00 |
| TOOL_SANDBOX_SECURITY | 10 | 3.80 | 4.90 | 8 | 2 | 0 | 0.00 |
| FAILURE_RECOVERY | 10 | 3.70 | 4.90 | 8 | 2 | 0 | 0.00 |
| MICROSERVICE_DEPLOYMENT | 8 | 4.00 | 4.50 | 2 | 6 | 0 | 0.00 |
| OBSERVABILITY_EVAL | 7 | 3.86 | 5.00 | 3 | 4 | 0 | 0.00 |
| ENGINEERING_INTERVIEW | 5 | 4.00 | 5.00 | 5 | 0 | 0 | 0.00 |

question_count: 100
avg_answer_defensibility: 3.61
avg_architecture_project_fitness: 4.57
p0_count: 58
p1_count: 42
unsupported_count: 0
unsupported_rate: 0.00

## Campaign Summary

coverage_status: COMPLETE_FOR_V2_PROTOCOL
p0_total: 58
p1_total: 42
reopened_gap_count: 0
decision: NOT_PASSED_PENDING_USER_GATE

## Baseline Delta

- 相比旧 Round，V2 明确固定 100Q 配额、逐题 Blue Contract、0–5 Red Score、Complexity Card 和 Critical Gate。
- 本轮基线为 `main@1155d696`，不是旧会话的历史代码基线；旧 `RB-ARCH-001` 仅作为 parent/baseline session。
- 本轮不把 Round 分数、Blue Proposal 或历史会话改写为 Canonical Architecture。

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/gaps.md`

# ROUND-001 Gaps and Blocker Burn-down

本文件把逐题 Gap 聚类；Blue Proposal 不会自动关闭 Gap。所有 Gap 当前至少是 `OPEN` 或 `BLUE_PROPOSED`，需要事实恢复、Benchmark、ADR 或实现证据后再重开评审。

## CLUSTER-001

Gap IDs: GAP-V2-001, GAP-V2-002, GAP-V2-003, GAP-V2-005
Questions: Q001, Q002, Q003, Q004, Q005, Q007, Q009, Q075, Q091, Q092, Q100
Category: FACT_GAP
Description: 法院原始工作流、客户 QA/Gold Evidence、业务验收和法律对象真实范围仍未完全恢复。
Why It Matters: 没有真实任务和人工基线，Domain、Graph、Memory 和评测都可能是技术倒推。
Required Evidence: 用户确认、旧 QA/PPT/截图/任务记录、脱敏样例、反馈协议。
User Recall Prompt: 收到什么材料、人工怎样处理、客户 Demo 具体问什么、哪类错误被指出？
Architecture Impact: 可能缩减 Matter/Finding/Review 或改变 Retrieval/Agent 优先级。
Status: OPEN
Resolution: NEEDS FACT RECOVERY

## CLUSTER-002

Gap IDs: GAP-V2-004, GAP-V2-020
Questions: Q008, Q010, Q018, Q029, Q035, Q038, Q041, Q042, Q044, Q049, Q050, Q089, Q090, Q091, Q092, Q095, Q100
Category: BENCHMARK_BLOCKER
Description: WorkBuddy+Legal Backend、Native Runtime、Graph、Memory、Single Agent 等替代方案尚无受控测量。
Why It Matters: 没有 A/B/C 和消融不能证明 Zuno Runtime 或专业组件创造增益。
Required Evidence: 固定模型/语料/工具/预算、held-out 任务、逐阶段指标、成本/延迟/调用 Trace、Reviewer 结果。
Architecture Impact: C≈B 时删除 Native Runtime；Graph/Memory/Multi-Agent 可能 DEFER/DELETE。
Status: OPEN
Resolution: NEEDS BENCHMARK

## CLUSTER-003

Gap IDs: GAP-V2-006, GAP-V2-007, GAP-V2-014
Questions: Q021, Q022, Q023, Q024, Q025, Q026, Q030, Q031, Q032, Q033, Q034, Q035, Q053, Q059, Q074
Category: RUNTIME_STATE_GAP
Description: Plan、Branch、Budget、Replan、HITL、Domain Generation 和 Runtime Checkpoint 的 Current reconciliation trace 未证明。
Why It Matters: 设计可解释不代表 Crash/Resume/Concurrent Plan 已实现。
Required Evidence: failure injection、checkpoint/domain 双写矩阵、PlanVersion/epoch/Join tests。
Architecture Impact: 可能削薄 LangGraph/Native Runtime，或先采用普通 Workflow。
Status: OPEN
Resolution: NEEDS IMPLEMENTATION EVIDENCE

## CLUSTER-004

Gap IDs: GAP-V2-009, GAP-V2-010
Questions: Q006, Q028, Q036, Q037, Q038, Q039, Q040, Q041, Q042, Q043, Q044, Q050, Q057
Category: KNOWLEDGE_GRAPH_GAP
Description: Evidence Sufficiency、Graph Projection、Index Version、Conditional Retrieval 和 Graph Kill Benchmark 未执行。
Why It Matters: Graph 可能只是投影成本，不能代替 Domain Evidence。
Required Evidence: Query Class 数据集、Vector/Hybrid/Always Graph/Conditional 对照、source span/版本/权限、错误边重建测试。
Architecture Impact: Graph 可能降为 Conditional Provider 或删除。
Status: OPEN
Resolution: NEEDS BENCHMARK

## CLUSTER-005

Gap IDs: GAP-V2-011, GAP-V2-012
Questions: Q015, Q017, Q047, Q048, Q049, Q100
Category: MEMORY_GAP
Description: Memory 的历史用途、OpenViking 接入细节、Scope/Authority/Conflict/Recall/污染和 Provider Fit 未完整恢复/验证。
Why It Matters: Memory 不能成为隐性 Domain Fact Store，也不能因为历史参与就成为 Current。
Required Evidence: 用户具体任务回忆、旧 Adapter/API/Trace、Memory benchmark、权限/污染 fault test。
Architecture Impact: OpenViking 可能只是 Provider、Matter DB+Checkpoint 可能足够。
Status: OPEN
Resolution: NEEDS FACT RECOVERY + BENCHMARK

## CLUSTER-006

Gap IDs: GAP-V2-013
Questions: Q016, Q025, Q040, Q051, Q052, Q056, Q059, Q073, Q078, Q094, Q097
Category: DATA_RECOVERY_GAP
Description: Domain DB、Projection、Cache、Checkpoint、Outbox 和 Trace 的实际 ownership/rebuild/restore 证据缺失。
Why It Matters: 多存储架构的核心风险是双写、丢失和事实冲突。
Required Evidence: owner registry、restore/rebuild、outbox、checkpoint failure 和 trace completeness tests。
Architecture Impact: 可能合并数据层或推迟服务拆分。
Status: OPEN
Resolution: NEEDS ADR + IMPLEMENTATION EVIDENCE

## CLUSTER-007

Gap IDs: GAP-V2-015, GAP-V2-016
Questions: Q027, Q033, Q043, Q048, Q061, Q063, Q064, Q065, Q066, Q067, Q070, Q096, Q100
Category: SECURITY_BLOCKER
Description: 权限前置过滤、Approval/Epoch、Tool Scope、Sandbox、Prompt Injection、Secret Trace 和 Effect Gate 尚无完整测试。
Why It Matters: 任何安全/审批绕过都是 P0，无论 Round 分数多高都不能通过。
Required Evidence: cross-tenant、revocation、injection+tool、secret leakage、sandbox boundary、stale credential、approval replay tests。
Architecture Impact: Tool/Sandbox 边界可能加强或合并，但不能移除最小安全 Contract。
Status: OPEN
Resolution: NEEDS SECURITY REVIEW

## CLUSTER-008

Gap IDs: GAP-V2-017
Questions: Q064, Q068, Q071, Q072, Q073, Q076, Q077, Q078, Q080, Q097, Q100
Category: FAILURE_BLOCKER
Description: Queue/Worker/Effect/Lease/Unknown Outcome/Retry Storm 的运行参数、故障演练和对账证据缺失。
Why It Matters: 不可逆副作用和重复执行必须有可恢复语义。
Required Evidence: idempotency key、provider operation ID、lease/fencing、DLQ、timeout/cancel、fault injection。
Architecture Impact: 可能把部分异步能力降为同步或外部化，但不能靠“重试”隐藏未知结果。
Status: OPEN
Resolution: NEEDS IMPLEMENTATION EVIDENCE

## CLUSTER-009

Gap IDs: GAP-V2-018
Questions: Q013, Q055, Q069, Q080, Q081, Q082, Q083, Q084, Q085, Q087, Q088, Q100
Category: SERVICE_BOUNDARY_GAP
Description: Microservice Target 已固定，但五服务数量、edge 物理拆分、Knowledge Worker 与 Tool/Sandbox 边界没有 workload/failure/security/lifecycle 证据。
Why It Matters: Microservice 不等于 11 模块或五服务已获批。
Required Evidence: CPU/GPU/IO、队列、SLO、失败域、安全隔离、独立发布和本地开发成本矩阵。
Architecture Impact: 五服务可合并/拆分；逻辑 capability 与 physical service 继续分离。
Status: OPEN
Resolution: NEEDS SERVICE BOUNDARY REVIEW

## CLUSTER-010

Gap IDs: GAP-V2-019
Questions: Q086, Q093, Q094
Category: DEPLOYMENT_OBSERVABILITY_GAP
Description: Developer/Staging/Production profile、Trace、Artifact、Backup/DR、HA 和 Release Rollback 未由运行证据证明。
Why It Matters: Compose/Verifier/Target 文档不能证明 Production Ready。
Required Evidence: profile E2E、load/fault/DR/security/observability/artifact evidence。
Architecture Impact: Production Profile 和 deployment technology 继续 DEFER。
Status: OPEN
Resolution: NEEDS IMPLEMENTATION EVIDENCE

## CLUSTER-011

Gap IDs: GAP-V2-022
Questions: Q005, Q011, Q012, Q014, Q016, Q017, Q019, Q020, Q034, Q045, Q100
Category: CONTRACT_GOVERNANCE_GAP
Description: Domain/Capability/Provider/Document/Service/Runtime 的唯一 Owner 和 Contract 已有 Target，但 Current conformance、mutation denial 和 Canonical Write Gate 仍需加强。
Why It Matters: 没有 Contract verifier，语义可能随 Prompt/Provider/文档漂移。
Required Evidence: schema/conformance/mutation/ownership verifier、Debate Trace 到 Canonical Path 的追踪。
Architecture Impact: Kernel 可能缩小为 Contract+Owner；文档 taxonomy 不等于行为证明。
Status: BLUE_PROPOSED
Resolution: NEEDS ADR + VERIFIER

## CLUSTER-012

Gap IDs: GAP-V2-023
Questions: Q045, Q046, Q087, Q093, Q099
Category: BUILD_BUY_LICENSE_GAP
Description: 法律研究、OpenViking、RAG/Graph/Memory Provider 的源码、模型、数据、License、升级和退出路径未完成逐项审查。
Why It Matters: Public GitHub/论文不自动等于可商业复用。
Required Evidence: official source/license、SBOM、modification surface、adapter spike、migration/exit plan。
Architecture Impact: Adopt/Extend/Build/Delete 可能改变。
Status: OPEN
Resolution: NEEDS BUILD_BUY_REVIEW

## CLUSTER-013

Gap IDs: GAP-V2-024
Questions: Q062, Q071, Q098
Category: PERSONAL_OWNERSHIP_GAP
Description: 用户确认的 Agent/Memory/OpenViking/Tool Calling 参与范围已有锚点，但具体任务、文件、输入输出、Bug、调试和验证仍未知。
Why It Matters: 不能把团队、框架或 Target 架构写成个人实现。
Required Evidence: 用户场景回忆、旧提交/任务/Review/截图；不确定部分保持 UNKNOWN。
Architecture Impact: 影响面试叙事和实施归属，不直接改变 Domain Target。
Status: OPEN
Resolution: NEEDS FACT RECOVERY

## Blocker Burn-down

| Blocker | Related Clusters | Current Decision | Owner | Status |
|---|---|---|---|---|
| Concept Blocker | 001, 002, 005 | 保持最小 Domain/Host 假设 | Product/Domain/Eval | OPEN |
| Fact Blocker | 001, 005, 013 | 进入 Fact Recovery Queue | Facts Owner / User | OPEN |
| Contract Blocker | 003, 006, 011 | 补 Contract/Mutation/Owner 验证 | Domain/Runtime/Data | OPEN |
| State Blocker | 003, 006 | 双状态、版本和 stale 对账 | Runtime/Domain | OPEN |
| Failure Blocker | 006, 008 | Receipt/Idempotency/Reconcile | Tool/Runtime/Data | OPEN |
| Security Blocker | 007 | 先做安全测试再宣称通过 | Security/Tool | OPEN |
| Data Blocker | 006 | Source/Projection/Cache/Checkpoint 分层 | Data/Knowledge | OPEN |
| Benchmark Blocker | 002, 004, 005 | A/B/C、Graph、Memory、Agent 消融 | Eval | OPEN |
| Implementation Evidence Blocker | 003, 008, 009, 010 | Trace/Fault/E2E/DR | Engineering | OPEN |

## Resolution Routing

```text
Fact Recovery：CLUSTER-001 / 005 / 013
Benchmark：CLUSTER-002 / 004 / 005
ADR / Contract：CLUSTER-003 / 006 / 011
Security Review：CLUSTER-007
Service Boundary Review：CLUSTER-009
Implementation Evidence：CLUSTER-006 / 008 / 010
Build-vs-Buy / License：CLUSTER-012
```

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/blue-change-set.md`

# ROUND-001 Blue Change Set

本文件只保存 Blue Reconstruction Proposal。当前 `User Gate=PENDING`、`Sync Status=NOT_APPLIED`，因此没有任何内容写回 `docs/project/`，也没有生成 implementation task。

## CHANGE-001

Source Cluster IDs: CLUSTER-001, CLUSTER-002, CLUSTER-005
Before: Zuno/Native Runtime/Legal Domain 作为整体产品差异候选。
Attack: WorkBuddy + Legal Backend、普通 Workflow 和 JSON + PostgreSQL 可能已经足够。
Decision: REFINE / DEFER
After: 保留 Host-agnostic 最小 Domain Contract 候选；Native Domain-aware Runtime、完整 Kernel、长期 Memory 保持 DEFERRED/HYPOTHESIS，等待 A/B/C 和 Domain mutation/review/stale 测试。
New Complexity: 需要 A/B/C harness、Contract/Owner test、退出适配。
Removed Complexity: 不默认自建完整 Host、Native Runtime、所有 Legal Objects。
Canonical Paths: `docs/project/domain/`, `docs/project/agents/`, `docs/project/eval/`, ADR-0008
Evidence Needed: A/B/C、Kill Domain/Runtime、事实工作流、review/stale trace。
Validation Run: NOT_RUN
Validation Not Run: Runtime benchmark、Domain E2E、用户 Architecture Gate。
Rollback: 删除 Native Runtime/Kernel candidate，保留 Provider Contract 和 Host integration。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-002

Source Cluster IDs: CLUSTER-004, CLUSTER-005
Before: GraphRAG、Graph、Memory 可被技术名称误认为默认关键路径。
Attack: Hybrid RAG、Matter DB + Checkpoint 和普通 Workflow 可能同等有效。
Decision: REFINE / DEFER
After: Graph 是 Conditional Provider；Memory 是 policy/contract + replaceable provider；所有收益必须按 Query Class/Scope/Task 做消融。
New Complexity: Benchmark dataset、projection rebuild 和 provider conformance。
Removed Complexity: Always-on Graph、无证据 Long-term Memory。
Canonical Paths: `docs/project/knowledge/`, `docs/project/agents/`, `docs/project/eval/`, ADR-0006/0008
Evidence Needed: Graph Kill、Memory ablation、permission/stale/rebuild tests。
Validation Run: NOT_RUN
Validation Not Run: 真实法律 QA、成本/延迟、Graph 错边 fault test。
Rollback: 固定 Hybrid/DB+Checkpoint，删除 Graph/Memory Provider。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-003

Source Cluster IDs: CLUSTER-003, CLUSTER-006, CLUSTER-008
Before: Runtime/Domain/Queue/Tool 的状态边界只在 Target 文档中描述。
Attack: partial commit、unknown effect、duplicate job 和 checkpoint mismatch 会造成业务错误。
Decision: REFINE / BUILD DELTA PROPOSAL
After: 固定 Domain State、Runtime Control、Job Delivery、Effect Receipt 四类状态；要求 generation、idempotency、provider operation ID、lease、reconcile 和 fault tests。
New Complexity: Recovery contract、fault injection、trace fields。
Removed Complexity: checkpoint/queue 作为唯一事实源的隐含假设。
Canonical Paths: `docs/project/data/`, `docs/project/services/`, `docs/project/agents/`, ADR-0010
Evidence Needed: crash matrix、outbox/lease/effect/reconcile E2E。
Validation Run: NOT_RUN
Validation Not Run: 任何业务 Runtime 修改和实际故障演练。
Rollback: 只保留设计/Gaps，不进入生产代码；失败时收缩为同步/人工对账。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-004

Source Cluster IDs: CLUSTER-007, CLUSTER-009, CLUSTER-010
Before: Tool/Sandbox、Service Count、Deployment Profile 由候选拓扑描述。
Attack: 合并服务可能足够；Sandbox/secret/permission/Production 证据缺失。
Decision: KEEP CONTRACT / DEFER PHYSICAL TOPOLOGY
After: 保留 Tool Effect/Sandbox Security Contract；五服务只作为 Candidate，按 workload/failure/security/lifecycle 证据合并或拆分；Compose 不升级 Production。
New Complexity: security tests、service boundary matrix、profile evidence。
Removed Complexity: 11 modules=11 services、Compose=Production、K8s default。
Canonical Paths: `docs/project/services/`, `docs/project/security/`, `docs/project/deployment/`, ADR-0010
Evidence Needed: sandbox escape/egress/secret/revocation、resource profile、HA/DR/trace。
Validation Run: NOT_RUN
Validation Not Run: no runtime/deployment implementation in this Round。
Rollback: merge deployables while preserving logical owner/effect receipt contracts。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-005

Source Cluster IDs: CLUSTER-011, CLUSTER-012, CLUSTER-013
Before: 文档/研究/个人贡献容易被读者当成统一事实。
Attack: Public research、历史参与、Target ownership 和个人实现边界混淆。
Decision: KEEP GOVERNANCE / FACT RECOVERY
After: 每个 Candidate 绑定 Evidence State、Evidence ID、Scope、Cannot Infer；Provider 需 License/Fit/Exit；个人贡献继续由 User/Artifact Gate 决定。
New Complexity: Round traceability、Complexity Cards、License ledger。
Removed Complexity: “公开仓库可商用”“参与过即负责”“Target 即 Current”的隐含叙事。
Canonical Paths: `docs/project/facts/`, `docs/governance/`, `docs/decisions/`, Lab only until User Gate
Evidence Needed: old artifacts, official licenses, user confirmations, verifier evidence。
Validation Run: NOT_RUN
Validation Not Run: Fact Recovery and Build-vs-Buy review。
Rollback: 保持 UNKNOWN/DEFERRED，不删除历史材料。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## Canonical Write Gate

```text
Question traceability + Red objection + Blue answer + Red score
  + Decision + Open risk + Required evidence + User Gate
  → only then Canonical Sync
```

本轮所有 Change 都是 `NOT_APPLIED`；不存在 Canonical Docs Changed，也不存在由 Round 自动产生的架构事实。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/retest.md`

# ROUND-001 Counter Attack / Retest

本文件记录 Counter Attack 的设计和当前状态。由于 Blue Change Set 尚未通过 User Gate，所有 Retest 都是 `NOT_STARTED`，不伪装成已经验证。

## RETEST-001

上一轮 Gap: GAP-V2-004, GAP-V2-020
Change IDs: NONE
Mutation Variable: 将 C 与 B 的模型、语料、工具、Token/Time Budget 固定，并加入 WorkBuddy Host + Legal Backend 与 Native Runtime 的同任务比较。
Red Counter Attack: 如果 C 只是在 Runtime 内重复 B 已完成的 Domain Conditions、Evidence Gate 和 Reconciliation，C 不能因 first-class 命名保留；如果 C 只增加 Calls/Latency/Cost，也必须删除或外部化。
Expected Evidence: A/B/C preregistration、trace、quality/efficiency metrics、attribution report。
Result: NOT_STARTED
Status: OPEN

## RETEST-002

上一轮 Gap: GAP-V2-013, GAP-V2-017
Change IDs: NONE
Mutation Variable: 在 Domain Commit、Checkpoint、Queue ACK、Tool Provider Success 四个交叉点注入 crash/timeout/restart。
Red Counter Attack: 如果任一恢复路径把 Node complete 当业务完成、把 timeout 当失败或盲目重试不可逆 Effect，Runtime/Tool/Data Contract 不能通过。
Expected Evidence: fault injection、EffectReceipt、provider operation ID、idempotency/reconcile trace。
Result: NOT_STARTED
Status: OPEN

## RETEST-003

上一轮 Gap: GAP-V2-015, GAP-V2-016
Change IDs: NONE
Mutation Variable: 注入恶意 PDF/Memory/Observation、撤销父 Grant、修改 ToolVersion/参数和改变 Approval Epoch。
Red Counter Attack: 如果内容能改变授权、旧审批能执行新参数或 Secret 出现在模型/Trace/Memory，安全 Gate 仍然 OPEN。
Expected Evidence: injection+tool、cross-tenant、revocation、stale credential、secret leakage、version mismatch tests。
Result: NOT_STARTED
Status: OPEN

## RETEST-004

上一轮 Gap: GAP-V2-018
Change IDs: NONE
Mutation Variable: 低用户数/单节点、重 CPU/GPU ingestion、长 Agent Run、Sandbox 高风险 effect 和独立发布分别施加资源/故障约束。
Red Counter Attack: 如果五个服务没有独立 scaling/failure/security/lifecycle收益，必须合并物理部署；如果 Knowledge/Sandbox 有强边界，不能用“一个服务更简单”掩盖风险。
Expected Evidence: workload/failure/security/deployment matrix and cost/latency comparison。
Result: NOT_STARTED
Status: OPEN

## RETEST-005

上一轮 Gap: GAP-V2-001, GAP-V2-002, GAP-V2-024
Change IDs: NONE
Mutation Variable: 只允许用户确认、Artifact 或仓库证据升级 Historical Claim；拒绝用 Target/论文/团队工作补齐个人贡献和法院 QA。
Red Counter Attack: 如果架构回答需要虚构客户流程、QA 数量、个人文件或生产指标，返回 Fact Recovery，而不是继续 Blue Architecture。
Expected Evidence: user confirmation/artifact ledger/commit-task mapping。
Result: NOT_STARTED
Status: OPEN

## 当前结论

`counter_attack_status: WAITING_FOR_USER_GATE`。当前下一执行阶段是 `RB-BLUE-REPAIR-001`，不是
Round-002。Repair Closure、Final P0、Evidence 和 User Architecture Gate 通过后，才重新设计
Round-002；届时至少 70% 是新问题，最多 30% Regression，不能因为 Round-001 分数较高而降低攻击难度。

---

## Decisions / Gaps / Retest: `project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001/round-report.md`

# ROUND-001 Report

## Round Metadata

- Round：`ROUND-001`
- Protocol：`ZUNO-RED-BLUE-WORKFLOW-V2`
- Base SHA：`1155d696fa0dcc08a7682f3c873c345cfccf016a`
- Fact Baseline：`4b960408f0693a42edd9a1a89accb98ac49d1edc`
- Questions：100 / 100
- Categories：A10 / B10 / C15 / D15 / E10 / F10 / G10 / H8 / I7 / J5

## Scores

- Answer Raw：`361 / 500`
- Answer Normalized：`72.2 / 100`
- Architecture Fitness Raw：`457 / 500`
- Architecture Fitness Normalized：`91.4 / 100`
- P0：58
- P1：42
- Unsupported：0（仅表示本 Round 没有另行标记 unsupported，不代表历史事实完整）
- Round Result：`NOT_PASSED_PENDING_USER_GATE`

## Strongest Surviving Principles

- Facts Structure Frozen；Fact Content 继续通过 Evidence/Memory Recovery 增量恢复；
- Domain State、Runtime Control、Knowledge Projection、Memory、Tool Effect 分离；
- Provider 只能产生 Proposal/Candidate/Observation/Reference/Receipt；Canonical Owner 才能提交业务事实；
- WorkBuddy/Dify/普通 Workflow + Legal Backend 仍是有效简化基线；Native Runtime 不能默认保留；
- Graph、Memory、Multi-Agent、LangGraph、物理服务数量和基础设施都必须通过 Kill Test/Benchmark；
- Microservice 是 Target Constraint，但 11 Logical Modules 不等于 11 Services，五服务仍是 Candidate；
- Tool Effect、Approval、Security、Idempotency、Receipt、Recovery 是不能用“少一个服务”隐去的复杂性。

## Killed / Deferred in this Round

| Candidate | Round disposition |
|---|---|
| 11 modules = 11 services | DELETE |
| Native Domain-aware Runtime as default | DEFER / HYPOTHESIS |
| Always-on GraphRAG | DEFER / CONDITIONAL PROVIDER |
| Persistent Multi-Agent Team | DEFER |
| Long-term Memory as default | DEFER |
| Event Sourcing / 2PC / Saga / Kubernetes / Kafka / Mesh by default | DEFER |
| WorkBuddy + Legal Backend as kill baseline | KEEP AS COMPETITOR BASELINE |
| Tool/Sandbox Effect Contract | KEEP AS NECESSARY COMPLEXITY CANDIDATE |

## Open Fact Gaps

法院原始工作流、QA/Evaluation 协议、质量错误分类、个人代码级 Ownership、OpenViking 具体改动、历史中间件主链路、真实服务/部署规模均未因本 Round 自动升级。

## Open Architecture Gaps

Domain Kernel 是否超出 Contract+Owner、Native Runtime 相对 Host+Backend 的收益、Graph/Memory/Multi-Agent 增益、五服务边界、Runtime/Domain/Effect 对账和 Security enforcement 仍未关闭。

## Canonical Sync

```text
Canonical Docs Changed: NONE
ADR Changed: NONE
Facts Changed: NONE
User Gate: PENDING
```

## Next Phase Focus（Round-002 暂缓）

先执行 `project-reconstruction-lab/sessions/RB-BLUE-REPAIR-001/`：

1. 10 个 Root-Cause Cluster 与 Part-A Blue Repair；
2. Severity Reclassification 和 P0 Burn-down；
3. Domain State/Effect/Checkpoint 的 fault matrix；
4. Tool/Sandbox security and unknown-effect reconciliation；
5. 真实法院任务、Court QA 和个人贡献的 Fact Recovery；
6. Counter Retest、Round Closure 和 User Architecture Gate。

只有 Repair Closure 满足 Gate 后，才重新设计 Round-002 的至少 70% 新问题。

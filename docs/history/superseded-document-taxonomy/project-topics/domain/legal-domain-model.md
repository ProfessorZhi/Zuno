# Legal Domain Model：法律业务世界是什么？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 哪些对象和版本代表法律业务世界中的正式事实？
owner: Legal Domain Owner
replaces: docs/project/modules/01-product-surface.md、03-knowledge-agentic-graphrag.md 中重复的领域描述（Superseded）

## Part A — Architecture Narrative

### 什么才算法律业务事实

Legal Domain Model 不是 LLM、Prompt、Knowledge Base、Memory、Skill、Tool、Graph 或 LangGraph State。它是系统对 Matter 中业务对象、来源、版本、依赖、权限和人工判断的正式表示。Fact、Evidence 或 Finding 是否成立，不由模型置信度单独决定，而由 Canonical Owner 按来源、版本、权限和审查规则决定。

### Target Scenario：从证据到 Finding

这是 Target Scenario，不是历史事实：

新的 EvidenceVersion 被接收后，解析和法律能力产生 FactProposal、ConflictProposal 或 FindingProposal。Proposal 带 EvidenceReference、SourceSpan、Provider、算法版本和输入 DomainVersion，先进入 Domain Admission。Domain Owner 验证 Schema、Provenance、Permission、Dependency 和 Version/CAS；需要人工判断时进入 Review。只有通过 Admission 的对象才能形成 FactVersion、ConflictVersion 或 FindingVersion，之后才能被 WorkProduct 引用。

### 最小对象和概念边界

Matter、Case、Party、DocumentVersion、Claim、Fact、Event、Evidence、Conflict、Dispute、LegalIssue、StatuteVersion、LegalElement、ApplicableLaw、SimilarCase、Finding、HumanDecision 和 WorkProduct 是候选业务对象。Canonical 只保留能拥有 identity、version、provenance、state、dependency、review 或 audit 责任的对象；检索命中、Graph Path、Embedding、Memory Entry 和 Agent Step 是 Projection、Context 或 Runtime Object，不应膨胀成业务事实。

### 责任与非责任

Domain Owner 负责正式对象、版本、依赖、stale 传播和 Mutation Authority；Knowledge 负责 Source、Index、Citation 和 Candidate；Legal Capability Provider 负责 Observation/Proposal；Runtime 负责执行位置和预算；Security 负责授权；Review 负责必要的 HumanDecision。Domain Model 不负责选择模型、保存 Checkpoint、拥有 Graph、直接执行 Tool 或复制 Memory 系统。

### 为什么需要正式 Domain Model

普通 JSON 加 PostgreSQL 可以作为实现起点，但如果没有稳定 Owner 和 Admission Contract，任何 Agent 或 Tool 都可能把自由文本写成事实，版本变化也无法传播。Formal Model 的成本是 Schema、CAS、Provenance、Review 和迁移；它只有在跨文档分析、证据链、stale 和人工责任确实需要时才成立。若简单 JSON 加单一事务边界能通过同样的质量、恢复和审计测试，应缩减对象数量和 Domain Kernel。

### 失败、替代与反转

错误来源、过期材料、权限变更、重复 Proposal 或版本冲突都必须阻止静默提升。WorkBuddy + Zuno Backend 可以消费这些 Contract，不要求 WorkBuddy 持有 Canonical State。若外部 Host 通过普通 JSON Tool 已经能保持相同的版本、证据、审查和审计语义，Native Domain Runtime 不应继续存在。当前正式对象仍是 Target 设计，仓库模型不等于历史项目或生产事实。

### Current / Target / Gap

Current 以代码、Migration、测试和 Trace 为准；Target 是最小法律 Domain Kernel 和 Provider Proposal 边界；Hypothesis 是结构化 Domain State 对复杂任务质量、复用和恢复的贡献；Gap 是对象收敛、用户验证、Admission Test、stale 传播和真实法律评测。

## Part B — Detailed Architecture Specification

### Minimum Canonical Objects

| 对象 | 必要字段语义 | Mutation Authority |
|---|---|---|
| Matter/Case | identity、tenant、scope、status、owner | Domain |
| DocumentVersion | content hash、source、version、ACL、parser reference | Domain/Knowledge handoff |
| Evidence/Fact/Event | version、provenance、dependency、state、review | Domain |
| Conflict/Dispute/LegalIssue | related objects、reason、version、review state | Domain |
| StatuteVersion/LegalElement | jurisdiction、effective period、source | Legal Knowledge/Domain admission |
| Finding | claim、supporting evidence、applicability、version、review | Domain |
| HumanDecision/WorkProduct | reviewer、decision、source versions、delivery | Domain/Product |

### Canonical Admission Contract

Proposal 输入必须包含 proposal_id、matter_id、object_type、payload、source_references、input_domain_version、provider、provider_version、confidence/explanation、permission_context 和 idempotency_key。输出只能是 accepted_version、review_required、rejected、conflict 或 stale。Provider 不能直接写 FactVersion、FindingVersion 或 HumanDecision。

The write rule is simple: Provider produces Proposal; only Domain Owner writes Canonical Version。换言之，专业算法、模型和外部 Provider 都只能提交候选，不能绕过 Schema、Provenance、Permission、Version 和 Review 直接改变业务事实。

### Version、CAS 与 Staleness

每个 Canonical Object 使用 identity 加版本；Admission 通过 compare-and-set 检查 input_domain_version。新 EvidenceVersion 按 dependency graph 使受影响 Fact、Conflict、Dispute、ApplicableLaw 和 Finding 标记 stale 或 review_required。重新评价可以由 bounded Agent Run 触发，但触发本身不等于新事实提交。

### Storage、Security 与 Audit

PostgreSQL 是 Target System of Record；检索、Graph、Memory 和 Runtime 只能保存 Projection/Context/Control State。所有 Mutation 绑定 Tenant、Matter、Scope、Principal、Policy Epoch、Provenance 和 Trace。Audit 保留旧版本、来源、Admission Decision、Reviewer 和原因；法律保留或删除规则不得删除必要的审计链。

### Failure、Retry 与 Recovery

Admission failure、version_conflict、provenance_missing 和 permission_denied 必须作为 typed failure 返回；只有相同 Proposal 且幂等键不变的 transient validation 才能 bounded retry。恢复时重新读取 DomainVersion 和来源，不能把失败的 Proposal 直接提升为 Canonical Version。

### Testing and Evidence

必须测试重复 Proposal、错误来源、跨租户引用、CAS 冲突、新证据 stale、权限撤回、Review 驳回和恢复重放。Current 证据由实现和测试提供；Domain Quality、Legal Capability 增益和 Native Runtime 价值必须通过 A/B/C 或对象级 Benchmark 证明。

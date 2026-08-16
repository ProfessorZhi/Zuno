# 02 Legal Domain & Work Product（法律领域与工作成果）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 什么东西才值得成为长期业务事实

模型可以在一分钟里生成很多“事实”“争议点”和“适用法条”，但法律专业工作不能把每次模型输出都当成正式结果。真正需要长期保存的是：这次工作处理的是哪个事项、使用了哪一版材料、哪些主张和证据被正式接受、形成了什么结论、谁做了人工业务决定，以及最终交付了哪一版工作成果。

因此这个模块不是一个“LLM 输出数据库”，也不是试图一次性建立完整法律本体，而是法律业务世界的权威状态边界。

### 最小领域内核为什么要保持小

第一阶段只把七类对象当作 Canonical（正式领域对象）：Matter（事项）、DocumentVersion（材料版本）、Claim（主张）、Evidence（证据）、Finding（结论）、HumanDecision（人工决定）和 WorkProduct（工作成果）。

Event、Conflict、Dispute、LegalIssue、ApplicableLaw、SimilarCase 等仍然可以很重要，但默认先作为候选、派生视图或专业能力输出。只有未来证明它们需要独立身份、版本、来源、权限、依赖、失效、审核和审计，才值得升级为新的正式领域对象。

这样做的目的不是把法律问题简化，而是避免模型每多抽出一个概念，数据库就多一套长期状态机。

### 候选结果怎样变成正式结果

复杂分析通常先得到结论候选。领域模块检查它关联的材料版本、证据、当前权限、必要的人审和预期前置领域版本；条件成立后才进行正式准入。

正式提交不能只留下“数据库里多了一行”。它还要同时留下 AdmissionReceipt（正式准入回执），证明是哪次运行、哪一版计划、哪个步骤和哪个候选结果导致了哪个新的领域版本。领域变更与这份回执必须处在同一个 PostgreSQL 事务耐久边界中。

### 人工业务决定和安全审批为什么不同

HumanDecision（人工业务决定）表示专业人员对法律结果的确认、修改或拒绝，是领域事实的一部分。ApprovalDecision（安全审批决定）回答某个高风险动作当前是否获准执行，属于安全与治理。

同一个人可能在界面上连续点击“审核通过”和“允许提交”，但系统仍要保存两个不同的事实：前者改变法律业务结果的权威状态，后者只允许某个动作发生。

### 为什么检查点不能替代领域事实

智能体运行时可能在“领域提交成功、检查点还没更新”时崩溃。恢复时应读取已经提交的领域版本和正式准入回执，再修复运行控制状态。反过来，如果检查点写着 completed，但找不到匹配的正式准入回执，就不能宣布正式业务提交已经发生。

这条规则避免了两个系统互相猜测对方是否成功，也不需要在 PostgreSQL 与 LangGraph Checkpointer 之间引入跨存储两阶段提交。

### 历史引用为什么也归领域

知识与证据负责说明“当时怎样检索到这段材料”，但一份正式工作成果发布以后，它过去真正引用的是哪一版材料、哪个稳定位置，不能随着索引重建而改变。因此正式成果的 Historical Citation Binding（历史引用绑定）由领域侧持久化；向量 ID、Chunk ID、Graph Node ID 不能成为长期引用权威。

### 新证据怎样影响旧结果

新材料或新证据进入后，系统根据正式依赖关系找到受影响的结论和工作成果，把它们标记为失效或需要复核，并只对受影响部分重新分析。新的分析仍然先形成候选，再经过准入产生新版本；不能直接覆盖旧版本，让过去发生过的专业判断失去历史可解释性。

法律领域拥有“某个工作成果版本已经失效”的事实，但不负责外部通知是否已经送达；通知状态属于应用与集成。

### 为什么值得独立成一个责任域

如果领域事实放进运行时，任务结束后业务真相就和某个框架的 checkpoint 绑死；如果放进知识库，检索索引就会获得它不该拥有的业务权威。独立领域边界让模型、检索、Agent Runtime 和 Host 都可以被替换，而正式法律工作仍有稳定语义。

### 当前、目标与缺口

Current Evidence 已证明有限的 Canonical Domain Mutation：领域准入边界、CAS 版本冲突、幂等 mutation、事务失败不推进版本，以及 SQLAlchemy 持久化路径；Citation Provenance Guard 也能验证 Claim→Evidence→SourceSpan→DocumentVersion 的部分关系。真实 PostgreSQL 并发、完整 AdmissionReceipt、工作成果版本生命周期、跨运行失效传播和正式 HumanDecision E2E 仍未完整证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Canonical kernel**：Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct。

**Owns**：Domain Version、Formal Admission、AdmissionReceipt、WorkProduct historical citation binding、domain invalidation truth、正式依赖与失效语义。

**Does not own**：CitationLineage、Runtime Checkpoint、Authorization / Approval policy、Tool Effect truth、Delivery/Ack state。

### B2 Inputs / Outputs

输入：候选结果、Evidence / Citation references、Authorization refs、必要 HumanDecision、run / plan / step causation、expected prior domain version、idempotency identity。

输出：新的 Canonical Version、AdmissionReceipt、historical citation binding、domain invalidation fact、typed domain snapshot/reference。

### B3 Cross-boundary Contracts

沿用 `AdmissionReceipt`、`WorkProductCitationBinding`、`WorkProductInvalidationFact` 以及 Security / Knowledge / Runtime 已拥有的引用。本骨架不新增 Canonical Object。

### B4 State / Lifecycle

领域对象必须支持身份、不可变历史版本或受控版本演进、来源、依赖、人工业务决定、失效和审核。具体 enum 在模块深设计时冻结；不得为了方便把所有 Proposal 自动升级为正式对象。

WorkProduct 新版本不得静默覆写旧版本；Finding/WorkProduct 的 staleness / review requirement 必须能追溯到新的 Evidence/DocumentVersion 依赖变化。

### B5 Failure / Recovery / Idempotency

- expected DomainVersion 不匹配：版本冲突，不覆盖写。
- 同一 idempotency identity + 同一输入：返回既有结果。
- 同 key 不同输入：拒绝。
- 缺证据、缺必要 HumanDecision 或授权失效：不准入。
- Domain commit + Receipt 成功、Checkpoint 失败：Receipt 驱动控制状态修复。
- Checkpoint 完成、Receipt 缺失：不得声明 Formal Admission 成功。

### B6 Security / Persistence / Observability

PostgreSQL 保存 Canonical Domain State 和正式准入因果；默认不引入 Event Sourcing。生命周期政策由 Security & Governance 决定，领域存储负责执行自身部分并留下执行状态/回执。Telemetry 可引用 Domain Version / Receipt，但不能替代它们。

### B7 Current / Target / Gap

Current 见 [`implementation-wave-001.md`](../evidence/implementation-wave-001.md)。Target 是完整七对象领域内核、正式准入、历史引用和失效传播。Gap 包括真实 PostgreSQL 集成/并发、HumanDecision E2E、WorkProductVersion、Admission causation fault injection 和新证据局部重评。

### B8 Code / Database / Migration Constraints

后续设计必须先冻结对象身份、版本、依赖、准入和失效语义，再讨论 ORM、表和 Migration。不得仅因为数据库已有字段就把 Proposal 概念升级为 Canonical，也不得仅因为某个法律概念在 Prompt 中常见就新增正式聚合根。

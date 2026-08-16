# 02 Legal Domain & Work Product（法律领域与工作成果）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 什么东西才值得成为长期业务事实

模型可以在一分钟里生成很多“事实”“争议点”“法条”和“结论”，但法律专业工作不能把每次模型输出都当成正式结果。真正需要长期保存的是：这次工作处理的是哪个事项、使用了哪一版材料、哪些主张和证据被正式接受、形成了什么结论、谁做了人工业务判断，以及最终交付了哪一版工作成果。

法律领域与工作成果模块因此不是一个“LLM 输出数据库”，而是 Zuno 对法律业务世界的权威状态边界。运行时可以重启，向量库可以重建，模型可以替换；正式业务事实不能因此失去身份、版本和来源。

### 七对象最小内核不是完整法律本体

第一阶段只把七类对象当作 Canonical（正式领域对象）：Matter（事项）、DocumentVersion（材料版本）、Claim（主张）、Evidence（证据）、Finding（结论）、HumanDecision（人工业务决定）和 WorkProduct（工作成果）。

Event、Conflict、Dispute、LegalIssue、ApplicableLaw、SimilarCase 等仍然可以很重要，但默认先作为候选、派生视图或专业能力输出。只有未来证明某类对象需要独立身份、版本、权限、依赖、失效、审核和审计，才值得升级为新的正式领域对象。

这条约束是为了防止“因为模型能抽取，所以数据库就要建表”的对象膨胀。领域内核只保存真正需要长期业务权威的东西，而不是把所有中间推理都永久化。

### Evidence 为什么既来自知识模块，又属于正式领域对象

知识与证据可以返回 `EvidenceCandidate`（证据候选）和检索引用链，表示“系统在当前材料范围里找到了什么”。但证据候选是否被正式接纳为某个事项、主张或结论的业务证据，是领域决定。

因此检索结果不能直接成为正式 Evidence。正式 Evidence 至少要绑定明确的材料版本、稳定来源位置、必要的权限和来源信息，并在准入后进入领域版本关系。知识模块保留“怎么找到的”，领域模块保留“最终正式采用了什么”。

### 候选结果怎样变成正式结果

复杂分析通常先得到结论候选。领域模块不会因为模型“置信度高”就自动提交，而是检查材料版本、证据、当前授权、必要人工复核、幂等身份和预期前置领域版本。条件成立后才执行 Formal Admission（正式准入）。

正式提交不能只留下“数据库里多了一行”。它必须同时留下 `AdmissionReceipt`（正式准入回执），证明是哪次运行、哪一版计划、哪个步骤、哪个候选结果和哪个幂等身份导致了哪个新的领域版本。领域变更和回执必须位于同一个 PostgreSQL 事务耐久边界。

### HumanDecision 和安全审批不是同一件事

HumanDecision 表示专业人员对法律业务结果的确认、修改、拒绝或其他正式判断，属于领域事实。`ApprovalDecision`（审批决定）则回答“某个高风险动作是否允许执行”，属于安全与治理。

一个人可能在同一界面里先审查法律结论、再批准外部提交，但这两个点击背后的语义完全不同。前者改变业务世界承认什么，后者改变某个动作是否允许发生，不能因为都由“人”完成就共用一个状态。

### 为什么检查点不能替代领域事实

运行时可能在“领域提交和正式准入回执已经成功，但检查点还没更新”时崩溃。恢复时应读取已经提交的领域版本和匹配回执，再修复运行控制状态。反过来，如果检查点写着 completed，但找不到匹配回执，就不能宣布正式业务提交已经发生。

更高的领域版本也不自动证明当前 Step 成功，因为它可能来自另一次运行。恢复必须匹配 run、plan version、step run、proposal / admission 和 idempotency 等因果身份，而不是只比较“版本号变大了没有”。

### 历史引用为什么归领域

知识与证据负责说明“当时怎样检索到这段材料”，但一份正式工作成果发布以后，它过去真正引用的是哪一版材料、哪个稳定位置，不能随着索引重建而变化。因此正式成果的 Historical Citation Binding（历史引用绑定）由领域侧持久化。

长期引用应能回到不可变 DocumentVersion、稳定 source location / span、来源表示或 hash，以及必要的 excerpt / evidence hash。Chunk ID、Vector ID、Graph Node ID 和当前索引 identity 都可以重建或变化，不能成为长期引用权威。

### 新证据出现以后为什么不能覆盖旧结果

昨天 Evidence V1 可能支持 Finding V3 和 WorkProduct V5。今天出现 Evidence V2 后，系统需要沿正式依赖关系找到受影响的结论和工作成果，把旧版本标记为失效或需要复核，再对受影响部分进行 bounded re-evaluation（有界重新评估）。

V5 仍然是历史上真实存在并曾经交付过的版本，不能被新版本静默覆盖。领域模块拥有“哪个版本当前有效、哪个版本已经失效”的事实；应用与集成负责把失效通知送出去，消费者是否确认又是另一个事实。

### 为什么值得独立成一个责任域

如果领域事实放进运行时，任务结束后业务真相就和某个框架的 checkpoint 绑死；如果放进知识库，检索索引会获得不该拥有的业务权威；如果让模型直接写库，则不确定性会穿过所有门禁直接污染长期事实。

独立领域边界让模型、检索、Agent Runtime、Host 和底层数据库实现都可以演进，而正式法律工作仍保留稳定的身份、版本、来源、人工判断和恢复语义。

### 当前、目标与缺口

Current Evidence 已证明有限的 Canonical Domain Mutation：领域准入边界、CAS 版本冲突、幂等 mutation、事务失败不推进版本，以及 SQLAlchemy 持久化路径；Citation Provenance Guard 还能验证 Claim→Evidence→SourceSpan→DocumentVersion 的部分关系。真实 PostgreSQL 并发、完整 AdmissionReceipt、HumanDecision E2E、WorkProduct 生命周期、跨运行失效传播和新证据局部重评仍未完整证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

本模块是正式法律业务状态唯一权威边界。七对象最小内核不自动扩张；模型 / 检索 / Capability / Specialist 只产生候选；正式准入需要领域校验和耐久因果；历史版本不得被覆盖；领域事实不依赖 Runtime Checkpoint 存活。

### B2 Responsibility / Ownership

**Canonical kernel**：Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct。

**Owns**：Domain Version、Formal Admission、AdmissionReceipt、正式 Evidence / Finding / WorkProduct 依赖、WorkProduct historical citation binding、domain invalidation truth、正式人工业务决定。

**Does not own**：CitationLineage、Runtime Checkpoint / Plan、Authorization / Approval policy、Tool Effect truth、Delivery / Ack state、Knowledge Generation。

### B3 Upstream / Downstream

上游主要接收 03 的证据候选和引用、05 的专业候选、04 的 run / plan / step 因果、08 的授权 / 审批引用、必要的人工业务决定。下游向 04 返回 AdmissionReceipt，向 01 返回正式 WorkProduct / invalidation fact，向 09 暴露脱敏领域版本与评测引用。

### B4 Authoritative Facts / Core Objects

每个正式对象至少需要可解释的 Identity、Version、Provenance、State、Ownership、Mutation Authority、Dependency、Staleness、Review 和 Audit 语义。具体字段后续冻结，但“独立身份和值得长期业务权威”是进入 Canonical Kernel 的前提。

`WorkProductVersion` 优先作为 WorkProduct 的版本化表达或子结构，而不是为了版本号单独增加新聚合；只有独立生命周期证据出现才扩大聚合边界。

### B5 Cross-boundary Contracts

核心跨边界 Contract：`AdmissionReceipt`、`WorkProductCitationBinding`、`WorkProductInvalidationFact`，以及对 Authorization / Approval、Evidence / Citation、run / plan / step causation 的引用。领域不复制这些上游事实，只保存必要的稳定引用和 admission evidence。

### B6 Normal Flow

proposal / evidence refs → validate material versions and provenance → validate current authorization / required HumanDecision → compare expected prior DomainVersion → idempotency check → atomic domain mutation + AdmissionReceipt → publish new domain version → emit invalidation facts for affected older results when applicable。

### B7 State / Lifecycle

详细 enum 尚未冻结，但至少要表达：版本创建、正式有效、需要复核、失效 / stale、被新版本替代但仍保留历史、人工接受 / 修改 / 拒绝等业务语义。新证据不会物理删除旧版本，而是通过依赖和有效性关系形成新的正式版本。

### B8 Failure Taxonomy

主要失败包括：expected DomainVersion 冲突、材料版本不匹配、证据不足、来源无法稳定绑定、授权失效、缺少必要 HumanDecision、同一幂等键输入冲突、事务失败、历史引用不完整、依赖失效无法安全局部重评。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

同一 idempotency identity + 同一输入返回既有结果；同 key 不同输入拒绝。版本冲突不覆盖写，由调用方重新读取当前领域版本后决定重规划或人工处理。Domain commit + Receipt 成功、Checkpoint 失败时由 Receipt 驱动 Runtime 修复；Checkpoint 完成但 Receipt 缺失时不得声明正式准入成功。

领域自身不负责外部 Effect Reconcile；如果正式结果依赖外部动作事实，只消费 06 已确认的 Effect / Reconciliation receipt。

### B10 Security / Approval / Audit

正式准入消费当前授权和必要审批 / HumanDecision 引用。HumanDecision 属于领域，ApprovalDecision 属于 08。生命周期政策由 08 决定，领域 Store 执行自身 retention / legal hold / deletion obligations，并保存执行状态或回执。

### B11 Persistence / Transaction Boundaries

PostgreSQL 保存 Canonical Domain State、不可变 / 受控版本、依赖、HumanDecision、历史引用和 AdmissionReceipt。Domain mutation 与匹配 Receipt 必须同事务提交。默认不引入 Event Sourcing，也不在 PostgreSQL 与 LangGraph Checkpointer 之间做 2PC。

### B12 Observability / Evaluation

Telemetry 至少关联 Matter、DocumentVersion、DomainVersion、Finding / WorkProduct refs、AdmissionReceipt、staleness event 和 human review outcome，但默认不导出敏感正文。评测关注 provenance completeness、citation binding correctness、unsupported admission、review acceptance、stale propagation correctness 和 recovery correctness。

### B13 Current / Target / Gap / Evidence

Current 见 [`implementation-wave-001.md`](../evidence/implementation-wave-001.md)。Target 是完整七对象领域内核、正式准入、历史引用、版本化失效和人审闭环。Gap 包括真实 PostgreSQL 集成 / 并发、Admission causation fault injection、HumanDecision E2E、WorkProduct version lifecycle、新证据 bounded re-evaluation 和 lifecycle enforcement。

### B14 Code / Database / Migration Constraints

后续必须先冻结对象身份、版本、依赖、准入、历史引用和失效语义，再讨论 ORM、表、索引和 Migration。不得因为数据库已有字段或模型能抽取某概念，就把 Proposal 自动升级为 Canonical。所有 Migration 必须保留旧版本可追溯性，不能通过 destructive rewrite 破坏已发布成果历史依据。

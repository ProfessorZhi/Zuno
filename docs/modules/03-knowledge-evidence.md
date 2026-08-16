# 03 Knowledge & Evidence（知识与证据）

<!-- status: design-baseline-v1; implementation: not-authorized -->

## Part A — Human Narrative

### 上传成功为什么不等于可以回答

用户上传一百份材料，接口返回 200，并不意味着系统已经有资格基于这一百份材料形成正式分析。PDF 可能仍在解析，扫描件可能 OCR 失败，附件可能缺失，索引也可能还对应上一版材料。

知识与证据首先解决的不是“选哪个向量库”，而是更基本的问题：**在某个明确的材料版本、任务范围和最低能力要求下，哪些内容现在真的可以被使用，系统能够从中恢复出什么证据和引用？**

### Knowledge Readiness 不是一个永久布尔值

同一份材料对于不同任务，是否“就绪”可能不同。只回答“合同第 8 条写了什么”，文本解析完成也许已经足够；如果任务要求跨附件对齐金额、读取扫描表格并建立多文档关系，仅有正文向量索引就不能视为完整就绪。

因此 Knowledge Readiness（知识就绪状态）至少要绑定材料版本、知识生成版本、任务 Scope 和当前任务要求。它回答的是“当前这次任务能否基于这组知识派生结果安全工作”，而不是给文件打一个永远不变的 `ready=true`。

### 一份材料怎样变成可用知识

应用入口接收文件后，正式材料身份和 DocumentVersion 仍由法律领域拥有。知识与证据围绕这个版本进行解析、OCR、切分、关键词 / 向量 / 图等派生处理，并形成自己的 `KnowledgeGeneration`（知识生成版本）。

新生成版本不能因为某个索引写入成功就自动成为 Serving 版本。系统需要知道这一代生成覆盖了哪些材料、采用什么处理规格、哪些子任务失败、是否通过必要完整性和来源检查，再决定它是否可以服务某类任务。

部分材料可用时，可以明确缩小任务范围返回局部结果，但不能静默把“40/100 已处理”包装成“100/100 已覆盖”。完整范围任务要等待、拒绝或明确降级。

### 检索的目标不是找最相似的句子

检索可以组合关键词、向量、重排、图视图或其他策略，但底层算法不是长期架构边界。长期要保留的是：检索针对哪一版材料、哪一代知识视图和哪个权限范围，返回了哪些 `EvidenceCandidate`（证据候选），来源位置是什么，以及当时如何得到这些候选。

`CitationLineage`（检索引用链）记录“系统当时怎样找到和排序这个候选”。如果候选最终进入正式工作成果，领域模块再把实际采用的材料版本和稳定位置绑定成长期历史引用。这样索引可以重建，已发布工作成果过去真正依赖的材料不会跟着索引漂移。

### GraphRAG 为什么不能默认常开

图结构适合表达某些跨文档实体、事件和关系，但不是所有法律问题都需要图。简单条文定位、明确关键词和局部问答可能使用 BM25 / 向量 / 重排已经足够；如果强制所有任务先构图，不仅增加生成和维护成本，也扩大 stale、重建和故障面。

因此 GraphRAG 仍是按 Query Class（问题类别）启用的条件能力。只有在固定语料、同模型和可比预算下证明某类问题稳定获益，才把图路径保留下来。

### 索引为什么可以替换

Milvus、pgvector、图存储、关键词引擎和切分算法都属于可替换的物理实现。它们应该被视为可重建的知识派生视图，而不是业务真相。

当索引损坏时，恢复重点是从不可变材料版本和知识生成规格重新构建；当正式历史引用缺失时，则不能靠“重新检索一次相似内容”补成过去发生过的事实。这两个恢复问题不能混在一起。

### 权限为什么也会影响知识结果

知识处理和检索都必须尊重当前租户、事项、材料范围和安全决定。授权变化后，旧缓存和旧检索结果不能继续被当成可用证据；同一 KnowledgeGeneration 可以物理存在，但针对当前请求的 Readiness / Retrieval 仍必须重新经过有效范围判断。

安全与治理拥有“是否允许访问”的决定，知识模块负责在自己的处理、检索和 Serving 边界执行这个决定，不能用“索引里已经有了”作为越权理由。

### 出问题以后怎样恢复

解析失败要精确到材料或页面层级，不把失败吞成一个空字符串；部分索引写入不能自动激活新 generation；旧 generation 不能冒充新 DocumentVersion；来源无法稳定绑定时，候选不能进入正式引用链；索引损坏可以重建，但重建后仍要重新验证完整性和 Serving 资格。

如果当前任务只依赖未受影响的材料，可以在显式缩小 Scope 后继续；如果缺失内容影响完整性，则必须等待、拒绝或返回明确不完整结果。

### 为什么值得独立成一个责任域

把知识派生放进法律领域，会让领域状态被向量库、切分算法和图实现污染；把它完全塞进运行时，又会丢失版本、就绪、来源和索引切换的长期治理。

独立知识边界让上层只依赖“哪些材料可用、找到了什么证据、引用怎样恢复”这些稳定语义，而不用知道底层到底是 BM25、向量、GraphRAG 还是未来的其他 Provider。

### 当前、目标与缺口

Current Evidence 已能证明部分 Citation Provenance Guard、stale / scope 检查以及产品 ingestion 的持久化入口；仓库也已有索引和 GraphRAG 相关实现表面。但真实数据库 lineage lookup、完整 Knowledge Readiness、跨版本 ingestion、原子 Serving 切换、全量 fault recovery、GraphRAG query-class 收益和生产索引迁移仍未完整证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

本模块拥有可重建知识派生的语义，不拥有正式材料身份和法律业务结果。`Document Uploaded != Knowledge Ready`；Readiness 不是文件级永久布尔值；物理索引写成功不等于 generation 已激活；Chunk / Vector / Graph ID 不成为长期 Citation Authority。

### B2 Responsibility / Ownership

**Owns**：material processing projection、KnowledgeGeneration / KnowledgeView、ReadinessDecision、EvidenceCandidate、RetrievalResult、CitationLineage、IndexManifest / Serving Watermark 的知识语义。

**Does not own**：DocumentVersion canonical identity、Finding / WorkProduct、formal Evidence admission、historical WorkProduct citation authority、Security policy、底层存储本身的业务成功语义。

### B3 Upstream / Downstream

上游主要接收 02 的 DocumentVersion reference、08 的 Authorization / Security Epoch、01 / 04 的 task Scope 与 retrieval requirement，以及 Platform 返回的物理处理 / 索引回执。下游向 01 / 04 返回 ReadinessDecision，向 04 / 05 / 02 返回证据候选与检索引用链，向 09 输出检索与 ingestion 评测引用。

### B4 Authoritative Facts / Core Objects

核心对象族包括 KnowledgeGeneration、processing item / projection、IndexManifest、Serving Watermark、ReadinessDecision、EvidenceCandidate、RetrievalResult、CitationLineage。具体数据库形态未冻结；关键是每个结果能绑定 source DocumentVersion、generation、scope 和处理规格。

### B5 Cross-boundary Contracts

沿用总体架构中的 Readiness、Evidence / Citation reference，以及现有 Registry 的 Index Spec / Manifest / Write Receipt / Serving Watermark 边界。正式 WorkProduct 只保存必要的 CitationLineage reference，长期引用权威由 02 的 `WorkProductCitationBinding` 负责。

### B6 Normal Flow

DocumentVersion ref → processing spec / generation identity → parse / OCR / normalize → build derived views → collect per-item receipts → validate completeness / lineage → stage manifest → activate serving generation → evaluate readiness for task scope → retrieve / rerank / optional graph path → EvidenceCandidate + CitationLineage。

### B7 State / Lifecycle

详细 enum 未冻结，但至少区分：未处理 / 处理中、部分成功、生成已构建但未激活、Serving generation、stale generation、失败 / 需重建，以及针对具体任务的 ready / partial / blocked 结果。Generation 生命周期和 task-level Readiness 必须分开。

### B8 Failure Taxonomy

主要失败包括 parsing / OCR failure、附件缺失、partial index write、manifest 不完整、来源位置不稳定、stale generation、serving watermark 漂移、authorization / scope 失效、检索证据不足、图构建失败、index corruption 和 provider outage。

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

纯处理失败在同一 DocumentVersion + processing spec 下可以幂等重试；同一 generation identity 不得混入不同处理规格。部分索引写入后不激活 Serving。能力或数据假设变化导致当前 plan 不再成立时，由 04 重规划。知识模块没有外部副作用对账主权；物理 Provider 回执只用于决定是否接受 / 激活 generation。

### B10 Security / Approval / Audit

所有处理、检索和派生视图按 tenant / matter / scope / current security decision 约束。对受保护材料的模型外发还需消费 08 的 egress policy。缓存、索引和 Graph 不能绕过删除 / legal hold / recall policy。

### B11 Persistence / Transaction Boundaries

原始材料和正式 DocumentVersion 归 02 / Platform 的相应持久化边界；知识模块持久化 generation metadata、manifest、lineage、processing status 和必要 serving pointer。索引激活应通过稳定 manifest / watermark 形成可恢复切换，避免半写 generation 被误当成 Current Serving。

### B12 Observability / Evaluation

至少记录 processing coverage、parse / OCR error、generation build latency、activation result、retrieval latency、candidate count、citation lineage completeness、recall / precision / rerank 指标、stale-hit 和 scope rejection。GraphRAG 必须按 query class 做有对照的质量 / 成本测量，而不是只报告总体平均分。

### B13 Current / Target / Gap / Evidence

Current 见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 与 [`implementation-wave-001.md`](../evidence/implementation-wave-001.md)。Target 是可版本化、可恢复、可测量的 Knowledge Generation + Readiness + Evidence / Citation 边界。Gap 包括真实数据规模、跨版本 ingestion、manifest / serving 切换、lineage lookup、GraphRAG 对照测量、security revocation 和完整 fault injection。

### B14 Code / Database / Migration Constraints

先冻结 generation identity、processing spec、readiness semantics、evidence identity、citation lineage 和 serving activation，再决定 index schema。不得用某个向量库的内部 ID 反向定义领域模型，也不默认建立独立 Knowledge 微服务。底层 Provider 更换必须通过 adapter / manifest 迁移，不改写已经发布 WorkProduct 的历史引用。

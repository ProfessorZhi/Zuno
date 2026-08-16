# 03 Knowledge & Evidence（知识与证据）

<!-- status: design-skeleton; implementation: not-authorized -->

## Part A — Human Narrative

### 上传成功为什么不等于可以回答

用户上传了一百份材料，接口返回 200，并不意味着系统已经有资格基于这一百份材料形成正式分析。PDF 可能仍在解析，扫描件可能 OCR 失败，附件可能缺失，索引也可能还对应上一版材料。

知识与证据首先解决的不是“选哪个向量库”，而是更基本的问题：**在某个明确的材料版本和任务范围下，哪些内容现在真的可以被使用，系统能从中恢复出什么证据和引用？**

### 一份材料怎样变成可用知识

应用入口接收文件后，材料身份和正式版本仍由法律领域拥有。知识与证据围绕这个不可变版本执行解析、OCR、结构化、切分和索引，必要时建立关键词、向量或图等派生视图，并形成自己的知识生成版本。

物理写入完成还不够。系统需要知道对应视图是否可见、是否通过基本校验、是否仍对应当前材料版本，最终才能对某个任务范围给出“已经完整可用、只能部分使用、仍需等待或不可用”的判断。

### 就绪不是一个文件上的全局布尔值

同一份材料可能已经完成文本解析，但图谱仍在重建；某个简单问答只需要条款原文，另一个复杂任务可能要求附件、表格和跨文档关系全部可用。因此 Knowledge Readiness（知识就绪状态）应围绕**材料版本集合、当前知识生成、任务范围和最低能力要求**来判断，而不是给文件挂一个永久 `ready=true`。

如果产品允许先看部分结果，就必须显式缩小 Scope，并把输出标成对应范围的草稿或临时分析。不能把“40/100 已处理”包装成“100/100 已覆盖”。

### 检索的目标不是找最相似的句子

检索可以组合关键词、向量、重排、图视图或其他策略，但这些实现不是长期业务权威。上层真正需要的是：检索针对哪个材料版本和权限范围、返回了哪些证据候选、来源位置是什么、当时用的是哪一代知识视图，以及证据是否足以支持当前任务。

CitationLineage（检索引用链）记录“系统当时怎样找到和筛选这个候选”。如果候选最终进入正式工作成果，真正长期保存的历史引用由法律领域重新绑定到不可变材料版本和稳定位置。

### 索引为什么可以替换

向量库、图存储、关键词引擎和切分算法都可能变化。它们应该被视为可重建的知识派生视图，而不是业务真相。索引写成功只证明物理写入，不自动证明新知识生成已经被接受和激活。

这使得 Zuno 可以以后从 Milvus 换到其他向量方案、删除某个图实现或调整切分算法，而不改写已经发布工作成果的历史依据。GraphRAG 也只是特定查询类别下可能有收益的 Provider / 策略，不是所有请求的默认必经路径。

### 出问题以后怎么办

解析失败、索引部分完成、来源无法稳定绑定、知识版本落后、权限变化或检索证据不足，都必须显式暴露。完整范围任务应等待、拒绝或缩小范围；旧知识版本不能静默冒充新 DocumentVersion 的知识视图。

如果只是可重建索引损坏，恢复重点是从不可变源版本重新生成并校验；如果是正式领域引用缺失，则不能靠“重新检索一次差不多的内容”补成历史事实。

### 为什么值得独立成一个责任域

把知识投影放进法律领域，会让领域状态被向量库和切分策略污染；把它完全交给运行时，又会丢失版本、就绪和来源治理。独立知识边界既允许底层替换，也给上层提供稳定的证据、就绪和来源语义。

### 当前、目标与缺口

Current Evidence 已能证明部分 Citation Provenance Guard、stale/scope 检查以及产品 ingestion 的持久化入口；但真实数据库 lineage lookup、完整 Knowledge Readiness、全量 ingestion fault recovery、GraphRAG query-class 收益和生产索引切换都没有被完整证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Ownership

**Owns**：material processing projection、KnowledgeGeneration / KnowledgeView、Readiness、EvidenceCandidate、RetrievalResult、CitationLineage、IndexManifest 的知识语义。

**Does not own**：DocumentVersion canonical identity、Finding / WorkProduct、historical WorkProduct citation authority、Security policy、physical index success semantics。

### B2 Inputs / Outputs

输入：DocumentVersion reference/set、任务 Scope、当前 Authorization / Security Epoch、查询或检索要求、索引物理回执。

输出：ReadinessDecision、EvidenceCandidate、CitationLineage、Knowledge Generation / Manifest references、检索质量和 evidence sufficiency signal。

### B3 Cross-boundary Contracts

沿用总体架构中的 Readiness、Evidence/Citation reference，以及现有 Registry 中 Index Spec / Manifest / Write Receipt / Serving Watermark 等边界。Chunk / Vector / Graph identity 不升级为长期 Citation Authority。

### B4 State / Lifecycle

材料处理从接收不可变 DocumentVersion 引用开始，经过解析/派生视图构建、可见性和验证，到针对具体 Scope 的可用性判断。具体 enum、阈值和生成激活状态在模块深设计时冻结；版本切换必须能区分旧 generation 与当前 serving generation。

### B5 Failure / Recovery / Idempotency

- parsing / OCR failure：记录材料级失败，不伪装成完整就绪。
- partial index write：不自动激活新 generation。
- stale generation：拒绝作为新 DocumentVersion 的完整知识视图。
- scope / authorization invalid：不返回越权候选。
- evidence insufficient：返回不足/拒绝正式回答，不让生成层补写不存在的依据。
- index corruption：从源版本重建并重新验证，不改变 Domain 历史引用。

### B6 Security / Persistence / Observability

所有检索和派生视图按 tenant / scope / current security decision 约束。原始材料和索引的物理存储可由 Platform 提供；知识模块拥有“是否接受/激活、对当前 Scope 是否就绪”的语义。Telemetry 记录 generation、latency、retrieval/eval 引用，不泄露 Secret 或不必要全文。

### B7 Current / Target / Gap

Current 见 [`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 与 [`implementation-wave-001.md`](../evidence/implementation-wave-001.md)。Target 是可版本化、可恢复、可测量的 Knowledge Readiness + Evidence/Citation 边界。Gap 是真实数据规模、跨版本 ingestion、索引切换、GraphRAG 对照测量和完整 fault injection。

### B8 Code / Database / Migration Constraints

先冻结 generation、readiness、evidence identity 和 citation lineage，再决定 index schema。不得用某个向量库的内部 ID 反向定义领域模型，也不得把“索引写成功”直接映射成 Knowledge Ready。

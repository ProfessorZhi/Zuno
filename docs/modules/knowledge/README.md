# 03 Knowledge & Evidence（知识与证据）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 一百份材料上传成功，任务仍可能不能开始

用户把一百份案件材料上传到系统。九十八份很快完成解析，两份扫描附件仍在 OCR。此时页面上每个上传请求都返回成功，向量库里也已经有大量 chunk。

如果用户问“合同第 8 条约定了什么”，现有材料也许已经足够；如果用户要求“基于全部材料判断违约金额”，缺失的两份附件可能正好决定结论。把“文件存在”“索引里有数据”或“最后一个 Worker 成功”当成全局 READY，都会让系统在证据范围并不完整时给出看似完整的答案。

03 的职责从这里出现。它不负责给正式材料创建业务身份，也不负责宣判某条检索结果已经成为法律证据。它负责把稳定的材料版本加工成可以重建的知识，并针对当前任务回答一个更实用的问题：**为了做这件事，现在到底有哪些材料和派生能力已经可用，缺的东西是否会影响任务。**

单文件 Demo 可以上传后立即切分、Embedding、写向量库，然后开始查询。复杂材料处理只有在 OCR、版本更新、异步 Worker、重建和不同任务需求真正出现以后，才需要更明确的知识生命周期。

### 从正式材料到可查询知识，需要两个不同的判断

合同 v3 先由 02 作为正式 `DocumentVersion（材料版本）` 保存。03 不再创造另一套“真正文件 id”，而是引用这个稳定身份进行 OCR、解析、切分、Embedding、实体抽取、图构建和索引。

这些派生结果会随算法变化。今天换了 OCR Provider，明天调整 chunk 策略，后天升级 embedding；正式合同仍然是同一个 v3，围绕它构建的知识配方和结果却可以产生新一代。工程上把这组可重建派生称为 `KnowledgeGeneration（知识生成版本）`。

一代知识完成到什么程度，只回答“这批派生是否完整、经过验证、可以提供查询”。它还不能回答所有任务都能不能开始。全案争议分析可能要求扫描附件、事件结构和跨文档关系都可用，普通条款定位只需要正文和基础索引。

所以在真正执行任务前，还会针对 task class、Scope、所需能力和当前安全条件形成 `ReadinessDecision（知识就绪判断）`。它可以告诉上层当前范围已经足够、只覆盖部分材料，或者缺少关键输入而应该阻断。

这样做不会把系统变成“所有东西都等到最慢组件完成”。简单任务可以在需要的最小知识已经准备好时继续；复杂任务则明确知道自己还缺什么。Readiness 是面向任务的判断，不是整个平台只有一个绿色灯。

### 检索负责找到候选，不负责把“没找到”写成事实

知识准备好以后，03 才开始回答检索问题。

一次检索可以返回片段、来源、分数、实体关系和机器候选，并记录它们来自哪一版材料、哪一代知识、哪条 route 和哪个稳定位置。这个 lineage 对调试和后续正式准入都很重要：如果回答引用错了，工程师可以追到 OCR、chunk、query route、reranker 或材料版本。

但检索的边界同样重要。Top-K 没找到某条信息，可能因为 OCR 失败、query 表达不好、索引路线不合适、reranker 漏排，或者当前 Scope 根本不包含相关材料。一次 retrieval miss 不能直接升级成“案件中不存在该事实”。

需要做否定性判断时，系统至少要先知道要求覆盖的材料范围是否准备好、是否使用了足够适合的路线，以及仍有哪些检索缺口没有解决。03 可以告诉上层“当前检索没有发现”“覆盖仍不完整”或“需要扩大 route”，而正式法律判断继续由 02 接纳。

同理，今天的 CitationLineage 解释这次候选如何被找到；正式 WorkProduct 当时真正采用的材料和位置，由 02 在准入时保存成长期引用绑定。03 可以重建索引，不能让历史 WorkProduct 的引用跟着新索引漂移。

### 知识层不仅服务搜索，也形成案件研究的专业中间结构

如果 03 最终只输出 chunk 和 Top-K，葛季栋 / LIPLAB 已有的事件抽取、冲突识别、事实—法条关系等研究能力仍然只是检索插件。它们更有价值的用法，是把非结构化材料逐步转换成专业人员能够持续复核的案件结构。

例如，事件抽取与事件对齐可以形成案件时间线的候选；双方材料中的不同陈述可以形成冲突线索；证据抽取可以把某个主张和支持或反驳材料连接起来；事实—法条对应与法条推荐可以形成“哪些事实可能关联哪些法律依据”的候选关系。Agent 后续做研究时，不必每一步都重新阅读全部原文，而可以先从这些结构发现缺口，再回到稳定引用核对原始材料。

这些结构仍然属于**可重建的知识派生和机器候选**。它们绑定 DocumentVersion、KnowledgeGeneration、来源位置和产生它们的 Capability / Provider 条件；算法升级以后可以重新生成。03 不因为把信息整理成“事件时间线”或“Fact–Article Map”就获得正式法律 Authority，也不把某个研究模型的判断直接写成长期 Finding。专业人员最终采用了什么、修改了什么，仍由 02 的 HumanDecision 和正式 WorkProduct 记录。

这个区分使案件工作空间能够随模型演进而保持稳定。底层事件抽取可以从论文模型换成更强 LLM，检索路线可以从 Hybrid 增加 Graph route，专业人员看到的仍然是同一类事件、冲突、证据关系和法律依据候选；Provider 的变化通过来源和版本被记录，而不是迫使产品界面围绕某个模型重做。

这里也没有必要把每一种专业结构都升级成新的一级 Domain 对象。只要它主要服务检索、研究和候选分析，可以继续作为 Knowledge projection / structured artifact 存在。只有某项内容被业务长期采用、需要独立版本和正式有效性语义时，才进入 02 的业务边界。

### 复杂检索只在简单路线暴露缺口时出现

很多问题不需要 GraphRAG。

精确条款定位可能适合 lexical / BM25；语义相似问题适合 dense retrieval；已知 Matter、文件类型或时间范围时，metadata / source scoped retrieval 往往更直接。跨文档实体关系和多跳事件链才可能真正从 graph route 获益。

因此更合理的起点是 Hybrid Retrieval，再根据 QueryClass 和已知证据缺口加入额外 route，最后做融合和 rerank。不是“能走多少 route”决定系统先进程度，而是新的 route 是否稳定找到 baseline 漏掉、且任务真正需要的证据。

Agentic Retrieval 也需要停下来。模型可以不断改写 query、扩图、再 rerank，但“再搜一次也许会更好”不是停止策略。继续检索应该能够指出一个尚未满足的证据缺口，并观察新一轮是否真的带来新的有效材料；当新增证据已经很少、任务所需范围已经满足，继续搜索只会增加 token、延迟和故障面。

GraphRAG 的位置因此是按需的候选机制，而不是 Knowledge 的默认身份。它带来图抽取误差、存储、新鲜度和查询成本，应该和更简单 Hybrid baseline 在同语料、同模型和可比预算下评测。某类 query 没有稳定收益时，图路径就应该关闭或只保留在少数任务中。

### 索引可以重建，正在服务的知识版本不能是半成品

后台直接在正在查询的索引上原地改写，最容易产生一个难以解释的状态：新 chunk 写进去一半，旧图还没替换，某个 Worker 又失败了；用户这时发起检索，没有人能说清这次查询使用的是哪一套完整知识。

Target 更倾向于构建新的 KnowledgeGeneration。各阶段按照自己的事务边界写入 artefact，generation-level validation 检查要求的 manifest、覆盖和必要 projection，全部满足当前 profile 后，再原子切换 ServingPointer。查询入口只消费已经验证的 generation，不跟随后台写入进度。

这也避免要求 PostgreSQL、Object Store、vector index 和 graph store 做一笔跨 Store 2PC。每个 Store 保存自己的完成事实，最后只让“哪一代对外服务”这个小而关键的指针原子变化。可选 projection 失败是否阻断激活，由当前 generation profile 决定，而不是要求所有技术组件永远一起成功。

Worker 可以至少一次执行，重复项由稳定 item identity、CAS 或幂等写吸收。某个 OCR 或 embedding task 重试成功，只证明那个处理项完成，不自动改变 serving truth。

缓存同样只加速派生知识。cache key 需要绑定真正影响结果的材料版本、ProcessingSpec、query config 和必要安全 Scope；权限撤销以后，即使旧缓存还在，也不能继续返回已经失去当前读取资格的内容。

数据删除或 Legal Hold 也会跨多个 Store。查询层可以先停止 recall，底层向量段、对象存储和 cache 再按治理流程清理；相反，Legal Hold 可能要求字节继续保留却禁止普通召回。03 消费 08 的生命周期决定，不能用“向量还在”或“查询不到了”替整个系统宣布物理删除完成。

### 什么时候知识架构应该缩小

如果语料很小、都是干净文本、没有多版本、没有 OCR、没有复杂 Scope，也没有跨文档关系任务，一个版本化 lexical / dense index 已经足够。此时没有必要引入 graph store、复杂 generation orchestrator 和多路 Planner。

即使系统已经做出 GraphRAG，也要允许它被 Eval 关闭。Knowledge 架构的复杂度来自材料规模、异步处理、版本重建、权限边界和 query 类型，而不是来自“RAG 平台应该有哪些组件”。

这条退出条件同样适用于 Worker 和服务拆分：没有独立吞吐、资源或故障隔离需求时，逻辑阶段可以共进程；只有真实资源约束出现后再拆部署。

### Current / Target / Gap

**Target：** 03 围绕 02 的稳定 DocumentVersion 建立可重建 KnowledgeGeneration，按任务形成 ReadinessDecision，检索和专业派生产生带来源的候选结构，并通过 generation activation 保护 serving 完整性。正式 Evidence / Finding / WorkProduct 仍由 02 负责。

**Current：** 仓库历史已经有知识任务模型、RabbitMQ 异步流水线、Redis 进度、RAG / GraphRAG 路径和评测工作，但它们不能自动证明 Target 中完整的 generation lifecycle、task readiness、原子 serving switch、案件专业中间结构和跨 Store 生命周期治理已经落地。

**Gap：** 真实多版本材料的 readiness 规则、generation activation、跨 Store purge、权限撤销后的召回收敛、负面证据条件、事件 / 冲突 / Fact–Article 等专业结构的稳定语义、GraphRAG 按 query class 的稳定收益和真实法院语料成本仍需要测试与 Eval。

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。

# 03 Knowledge & Evidence（知识与证据）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail_design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块先解决一个反直觉问题：文件到了，不代表任务已经能用

用户上传一百份材料，接口全部返回成功，并不能说明“请基于全部材料分析争议”这个任务已经准备好。两份关键扫描附件可能还没 OCR，某一版材料可能刚被替换，索引可能只完成部分写入，当前用户也可能没有权限读取其中一部分。

03 因此不是一个“向量数据库封装层”。它负责把正式材料版本变成可重建知识派生，并针对具体任务判断当前范围到底可不可用；检索只在这个基础上产生有来源的候选，而不是把命中结果直接升级为法律事实。

### 最简单的一份文件一个向量索引为什么会失效

最简单方案是文件上传后立即切分、embedding、写向量库，然后用“索引里有数据”表示准备完成。对单文件 Demo 这通常可行。

真实材料处理中，OCR、解析、chunk、embedding、图构建和元数据写入可能分别成功或失败；算法升级还会要求重建索引。如果把向量库当前内容当成正式材料身份，重建时历史引用会漂移；如果把任意子步骤成功当成 READY，系统会在关键材料缺失时输出看似完整的答案。

### 正式材料、知识派生和任务就绪为什么是三层

DocumentVersion 是 02 拥有的正式业务材料身份。03 围绕它建立 KnowledgeGeneration：某一组解析、OCR、切分、embedding、图和其他派生视图的可重建版本。具体任务再结合 Scope、所需能力和当前安全条件形成 ReadinessDecision。

三层分开以后，材料历史不会随着索引重建而漂移，派生算法可以升级，任务也不会因为“总体构建完成”就自动获得完整使用资格。

### KnowledgeGeneration lifecycle != task-level ReadinessDecision

KnowledgeGeneration 的生命周期回答“这一代派生知识构建到什么程度、是否经过验证、是否可以 serving”；ReadinessDecision 回答“针对这一次任务要求，现在是否有足够且被允许的知识可用”。

一个 generation 可以 serving，但某个任务需要的关键附件不在覆盖范围，因此仍然 BLOCKED；反过来，一个简单单文档问题可能只需要 generation 中已准备好的那一小部分。把两者合并，会让系统不是过度等待，就是在覆盖不足时误报 READY。

### 为什么部分完成必须显式，而不能假装成功

知识构建天然是多阶段异步流程。九十八份材料完成、两份关键附件失败时，系统最危险的行为不是报错，而是静默把九十八份当成“全量知识”。

Readiness 应该显式表达 READY、PARTIAL、BLOCKED 一类业务含义，并解释缺什么、覆盖什么。上层可以据此等待、缩小 Scope 或向用户说明限制，但不能把 PARTIAL 通过 Prompt 包装成完整分析。

### 检索命中为什么仍然只是候选

检索系统的任务是提高找到相关材料的概率，而不是拥有正式法律事实。它可以返回片段、来源、分数、关系和证据候选，但最终是否被法律业务采用由 02 决定。

因此保持 `EvidenceCandidate != formal Evidence`。这个边界允许 03 自由升级 embedding、reranker、GraphRAG 或 query rewrite，而不会让算法变更直接修改长期领域事实。

### CitationLineage 为什么只解释“怎么找到的”

检索结果需要知道来自哪一版材料、哪个位置、哪条检索路线和处理版本，才能调试“为什么找到这一段”。这些信息构成当前检索 lineage。

正式 WorkProduct 的历史引用则需要在未来稳定回到当时采用的材料版本和位置。索引可以重建，正式引用不能漂移，所以必须保持 `CitationLineage != WorkProductCitationBinding`。03 提供候选来源，02 在正式准入时保存长期 binding。

### 为什么一条 Retrieval Pipeline 不应该处理所有问题

精确条款定位、语义相似问题、实体关系问题和跨文档多跳分析的最佳检索方式不同。如果所有 query 都强制走最复杂 GraphRAG，简单问题会付出不必要延迟和故障面；如果所有 query 都只做向量 Top-K，复杂关系又可能覆盖不足。

Target 因此采用按 QueryClass 选择路线的思路：lexical / BM25、dense、metadata/source scoped、entity/fact、graph/multi-hop 可以按需要组合，再做融合和 rerank。重点是根据任务选择最小充分路线，而不是把“路由越多”当成先进性。

### 多路检索以后为什么还需要停止条件

Agentic Retrieval 很容易陷入“再搜一次也许更好”。如果没有停止条件，一次问题会不断 query rewrite、graph traversal、rerank 和模型判断，成本上升却没有可解释收益。

所以复杂检索需要观察新增证据是否真的增加覆盖，当前证据是否已经足以支持任务，以及继续检索还能解决什么缺口。EvidenceGain / Sufficiency 是对这种概念的工程化表达，核心是让“继续找”有因果理由。

### GraphRAG 为什么只能是条件能力

图结构对跨文档实体关系、事件链和多跳问题可能有价值，但图构建本身带来抽取误差、存储成本、新鲜度问题和额外查询延迟。不是所有法律问题都需要图。

因此 GraphRAG 必须和更简单 Hybrid Retrieval 做同语料、同模型、可比预算的对照。只有特定 query class 稳定获益时才扩大使用；否则保持按需路线，甚至删除图路径。

### 新材料进入时为什么不能原地修改 serving 索引

如果正在 serving 的 generation 被后台 Worker 一边查询一边原地改写，读者很难知道某次检索到底使用了哪个完整版本。部分写入失败还可能把不完整新数据暴露给在线任务。

更稳妥的概念是构建新的 generation，验证 Manifest 和覆盖以后再原子切换 ServingPointer。旧 generation 可以在策略允许的时间内保留用于历史解释或回滚，可重建数据最终再按生命周期清理。

### Worker 重试为什么不能让部分写入变成“已激活”

OCR 或 embedding Worker 失败可以按处理项重试，但某个子任务成功不代表整代知识可 serving。Activation 必须依赖 generation-level validation，而不是最后一个 Worker 的“成功回调”。

这样 Worker 可以横向扩展和至少一次执行，重复处理由 item identity / CAS 等机制吸收；无论重试多少次，都不能跳过完整性判断直接修改 serving truth。

### Cache 为什么只能优化派生数据

检索 cache、embedding cache 和解析 cache 都能显著降低成本，但 Cache 失效不应该改变正式材料和业务成果。cache key 需要绑定真正影响结果的材料版本、处理版本、查询配置和必要安全 Scope。

缓存命中仍然要通过当前授权和任务新鲜度判断。它加速的是 Projection / Derived Knowledge，不是产生永久授权或正式 Evidence。

### 权限变化为什么会让“之前算好的知识”暂时不可用

材料派生数据可能在技术上仍然存在，但用户权限或模型外发政策变化后，新的读取和检索不能因为 cache / generation 已经构建就继续复用旧 allow。

03 消费当前 Security decision 决定哪些内容可以返回。安全变化通常不要求立刻物理重建所有索引，但必须影响新的受保护访问和 Readiness；历史合法处理事实与未来是否允许继续使用要分开。

### Knowledge stale 和 Domain stale 为什么属于不同 Owner

材料或处理版本变化后，旧索引可能需要重建，这是 Knowledge 层的新鲜度问题；新的正式 Evidence 进入后，旧 Finding / WorkProduct 是否需要复核，则是 Domain 问题。

所以保持：`stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02`。03 可以通知上层旧 generation 不再适合新任务，却不能直接把正式 WorkProduct 改成 stale；02 根据正式依赖关系决定业务失效。

### 什么时候 03 应该更简单

如果语料小、全部是干净文本、没有多版本、没有 OCR 和复杂 Scope，一个版本化的 lexical / dense index 可能已经足够。此时不需要 Graph Store、多路 Planner 或复杂 generation orchestrator。

Knowledge 架构的复杂度应由材料规模、处理异步性、版本重建和 query 类型驱动。能够删掉 GraphRAG、减少 Route、合并 Worker 或不用独立 serving service，都是正常架构优化。

### Processing Spec 为什么必须进入 generation 身份

同一批 DocumentVersion 用不同 OCR、parser、chunker、embedding 或 graph extractor 处理，会得到不同派生知识。如果 generation 只按“有哪些文件”标识，系统无法解释索引升级前后的差异，也无法可靠回滚。

因此 generation identity 需要能够绑定影响语义的 ProcessingSpec / provider versions。它不是要求把每个运行参数都暴露给业务，而是让可重建数据知道自己“由什么配方生成”。算法升级时构建新 generation，而不是静默覆盖旧 serving 数据。

这种版本化也为 Eval 提供了可比对象：质量变化可以关联到处理版本，而不是只看到数据库内容突然不同。

### Readiness 为什么必须按 Required Capability 判断

一个任务只需要文本定位，OCR + lexical / dense index 就绪可能已经足够；另一个任务需要跨文档关系分析，则还可能要求实体 / graph projection 可用。用单一全局 READY 会让前者无谓等待最慢组件，或者让后者在缺关键能力时过早运行。

Task Readiness 因此应结合 task class / required capability 和当前 Scope。它回答的是“为了完成这件事还缺什么”，不是“整个知识平台是否健康”。这一设计允许按需建设复杂派生，也让降级更具体：缺 Graph 时某些任务退回 Hybrid，缺关键 OCR 时则必须阻断完整分析。

### Retrieval Quality 为什么不仅是 Recall@K

高召回很重要，但法律任务还关心来源是否可追溯、覆盖是否足够、冲突材料是否同时出现，以及候选是否来自当前允许的 DocumentVersion。一个检索器返回很多相似片段，不代表已经找到支持结论所需的证据集合。

所以 03 的评测需要按 query / task class 看 retrieval recall、source correctness、evidence coverage、latency 和 cost；复杂 Agentic Retrieval 还要看额外 route 是否真正增加新证据。质量判断最终交给 09 的可复现实验，而不是由“Top-K 看起来相关”主观决定。

这也是停止条件的依据：继续检索只有在可以填补已知证据缺口时才有价值。

### Serving 切换为什么比“所有 Store 同时完成”更现实

一个 KnowledgeGeneration 可能包含 PostgreSQL metadata、Object Store artefacts、vector index 和 graph projection。要求它们跨 Store 原子 commit 很难实现，也没有必要。

更合理的是每个构建阶段记录自己的完成事实，generation-level validation 检查要求的 artefacts 和 manifest，最后只原子改变一个 ServingPointer / active generation reference。查询入口只消费已经验证的 generation，不直接跟踪后台写入进度。

如果某个可选 projection 构建失败，是否阻断激活取决于当前 generation profile；关键不是所有东西都成功，而是对外承诺和实际可用能力一致。

### 数据生命周期为什么要区分“停止召回”和“物理清除”

某份材料权限撤销或删除请求生效后，新检索应该立刻停止召回，即使底层向量段、缓存或对象存储还在按异步流程清理。相反，Legal Hold 可能要求物理字节继续保留，但业务上不再允许普通召回。

03 因此消费 08 的 lifecycle decision，先执行 recall eligibility，再让各派生 Store 完成 purge / rebuild。知识系统不能因为“向量还没删完”就继续返回，也不能因为查询层已经屏蔽就宣称物理删除全部完成。

这种分层使安全语义先收敛，昂贵的数据清理随后可恢复执行。

### “没检索到”为什么不能直接解释成“材料里没有”

Retrieval 是概率性和覆盖受限的。一次 Top-K 没找到某条信息，可能因为 OCR 失败、query 表达不佳、索引路线不合适、reranker 漏排或当前 Scope 没覆盖相关材料。把 retrieval miss 直接写成“没有证据”会把搜索能力边界伪装成法律事实。

因此否定性结论需要更强证据：至少知道任务要求的材料范围是否 READY、相关 query class 是否使用了足够路线、关键来源是否真正被处理。无法证明覆盖时，正确结果可以是“当前没有找到”或“证据不足”，而不是“事实不存在”。

这个边界也让 09 的 Eval 更真实：不仅测命中什么，还要测系统在找不到时是否诚实表达 coverage 和 uncertainty。

### 检索结果为什么要保留来源多样性，而不是只追求相似度最高

法律分析里，Top-10 全部来自同一份文件的相邻 chunk，可能拥有很高相关分，却无法代表多材料事项的证据覆盖。相反，一条支持材料、一条反驳材料和一条关键时间线来源，可能对专业判断更有价值。

所以融合和 rerank 的目标不能只有单点相似度，还要考虑 source diversity、版本、冲突材料和任务所需 coverage。具体算法可以变化，但系统应该避免把重复片段数量误当成证据数量。

这也是 Graph / entity 路线可能有价值的地方之一：帮助发现跨文档关系；但如果简单 source-aware Hybrid 已经达到同样覆盖，就没有理由为“多样性”永久保留更复杂图路径。

### 新一代知识构建失败时，为什么旧 Serving 不应该一起被拖垮

后台正在构建 KnowledgeGeneration V8 时，V7 可能仍然是最后一个经过完整校验的 serving 版本。某个新 embedding Provider 故障或 graph projection 失败，不应该原地破坏 V7，让所有在线查询同时不可用。

更稳妥的做法是把构建和 serving 隔离：V8 在独立 generation 中完成、验证后再切换。失败时继续服务 V7，只能覆盖 V7 已经声明包含的 DocumentVersion 和能力；如果用户任务明确要求 V8 才包含的新材料，Readiness 就应该 BLOCKED / PARTIAL，而不是假装旧索引已经包含新事实。

这同时解决可用性和正确性的冲突：旧 verified generation 可以保住已有能力，但不能借“降级”名义隐瞒新材料缺失。

### Ingestion 和 Retrieval 为什么需要不同的资源隔离

OCR、解析、embedding 和 graph build 是重 CPU / GPU / I/O 的批处理，在线 Retrieval 更关注低延迟。如果两者无界共享同一个 Worker / connection pool，大批材料导入可能把已经就绪的在线查询一起拖死。

第一步通常不是拆微服务，而是区分 queue、并发、quota 和 backpressure，让 serving 有稳定资源下限，批处理按容量排队。只有当负载、故障半径或部署生命周期长期不同，才需要进一步物理拆分。

资源隔离的目标是保护“已验证知识仍可被使用”，而不是为了架构对称把每个 processing stage 都服务化。

### 当前、目标与缺口

Current 是否已有完整 generation、serving pointer、readiness、multi-route retrieval 或 graph path，必须回到代码、测试和 Eval 证据判断；Target 文档不能把设计写成已实现。

Target 已明确正式 DocumentVersion、可重建 KnowledgeGeneration、任务级 Readiness 和检索候选的边界，并要求复杂检索有 simpler baseline 和停止条件。Gap 仍包括字段冻结、真实材料覆盖测量、部分失败与切换测试、Graph / multi-route 的边际收益、容量成本和安全隔离实现。

---

工程 / Agent 精确参考与跨模块一致性规则见 [`reference.md`](reference.md)。

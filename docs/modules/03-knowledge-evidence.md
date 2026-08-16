# 03 Knowledge & Evidence（知识与证据）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2 -->

## Part A — Human Narrative

### 这个模块先回答的不是“用哪个向量库”

用户把一百份材料上传成功，接口全部返回 200，并不意味着系统已经可以基于这一百份材料形成正式分析。扫描件可能还没完成 OCR，附件可能缺失，某些表格可能解析失败，当前索引也可能仍然对应上一版材料。

知识与证据模块先回答的是一个更基础的问题：**对于当前事项、当前材料版本和这次任务要求，系统现在究竟掌握了哪些可用知识，能从中恢复出什么证据和引用？**

向量库、关键词检索、GraphRAG（图增强检索）和重排只是实现这件事的工具。它们都不能替代“当前这次任务到底可不可以安全使用这些知识”的判断。

### 用一百份材料的场景理解“知识就绪”

假设一个事项包含 100 份材料。90 份文本解析完成，8 份扫描件完成 OCR，还有 2 份关键附件 OCR 失败。

如果用户只问“合同第 8 条原文是什么”，而这份合同已经完整解析，那么当前任务可能已经可以回答。

如果用户问“综合全部证据判断双方金额差异”，而那 2 份失败附件正是关键发票，那么同一批材料对这个任务就还没有达到完整可用条件。

所以 Knowledge Readiness（知识就绪判断）不是文件身上的永久 `ready=true`。它是一次任务级判断，至少依赖：

- 本次任务声明使用哪些 DocumentVersion（材料版本）；
- 当前使用哪一代 KnowledgeGeneration（知识生成版本）；
- 任务 Scope（范围）是什么；
- 当前任务最低需要哪些处理能力，例如正文、OCR、表格或跨文档关系；
- 当前权限和安全策略是否仍允许使用这些材料。

同一 KnowledgeGeneration 对任务 A 可以 READY，对任务 B 可以 PARTIAL 或 BLOCKED。这不是矛盾，而是任务要求不同。

### 一份正式材料怎样变成可检索知识

DocumentVersion（材料版本）的正式业务身份由法律领域与工作成果模块拥有。知识模块不重新发明一个“索引文件 ID”来替代它，而是围绕这个稳定版本做派生加工。

典型链路是：解析、OCR、规范化、切分，再生成关键词索引、向量视图、图视图或其他可重建结构。一次明确处理规格形成一代 KnowledgeGeneration（知识生成版本）。

```mermaid
flowchart LR
  D[DocumentVersion（正式材料版本）] --> G[KnowledgeGeneration（知识生成版本）]
  G --> P[解析 / OCR / 规范化]
  P --> V[关键词 / 向量 / 图等派生视图]
  V --> M[完整性与来源校验]
  M --> S[可服务的 generation]
  S --> R[针对具体任务计算 Readiness]
  R --> E[检索 EvidenceCandidate（证据候选）]
```

这里最重要的边界是：**generation 建好，不等于所有任务都 Ready；某个索引写成功，也不等于 generation 已经可以对外服务。**

### 为什么“生成完成”和“任务就绪”必须是两套状态

KnowledgeGeneration 生命周期回答“这一代知识派生本身处理到哪里了”。它关注哪些材料已经处理、哪些处理项失败、manifest 是否完整、当前哪一代正在 Serving（提供检索服务）。

ReadinessDecision（知识就绪判断）回答“这次任务能不能基于某个 generation 和当前材料范围工作”。它还要考虑任务 Scope、最低能力要求和当前安全条件。

如果把两者压成一个 `ready` 字段，会出现很难解释的情况：全文问答已经可用，但跨表格任务仍然不可用；或者 generation 本身完整，但用户刚刚失去某份材料访问权限。文件级 `ready=true` 无法表达这些差异。

因此目标架构明确分开：

```text
KnowledgeGeneration lifecycle
    !=
ReadinessDecision for one task
```

### 部分材料可用时，系统到底应该怎样做

部分知识不是一定不能使用，但必须诚实说明范围。

如果 100 份材料只有 40 份完成处理，系统可以在用户明确接受后，把任务 Scope 缩小到那 40 份，并产生“仅基于当前子集”的临时结果；也可以等待剩余处理完成；如果缺失材料会直接影响结论完整性，则应拒绝完整范围分析。

不能做的是：内部只覆盖 40/100，却继续沿用原来的完整 Scope，让上层误以为结果覆盖了全部材料。

因此 PARTIAL（部分可用）不是一种“尽量回答就好”的许可，它必须和明确的 covered scope、missing requirement 以及结果资格一起被上层消费。

### 检索目标不是“找最像的一段文字”

检索真正需要输出的是：在当前允许访问的材料版本和知识生成版本里，哪些内容可以成为证据候选，它们来自哪里，以及系统为什么找到了它们。

知识模块可以组合 BM25、向量召回、重排、图路径或其他策略，但这些算法都属于可替换实现。长期架构只要求结果能稳定绑定：

- DocumentVersion；
- KnowledgeGeneration；
- 当前 Scope；
- 稳定来源位置；
- EvidenceCandidate（证据候选）；
- CitationLineage（检索引用链）。

CitationLineage 记录“系统当时怎样找到和排序候选”。如果候选最终被正式工作成果采用，02 法律领域与工作成果模块再建立 WorkProductCitationBinding（工作成果历史引用绑定），保存“正式成果当时实际采用了什么”。

### EvidenceCandidate（证据候选）为什么还不是 Evidence（正式证据）

知识模块可以证明某一段文字存在、来源稳定，并在当前检索中与问题相关，但它不能单独决定“这段材料已经成为某个事项中的正式法律证据”。

正式 Evidence 属于法律领域。领域边界还要判断它和 Matter、Claim、Finding 的业务关系、当前授权、必要人工判断和正式准入条件。

因此知识模块对外输出的是候选和来源，而不是绕过领域直接提交正式证据。

### GraphRAG 为什么是条件能力，而不是默认主干

图结构适合某些跨文档实体、事件、时间和关系问题，但不是所有法律问题都需要图。

简单条文定位、明确关键词问答和局部证据查找，关键词 + 向量 + 重排可能已经足够。如果所有材料都强制构图，系统会增加构建成本、失效传播、重建复杂度和新的错误来源。

因此 GraphRAG 仍然按 Query Class（问题类别）启用。只有在同一原始语料、同模型和可比预算下，某一类任务被重复证明稳定获益，图路径才值得保留。没有对照测量时，“项目里有图数据库”不能成为默认启用理由。

### 为什么索引可以替换，但正式历史引用不能漂移

Milvus、pgvector、图存储、关键词引擎、chunking（切分方式）都可以替换。它们是从正式材料派生出来的可重建视图。

索引损坏时，可以从不可变 DocumentVersion 和处理规格重新生成 KnowledgeGeneration；重建以后，Chunk ID、Vector ID 或 Graph Node ID 都可能变化。

但一份已经正式发布的 WorkProduct 过去究竟引用了哪份材料的哪一处，是历史业务事实，不能靠“现在再检索一次最相似内容”来补写。这个长期绑定归 02 领域模块。

所以：

```text
索引恢复 = 可以重新计算
正式历史引用恢复 = 必须读取过去已经持久化的正式绑定
```

### 权限变化以后，为什么旧索引不能继续直接用

某个 KnowledgeGeneration 可以继续物理存在，但用户是否还能从中读取内容，是另一个问题。

Security & Governance（安全与治理）拥有当前授权决定。知识模块在解析、检索、Serving 和模型外发边界执行这些决定。权限撤销以后，旧缓存、旧检索结果和已经加载的候选都不能自动获得继续使用资格；后续新的受保护访问需要重新检查当前 Security Epoch（安全策略版本）。

这也说明 ReadinessDecision 必须考虑当前安全条件，而不能只看 generation 是不是构建成功。

### 新材料出现以后，知识模块和领域模块各自发生什么

当新的 DocumentVersion 正式进入领域后，知识模块为新版本建立新的 KnowledgeGeneration。旧 generation 可能继续保留用于历史重建，但对于声明使用新材料版本的任务，它不能继续冒充当前 generation。

知识模块负责识别“当前检索视图是否陈旧、是否覆盖新材料”；领域模块负责判断“新正式材料或新 Evidence 是否使旧 Finding / WorkProduct 失效”。

也就是说：

- stale KnowledgeGeneration（陈旧知识生成版本）是知识派生状态；
- stale WorkProduct（失效工作成果）是正式领域事实。

前者不能直接修改后者；后者也不要求把所有旧知识视图立即物理删除。

### 出问题以后怎样恢复

解析失败要定位到具体材料、页面或处理项，不能吞成空字符串；部分索引写入不能自动激活 Serving generation；一个旧 generation 不能被标成当前 DocumentVersion 的新知识；来源位置不稳定时，EvidenceCandidate 不能获得完整引用资格。

Provider 或索引损坏时，可以根据 DocumentVersion + processing spec（处理规格）重建派生视图；重建完成以后还要重新做完整性、来源和 Serving 激活检查。

如果任务只依赖未受影响材料，可以显式缩小 Scope 后继续；如果缺失内容影响完整性，则返回 PARTIAL / BLOCKED，让入口、运行控制或人工决定下一步，而不是由知识模块自己扩张结果资格。

### 它和法律领域模块到底怎样分工

可以用四个成对概念记住边界：

| 知识与证据 | 法律领域与工作成果 |
| --- | --- |
| 读取 DocumentVersion ref | 拥有 DocumentVersion 正式身份 |
| KnowledgeGeneration / ReadinessDecision | 正式 DomainVersion / WorkProduct validity |
| EvidenceCandidate | Evidence |
| CitationLineage | WorkProductCitationBinding |

知识模块回答“现在能够基于哪些材料可靠地找什么”；领域模块回答“哪些结果已经正式被业务承认”。这条边界是整个法律 Agent 架构能够替换检索实现而不改写正式业务历史的关键。

### 为什么它值得成为独立责任域

如果把知识派生全部放进法律领域，领域状态会被 OCR、chunk、向量库和图实现污染；如果把它全部塞进运行时，又会丢失 generation、Serving、来源、可重建和任务级就绪这些长期语义。

独立知识边界让上层只依赖稳定的问题：哪一版材料已经被怎样处理，当前任务能不能安全使用，找到了什么证据候选，以及候选怎样回到原始来源。底层到底使用 BM25、向量、GraphRAG 还是未来其他 Provider，都可以在这个边界内替换。

### Ingestion（知识加工）为什么必须按材料和处理项留下可恢复边界

一百份材料的加工不是一个黑盒“大任务”。某些 PDF 可能文本抽取成功但表格失败，某些扫描件可能只坏了两页，某一代向量索引可能只漏写一个分区。如果系统只保存一个总状态 `INGESTION_FAILED`，恢复时就只能全量重跑，也无法向上层准确解释缺失范围。

更合理的做法是让 KnowledgeGeneration 下面保留足够细的 processing item / projection 状态：哪一个 DocumentVersion、哪一类处理、哪一页或哪一个派生视图成功，失败原因是什么，能否按同一处理规格幂等重试。这样可以局部恢复，又不会把这些工程状态升级成法律领域事实。

这也意味着“100 个任务都执行成功”仍然不自动等于 generation 可以 Serving。最终还要用 manifest 检查这一代知识实际覆盖了什么、来源是否一致、必须的派生视图是否齐全，再决定是否激活。

### Serving（提供检索服务）切换为什么需要一个明确的发布点

假设 V1 generation 正在稳定提供检索，V2 正在后台重建。V2 的向量索引已经写完，但图视图还缺一部分。如果每写完一个索引就让查询自动看到新结果，同一个请求可能一半读取 V1、一半读取 V2，最终引用链也很难解释。

因此知识模块需要一个明确的 Serving generation / watermark 概念：后台可以构建、校验、失败和重试，但只有一代通过完整性检查以后才把服务指针切过去。切换失败时，旧的合法 generation 可以继续承担原本允许的任务；新 generation 不因为“已经花了很多计算”就获得服务资格。

这个发布点只在知识边界内部保证可恢复切换，不意味着要和 02 的领域事务或 04 的运行检查点做跨系统两阶段提交。

### Query Rewrite（查询改写）为什么可以改变表达，不能偷偷扩大任务范围

用户问“看看还有没有类似情况”时，查询改写器可以把自然语言转换成更适合关键词、向量或图检索的表达，也可以生成多个检索子问题。但改写器不能因此把原本限定在合同与补充协议的 Scope 扩大到整个事项，也不能因为“召回更多可能更好”而越过当前权限读取其他材料。

查询改写的输出仍然受原始 task Scope、DocumentVersion set、当前 Security Decision 和 retrieval requirement 约束。改写可以帮助“怎样找”，不能修改“允许找什么”。如果真正需要扩大材料范围，应回到入口或运行控制形成新的明确任务条件，再重新计算 Readiness。

### 缓存为什么必须和版本、新鲜度及权限一起看

检索缓存、Embedding 缓存和解析缓存都能显著降低成本，但缓存也是最容易把旧事实带进新任务的地方。

一个检索结果只有在它绑定的 DocumentVersion、KnowledgeGeneration、Scope、检索规格和必要安全条件仍然有效时才可能复用。新 DocumentVersion 已经进入当前任务、Serving generation 已切换、权限已经撤销，或者调用方要求的处理能力变化以后，旧缓存不能因为 key 看起来相同就继续命中。

缓存失效不是要“任何变化都清空全部缓存”，而是要让缓存身份包含真正影响语义的版本和范围。这样既能保留性能收益，又不会把 stale candidate 包装成新的 EvidenceCandidate。

### 检索路径降级什么时候是安全的，什么时候必须明确阻断

向量 Provider 暂时不可用时，系统可能仍然有关键词检索；GraphRAG 构图失败时，也可能还能做普通条文定位。是否可以降级，取决于当前任务最低要求，而不是“还有一个搜索引擎能用”。

如果用户只是找合同中的明确条款，BM25 等简单路径可能已经满足要求；如果任务明确依赖跨文档关系、表格抽取或图路径，而这些能力当前缺失，就应该返回 PARTIAL / BLOCKED，或者让 04 Replan，而不是静默换成质量能力不同的检索方式。

所以 Provider fallback 需要回答“替代路径是否仍满足同一 task requirement”。能满足才叫降级继续；不能满足就只是把失败隐藏起来。

### 来源位置为什么要能跨索引重建保持可解释

法律引用最终要回到原始材料，而不是停在“chunk 381”或“vector 9921”。对于 PDF，可以保存页码、字符区间、段落 / 表格位置、原始表示 hash 等稳定信息；对于结构化材料，可以使用业务可解释的 section / row / cell location。具体字段要等格式和解析器详细设计，但原则不能变：来源必须能回到不可变 DocumentVersion 的原始表示。

这样即使 chunking 算法升级、向量库迁移、Graph 节点重建，新的检索实现仍然可以找到同一原始位置；而已经正式采用的历史 WorkProductCitationBinding 也不会因为索引身份变化而失去解释能力。

### 当前、目标与缺口

Current Evidence（当前证据）已经证明部分 Citation Provenance Guard（引用来源校验）、stale / scope 检查和产品 ingestion 持久化入口；仓库也存在索引和 GraphRAG 相关实现表面。

这些证据还不能证明完整 Knowledge Readiness、跨版本 ingestion、原子 Serving 切换、真实数据库 lineage lookup、全量故障恢复或 GraphRAG 的 query-class 收益。目标仍然是 design available；质量、规模和生产可靠性尚未证明。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

本模块拥有可重建知识派生和任务级知识资格语义，不拥有正式材料身份和法律业务结果。全局不变量：

1. `Document Uploaded != Knowledge Ready`。
2. DocumentVersion canonical identity 归 02；03 只围绕稳定 DocumentVersion ref 建立派生知识。
3. KnowledgeGeneration lifecycle != task-level ReadinessDecision。
4. Index write success != generation activated / serving。
5. PARTIAL 必须绑定显式 covered scope / missing requirement，不能冒充完整范围 READY。
6. EvidenceCandidate != formal Evidence；CitationLineage != WorkProductCitationBinding。
7. Chunk / Vector / Graph Node ID 不成为长期 Citation Authority。
8. Security revocation 可以使一次新的 Readiness / Retrieval 不成立，但不会把一个历史 KnowledgeGeneration 改写成新的 Domain fact。
9. GraphRAG 是 query-class / evidence-gated 能力，不默认 always-on。

### B2 Responsibility / Ownership

| 责任 / 事实 | 本模块权限 | 其他边界权限 |
| --- | --- | --- |
| DocumentVersion | 只消费稳定 ref | 02 创建 / 版本化 / 拥有正式身份 |
| KnowledgeGeneration | 创建、处理、版本化、stale / rebuild | Platform 只提供物理原语 |
| Processing projection / item status | 创建、更新、重试 | 不成为 Domain truth |
| IndexManifest / Serving Watermark | 校验、激活、切换、回滚到合法 generation | 物理 Index Provider 不拥有 Serving 语义 |
| ReadinessDecision | 针对 task scope + requirements + security 计算 | 01 / 04 消费，不重算知识事实 |
| EvidenceCandidate / RetrievalResult | 产生、排序、来源绑定 | 02 可正式接纳为 Evidence |
| CitationLineage | 创建、持久化必要 lineage | 02 只保存可选 lineage ref / 正式 historical binding |
| WorkProductCitationBinding | 不拥有 | 02 是唯一正式历史引用 Owner |
| Knowledge retention / deletion execution | 执行本 Store 的政策 | 08 是 Effective Lifecycle Policy Owner |

### B3 Upstream / Downstream

| 方向 | 责任域 | 本模块接收 / 输出 | 边界规则 |
| --- | --- | --- | --- |
| 上游 | 02 Legal Domain | DocumentVersion refs、matter / source identity | 03 不重新定义材料正式身份 |
| 上游 | 08 Security | AuthorizationDecision、Security Epoch、egress / lifecycle refs | 03 执行，不重算政策 |
| 上游 | 01 / 04 | task Scope、retrieval requirement、minimum processing capability | Readiness 必须绑定请求要求 |
| 上游 | Platform / Providers | parse / OCR / index write physical receipts | 物理成功不自动成为 knowledge success |
| 下游 | 01 / 04 | ReadinessDecision、coverage / missing requirement | 由调用方决定等待、缩小 Scope 或停止 |
| 下游 | 02 / 04 / 05 | EvidenceCandidate、RetrievalResult、CitationLineage | 候选不能绕过 02 正式准入 |
| 下游 | 09 | processing / retrieval / generation metric refs | Telemetry 不成为来源权威 |

### B4 Authoritative Facts / Core Objects

这里冻结对象职责，不冻结表或 class：

| 对象 / 事实 | 目的 | 最低语义 |
| --- | --- | --- |
| KnowledgeGeneration | 标识一代可重建知识派生 | 绑定 DocumentVersion set / processing spec / generation identity |
| ProcessingItem / Projection | 跟踪材料、页面或处理项状态 | 可以失败和重试，不能静默吞错 |
| IndexManifest | 描述某 generation 实际包含哪些派生视图 | 用于完整性和激活校验 |
| Serving Watermark / ServingGeneration | 指示当前可服务的合法 generation | 激活必须在完整性校验之后 |
| ReadinessDecision | 判断某 task scope 是否可安全使用当前知识 | 绑定 generation、scope、requirements、security refs |
| EvidenceCandidate | 从当前允许范围中恢复出的证据候选 | 绑定 source DocumentVersion / stable location |
| RetrievalResult | 一次检索 / 重排输出 | 保留 query / generation / scope / candidates refs |
| CitationLineage | 解释候选怎样被检索和排序 | 不替代正式历史引用绑定 |

KnowledgeView 可以作为 generation 内部或跨 Provider 的派生视图概念；是否需要独立持久对象由后续详细设计决定，不因为某种存储存在就自动新增 Canonical data model。

### B5 Cross-boundary Contracts

#### ReadinessDecision（生产）

- Purpose：回答当前任务是否能够基于指定材料和知识 generation 安全执行。
- Producer / Authoritative Owner：03 Knowledge & Evidence。
- Consumer：01 Application & Integration、04 Agent Runtime & Control；必要时 02 admission eligibility 消费引用。
- Input / Output：DocumentVersion refs、KnowledgeGeneration ref、task Scope、minimum processing / retrieval requirement、Authorization / Security refs → READY / PARTIAL / BLOCKED 类语义 + coverage / missing requirement refs。
- Versioning：绑定 generation、task scope 和 policy / security refs；最终字段 / enum 尚未冻结。
- Validation：scope coverage、source version、generation serving eligibility、required processing capability、authorization 均可追溯。
- Failure Semantics：不完整时返回 PARTIAL / BLOCKED，不默认扩大结果资格。
- Idempotency / Replay：相同输入条件可重复计算；安全策略或 serving generation 改变后必须重新评估。
- Security Requirements：当前授权是判断输入，不可使用过期授权缓存静默放行。
- Persistence Requirement：保存决定或足够的可重建 refs 由后续模块评审决定；关键 serving / generation facts 必须耐久。
- Observability Requirement：记录 decision identity、coverage、missing reason，不记录不必要全文。
- Evidence：Partial Knowledge Fault Test、security revocation tests、跨版本 readiness tests。

#### EvidenceCandidate + CitationLineage（生产）

- Purpose：把当前允许范围中的证据候选和检索来源交给 Runtime / Capability / Domain。
- Producer / Authoritative Owner：03。
- Consumer：02、04、05、01 direct QA path。
- Input / Output：query / task scope + serving generation + security scope → candidate refs、source DocumentVersion / stable location、retrieval / rerank lineage。
- Versioning：绑定 DocumentVersion、KnowledgeGeneration 和 retrieval identity。
- Validation：来源必须稳定定位；stale generation / unauthorized source / scope mismatch 不得静默返回为合法候选。
- Failure Semantics：zero evidence、insufficient evidence、partial coverage、provider failure 必须显式区分。
- Idempotency / Replay：同一固定输入可重放，但 ranking provider 变化需记录 provider / spec reference；不以重放结果改写过去正式 citation。
- Security Requirements：retrieval 前和必要外发边界消费当前授权。
- Persistence Requirement：必要 lineage / source refs 可耐久保存；底层完整 ranking trace 不自动成为长期业务事实。
- Observability Requirement：记录候选数、来源完整性、检索策略 / latency refs，敏感正文最小化。
- Evidence：Citation Provenance Guard、retrieval / lineage integration tests。

#### KnowledgeGeneration / Serving Activation（跨 Platform / Provider）

- Purpose：把物理处理和索引写入提升为一个可恢复、可服务的知识 generation，而不是用单个 provider 成功回执宣布 READY。
- Producer：03 组合 generation / manifest / activation；Platform / Index Provider 产生物理 write receipts。
- Consumer：03 Readiness / Retrieval、01 / 04 indirect consumers。
- Authoritative Owner：03 拥有 knowledge generation 和 serving eligibility；Platform 只拥有其物理 primitive receipt。
- Input / Output：DocumentVersion set + processing spec + per-item / index receipts → staged manifest → validated serving generation / failed activation。
- Versioning：generation identity 与 processing spec 不可混用；新的 source version 产生新的或明确派生 generation。
- Validation：manifest completeness、source lineage、required projections 和 provider receipt 一致。
- Failure Semantics：partial write / incomplete manifest / source mismatch 时不得激活。
- Idempotency / Replay：同 generation + spec 的 processing item 可幂等重试；激活操作必须识别既有 watermark。
- Security Requirements：生成和索引遵守 tenant / matter / lifecycle / egress policy。
- Persistence Requirement：generation metadata、manifest、processing state 和 serving pointer 需要可恢复。
- Observability Requirement：build / activation / rollback / stale reasons 可观测，但 receipt 不等于 business truth。
- Evidence：后续 serving switch fault tests、index rebuild tests。

### B6 Normal Flow

**构建与激活：**

```text
DocumentVersion refs
→ derive processing spec + KnowledgeGeneration identity
→ parse / OCR / normalize / chunk
→ build keyword / vector / optional graph views
→ collect per-item / provider receipts
→ validate manifest + source lineage + required coverage
→ stage generation
→ atomically publish / move serving pointer within knowledge boundary
→ expose generation for task-level ReadinessDecision
```

“atomically publish”指知识边界内的 serving pointer / manifest 可恢复切换，不意味着和 Domain Store、Runtime Checkpointer 做跨系统 2PC。

**任务检索：**

```text
task Scope + requirements + current AuthorizationDecision
→ choose eligible serving generation
→ compute ReadinessDecision
→ READY: retrieve / rerank / optional GraphRAG
→ EvidenceCandidate + CitationLineage

PARTIAL: expose covered scope + missing requirements
BLOCKED: no full-scope retrieval eligibility
```

### B7 State / Lifecycle

必须分开两套状态语义；这里不冻结最终 enum。

**KnowledgeGeneration 生命周期：**

```text
DECLARED
→ PROCESSING
→ STAGED / BUILT
→ SERVING
→ STALE / SUPERSEDED
→ REBUILDING when needed

任何阶段都可能 → FAILED / PARTIAL_BUILD
```

含义：Generation 生命周期描述一代知识派生本身。`STAGED / BUILT` 不等于 `SERVING`；`SERVING` 也不代表所有 task requirement 都满足。

**ReadinessDecision（任务级判断）：**

```text
(DocumentVersion refs + serving generation + task Scope + requirements + security)
→ READY
→ PARTIAL
→ BLOCKED
```

PARTIAL 必须携带 covered scope / missing requirement；当调用方接受缩小 Scope 后，应重新计算一个针对新 Scope 的 ReadinessDecision，而不是把原 PARTIAL 直接改名为 READY。

**Staleness 分离：** stale KnowledgeGeneration 归 03；stale Finding / WorkProduct 归 02。Generation stale 可以触发上层重新评估，但不能直接写领域失效事实。

### B8 Failure Taxonomy

| 失败 | 检测 Owner | Canonical / knowledge fact | 立即动作 | Retry / Replan / Human |
| --- | --- | --- | --- | --- |
| parse / OCR 单项失败 | 03 | processing item failed | 保留精确失败范围 | 同 spec 可 Retry；关键缺失时上层决定 |
| partial index write | 03 + provider receipt | generation 不得 SERVING | 继续 / 回滚未完成 generation | Retry processing，不需要 Domain 回滚 |
| manifest incomplete | 03 | activation rejected | 不移动 serving pointer | 修复后 Retry activation |
| source DocumentVersion mismatch | 03 | generation invalid for requested source | BLOCKED / stale | 新 generation；04 可能 Replan |
| serving watermark 漂移 / 丢失 | 03 | serving eligibility unknown | fail closed / recover pointer | Recovery；无法判断时人工运维 |
| security revoked | 08 决定，03 执行 | 新 Readiness / Retrieval denied | 不再读取受保护内容 | 重新授权后重算 |
| zero evidence | 03 | valid retrieval result with no candidates | 返回 ZERO / insufficient | 不应盲目重复；04 / 05 决定重写 query / Replan |
| evidence coverage partial | 03 | PARTIAL | 返回缺失范围 | 可缩 Scope / 等待 / Human |
| GraphRAG path failed | 03 provider | graph path unavailable | 若非硬要求可回退已资格路径 | 回退需满足同一 task requirement；否则 Replan |
| index corruption | 03 / Platform | derived view invalid | 从 immutable source rebuild | Recovery / rebuild |
| provider outage | 03 / Platform | processing / retrieval unavailable | 暂停或切 eligible provider | Retry；provider semantic change 需 Replan |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

- **Retry（重试）**：DocumentVersion 和 processing spec 不变时，parse / OCR / embedding / index item 等纯派生处理可按稳定 item identity 幂等重试。
- **Replan（重规划）**：任务依赖的材料版本、所需 capability、可用 retrieval path 或 coverage 假设发生变化时，由 04 决定新计划；03 只返回知识事实。
- **Reconcile（对账）**：03 不拥有外部业务副作用对账。对物理 Provider 的 write receipt 只用于确认 generation 构建 / 激活，不升级为 Tool Effect business truth。
- **Recovery（恢复）**：以不可变 DocumentVersion refs + processing spec + KnowledgeGeneration metadata + manifest + serving pointer 为知识恢复锚点；索引可以重建。
- **Idempotency（幂等）**：同一 generation identity 不得混入不同 processing spec；重复 item / manifest / activation 必须识别已有结果。

### B10 Security / Approval / Audit

所有处理、检索、缓存、派生视图和模型外发受 tenant / matter / source scope / current Security Epoch 约束。

03 不拥有 Authorization / Approval policy。它执行 08 的决定：没有权限的 source 不进入新的检索；受保护内容外发模型还要满足 model egress policy；Secret 不写入 chunk / embedding metadata / trace。

Effective Lifecycle Policy 由 08 决定。03 Store 执行自己的 retention / deletion / legal hold / purge obligation。删除未来 Recall / Retrieval 资格与是否因 Legal Hold 保留物理字节是不同语义。

普通 ingestion / retrieval telemetry 不替代安全审计；需要 mandatory durable audit 的动作必须使用对应安全策略要求的耐久边界。

### B11 Persistence / Transaction Boundaries

原始业务 DocumentVersion identity 归 02；原始文件字节由相应 Platform / object storage primitive 承载。03 至少需要可恢复保存 generation metadata、processing status、manifest、必要 lineage 和 serving pointer / watermark；具体 schema 未冻结。

关键知识发布边界：

```text
per-item processing / provider writes
    ↓
validated generation manifest
    ↓
serving activation pointer
```

只有 validated manifest 对应的 generation 才能被激活。部分写入不能通过某个 index provider 的 2xx / ACK 自动成为 current serving generation。

Serving 激活是知识边界内部的可恢复切换，不要求与 02 Domain transaction 或 04 Runtime checkpoint 同事务。跨 Store 2PC 不是默认方案。

重建索引时必须从稳定 DocumentVersion / source representation + processing spec 恢复，不通过当前最相似 chunk 反推过去正式引用。

### B12 Observability / Evaluation

处理链至少观测：source / generation identity、processing coverage、parse / OCR failure、build latency、manifest completeness、activation / rollback result、stale reason。

检索链至少观测：task / scope / generation refs、ReadinessDecision、retrieval latency、candidate count、zero-evidence、lineage completeness、recall / precision / rerank、security / scope rejection。

GraphRAG 必须按 query class 对比简单 retrieval baseline，在同模型、同语料和可比预算下测量质量、成本、延迟和维护失败面。只报告“GraphRAG 能跑”不能证明它值得成为默认路径。

### B13 Current / Target / Gap / Evidence

**Current**：[`current-runtime-baseline.md`](../evidence/current-runtime-baseline.md) 与 [`implementation-wave-001.md`](../evidence/implementation-wave-001.md) 证明部分 ingestion owner、Citation Provenance Guard、stale / scope 校验和若干索引 / GraphRAG 实现表面。

**Target**：可版本化、可恢复的 KnowledgeGeneration + serving activation + task-level ReadinessDecision + EvidenceCandidate / CitationLineage 边界；底层 retrieval / graph provider 可替换。

**Gap**：真实数据规模和数据库 lineage lookup、跨 DocumentVersion ingestion、manifest / serving atomic switch、partial knowledge E2E、security revocation、provider corruption recovery、GraphRAG query-class 对照测量和生产索引迁移。

**Evidence required before Current upgrade**：真实或代表性语料 ingestion、数据库 / object store / index integration、fault injection、stale / scope / revocation tests、retrieval evaluation、rebuild / serving switch recovery。文档和类名不算实现证据。

### B14 Code / Database / Migration Constraints

实现前先冻结 generation identity、processing spec、manifest / serving semantics、ReadinessDecision 输入与资格语义、EvidenceCandidate identity 和 CitationLineage 稳定引用，再决定数据库和索引 schema。

不得用向量库、图数据库或 chunker 的内部 ID 反向定义正式领域模型。Provider 更换和 index migration 必须能在不改写已发布 WorkProductCitationBinding 的前提下完成。

本 Design Baseline 不默认建立独立 Knowledge 微服务，不要求 always-on GraphRAG，不授权全量索引重构。实现应优先使用 adapter / worker / modular backend，物理拆分继续受 ADR-0012 的证据门控。

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

知识构建完成必须按层次证明：Provider 写入成功只证明物理动作；validated manifest 证明 generation 的声明内容与来源一致；serving pointer / watermark 证明当前 generation 已被知识边界激活；ReadinessDecision 才证明某个具体 task scope 在当前 requirement 与安全条件下可使用。

因此：

```text
index write success
!= generation valid
!= generation serving
!= task READY
!= formal Evidence / WorkProduct
```

03 的 EvidenceCandidate / CitationLineage 也不是 02 的正式 Evidence / WorkProductCitationBinding。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Readiness / Retrieval 至少绑定：DocumentVersion set、KnowledgeGeneration、processing spec / serving generation、task Scope、minimum requirements、AuthorizationDecision / SecurityEpoch 和 retrieval identity。任何关键绑定变化后，旧 Readiness 不能静默复用。

KnowledgeGeneration identity、ProcessingItem identity、ReadinessDecision identity、Retrieval identity 分属不同幂等 / 因果 namespace；不能使用一个“document job id”同时代表处理、激活、检索和任务资格。

向 02 / 04 / 05 输出晚到候选时，必须保留其 source DocumentVersion、generation 和 scope，供消费者判断它是否仍适用于当前 PlanVersion / DomainVersion。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

取消 ingestion / rebuild 只能停止后续派生工作；未通过完整性校验的 generation 不得因为“多数 item 已完成”而进入 serving。已经 serving 的旧 generation 是否继续服务，由当前 source / policy / activation 状态决定，不因新 build 被取消而自动消失。

晚到的 OCR、embedding、graph 或 retrieval 结果必须校验 generation / processing spec / DocumentVersion / security scope；属于旧 generation 或旧权限的结果不能写入当前 manifest，也不能参与新的 task Readiness。

03 的 stale 只描述知识派生新鲜度。新 DocumentVersion 到来后，03 可以把旧 generation 标成不适用于新 source set，但正式 Finding / WorkProduct 是否 stale 仍由 02 依据正式依赖判断。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

知识恢复顺序优先使用不可变源与自己的 durable metadata：

```text
02 DocumentVersion / source identity
→ 03 generation metadata + processing spec
→ per-item / provider receipts
→ validated manifest
→ serving pointer / watermark
→ current 08 security input
→ recompute task Readiness
→ 09 补 telemetry
```

至少验证：partial write 不激活；build 取消后 generation 非 serving；serving pointer 写入前 / 后崩溃；新 DocumentVersion 到来时旧 retrieval 晚到；权限撤销发生在 Readiness 后、retrieval 前；同 generation identity 混入不同 processing spec 时拒绝；GraphRAG provider 失败仅在同一 requirement 可满足时回退；索引重建后历史 WorkProduct 引用不漂移。
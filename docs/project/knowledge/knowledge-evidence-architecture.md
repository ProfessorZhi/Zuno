# Knowledge & Evidence Architecture：文档如何变成可引用证据？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 文档如何经过摄取、检索和验证形成可追溯的 Evidence Candidate？
owner: Knowledge and Evidence Owner
replaces: docs/project/modules/02-input-document-ingestion.md、03-knowledge-agentic-graphrag.md（Superseded）

## Part A — Architecture Narrative

### Knowledge 的业务目的

Knowledge 层解决的是“从哪些材料找到什么证据”，不是直接宣布法律事实。它把 DocumentVersion 解析为 SourceSpan，按 QueryClass 和 Scope 选择检索策略，返回带来源的 EvidenceCandidate 和 CitationLineage。Memory 是可过期的 Context，Graph 是一种关系 Projection，Knowledge 结果也不等于 Domain Truth。

### Target Scenario：从材料到证据

这是 Target Scenario，不是历史事实：

用户上传 DocumentVersion，系统保留原始内容 hash、来源和 ACL。Ingestion 解析文档、页码、段落和 SourceSpan，建立词法、Dense、Hybrid 或 Rerank 索引。Agent 提出 Claim 和 EvidenceRequirement，Knowledge 根据查询类型检索 EvidenceCandidate；候选引用 DocumentVersion、SourceSpan、Scope 和 IndexVersion。若 Parser 或索引版本并发完成，只有带有 published generation 的结果可以进入检索；Domain Owner 后续决定是否接收为 EvidenceVersion。

Happy Path 是：DocumentVersion → Parse → SourceSpan → QueryClass/Scope → Retrieval → EvidenceCandidate → Domain Admission。

### Graph、Memory、Citation 和 Truth 的边界

Exact Statute、简单语义相似和短查询可能由 Lexical/Hybrid 完成；跨文档关系、事实—要件—法条链或 Party Event ↔ Conflict ↔ Event 可能需要 Graph Provider。Graph Path 不是 Citation，Citation 必须落到可审计 SourceSpan。Memory 不是 Knowledge，Knowledge 也不能取代 Domain State。GraphRAG 只有在 Kill Graph Test 中有增益才进入条件路径。

### 责任与非责任

Knowledge Owner 负责 Source、Parse、Chunk、Index、Retrieval、Citation Lineage、Graph/Vector Projection 和 EvidenceCandidate；不负责接受 Fact、Finding、HumanDecision，不拥有 Matter 权限真相，也不决定 Tool Action。Domain 提供 DocumentVersion 和 ACL，Security 决定可见 Scope，Agent Runtime 提供任务和 Claim。

### 失败、取舍与反转

索引可能 stale、不可用、互相不一致或返回错误 span；Scope 选择错误还可能造成跨 Matter 泄漏。系统必须显式返回 no_evidence、stale_index、scope_denied 或 provider_unavailable，而不是伪造高置信答案。索引、Graph 和 Rerank 增加构建、存储、延迟和维护成本；若 Hybrid RAG 覆盖目标任务，Graph 降级；若 Matter DB 加简单检索已足够，删除复杂 Projection。发布门本身也要可恢复：旧 Projection 可以继续服务已声明范围，但不能把未发布的部分混入同一 CitationLineage。

### Current / Target / Gap

Current 只由代码、配置、测试和运行证据证明；Target 是多 Scope Knowledge、证据引用和条件 Graph Provider；Hypothesis 是定向检索和跨文档关系改善证据充分性；Gap 是 Court QA、Citation、Graph Kill Test、ACL、stale Index、成本和召回测量。

## Part B — Detailed Architecture Specification

### Ingestion Contract

输入是 DocumentVersion、ContentHash、Source、ACL、ParserVersion 和 JobId；输出是 ParseArtifact、SourceSpan、Chunk、IndexWriteBatch、ProjectionVersion 或 typed failure。重复上传和重复 Job 必须由 DocumentVersion Identity 与 Idempotency Key 收敛。原始 Artifact 属于 Domain/Document Owner，解析和索引属于 Knowledge Projection。

### Retrieval Contract

请求包含 Matter/Scope、QueryClass、Claim、EvidenceRequirement、DocumentVersion Range、budget 和 SecurityEpoch。响应包含 EvidenceCandidate、SourceSpan、DocumentVersion、IndexVersion、retrieval_method、rank、CitationLineage、Receipt、stale/denied 状态。结果不能直接产生 FactVersion 或 FindingVersion。

### Scopes and conditional GraphRAG

Knowledge Scope 至少区分 Public、Organization、Matter 和 User/Session；Scope selection 只限制候选边界，不等于 retrieve everything。GraphRAG 是 conditional provider：只有 Kill Graph Test 证明关系型、跨文档或多证据链任务获得 Recall、Evidence Sufficiency 或 Citation Correctness 增益，才进入对应 QueryClass；Exact Statute 等任务可以继续使用 Lexical/Hybrid。

### Scope and security

Public、Organization 和 Matter Scope 分层选择；Scope selected 不等于 retrieve everything。每次检索按 Tenant、Matter、ACL、Policy Epoch 和 legal hold 检查。跨 Scope 或授权失效返回 scope_denied，并留下审计引用。

### Index and Graph policy

Lexical、Dense、Hybrid、Rerank、Graph 和 Corrective Retrieval 是 Provider 策略。Graph Build 记录 source version、edge provenance、projection version 和 rebuild cursor；Graph 不可用时回退到 Hybrid 或明确 blocked。Graph Path 不能作为 Citation，最终引用必须有 SourceSpan。

### Publication and staleness gate

Ingestion、Index 和 Graph Worker 只能写候选 Projection；Knowledge Owner 根据 SourceVersion、ACL、ProjectionVersion 和发布游标原子地发布可检索范围。检索前比较 Matter/DocumentVersion 与 ProjectionVersion，发现撤权、删除、回滚或覆盖不足时返回 stale/denied/blocked。旧 Citation 不被静默改写；需要新 span 时产生新的 lineage，供 Domain Admission 决定是否重算。

### Failure、Retry 与 Recovery

Parser、Index 和 Provider 的 transient failure 可以 bounded retry；timeout、stale_index、scope_denied、version_conflict 和 unknown result 必须显式传播。Recovery 重新读取 DocumentVersion、ACL 和 ProjectionVersion，再 Resume、Rebuild、Fallback 或进入 Review，不能把队列完成当作 Evidence 成功。

### Failure, retry and evidence

Parser/Index/Provider transient failure 可以 bounded retry；版本变化、ACL 变化、索引不一致和 stale 必须重新检索或人工审查。测量至少包含 Recall@K、nDCG、Evidence Sufficiency、Citation Correctness、Unsupported Claim Rate、Latency、Token 和 Cost。

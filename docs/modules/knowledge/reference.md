# 03 Knowledge & Evidence（知识与证据） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

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

**Current**：[`current-runtime-baseline.md`](../../evidence/current-runtime-baseline.md) 与 [`implementation-wave-001.md`](../../evidence/implementation-wave-001.md) 证明部分 ingestion owner、Citation Provenance Guard、stale / scope 校验和若干索引 / GraphRAG 实现表面。

**Target**：可版本化、可恢复的 KnowledgeGeneration + serving activation + task-level ReadinessDecision + EvidenceCandidate / CitationLineage 边界；底层 retrieval / graph provider 可替换。

**Gap**：真实数据规模和数据库 lineage lookup、跨 DocumentVersion ingestion、manifest / serving atomic switch、partial knowledge E2E、security revocation、provider corruption recovery、GraphRAG query-class 对照测量和生产索引迁移。

**Evidence required before Current upgrade**：真实或代表性语料 ingestion、数据库 / object store / index integration、fault injection、stale / scope / revocation tests、retrieval evaluation、rebuild / serving switch recovery。文档和类名不算实现证据。

### B14 Code / Database / Migration Constraints

实现前先冻结 generation identity、processing spec、manifest / serving semantics、ReadinessDecision 输入与资格语义、EvidenceCandidate identity 和 CitationLineage 稳定引用，再决定数据库和索引 schema。

不得用向量库、图数据库或 chunker 的内部 ID 反向定义正式领域模型。Provider 更换和 index migration 必须能在不改写已发布 WorkProductCitationBinding 的前提下完成。

本 Design Baseline 不默认建立独立 Knowledge 微服务，不要求 always-on GraphRAG，不授权全量索引重构。实现应优先使用 adapter / worker / modular backend，物理拆分继续受 ADR-0012 的证据门控。

#### B14.1 Detail Freeze Candidate：KnowledgeGeneration / ProcessingSpec / Manifest 字段组

下面只冻结 Target 的语义字段组，不冻结最终表名、ORM class、索引 Provider collection schema 或消息队列 payload。

**KnowledgeGeneration candidate** 至少需要：

```text
tenant_id / matter_id
generation_id
document_version_set_ref 或稳定 document_version_set_hash
processing_spec_id / processing_spec_hash
required_view_profile
lifecycle_state
created_at
```

`processing_spec` 必须能解释这一代知识采用的 parser / OCR / normalization / chunking / embedding / optional graph 构建等会影响语义或可重建性的规格。它不是一个随意的“配置 JSON”；发生语义改变时必须能够区分新旧 generation。

**ProcessingItem identity** 至少绑定：

```text
generation_id
document_version_ref
item_kind
item_locator
processing_spec_hash
```

`item_locator` 可以表示 document/page/table/view partition 等可恢复工作单元。重复 Worker delivery 必须落回同一个稳定 item identity；不能因为一次队列 delivery_id 不同就生成第二份逻辑处理结果。

**IndexManifest candidate** 至少描述：generation、DocumentVersion set / hash、processing spec hash、required view profile、各类 ProcessingItem 完成 / 失败覆盖、Provider receipt refs、view descriptors、source lineage digest、manifest hash、validation result 和 validated_at。

**ServingPointer candidate** 是 03 的小型权威元数据，不是向量库 alias 本身。逻辑上至少按 `(tenant, matter, knowledge_profile)` 选择当前可服务 generation，并保存 current generation、previous generation / rollback ref、activation version 和 activated_at。具体是否使用单表、CAS 行或其他存储由实现任务确定。

#### B14.2 Detail Freeze Candidate：Readiness / Retrieval / EvidenceCandidate Contract

一次 `ReadinessDecision` 不能只保存 `READY`。输入指纹至少绑定：

```text
requested DocumentVersion set / set hash
task scope / scope hash
minimum processing capabilities
retrieval requirement / quality profile when applicable
selected serving generation
AuthorizationDecision ref / SecurityEpoch
```

输出 candidate 至少包含：

```text
readiness_decision_id
input_fingerprint
generation_id
READY | PARTIAL | BLOCKED 类语义
covered_scope / covered_document_refs
missing_requirements / missing_sources / reason codes
security_epoch_ref
evaluated_at
```

PARTIAL 只有在“覆盖了什么、缺了什么”都可解释时才有意义。调用方缩小 Scope 后产生新的 input fingerprint 和新的 ReadinessDecision；禁止原地把旧 PARTIAL 改成 READY。

一次 RetrievalRequest 至少绑定 `retrieval_id + readiness_decision_id + query/query_hash + generation_id + scope + retrieval_strategy_version + current security refs`。Query Rewrite 可以改变检索表达，但不得修改原始允许 Scope。

EvidenceCandidate candidate 至少保存或可稳定恢复：candidate identity、source DocumentVersion、stable source location、source representation hash、candidate/excerpt hash、generation、retrieval identity、CitationLineage ref，以及非权威 ranking / score metadata。相似度分数不是 Evidence identity，也不能决定正式准入。

#### B14.3 Detail Freeze Candidate：Generation / Serving / Readiness 状态 Guard

KnowledgeGeneration 的状态变更至少服从：

```text
DECLARED
  → PROCESSING
  → STAGED
  → SERVING
  → STALE / SUPERSEDED

PROCESSING / STAGED → FAILED / PARTIAL_BUILD when applicable
```

关键 Guard：

1. `PROCESSING → STAGED`：所要求的处理项已经达到可验证终态，manifest 可生成且来源集合匹配；
2. `STAGED → SERVING`：manifest validation 通过，DocumentVersion set / processing spec 没漂移，required view profile 满足，当前 lifecycle / security policy 没禁止服务，并且 serving activation version 条件匹配；
3. `SERVING → STALE`：源材料版本集合、processing eligibility、生命周期政策或 provider integrity 发生使该 generation 不再适合当前服务的变化；
4. 新 generation SERVING 后，旧 generation 可以变为 SUPERSEDED 并按政策保留用于恢复 / 历史 provenance；不能直接覆盖其 metadata；
5. FAILED / PARTIAL_BUILD generation 不因“多数 item 成功”自动获得 Serving 资格。

ReadinessDecision 是一次判断结果，不是长生命周期实体的状态机。其输入任一关键 version / scope / security 条件改变后，必须重新计算；旧 READY 不被“更新”为新 READY。

#### B14.4 Detail Freeze Candidate：Persistence 与 Serving Activation 事务候选

第一阶段把三类耐久事实分开：

- 原始材料字节：Platform Object Store primitive，业务身份仍由 02 DocumentVersion 拥有；
- generation / processing / manifest / serving metadata：03 的 durable metadata store；
- BM25 / vector / graph 等派生内容：Provider-specific derived stores，可重建。

Provider 写入可能跨多个系统，因此不使用跨所有 Index Provider 的 2PC。目标流程是：

```text
build provider projections
→ collect receipts / descriptors
→ persist and validate complete manifest
→ short metadata transaction / CAS:
     compare expected activation version
     point serving profile to validated generation
     record activation fact / version
→ expose to new Readiness decisions
```

Serving 切换必须是一个可恢复发布点。若 Provider 已写成功但 metadata / manifest 没完成，这些数据只是 orphan / staged derivative，不获得服务资格；后台清理可以后做，正确性不能依赖立即物理删除。

并发构建两个 generation 时允许两者都 STAGED，但同一个 serving profile 的切换通过 `expected_activation_version` 或等价 CAS 条件序列化。失败者重新读取当前 pointer 后再决定是否仍值得激活，而不是 last-write-wins。

#### B14.5 Detail Freeze Candidate：Worker、Backpressure、Cache 与并发规则

Ingestion / rebuild Worker 默认按 **at-least-once 可重放** 思路设计：Queue 只负责调度，不证明处理完成。稳定 ProcessingItem identity + generation/spec/content fingerprint 负责去重；同 identity 不同 processing spec 必须冲突或进入新的 generation。

长耗时 OCR / embedding / graph 构建可以并行，但必须受 tenant quota、Provider quota、Worker capacity 和资源预算约束。Queue backlog 达到门限时，03 应显式限制新的 build / rebuild 接收或降低调度速率；不能因为排队过长就在 Readiness 中假装任务已经覆盖。

如果实现需要 Lease / Fencing，由 Platform 提供原语，03 定义业务验收条件：晚到 Worker 结果只有在 generation、processing spec、item identity 和当前 lease/fencing 条件仍匹配时才可进入 manifest；失效 Worker 的成功回执不能污染新 generation。

缓存分三类看待：解析 / embedding 等内容寻址缓存、retrieval cache、readiness 辅助 cache。Cache key 必须包含真正影响语义的新鲜度，例如 source/content hash、processing spec、generation、scope、retrieval strategy 和必要 SecurityEpoch。默认不得跨 tenant 共享带业务内容的 cache entry；如果未来做共享内容缓存，需要独立的去标识化 / 权限证明。

Cache 永远只是 Projection 优化。缓存丢失只应该降低性能，不得丢失 Serving truth、Readiness authority 或正式 Citation history。

#### B14.6 Detail Freeze Candidate：Crash Window 与恢复矩阵

| Crash Window | 当前可以相信什么 | 恢复动作 | 禁止动作 |
| --- | --- | --- | --- |
| Provider write 成功、ProcessingItem metadata 未写 | 只有 provider physical data | 按 item identity 查询 / 重做并收敛 metadata | 直接计入 manifest complete |
| manifest 已保存，validation / activation 前崩溃 | generation 仍是 STAGED / non-serving | 重新校验 manifest 后 Retry activation | 查询自动看到新 generation |
| serving pointer 已切换但响应丢失 | 当前 pointer / activation version 是 03 truth | 重读 pointer，返回既有 activation | 再次无条件覆盖 pointer |
| 两个 STAGED generation 同时激活 | 只有一个满足 activation CAS | 失败方重读并重新决策 | last-write-wins |
| build 被取消且已有部分 provider 写入 | 部分派生可能物理存在 | 标记非 serving；后续清理或重建 | 因“已经算完很多”强制激活 |
| Readiness 后、Retrieval 前权限撤销 | 旧 decision 的 allow 已过期 | Retrieval 前重新消费当前 SecurityEpoch / authorization | 复用旧 READY 绕过权限 |
| Readiness 后新 DocumentVersion 进入目标 Scope | 旧 decision 只绑定旧 version set | 新任务 / 新 scope 重新选择 generation 与 Readiness | 把旧 READY 静默扩到新材料 |
| retrieval 结果晚到时 generation 已 superseded | 结果仍是旧 generation 的历史候选 | 消费者按 version/scope/freshness 判断丢弃或复核 | 自动挂到当前 generation |

#### B14.7 Detail Freeze Candidate：Schema / Provider Evolution 规则

Parser、OCR、normalizer、chunker、Embedding、Graph extraction 或 retrieval processing spec 的变化，需要先判断是否改变可重建语义。如果改变了 source representation、chunk boundary、embedding space、graph schema 或 manifest requirement，就应形成新的 processing spec / generation，而不是原地重写当前 SERVING generation。

Provider migration 推荐 `build new generation → validate → switch serving pointer → observe → retire old provider data by lifecycle policy`。这使 Milvus / pgvector / graph store 迁移保持在知识投影层，不改写 02 的 DocumentVersion / WorkProductCitationBinding。

Metadata schema 迁移遵循 additive-first：新增字段 → backfill / reconstruct from durable refs → verify → 收紧约束。generation / manifest identity 算法如升级必须带 algorithm/version，旧 generation 继续可解释。

删除与 Legal Hold 继续遵守 08 的 Effective Lifecycle Policy。禁止未来 Retrieval 与物理 purge 完成是两个事实：某 generation 已不可召回，不代表其对象存储 / 索引副本已经全部擦除；反过来也不能因旧 bytes 尚存而继续提供检索资格。

大规模索引重建、online migration、dual-read / dual-write 是否必要，必须由真实数据规模、切换窗口和 rollback 需求决定；本文不预设 Kafka、CDC 或复杂双写架构。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

03 只有在以下矩阵形成实现和验证证据后，才进入 Module Detail Freeze Review：

| 场景 | 必须证明 |
| --- | --- |
| parse / OCR / embedding 单项失败 | 失败范围可定位；未完成 generation 不冒充 Ready |
| partial index write | manifest / Serving 不激活 |
| build cancel | 已写派生不获得 Serving 资格 |
| manifest source/spec mismatch | validation fail closed |
| same generation identity + different spec | 明确拒绝，不混写 |
| concurrent serving activation | CAS / 等价条件保证唯一 current pointer |
| crash before / after pointer switch | 能从 manifest + activation version 恢复正确 current generation |
| late Worker result | 旧 generation/spec/lease 结果不污染新 manifest |
| new DocumentVersion after old Readiness | 旧 decision 不自动覆盖新 version set |
| SecurityEpoch changes after Readiness | Retrieval 新受保护访问重新门禁 |
| retrieval cache stale | version/scope/security mismatch 不命中 |
| GraphRAG provider unavailable | 只有满足相同 task requirement 的 fallback 才继续，否则 PARTIAL/BLOCKED/Replan |
| provider index corruption | 可从 immutable DocumentVersion + processing spec rebuild |
| full reindex / chunk migration | 已发布 WorkProductCitationBinding 仍定位原 DocumentVersion / stable source location |

Freeze Review 还需要 representative corpus ingestion、object store / metadata store / provider integration、并发 activation、故障注入、security revocation、retrieval eval、GraphRAG query-class 对照和 rebuild evidence。设计字段写完不等于 Knowledge 实现完成。

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
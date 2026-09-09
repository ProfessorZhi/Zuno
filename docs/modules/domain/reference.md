# 02 Legal Domain & Work Product（法律领域与工作成果） — Engineering Reference

human_source: README.md
overall_architecture: ../../architecture/reference.md
current_evidence: ../../evidence/

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

本模块是正式法律业务状态的唯一权威边界，遵守以下全局不变量：

1. 第一阶段 Canonical Kernel 仅包含 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct；扩张必须另有架构依据。
2. Model、Knowledge、Capability、Specialist 和 Runtime 只产生 Proposal、Candidate、Observation、Reference 或 Receipt，不直接写 Canonical Domain State。
3. EvidenceCandidate != Evidence；CitationLineage != WorkProductCitationBinding。
4. Formal Admission 只有在持久化 Domain mutation 与匹配 AdmissionReceipt 成功后才成立。
5. 历史版本不可被静默覆盖；新证据通过依赖关系导致 review-required / stale 和新版本，而不是 destructive rewrite。
6. Runtime Checkpoint、Index write、Queue ACK、HTTP 2xx 和 Telemetry 都不能单独证明 Domain Success。
7. Domain Commit + AdmissionReceipt 与 Runtime Checkpoint 之间默认不使用跨 Store 2PC。

### B2 Responsibility / Ownership

| 责任 / 事实 | 本模块权限 | 其他边界权限 |
| --- | --- | --- |
| Matter / DocumentVersion identity | 创建、版本化、失效 / 生命周期执行 | 读取稳定引用，不自行创建替代身份 |
| Claim / Evidence / Finding | 正式准入、变更、依赖与失效 | 产生候选或读取快照 |
| HumanDecision | 保存正式人工业务决定 | UI / Host 可以采集输入，但不能拥有业务语义 |
| WorkProduct | 正式版本、有效性、历史保留 | 01 负责交付，不重算正式有效性 |
| AdmissionReceipt | 创建并与领域变更同事务提交 | 04 读取用于恢复，不修改 |
| WorkProductCitationBinding | 创建、验证、长期持久化 | 03 提供 CitationLineage / source refs，不拥有正式历史绑定 |
| Domain invalidation truth | 创建 / 变更 | 01 负责通知 Delivery / Ack observation |
| Retention / Deletion / Legal Hold policy | 不拥有政策，只执行本 Store 义务 | 08 是政策 Owner |
| Recovery truth | 领域版本 + AdmissionReceipt 是正式准入恢复锚点 | 04 修复 Runtime Control State |

**Does not own**：KnowledgeGeneration、ReadinessDecision、CitationLineage、Runtime Plan / Checkpoint、Authorization / Approval policy、Tool Effect truth、Delivery / Ack state、Telemetry projection。

### B3 Upstream / Downstream

| 方向 | 责任域 | 本模块接收 / 输出 | 边界规则 |
| --- | --- | --- | --- |
| 上游 | 03 Knowledge & Evidence | EvidenceCandidate、CitationLineage、source / generation refs | 候选不能自动升级为正式 Evidence |
| 上游 | 05 Capability & Skill | Finding / analysis proposal | 只接受候选，不接受 Provider 自称“已正式提交” |
| 上游 | 04 Agent Runtime & Control | run / PlanVersion / StepRun causation、proposal identity | Runtime 只能请求 Admission |
| 上游 | 08 Security & Governance | AuthorizationDecision、ApprovalDecision / policy refs | Domain 消费，不重算安全政策 |
| 上游 | Human / 01 Application | Human review input | 采集边界与领域决定语义分开 |
| 下游 | 04 Agent Runtime & Control | AdmissionReceipt、resulting DomainVersion | 用于完成条件和恢复 |
| 下游 | 01 Application & Integration | WorkProductVersion、WorkProductInvalidationFact | 01 负责发布 / 交付 / 通知 |
| 下游 | 09 Observability & Evaluation | 脱敏 domain/version/review refs | Telemetry 不成为业务权威 |

### B4 Authoritative Facts / Core Objects

七对象最小内核的职责语义如下；这里冻结语义，不冻结 ORM 字段或表：

| 对象 | 业务身份 | 关键依赖 / 生命周期 |
| --- | --- | --- |
| Matter | 一次长期法律业务事项 | 约束材料、主张、证据、结论和成果的业务范围 |
| DocumentVersion | 不可变材料业务版本 | 是知识派生和历史引用的稳定来源锚点 |
| Claim | 被正式记录的主张 | 可被 Evidence 支持 / 反驳，并影响 Finding |
| Evidence | 正式采用的证据 | 来源于稳定 DocumentVersion / span，可建立 Claim / Finding 依赖 |
| Finding | 正式结论 | 依赖 Claim / Evidence / HumanDecision，可能因新证据失效 |
| HumanDecision | 人工业务判断 | 接受、修改、拒绝或要求补充；不同于 Security Approval |
| WorkProduct | 对外或对内长期工作成果 | 版本化、绑定 Finding / Evidence / citation、支持 stale / review-required |

`WorkProductVersion` 是 WorkProduct 的版本化表达，不因为需要版本号就自动创建新的一级聚合。Event、Conflict、Dispute、LegalIssue、ApplicableLaw、SimilarCase 等默认保持 Proposal / Projection / Derived View，除非后续独立评审证明需要正式身份和生命周期。

### B5 Cross-boundary Contracts

#### EvidenceCandidate + CitationLineage（消费）

- Purpose：把 03 找到的证据候选及其检索来源送入正式领域判断。
- Producer：03 Knowledge & Evidence。
- Consumer：02 Legal Domain & Work Product。
- Authoritative Owner：EvidenceCandidate / CitationLineage 归 03；正式 Evidence 归 02。
- Input / Output：DocumentVersion ref、KnowledgeGeneration ref、source location、candidate payload / refs、CitationLineage → admission input。
- Versioning：必须能绑定明确 DocumentVersion / generation / scope；字段未冻结。
- Validation：来源可定位、版本未漂移、当前 Scope / Security 可用。
- Failure Semantics：来源不稳定、版本不匹配或 evidence insufficient 时不得自动准入。
- Idempotency / Replay：候选可重放；正式 Admission 由领域 idempotency identity 去重。
- Security Requirements：消费当前授权，不因候选已缓存而绕过权限。
- Persistence Requirement：候选可以是派生事实；正式采用后必须保存领域侧稳定引用。
- Observability Requirement：记录 candidate / lineage identity，不导出敏感正文。
- Evidence：Citation Provenance Guard、后续真实 lineage lookup tests。

#### AdmissionReceipt（生产）

- Purpose：证明某次运行请求导致了哪一个正式领域版本。
- Producer / Authoritative Owner：02 Domain Admission boundary。
- Consumer：04 Runtime、Recovery、Audit / Review。
- Input / Output：run identity、PlanVersion、StepRun identity、proposal / admission identity、idempotency identity、expected prior DomainVersion → resulting DomainVersion receipt。
- Versioning：绑定唯一 resulting DomainVersion 与预期前置版本。
- Validation：Domain mutation 与 Receipt 必须同一 PostgreSQL transaction durability boundary。
- Failure Semantics：无匹配 Receipt 时，不得宣布要求 Formal Admission 的 Step 正式完成。
- Idempotency / Replay：同一 admission / idempotency identity 重放返回既有合法结果；同 key 不同输入拒绝。
- Security Requirements：提交时重新消费当前授权和必要 HumanDecision / Approval references。
- Persistence Requirement：durable Domain boundary；不能只存在 Checkpoint / Trace。
- Observability Requirement：Trace 只引用 Receipt identity。
- Evidence：当前 mutation evidence + 后续 admission causation fault tests。

#### WorkProductCitationBinding（生产）

- Purpose：保存正式 WorkProductVersion 当时实际使用的不可变材料位置。
- Producer / Authoritative Owner：02，在正式准入时建立或验证。
- Consumer：Review、Audit、01 Delivery、后续 staleness analysis。
- Input / Output：DocumentVersion、immutable source ref / hash、stable location / span、source representation identity / hash、必要 excerpt / evidence hash、可选 CitationLineage ref → durable binding。
- Versioning：绑定 WorkProductVersion；不能被新 Index / Graph / Chunk 替换。
- Validation：必须回到原始不可变表示；索引内部 ID 不可作为唯一长期权威。
- Failure Semantics：正式成果要求的绑定不完整时，不得 Formal Admit 该成果。
- Idempotency / Replay：同一 WorkProductVersion + binding identity 幂等。
- Security Requirements：引用最小化、按权限展示，必要正文不写普通 Trace。
- Persistence Requirement：Domain durable boundary。
- Observability Requirement：只暴露稳定 identity / completeness 结果。
- Evidence：后续 source replacement / historical citation tests。

#### WorkProductInvalidationFact（生产）

- Purpose：声明某个已存在 WorkProductVersion 因正式依赖变化而失效或需要复核。
- Producer / Authoritative Owner：02。
- Consumer：01 Delivery、04 targeted reevaluation、Review / current-validity query。
- Input / Output：new DocumentVersion / Evidence / dependency change → affected WorkProductVersion + invalidation reason / dependency refs。
- Versioning：绑定被影响的正式版本，不覆盖历史版本。
- Validation：必须能说明由哪个已接纳依赖变化触发；不能由一次检索排名变化直接改正式状态。
- Failure Semantics：依赖图不足时扩大复核范围或进入人工复核，不能假装局部影响已知。
- Idempotency / Replay：同一 invalidation cause 对同一版本幂等。
- Security Requirements：通知内容由 01 按当前权限最小化。
- Persistence Requirement：Domain durable fact。
- Observability Requirement：Telemetry 只记录失效 identity / reason code refs。
- Evidence：后续 new-evidence staleness / invalidation tests。

### B6 Normal Flow

**新正式结果：**

```text
EvidenceCandidate / proposal
→ validate DocumentVersion + source + dependency
→ consume current AuthorizationDecision
→ evaluate required HumanDecision
→ compare expected prior DomainVersion
→ idempotency check
→ atomic domain mutation + AdmissionReceipt
→ create / validate WorkProductCitationBinding when applicable
→ expose resulting DomainVersion / WorkProductVersion
```

如果 WorkProduct 的合法性依赖历史引用绑定，则准入事务不能先把成果标为正式有效，再异步“以后补引用”；要么引用绑定已经存在并被验证，要么作为同一领域提交所依赖的耐久事实一起成立。

**新证据导致失效：**

```text
new canonical DocumentVersion / Evidence
→ dependency lookup
→ mark affected Finding / WorkProduct review-required or stale
→ emit WorkProductInvalidationFact
→ request bounded reevaluation when safe
→ new proposal
→ HumanDecision when required
→ new Formal Admission / new version
```

### B7 State / Lifecycle

这里冻结状态语义族，不冻结最终 enum 名称。

**正式结果版本语义：**

```text
candidate（领域外）
→ admitted / current
→ review-required or stale  [依赖变化]
→ superseded by newer admitted version
```

旧版本即使被 superseded，也继续作为历史事实存在；默认不通过覆盖或删除消除过去发生过的正式结果。

**HumanDecision 语义族：** 接受、修改、拒绝、要求补充。是否需要更多状态由后续详细评审决定，但必须与 Security Approval 分开。

**WorkProduct 生命周期至少区分：** 已正式形成、当前有效、需要复核 / stale、存在更新版本但保留历史。Domain invalidation、01 的 Delivery state 和 Consumer acknowledgement 不允许压成一个 `WorkProduct.status`。

### B8 Failure Taxonomy

| 失败 | 检测 Owner | 正式事实 / 立即动作 | 是否可 Retry | 是否需要 Replan / Human |
| --- | --- | --- | --- | --- |
| expected DomainVersion 冲突 | 02 | 不覆盖写；返回 version conflict | 原请求不可盲重试 | 调用方重新读取后 Replan 或人工 |
| EvidenceCandidate 来源不稳定 | 02 + 03 refs | 不准入正式 Evidence / WorkProduct | 03 可修复派生处理 | 证据无法恢复时人工 |
| 证据不足 | 02 eligibility | 不创建正式 Finding | 单纯重复同输入无意义 | 补证据 / Replan / Abstain |
| Authorization 已失效 | 08 决定，02 执行 | fail closed / pause | 重新授权后才可继续 | 可能人工 |
| 缺必要 HumanDecision | 02 | 保持 proposal / review-required | N/A | Human required |
| 同一幂等 key 不同输入 | 02 | reject conflict | No | 调用方修正 |
| Domain transaction 失败 | 02 Store | DomainVersion 不推进 | 同输入可安全 Retry | 否，除非重复失败 |
| Domain commit 成功、Checkpoint 失败 | 04 检测 + 02 Receipt | 使用 Receipt 修复 Runtime | 不重复 Domain commit | Recovery |
| Checkpoint completed、Receipt 缺失 | 04 / 02 query | 不承认 Formal Admission | 不能以 checkpoint 重放提交 | Review / causation check |
| 新证据影响范围不确定 | 02 dependency | 扩大 review-required 范围 | N/A | bounded reevaluation 或 Human |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

- **Retry（重试）**：仅用于领域事务在提交前失败、且输入、前置版本、授权和准入条件仍成立的情况；同一幂等身份不得产生第二个正式结果。
- **Replan（重规划）**：DomainVersion 冲突、依赖结构改变、证据条件变化使原计划不再正确时，由 04 读取最新领域快照后决定新 PlanVersion；02 不自行规划任务。
- **Reconcile（对账）**：外部现实副作用由 06 负责。本模块只消费已经确认的 EffectReceipt / ReconciliationReceipt，不自行猜外部结果。
- **Recovery（恢复）**：正式准入恢复锚点是 DomainVersion + matching AdmissionReceipt + 必要 WorkProductCitationBinding，而不是 Runtime Checkpoint。
- **Idempotency（幂等）**：同一 idempotency identity + 同一规范化输入返回既有合法结果；同 identity 不同输入必须冲突失败。

### B10 Security / Approval / Audit

02 在正式读取 / 准入边界消费 08 的 AuthorizationDecision、Security Epoch 和必要 Approval reference，但不拥有授权政策。

HumanDecision 是业务事实；ApprovalDecision 是高风险动作是否允许执行的安全事实。两者可以引用同一 human principal，但不能共用状态语义。

Effective Lifecycle Policy（有效生命周期政策）由 08 拥有。本模块负责执行自己 Store 中的 retention、deletion、legal hold 和必要 purge / retention obligation，并保存执行事实；执行结果不能反向改变政策。

关键领域变更需要可审计，但普通 Telemetry 不能替代要求耐久化的 Audit Fact / AuditPersistenceReceipt。Secret 不进入普通 Domain payload。

### B11 Persistence / Transaction Boundaries

PostgreSQL 是第一阶段 Canonical Domain State 的默认耐久边界。至少需要保存正式对象版本、依赖、HumanDecision、WorkProductCitationBinding 和 AdmissionReceipt；具体表结构和 Migration 尚未冻结。

关键事务边界：

```text
expected DomainVersion check
+ canonical domain mutation
+ matching AdmissionReceipt
+ admission-critical citation binding / dependency facts when required
= one Domain transactional durability boundary
```

不在该事务中等待 LangGraph Checkpointer、远端 Consumer acknowledgement 或其他远端服务提交，因此默认不引入跨 Store 2PC。

Knowledge index、Runtime checkpoint、Telemetry、Delivery state 都可以在各自边界稍后恢复，但不得被解释成已经替代 Domain commit。

### B12 Observability / Evaluation

Telemetry 需要关联 Matter、DocumentVersion、DomainVersion、Claim / Evidence / Finding / WorkProduct refs、AdmissionReceipt identity、human review outcome 和 invalidation event，但默认不导出敏感正文。

评测至少覆盖：

- provenance completeness / citation binding correctness；
- unsupported formal admission rate；
- Human review acceptance / modification / rejection；
- stale / review-required propagation correctness；
- bounded reevaluation correctness；
- admission idempotency / version conflict；
- Domain commit vs Runtime checkpoint fault recovery。

这些测量证明模块行为，不等于整个产品 production ready。

### B13 Current / Target / Gap / Evidence

**Current**：[`implementation-wave-001.md`](../../evidence/implementation-wave-001.md) 证明有限 Domain mutation、CAS、幂等、事务失败保护和 Citation Provenance Guard；真实 PostgreSQL race、完整正式准入链仍未证明。

**Target**：完整七对象最小领域内核、Formal Admission + AdmissionReceipt、正式 Evidence、历史引用绑定、版本化 WorkProduct、HumanDecision、依赖失效和受控局部重评。

**Gap**：真实 PostgreSQL integration / concurrency、Admission causation fault injection、HumanDecision E2E、WorkProduct version lifecycle、新证据 bounded re-evaluation、historical citation replacement test、lifecycle enforcement 和跨运行 invalidation。

**Evidence required before Current upgrade**：代码 / Migration、真实 PostgreSQL 集成、单元 / 集成测试、故障注入、E2E、审计 / Trace 关联与评测结果。文档完整度不是实现证据。

### B14 Code / Database / Migration Constraints

后续实现必须先冻结对象 identity、version、dependency、admission、HumanDecision、historical citation 和 invalidation 语义，再讨论 ORM、table、index 和 Migration。

不得因为现有数据库字段、模型抽取结果或某个 Provider 返回结构存在，就把 Proposal 自动升级为 Canonical Object。Migration 必须保留历史版本和已发布成果的依据，不能通过 destructive rewrite 抹掉旧 WorkProductVersion 的来源。

本 Design Baseline 不授权新增 God Domain Service，不要求独立 Domain 微服务，不授权 Event Sourcing、跨 Store 2PC 或完整数据库重构。实现授权需要独立任务和验收标准。

#### B14.1 Detail Freeze Candidate：正式准入输入与回执字段组

下面冻结的是 **Target 语义字段组**，不是最终 ORM class、表名或 API JSON。字段名允许在实现评审时调整，但语义、唯一性和绑定关系不得在 Codex 实现阶段自行改变。

**AdmissionCommand candidate** 至少包含：

| 字段组 | 必需语义 |
| --- | --- |
| Scope | `tenant_id`、`matter_id`、`scope_ref` |
| Admission identity | `admission_id`、`idempotency_key`、`canonical_input_hash` |
| Concurrency | `expected_domain_version` |
| Causation | `proposal_ref`；Runtime 驱动时带 `run_id`、`plan_version`、`step_run_id` |
| Mutation | `mutation_type`、规范化 canonical payload / refs |
| Dependencies | `DocumentVersion`、既有 `Evidence / Claim / Finding / WorkProduct` version refs |
| Human authority | 需要人工业务判断时带 `human_decision_refs` |
| Security | `authorization_decision_ref`、`security_epoch_ref`、`principal_ref` |
| Provenance | 必要 `KnowledgeGeneration / CitationLineage / CapabilityVersion` refs，仅作来源，不升级为 Domain identity |

**AdmissionReceipt candidate** 至少包含：

```text
admission_id
idempotency_key
canonical_input_hash
tenant_id / matter_id
expected_domain_version
prior_domain_version
resulting_domain_version
admitted_object_version_refs
human_decision_refs when required
citation_binding_refs when required
run_id / plan_version / step_run_id when runtime-driven
proposal_ref
authorization_decision_ref / security_epoch_ref
committed_at
```

Receipt 不保存模型隐藏推理、Secret 或大段原始材料。正式成果正文、证据、引用和 HumanDecision 各自进入对应领域事实；Receipt 只证明“哪组输入以什么因果导致了哪次提交”。

逻辑幂等 namespace 至少按 `(tenant, matter, idempotency_key)` 隔离。同 key + 同 `canonical_input_hash` 重放返回既有合法结果；同 key + 不同 hash 必须冲突。当前 Wave-001 已有相近的 mutation 语义，但完整 AdmissionReceipt 仍是 Target，不得把当前 mutation record 直接宣称为最终 Receipt。

#### B14.2 Detail Freeze Candidate：七对象的 Identity / Version 规则

为避免“表里有一行就是业务身份”，第一阶段按以下语义实现：

- `Matter`：稳定 `matter_id` 是聚合根身份；每次正式变更推进该 Matter 的 `DomainVersion`。
- `DocumentVersion`：版本本身不可变，必须能绑定 source artifact identity、source representation hash / content hash 和业务可解释来源元数据；修订材料创建新 DocumentVersion，而不是覆盖旧版本。
- `Claim / Evidence / Finding / WorkProduct`：拥有稳定 logical identity，并以 immutable version record 表达历史；更新产生新 object version，不原地改写已经被 WorkProduct / Receipt 引用的旧版本。
- `HumanDecision`：默认是不可变业务决定记录；如果专业人员改变决定，创建新的决定事实并通过后续 Admission 改变当前业务结果，不回写旧决定。
- `DomainVersion`：对 `(tenant, matter)` 单调推进，只表达正式领域提交顺序，不代表 Runtime Step、Tool Effect 或 Publication 顺序。

第一阶段不要求每个对象独立维护一套全局序列。只要 logical identity、object version 与 Matter-level DomainVersion 能稳定关联，就足以支持历史和因果；不要为了“版本化完整”提前引入 Event Sourcing。

#### B14.3 Detail Freeze Candidate：依赖、引用与失效字段组

正式依赖至少需要表达：

```text
source_object_version_ref
→ dependent_object_version_ref
dependency_type
created_by_admission_id
created_at
```

`dependency_type` 只表达业务上确实影响有效性的关系，例如 Evidence supports / contradicts Claim、Finding depends on Evidence / Claim、WorkProduct includes / relies on Finding。检索相似度、模型 attention、向量邻居不自动成为正式依赖。

`WorkProductCitationBinding` 至少绑定：

```text
work_product_version_ref
evidence_ref when applicable
document_version_ref
stable_source_location
source_artifact_ref / source_representation_hash
excerpt_hash or evidence_hash when required
optional citation_lineage_ref
binding_identity
```

Stable location 可以按 PDF page/span、结构化 section/row/cell 等格式化表示；具体 locator schema 在文档格式详细设计中确定，但禁止只保存 Chunk ID / Vector ID / Graph Node ID。

失效事实至少绑定 `affected_object_version_ref + cause_object_version_ref + cause_type + invalidation_identity + created_at`。同一 cause 对同一版本必须幂等。01 的通知重试不能新增第二个 Domain invalidation fact。

#### B14.4 Detail Freeze Candidate：状态转换 Guard

本模块不把所有对象压成一个状态 enum，但正式版本至少遵守以下 Guard：

```text
proposal / candidate（领域外）
  --[版本匹配 + 来源有效 + 安全有效 + 人审满足 + 幂等合法]-->
admitted/current

admitted/current
  --[新的正式依赖变化且影响成立]-->
review-required 或 stale

review-required
  --[新的 HumanDecision / re-evaluation + 新 Admission]-->
新的 admitted version 或确认仍有效的新的 revalidation fact

admitted/current 或 stale
  --[新的 admitted version 成为当前版本]-->
superseded（历史仍保留）
```

禁止通过直接修改 `status='CURRENT'` 清除曾经发生的失效。若人工复核认为旧结论仍成立，也要保存新的决定 / revalidation 因果，而不是抹掉过去的 invalidation。

Formal Admission Guard 至少同时检查：

1. `expected_domain_version == current_domain_version`；
2. `canonical_input_hash` 与该 idempotency identity 已有记录一致；
3. 所有 admission-critical DocumentVersion / object version refs 仍存在且未被不允许的生命周期政策排除；
4. 需要正式来源的 Evidence / WorkProduct 已拥有可验证稳定引用；
5. 需要 HumanDecision 的规则已满足；
6. 当前受保护操作仍消费有效的 AuthorizationDecision / SecurityEpoch；
7. late proposal 的 causation 仍适用于当前业务版本。

任一 Guard 失败都不能靠“SQL 再试一次”转成成功。

#### B14.5 Detail Freeze Candidate：PostgreSQL 并发与事务候选

第一实现候选采用 **Matter-level serialized admission**：同一 `(tenant, matter)` 的正式 Admission 在短事务内串行化，不同 Matter 仍可并行。当前 `SqlAlchemyCanonicalDomainStore` 在 PostgreSQL 方言下已经使用 aggregate head `SELECT ... FOR UPDATE`，但真实 PostgreSQL race 尚未验证；本节只是把这一思路提升为 Target candidate，而不是把现有实现升级成 Production Evidence。

候选事务顺序：

```text
BEGIN
→ establish tenant / security execution context
→ read idempotency record by admission namespace
→ same key + same hash: return existing receipt
→ same key + different hash: reject
→ lock / compare Matter aggregate head
→ verify expected DomainVersion
→ validate admission-critical dependency refs
→ insert new immutable object versions / dependencies / citation bindings
→ advance Matter aggregate head
→ insert matching AdmissionReceipt
COMMIT
```

事务中禁止等待模型、远端 Tool、人工输入、LangGraph interrupt/resume 或外部 Consumer ACK。所有高延迟工作在进入 Domain transaction 前完成；提交窗口只做确定性校验和持久化。

PostgreSQL deadlock / serialization abort 属于数据库事务失败，只有在重新读取当前 DomainVersion、授权和依赖仍满足后才能重试。业务版本冲突则不是数据库 transient error，返回 `VERSION_CONFLICT` 类语义给调用方重新判断。

如果未来证明“同一 Matter 高频并发正式写”成为真实瓶颈，再评估更细粒度锁、optimistic concurrency 或分区；在没有 Load Evidence 前不为理论吞吐放弃简单、可证明的单聚合写顺序。

#### B14.6 Detail Freeze Candidate：Crash Window 与恢复矩阵

| Crash Window | Durable truth | 恢复动作 | 禁止动作 |
| --- | --- | --- | --- |
| 事务提交前进程退出 | 无 matching Receipt / DomainVersion 不推进 | 同 idempotency identity 重新校验后 Retry | 猜测“可能写了一半”并推进 Runtime |
| COMMIT 成功但响应丢失 | DomainVersion + matching Receipt 已存在 | 重放查询 Receipt，返回 ALREADY_APPLIED / committed result | 产生第二个版本 |
| Domain commit 成功、Checkpoint 失败 | 02 Receipt 是准入真相 | 04 读取 matching Receipt 修复 Step / Run control | 回滚领域或再次 Admission |
| Checkpoint 显示 completed、Receipt 缺失 | Formal Admission 未被证明 | 04 取消 formal-complete 推断并进入 causation check / review | 用更高 DomainVersion 冒充本 Step 结果 |
| Invalidation commit 成功、通知失败 | 02 invalidation truth 已成立 | 01 重试 Delivery；Pull validity 返回 stale | 因 Consumer 离线恢复为 current |
| proposal 计算完成后新 Evidence 先提交 | current DomainVersion / dependencies 已变化 | Admission Guard 拒绝旧 expected version；04 Replan / Human | 自动把旧 proposal 合并进新版本 |

#### B14.7 Detail Freeze Candidate：Schema Evolution / Migration 规则

具体表名仍由 Codex 任务设计，但 Migration 必须遵守以下约束：

1. 历史 `DocumentVersion / WorkProductVersion / HumanDecision / AdmissionReceipt / CitationBinding` 不做 destructive rewrite；旧版本必须继续可解释。
2. 新增 admission-critical 字段采用“新增 → backfill / verify → 约束收紧”的阶段式迁移；不能先加不可满足的强约束再临时伪造默认值。
3. 新的唯一性 / foreign-key / validation 约束上线前先检查历史冲突；发现冲突必须形成数据修复或显式 blocked migration，不静默丢数据。
4. `canonical_input_hash` 的规范化算法需要版本标识；未来算法变化时旧 Receipt 继续按原 hash algorithm/version 解释，不能重算后覆盖。
5. Citation locator / source representation schema 升级必须提供向后读取；不能因为新解析器上线就使旧 WorkProductCitationBinding 不可解析。
6. DomainVersion 不重新编号；Matter 合并、拆分或 tenant 迁移如果未来出现，必须单独 ADR / Migration 设计，不能在普通 schema cleanup 中处理。
7. 大表索引、约束和 backfill 的在线策略必须在实现任务里给出锁影响、回滚方案和实际数据库验证；本文不宣称零停机迁移已经成立。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

02 只有在以下最小矩阵通过后，才有资格从 `detail_design: candidate-v1` 进入 Module Detail Freeze Review：

| 场景 | 必须证明 |
| --- | --- |
| same idempotency key + same hash 重放 | 只返回同一 committed result，不新增版本 |
| same key + different hash | fail closed，不覆盖历史 |
| 两个 Admission 同时基于 D0 | 最多一个提交到 D1；另一个明确 VERSION_CONFLICT 或等价结果 |
| DB error / process crash before commit | DomainVersion 与 Receipt 均不推进 |
| response lost after commit | 重试能够通过 Receipt 恢复，不产生 D2 |
| Domain commit 后 Checkpoint 失败 | Runtime 从 matching Receipt 修复 |
| 新 Evidence 在旧 proposal Admission 前提交 | 旧 proposal 被 freshness / version Guard 拒绝或进入人工复核 |
| 缺失 required HumanDecision | 不创建正式 Finding / WorkProduct |
| SecurityEpoch 已变化 | 新 Admission 不使用旧 allow |
| Citation binding wrong-document / wrong-span | 正式成果准入失败 |
| WorkProduct stale 时 Consumer offline | Domain stale 不回滚；01 可独立重试通知 |
| 索引 / chunk 重建 | 历史 WorkProductCitationBinding 仍指向原 DocumentVersion / stable location |

Freeze Review 还需要真实 PostgreSQL integration、Migration apply / rollback 或等价安全验证、并发测试、故障注入和 Current Evidence 更新。只补完本节字段表不构成 implementation available。

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

02 唯一能够证明正式准入成功的锚点，是**匹配当前因果身份的 DomainVersion + AdmissionReceipt**，并满足本次准入要求的引用绑定和依赖事实。以下都不是正式准入证明：Runtime Checkpoint、RunOutcome、Model success、Capability success、Knowledge Retrieval、HTTP 2xx、Queue ACK、Telemetry span 或“发现了更高 DomainVersion”。

`WorkProductCitationBinding` 证明正式成果当时采用的历史来源；`WorkProductInvalidationFact` 证明某个正式版本已经失效 / 需复核。01 的 Delivery / Ack、09 的 Trace 都不能改变这两个领域事实。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

正式 Admission 至少可追到：

```text
Matter / expected prior DomainVersion
+ DocumentVersion / admitted Evidence dependencies
+ run_id / PlanVersion / StepRun when runtime-driven
+ proposal / admission identity
+ domain idempotency identity
+ current AuthorizationDecision / SecurityEpoch refs
→ resulting DomainVersion + AdmissionReceipt
```

对 CapabilityVersion、Model / Provider、KnowledgeGeneration 等非领域版本只保存必要 provenance ref，不把它们升级成 Domain identity。准入时必须检查与业务正确性相关的来源版本仍然有效；不能把旧 Readiness、旧授权或旧 proposal 静默用于新的 DomainVersion。

领域幂等身份只去重同一规范化领域变更，不与 Step、Tool Effect、Delivery、Model Attempt 等幂等 namespace 共用。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

Run / request cancellation 不撤销已经提交的 Domain transaction。已经正式存在的历史版本继续存在，是否 current / stale / superseded 由领域生命周期决定。

旧 PlanVersion、旧 Capability / Model invocation 或晚到并行分支产生的 Proposal，在进入 Admission 前必须重新校验 causation、DocumentVersion、expected prior DomainVersion、当前授权和必要 evidence / human-decision 条件；任何一个关键绑定过期，都不能因“计算已经完成”而直接准入。

新 Evidence / DocumentVersion 只在经过领域接纳以后触发依赖失效。03 的 stale KnowledgeGeneration、09 的质量告警或一次新的检索排序变化，本身不能直接把 WorkProduct 改成 stale；它们可以触发复核请求或新的候选输入。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

02 恢复正式业务事实时先读自己的 durable store，再帮助其他模块修复投影：

```text
Domain objects / versions
→ matching AdmissionReceipt / historical citation / dependency facts
→ current 08 lifecycle / authorization policy when继续受保护操作
→ 04 修复 Runtime Control State
→ 01 修复 publication / delivery projection
→ 09 补诊断视图
```

必须至少覆盖：Domain commit 后 checkpoint 失败；checkpoint completed 但 receipt 缺失；同 admission key 不同规范化输入；新证据在旧 Plan 并行分支运行期间到达；取消 Run 后 Admission 已经提交；旧 proposal 晚到；WorkProduct 已 stale 但旧 Delivery Ack 晚到；历史索引重建后 WorkProductCitationBinding 仍能回到原始 DocumentVersion。
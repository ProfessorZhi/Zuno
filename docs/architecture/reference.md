# Overall Architecture Engineering Reference

status: canonical-architecture-engineering-reference
owner: Cross-cutting Architecture Owner
human_source: docs/architecture/README.md
module_router: docs/modules/reference.md
decision_source: docs/decisions/
evidence_source: docs/evidence/

## Part B — Engineering / Agent Reference（工程 / Agent 参考）

Part B 是总体架构的机器可消费索引。它压缩 Part A 已经解释过的设计，不重新定义模块内部字段、最终 enum、数据库表或 Provider API。局部细节仍以 [`docs/modules/`](../modules/README.md) 和 ADR 为准。

### B1. Scope / Global Invariants

1. Target Architecture 固定为 9 个逻辑责任域；逻辑责任域不等于网络服务。
2. `Research Artifact != Capability != Provider != Qualified Provider != Formal Business Fact`。
3. `KnowledgeGeneration lifecycle != task-level ReadinessDecision`。
4. `EvidenceCandidate != Evidence`。
5. `CitationLineage != WorkProductCitationBinding`。
6. Runtime Checkpoint != Domain Commit != Tool Effect != Publication truth。
7. Formal Admission 只有在 Domain mutation 与 matching `AdmissionReceipt` 成立后才构成正式法律业务完成证明。
8. Action Proposal != `PreparedAction` != ToolAttempt != `EffectReceipt`；Outcome Unknown 不得降级成普通 Failed。
9. `Retry != Replan != Reconcile`。
10. AuthorizationDecision、ApprovalDecision、HumanDecision 由不同 Owner 产生，语义不能互换。
11. 新的受保护动作必须消费当前有效安全事实；旧授权不成为长期任务的永久票据。
12. Telemetry / Trace / Eval 解释和评测系统，不升级成 Domain、Knowledge、Security 或 Effect Authority。
13. 跨 Domain Store、Runtime Checkpointer、Tool Effect Store、Security Store 默认不做全局 2PC；恢复依赖 Owner Fact + causation refs。
14. Cancellation 停止未来工作，不全局回滚已经成立的 Domain fact 或已经发生/可能发生的现实 Effect。
15. 简单法律问答保持受控 RAG baseline；Native Runtime、GraphRAG、Reflection、Memory、Specialist、独立服务都必须由测量证明收益。
16. Target 文档不证明 Current 实现；实现资格只来自 Code / Migration / Test / Trace / Eval / runtime Evidence。

### B2. Authority / Ownership Matrix

| Owner | Authoritative facts | Consumes but does not own | Canonical module |
|---|---|---|---|
| 01 Application & Integration | 产品入口、Matter/Scope 组合、Publication / Delivery 语义 | Domain、Knowledge、Security、RunOutcome、Effect refs | [`application`](../modules/application/README.md) |
| 02 Legal Domain & Work Product | Matter / DocumentVersion canonical identity、Claim、Evidence、Finding、HumanDecision、WorkProduct、DomainVersion、AdmissionReceipt、WorkProductCitationBinding | Candidate、Readiness、Runtime、Effect、Security refs | [`domain`](../modules/domain/README.md) |
| 03 Knowledge & Evidence | KnowledgeGeneration、Serving eligibility、ReadinessDecision、EvidenceCandidate、RetrievalResult、CitationLineage | DocumentVersion canonical ref、Security decision | [`knowledge`](../modules/knowledge/README.md) |
| 04 Agent Runtime & Control | AgentRun、PlanVersion、StepRun、Checkpoint、Ready/Join/Barrier、Retry/Replan/Reconcile control、RunOutcome | Domain Receipt、Knowledge、Capability、Model、Effect、Security facts | [`runtime`](../modules/runtime/README.md) |
| 05 Capability & Skill | Capability semantics/version、Provider conformance、task qualification | Model/Knowledge inputs、Domain admission result | [`capability`](../modules/capability/README.md) |
| 06 Tool Runtime & Effects | ToolVersion effect semantics、PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt、RetrySafety | Authorization/Approval、Plan、Domain refs | [`effects`](../modules/effects/README.md) |
| 07 Model Gateway | Model role resolution、Provider eligibility、ModelAttempt、usage/cost truth | Capability quality、Security egress decision、Domain result | [`model-gateway`](../modules/model-gateway/README.md) |
| 08 Security & Governance | SecurityEpoch / PolicyVersion、AuthorizationDecision、ApprovalDecision、ModelEgressDecision、AuditRequirement、lifecycle policy decision | Domain HumanDecision、Effect truth、Store enforcement facts | [`security`](../modules/security/README.md) |
| 09 Observability & Evaluation | Telemetry、Eval run、experiment result、quality evidence | 所有业务 Authority refs | [`evaluation`](../modules/evaluation/README.md) |
| Platform / Infrastructure | DB/Object Store/Queue/Checkpointer/CAS/Lease/Fencing/Clock/Backup/Network/Secret Delivery 的物理原语事实 | 所有业务语义 | shared infrastructure |

### B3. Cross-boundary Contract Map

| Boundary | Producer / Authority | Consumer | Minimum durable causation |
|---|---|---|---|
| DocumentVersion -> KnowledgeGeneration | 02 -> 03 | 03/04/01 | stable DocumentVersion refs + generation identity + processing spec |
| KnowledgeGeneration -> ReadinessDecision | 03 | 01/04；必要时 02 admission eligibility | generation + task Scope + requirements + current security refs + coverage/missing requirements |
| Retrieval -> EvidenceCandidate / CitationLineage | 03 | 04/05/02/01 direct QA | source DocumentVersion + stable location + generation/retrieval identity |
| Research -> Capability | 05 | 04/01 | CapabilityVersion + semantics + Provider qualification refs |
| Capability/Runtime -> Model | 04/05 -> 07 | 04/05 | Model Role + policy/budget constraints -> ModelAttempt + usage refs |
| Candidate -> Formal Admission | 04/05/03 -> 02 | 04/01 | candidate/source/version/security/human causation -> DomainVersion + AdmissionReceipt |
| Runtime -> External Effect | 04/05 -> 06 | 04/02/01 | PreparedAction + action hash + ToolVersion + security/approval/audit refs |
| External send -> Effect truth | 06 | 04/02/01 | ToolAttempt + external correlation -> EffectReceipt or ReconciliationReceipt |
| Protected action -> Security decision | caller -> 08 | 02/03/04/05/06/07/01 | principal/scope/resource/action/purpose + SecurityEpoch -> typed decision ref |
| Runtime -> Publication / Delivery | 04/02/06/08 -> 01 | user/host/external boundary | RunOutcome + Domain/Effect/Security refs；01 保持自己的交付事实 |

### B4. Canonical Execution Profiles

**Profile A — Simple controlled QA**

```text
01 request/scope
→ 08 current authorization
→ 02 DocumentVersion refs
→ 03 ReadinessDecision
→ 03 retrieval + CitationLineage
→ optional 07 model call
→ answer policy / publication gate
→ 01 response
```

不要求 Native Runtime、Formal Admission 或外部 Effect；业务约束允许时继续保持这条短路径。

**Profile B — Complex legal analysis**

```text
01 Task
→ 04 AgentRun + immutable PlanVersion
→ 03 Readiness / EvidenceCandidate
→ 05 Capability + optional 07 Model Gateway
→ 04 Step Acceptance / Join / Replan when needed
→ 02 Formal Admission
→ matching AdmissionReceipt
→ 04 RunOutcome
→ 01 publication / delivery
```

**Profile C — Real-world side effect**

```text
04/05 Action Proposal
→ 06 PreparedAction
→ 08 current Authorization / Approval / Audit gates
→ durable ToolAttempt before dangerous send
→ external operation
→ confirmed: EffectReceipt
→ outcome unknown: Reconcile -> ReconciliationReceipt
→ 04 resumes from typed effect result
→ 02/01 consume effect ref when business flow requires
```

### B5. State / Lifecycle Families

本节只冻结跨模块状态语义，不冻结最终 enum 名称。

```text
KnowledgeGeneration:
DECLARED -> PROCESSING -> STAGED/BUILT -> SERVING -> STALE/SUPERSEDED -> REBUILDING

Domain:
Candidate -> Formal Admission -> DomainVersion + AdmissionReceipt
Current valid -> REVIEW_REQUIRED / STALE / SUPERSEDED when new causation invalidates assumptions

Runtime:
AgentRun: CREATED -> PLANNING -> RUNNING -> WAITING_* -> COMPLETED / FAILED / CANCELLED / ABSTAINED
PlanVersion: DRAFT -> ACTIVATED -> SUPERSEDED; ACTIVATED immutable
StepRun: PENDING -> READY -> DISPATCHED -> RUNNING -> ACCEPTED / RETRYABLE_FAILURE / REPLAN_REQUIRED / WAITING / TERMINAL_FAILURE

Effect:
PreparedAction -> ToolAttempt
UNCONFIRMED -> CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / OUTCOME_UNKNOWN
OUTCOME_UNKNOWN -> RECONCILING -> CONFIRMED_EXECUTED / CONFIRMED_NOT_EXECUTED / MANUAL_RECONCILIATION

Security:
PolicyVersion/SecurityEpoch evolves independently
Authorization/Approval may ALLOW/GRANT and later EXPIRE/REVOKE/SUPERSEDE for future protected actions
```

### B6. Completion Proof / Non-proof

| Question | Completion proof | Explicit non-proof |
|---|---|---|
| 当前任务知识是否够用 | matching `ReadinessDecision` bound to generation + Scope + requirements + current security refs | upload complete、OCR item success、index write、generation build alone |
| 正式法律结果是否成立 | Domain commit + matching `AdmissionReceipt` + applicable DomainVersion | Runtime Step completed、Model 2xx、Candidate existence、Checkpoint |
| Runtime 是否可以推进 | valid active PlanVersion + Step/Join/Barrier state + required external Owner facts | Domain success alone、old Checkpoint alone |
| 外部动作是否发生 | `EffectReceipt` or conclusive `ReconciliationReceipt` | HTTP timeout、transport success、ToolAttempt terminal state alone |
| 新受保护动作是否允许 | current matching Authorization/Approval/Audit/egress/secret facts as required | old ALLOW、historical approval with changed action hash、system-internal caller identity |
| 正式引用历史是否可解释 | `WorkProductCitationBinding` + stable DocumentVersion/location refs | current retriever rank、chunk/vector/graph node id alone |
| 复杂机制是否值得保留 | reproducible Eval / Evidence against simpler baseline | framework feature existence、single demo、research popularity |

### B7. Failure Taxonomy / Recovery Order

恢复顺序统一为：

```text
1. Identify the fact class that is in doubt
2. Query the authoritative Owner fact
3. Compare causation / version / freshness
4. Re-consume current Security eligibility before new protected work
5. Repair Runtime / Cache / Projection / Delivery state
6. Retry, Replan or Reconcile only after the fact is classified
```

关键故障窗口：

| Failure window | Wrong recovery | Required recovery anchor |
|---|---|---|
| Domain committed, Runtime Checkpoint not written | replay Formal Admission from Checkpoint | query matching AdmissionReceipt / DomainVersion; repair Runtime projection |
| Checkpoint says step completed, AdmissionReceipt absent | declare business success | deny formal completion; query 02 causation and re-enter valid admission path |
| external request timed out after possible send | map timeout to Failed and Blind Retry | PreparedAction + ToolAttempt + external correlation -> Reconcile |
| new DocumentVersion arrives during long run | continue old Plan silently | 03 recomputes knowledge eligibility; 02 invalidates/reviews affected facts; 04 Replan if assumptions changed |
| SecurityEpoch changes during wait/retry/resume | reuse old authorization | obtain new current decision before protected use |
| old Plan branch returns late | merge because computation succeeded | compare PlanVersion/input refs; reject stale or require reevaluation |
| cancellation after Domain/Effect success | roll back everything | stop future work; preserve existing Owner facts; compensate only through explicit new business action |

### B8. Retry / Replan / Reconcile / Idempotency

**Retry** requires Plan assumptions、inputs、Capability/Tool semantics、security、budget and external-world assumptions to remain valid. Attempt identity remains stable enough to prevent accidental double accounting or duplicate logical work.

**Replan** creates a new immutable PlanVersion when evidence、requirements、Capability/Tool semantics、budget or other planning assumptions changed. It does not mutate an already activated plan in place.

**Reconcile** belongs to uncertain external Effect truth. 06 resolves Outcome Unknown through remote query、business key、idempotency status or human reconciliation. 04 waits; it does not infer the answer from transport state.

Idempotency namespace is boundary-specific. Domain admission identity、Runtime attempt identity、Tool action identity、Model attempt identity、Publication/Delivery identity are not one global key.

### B9. Version / Freshness / Causation Bindings

| Fact | Must bind to | Freshness owner |
|---|---|---|
| KnowledgeGeneration | DocumentVersion set + processing spec + generation identity | 03 |
| ReadinessDecision | generation + task Scope + requirements + security/policy refs | 03 |
| EvidenceCandidate | DocumentVersion + stable location + generation/retrieval refs | 03 |
| WorkProductCitationBinding | formal WorkProduct/Domain version + stable DocumentVersion/location | 02 |
| PlanVersion | AgentRun + planning causation; immutable after activation | 04 |
| Capability output | CapabilityVersion + Provider/qualification refs + input versions | 05 |
| ModelAttempt | role/resolved Provider/model version + policy/budget refs | 07 |
| PreparedAction | ToolVersion + canonical action content/hash + target + run/plan/step causation | 06 |
| ApprovalDecision | action identity/hash + ToolVersion + policy epoch + expiry | 08 |
| AdmissionReceipt | normalized business input + expected DomainVersion + causation refs | 02 |
| Eval result | dataset/scenario/config/version refs required for reproducibility | 09 |

新的版本不会静默改写旧历史。Owner 判断旧事实是否仍 current、需要 review、stale、superseded 或重新执行。

### B10. Security / Approval / Human Authority

```text
AuthorizationDecision: 当前 principal 是否可执行某类受保护动作
ApprovalDecision: 某个具体高风险动作是否已获得治理批准
HumanDecision: 专业人员是否接受、修改或拒绝法律业务结论
```

三者不能互相替代。

- protected read / retrieval -> current 08 decision before use；
- model egress -> current ModelEgressDecision / provider eligibility；
- Secret -> ref/lease only，Secret Material 不进入普通 Prompt/Checkpoint/Trace/Receipt；
- high-risk Tool -> Authorization + action-bound Approval + required durable Audit before dangerous send；
- Formal Admission -> consume current applicable security facts，专业 HumanDecision 仍由 02 Domain 保存；
- resume / retry / replan / reconcile -> 新的受保护访问重新授权。

### B11. Persistence / Transaction Boundaries

| Store / boundary | Owns durable truth | Must not be promoted into |
|---|---|---|
| 02 Domain store | Canonical Domain + AdmissionReceipt + formal citation binding | Runtime checkpoint |
| 03 Knowledge store/index metadata | generation / manifest / serving / readiness / lineage facts | formal Domain fact |
| 04 Checkpointer/runtime store | control progress / plan / step / interrupt state | Domain or Effect truth |
| 06 Effect store | PreparedAction / Attempt / Effect / Reconciliation facts | Security policy or Domain admission |
| 08 security/audit boundary | policy/decision/approval/audit facts | HumanDecision or Effect truth |
| 09 telemetry/eval store | observations and experiment evidence | any business Authority |
| Platform primitives | physical durability / lease / fencing / queue / clock facts | business completion proof |

跨 Store 默认不依赖 2PC。需要跨边界一致性时，用稳定 identity、causation ref、receipt、owner query、recovery/reconciliation 收敛。

### B12. Build / Buy / Extend / Delete Conditions

**Prefer Buy / Reuse**：PostgreSQL、Object Store、Queue、Secret Manager、OpenTelemetry、Checkpointer、模型 SDK、身份系统、成熟 Policy Engine / Provider primitives。

**Zuno Owns**：Formal Admission、Domain authority、task-level Readiness semantics、Capability professional semantics、Runtime control semantics、Effect confirmation/reconciliation semantics、Security business policy mapping、Eval criteria for Zuno task quality。

**Extend only when measured constraints appear**：独立 Worker/Service、Native Runtime、GraphRAG、Reflection、Memory、Specialist、多模型路由、更强模型。

**Delete / simplify when**：复杂机制不能相对 baseline 提供可重复收益；独立服务没有独立扩缩容/隔离/故障半径/网络/生命周期需求；Generic Host 已经覆盖所需通用能力；简单 QA 不需要长期状态、Formal Admission 或现实 Effect。

### B13. Current / Target / Evidence / Unknown

**Target**：本文 A/B 描述的跨模块 Authority、边界、恢复和复杂度治理语义。

**Current**：只能由 [`docs/evidence/`](../evidence/README.md) 中与当前代码 SHA、Migration、Test、Trace、Eval、runtime evidence 对应的材料证明。总体架构文档本身不升级任何能力为 Current。

**Evidence**：模块文档 B13 指向当前可用的具体证据；需要判断某个 Target 是否已经落地时，优先读取对应 Module B13，再读取 evidence 原文和代码。

**Unknown / Measurement Needed**：Production Readiness、完整 fault-injection coverage、真实法院/业务环境收益、复杂机制 A/B baseline、性能与成本边界、部署拆分必要性，都不能从 Target Design 推导。

`implementation_authorization: NO` 仍然成立；文档完整不等于允许按未冻结 Detail 直接实现。

### B14. Machine Navigation / Source Precedence

机器或 Agent 回答架构问题时按以下优先级读取：

```text
Current Code / Test / Runtime Evidence
> canonical docs/architecture + docs/modules
> accepted ADR
> historical Red/Blue archive
> docs/research and external research
> speculation
```

定位规则：

- “为什么存在 / 为什么这样分” -> Part A；
- “谁拥有这个事实” -> Part B B2 + 对应 Module B2/B4；
- “跨边界传什么” -> Part B B3 + Module B5；
- “怎样证明完成” -> Part B B6 + Module C1；
- “崩溃后先查什么” -> Part B B7/B11 + Module B8/B9/C4；
- “版本或晚到结果怎样处理” -> Part B B9 + Module C2/C3；
- “权限/Approval/HumanDecision 谁说了算” -> Part B B10 + 08/02；
- “是否已经实现” -> Module B13 + [`docs/evidence/`](../evidence/README.md)；
- “字段/API/Migration” -> Module B14 / ADR / implementation artifacts，不从 Overall Architecture 猜测。

Part A 与 Part B 维护同一套事实。A 可以重写叙事顺序，B 可以提高检索密度；任何修改都不得让两个 Part 在 Owner、Authority、Completion Proof、Recovery、Security 或 Current/Target 上出现两套答案。
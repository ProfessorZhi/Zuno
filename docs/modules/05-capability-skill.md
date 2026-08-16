# 05 Capability & Skill（专业能力与技能）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2 -->

## Part A — Human Narrative

### 这个模块解决的不是“怎么多接几个 Tool”，而是研究成果怎样变成可靠的专业能力

Zuno 的法律能力可能来自论文算法、规则系统、Prompt、大模型、微调模型、知识图谱、外部 API、MCP 或若干步骤的组合。真正需要稳定的不是某个 Python 函数名字，也不是某个模型供应商，而是：**这项能力到底承诺完成什么专业任务、接受什么输入、返回什么结果、依赖什么证据、在哪些条件下可信、失败时怎样表达，以及换 Provider 以后语义有没有改变。**

如果这层边界不存在，研究代码很容易直接散落在 Agent Prompt、Tool wrapper 和业务服务里。Planner 只看到一堆名字，却不知道执行器真正能做什么；测试也很难区分“模型挂了”“能力退化”“检索证据不足”“计划写错了”到底是哪一种问题。

专业能力与技能模块就是研究成果进入工程系统的稳定出口。

### 用“冲突检测能力”理解 Research-to-Capability（研究成果工程化）

假设团队有一个研究算法，可以从原告陈述、被告陈述和证据中识别时间或金额冲突。Notebook 上的 Demo 能跑，并不等于它已经可以进入产品。

第一步要先定义专业语义：输入需要哪些材料和证据；输出是哪些冲突候选；是否返回来源位置和不确定性；它只识别文本层冲突，还是可以判断法律上的矛盾；缺少关键材料时应该返回 `insufficient evidence` 还是猜一个答案。

第二步才是把具体实现绑定到这份定义。实现可能是规则 + 模型，也可能是外部服务。Provider 必须通过 Conformance（契约一致性验证），证明输入输出、错误类型和边界行为都符合 Capability Contract。

第三步是通过法律任务评测和适用范围判断当前 Eligibility（可用资格）。只有被证明适合某类任务的 Provider，才进入 Runtime 可选集合。

```mermaid
flowchart LR
  R[Research Artifact（研究成果）] --> C[Capability Definition（能力定义）]
  C --> V[Capability Version（能力版本）]
  V --> P[Provider Binding（实现绑定）]
  P --> T[Conformance（契约验证）]
  T --> E[Evaluation（质量评测）]
  E --> Q[Eligibility（可用资格）]
  Q --> X[Runtime / Host 调用]
```

这条链把“论文里有算法”和“产品里可依赖的能力”明确分开。

### Capability（专业能力）、Skill（技能）和 Provider（实现提供方）到底是什么关系

Capability 描述稳定的专业语义，例如事件抽取、事件对齐、冲突检测、事实—法条对应、证据充分性判断、类案检索或法律适用性分析。它回答“这项能力承诺完成什么专业任务”。

Skill 更接近可复用的实现或组合包装。例如，一个“冲突检测 Skill”可能先做实体 / 事件抽取，再调用规则比较，再用模型解释冲突原因。Skill 可以被重构、拆分或替换；如果它没有独立业务生命周期，就不应该因为仓库里有一个 `skills/` 目录而升级成新的 Canonical Domain Object（正式领域对象）。

Provider 是某个 Capability Version 的具体实现来源。一个 Capability 可以同时绑定多个 Provider，用于不同成本、时延、质量或部署条件。

因此：

```text
Capability = 稳定专业语义
Skill      = 可复用实现 / 组合方式
Provider   = 具体实现来源
```

三者不能简单等同。

### 为什么 Capability 的输出只能是 Proposal（候选）

专业能力可以提出：“材料 A 和 B 在付款时间上存在冲突”“这段文字可能支持主张 C”“这些法条可能适用”。它不能直接写入正式 Finding、Evidence 或 WorkProduct。

原因不是不信任算法，而是专业能力只看到自己负责的一部分上下文。正式业务结果还需要材料版本、来源稳定性、当前权限、必要人工决定、并发版本和正式准入语义。

所以 Capability 输出的是 Proposal / Candidate / Observation / Reference（候选、观察、引用），02 法律领域再决定其中哪些最终成为正式业务事实。

### EvidenceCandidate（证据候选）来自知识，Capability 不能重新发明一套证据真相

03 知识与证据负责从已就绪材料中检索 `EvidenceCandidate（证据候选）` 和 `CitationLineage（检索引用链）`。05 可以消费这些候选并进行专业分析，但不能把自己的中间结果重新命名成“正式证据”。

例如，冲突检测能力可以输出：

```text
conflict_candidate
+ supporting EvidenceCandidate refs
+ capability version
+ uncertainty / reason
```

然后由 02 决定是否接纳相关材料为正式 Evidence、是否形成 Finding。

这条边界避免每个专业算法都发明自己的“事实表”。

### Planner 为什么必须知道能力边界，而不是只看到一个函数名

如果 Planner 只知道有一个 `legal_analysis()`，它可能生成一个巨大 Step：“读取所有材料、识别事实、寻找法条、判断争议、生成结论并提交结果”。这种 Step 无法可靠验收，也无法判断失败究竟发生在哪里。

Capability Definition 应向 04 运行控制暴露足够的信息：适用任务、前置条件、输入类型、输出类型、证据要求、是否需要某种 Knowledge Readiness、成本 / 时延级别、是否允许并行、当前资格和已知限制。

Planner 不需要知道 Provider 内部 prompt 或算法，但必须知道：**这项能力现在能不能完成这一步，结果怎样验收。**

### 能力版本为什么不能静默覆盖

假设冲突检测 V1 只识别“文字层明显矛盾”，V2 增加“时间区间推理”，V3 又改成“只返回高置信冲突”。如果 Provider 直接覆盖旧版本，上层计划和历史结果就无法知道当时到底使用了什么语义。

因此 Capability Version 需要不可变身份；Provider 升级后重新做与变化风险相匹配的 Conformance / Eval。旧运行继续引用原版本；新运行根据当前 eligibility 选择新版本。

版本弃用也不能等同删除历史。已经形成正式结果时，02 只需要保存足够的 capability / provider reference 解释当时来源，不要求旧 Provider 永久在线。

### Provider 临时故障和 Capability 语义变化为什么不是同一种失败

如果 Provider 503、限流或短时不可用，而 Capability Contract、输入和证据要求都没有变化，可以在预算和安全允许时 Retry（重试）或切换到已经验证等价的 Provider。

如果输入 schema、输出含义、适用范围、证据要求或副作用声明发生变化，原计划依赖的能力假设就失效。这时应该通知 04 Replan（重规划），而不是猜新参数或静默换成语义不同的 Provider。

所以能力层必须区分：

```text
provider execution failure
!=
capability semantic drift
```

### 它和 Model Gateway（模型网关）为什么不能合并

07 回答“怎样安全、统一地调用一个模型角色”；05 回答“怎样完成一个专业任务”。

一个事件抽取 Capability 可以由大模型实现，也可以由微调模型、规则或传统算法实现。如果把 Capability identity 直接绑定某个模型名，替换模型就等于改变业务 Contract。

因此 Capability 可以调用 Model Gateway，但 Model Gateway 不定义法律专业语义。

### 它和 Tool Runtime（工具运行）为什么不能合并

专业能力回答“怎样分析、应该提出什么候选”；06 回答“一个现实动作如何安全发生”。

Capability 的成功可能只是“得到可信冲突候选”；Tool Effect 的成功意味着“现实世界的动作已经被确认”。前者通常允许重新计算，后者可能需要幂等和对账。

如果某个 Capability 内部确实需要有现实副作用的 Tool，必须通过 06 执行并消费 EffectReceipt，不能因为调用发生在 Skill 内部就绕开 Tool Runtime。

### 研究成果什么时候值得进入一级 Capability Registry（能力注册表）

不是每个 helper、Prompt、规则函数都值得注册。

至少当某项能力需要被多个 Agent / Step 复用、需要独立版本、需要 Provider 替换、需要独立质量评测、需要 Planner 感知、需要弃用 / 回滚或需要明确安全前置条件时，才值得形成稳定 Capability identity。

如果只是一个局部实现细节，就继续留在 Skill / code 内部。这样可以防止 Registry 变成“所有函数的目录”。

### 当前、目标与缺口

Current 代码中已经存在能力、工具、模型 Provider、Skill 和跨模块 Contract 相关实现，但当前证据还不能证明完整 Capability Registry、Provider Conformance、Eligibility、版本兼容和 Planner Awareness 已经成为生产 Current。

Target 是 Research Artifact → Versioned Capability → Provider Binding → Conformance / Eval → Eligibility → Runtime / Host 调用的完整工程链。

Gap 包括 Capability Registry、法律任务级 Conformance / Eval、Provider 等价性、版本升级 / 回滚、Planner capability awareness、研究成果到 Capability 的 E2E、能力级成本 / 时延测量，以及哪些“Skill”真的需要独立生命周期的证据。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. Capability Contract 与 Provider 实现分离；Provider 更换不得静默改变专业语义。
2. Capability 输出只允许 Proposal / Candidate / Observation / Reference，不直接提交 Canonical Domain State。
3. EvidenceCandidate / CitationLineage 由 03 提供；正式 Evidence / Finding / WorkProduct 由 02 准入。
4. Planner 必须基于当前 Capability boundary 生成可验收 Step，不能假设万能执行器。
5. Capability Version 有稳定身份；激活使用中的语义不能被 Provider 原地覆盖。
6. Provider Conformance != task quality；通过 schema 验证不等于法律质量达标。
7. 临时 Provider failure 可 Retry；semantic / schema / applicability drift 触发 capability re-resolution / Replan。
8. Capability 不直接执行未经 06 / 08 控制的现实副作用。
9. Skill 默认是实现 / 组合层概念，不自动升级为 Canonical Domain Object。
10. Capability 是否值得长期保留必须接受 09 的质量 / 成本测量。

### B2 Responsibility / Ownership

**Owns**：Capability identity / version、semantic purpose、input / output contract、preconditions、evidence requirement、uncertainty / failure semantics、Skill / provider binding、provider conformance、capability eligibility、deprecation / compatibility policy、专业 Proposal / Candidate / Observation / Reference。

**Does not own**：02 的 Domain Admission；03 的 Knowledge Readiness / CitationLineage authority；04 的 Plan；06 的 Tool Effect truth；07 的 model routing；08 的 Authorization / Approval；01 的 publication。

### B3 Upstream / Downstream

上游：

- 03 提供 DocumentVersion / EvidenceCandidate / CitationLineage / Readiness refs；
- 04 提供 Step requirement、预算和调用上下文；
- 08 提供数据 Scope / provider / tool 安全决定；
- 07 提供模型调用结果；
- 06 提供必要的只读或受控 Effect result。

下游：

- 向 04 返回 capability metadata、eligibility 和 typed professional output；
- 向 02 返回可以进入正式准入判断的 Proposal / evidence refs；
- 向 09 输出 conformance / quality / cost signals。

### B4 Authoritative Facts / Core Objects

核心对象族：CapabilityDefinition、CapabilityVersion、CapabilityRequirement、ProviderBinding / ProviderVersion、ConformanceResult、EligibilityDecision / EligibilityReference、SkillCompositionRef、InvocationIdentity、TypedProposal / Candidate / Observation / Reference、Deprecation / Compatibility metadata。

具体 Registry 表结构、API 与存储尚未冻结。

### B5 Cross-boundary Contracts

#### Capability Definition / Version

至少表达：identity、version、semantic purpose、supported task class、input / output schema、preconditions、required evidence / readiness、uncertainty contract、failure taxonomy、side-effect declaration、cost / latency class、security requirements、compatibility policy。

#### Provider Binding / Conformance

绑定 capability version 与具体 implementation / provider version；Conformance 至少验证 schema、required semantics、deterministic guards、known failure behavior 和 version compatibility。

#### Capability Eligibility

表达某个 capability/provider 组合在指定 scope / task class / environment 下当前是否可使用。Eligibility 不等于一次 invocation 已成功。

#### Capability Output

只输出 Proposal / Candidate / Observation / Reference，并携带 capability version、provider ref、input / evidence refs、uncertainty / failure signal 和必要 provenance。

### B6 Normal Flow

```text
Research Artifact
→ define Capability semantic contract
→ create immutable CapabilityVersion
→ bind Provider / Skill implementation
→ run Conformance tests
→ run task / legal Evaluation
→ issue Eligibility for supported scope
→ Planner resolves current Capability
→ Runtime invokes provider
→ typed Proposal / Candidate / Observation / Reference
→ downstream Step Acceptance / Domain Admission when applicable
→ collect quality / cost evidence
→ deprecate / upgrade only through new version
```

### B7 State / Lifecycle

最终 enum 未冻结，但至少需要表达：

```text
Capability Definition:
DRAFT → REGISTERED → VERSIONED

Provider Binding:
BOUND → CONFORMANCE_PENDING → PASSED / FAILED

Eligibility:
NOT_EVALUATED → ELIGIBLE / RESTRICTED / INELIGIBLE
ELIGIBLE → DEPRECATED / SUSPENDED when evidence or policy changes

Invocation Result:
SUCCEEDED
/ INSUFFICIENT_EVIDENCE
/ UNSUPPORTED_INPUT
/ QUALITY_NOT_ESTABLISHED
/ PROVIDER_FAILURE
```

CapabilityVersion 语义不可原地修改；新语义创建新 version。

### B8 Failure Taxonomy

| 失败 | 责任判断 | 默认处理 | 是否影响 Plan |
| --- | --- | --- | --- |
| Provider timeout / 503 | 05 provider adapter / 07 if model-backed | Retry / equivalent provider | 通常否 |
| schema mismatch | 05 | Reject provider result | 可能，需要 re-resolution |
| semantic drift | 05 | Suspend eligibility | 是，Replan |
| unsupported input | 05 | Return unsupported | 是，Planner 需调整 |
| insufficient evidence | 05 + 03 refs | Return typed insufficiency | 可能扩大 retrieval / review |
| quality regression | 05 + 09 | Restrict / revoke eligibility | 后续运行需 Replan / provider change |
| provider unavailable | 05 | approved equivalent fallback / stop | 视等价性 |
| planner request 超出边界 | 04 + 05 | reject oversized / invalid requirement | 是 |
| internal model failure | 07 + 05 | model retry / provider fallback | 通常先局部处理 |
| internal Tool effect unknown | 06 | Reconcile | 05 不自行重试 Tool |
| security scope denied | 08 | deny / review | 是或终止 |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

**Retry**：Provider 临时失败且 capability semantic contract、输入、证据、当前资格和安全条件均未变化。

**Replan**：schema / semantics / preconditions / capability availability / task assumptions 改变，导致原计划不能继续。

**Reconcile**：05 本身不拥有现实 Effect Reconcile；内部副作用工具必须经过 06。

**Recovery**：按 capability version、provider version、invocation identity、input / evidence refs 和 conformance / eligibility 恢复调用上下文，不能只凭“同名 Skill”重放。

确定性或昂贵调用可以使用 stable invocation identity 做缓存 / duplicate suppression，但缓存键必须绑定 capability version、relevant input / evidence versions 和 security scope，避免把旧结果静默用于新材料。

### B10 Security / Approval / Audit

Capability definition 可以声明所需数据类别、模型外发、工具权限和其他前置条件，但 Authorization truth 由 08 决定。

Capability Provider 不长期持有 Secret；通过 07 / 06 / Platform 的受控引用使用。

如果 Skill 需要高风险 Tool Effect，必须经过 08 Authorization / Approval / Audit gates 和 06 Effect control；不能因为它被包在 Capability 内部而绕过。

专业输出进入普通 Trace 时遵守数据分类和脱敏；正式业务依据仍由 02 / 03 的 durable facts 保护。

### B11 Persistence / Transaction Boundaries

是否建立 Capability Registry PostgreSQL 表，取决于是否需要跨进程统一 version / eligibility / deprecation。第一原则先冻结 identity、version、contract、conformance 和 eligibility 语义。

大型中间产物、模型 chain-of-thought 或临时 provider payload 不默认进入领域数据库。正式 Domain state 只由 02 Admission 创建。

Capability Registry 与 Runtime Checkpoint、Domain Store、Model usage store 不做默认 2PC；通过 version / invocation / evidence refs 关联。

### B12 Observability / Evaluation

至少观测：capability identity / version、provider ref、input / output schema hash、precondition outcome、evidence sufficiency、latency、cost、failure class、quality signal、downstream Step Acceptance、Human Review / Domain Admission outcome（仅引用）。

评测必须区分：

```text
Provider 调用成功
!=
Capability contract 满足
!=
专业结果有用
!=
正式业务结果被接受
```

支持同一 Capability 的 Provider A/B、版本回归、成本 / 时延 / 质量 Pareto 比较和 Research-to-Capability 验证。

### B13 Current / Target / Gap / Evidence

**Current**：仓库已有 capability / skill / tool / model provider 和跨模块 Contract 基础，但完整 module-level Capability Registry / Conformance / Eligibility 尚未由专项证据证明。

**Target**：稳定专业语义 + 版本化 Provider + Conformance + Evaluation + Eligibility + Planner Awareness。

**Gap**：Registry、version compatibility、provider conformance suites、法律 Eval、Planner capability resolution、deprecation / rollback、Research Artifact → Capability E2E、provider equivalence 和 measurement evidence。

**状态**：design available；implementation available 与 quality proven 需另行证据。

### B14 Code / Database / Migration Constraints

- 不为每个研究算法创建独立微服务。
- 不让 Provider SDK / 模型 SDK 直接暴露给所有上层；通过 Capability / Gateway typed ports。
- 不把厂商模型名或某个 Skill 文件路径作为 Capability identity。
- 不因为存在 `skills/` 目录就建立新的业务实体和状态机。
- 先冻结 capability identity / version / contract / eligibility，再设计 registry schema 与 Migration。
- Provider fallback 必须是经过验证的等价路径，禁止静默语义降级。
- 物理拆分继续受 ADR-0012 Evidence Gate 约束。

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

05 的完成证明分为三个层级：Provider 调用完成、Capability Contract 满足、当前 Eligibility 允许该结果被本次 Step 使用。即使三者都成立，也只证明得到了合格的专业 Proposal / Candidate / Observation / Reference，不证明 04 Step 已最终验收，更不证明 02 已正式准入。

Conformance PASS 只能证明 Provider 符合 Capability Contract；09 Eval 达标才提供质量证据；02 AdmissionReceipt 才证明候选成为正式业务事实。任何一个层级都不能互相冒充。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

一次 Capability invocation 至少绑定：CapabilityVersion、ProviderVersion / SkillCompositionRef、InvocationIdentity、input identity、相关 DocumentVersion / EvidenceCandidate / KnowledgeGeneration refs、当前 eligibility、SecurityEpoch，以及调用它的 run / PlanVersion / StepRun（如存在）。

缓存 / 重放必须把这些会影响语义的版本纳入 key。Provider 同名、函数名相同或 input 文本相同，都不足以证明旧结果适用于新材料或新安全范围。

Capability invocation identity 不与 ModelCallAttempt、Tool Effect、StepRun、Admission 的幂等 identity 共用；内部模型 / 工具调用通过 refs 关联。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

Capability invocation 被取消，只阻止后续可取消计算；已经发生的内部 Model Usage 由 07 结算，已经进入 06 的外部 Effect 不因 05 cancel 而自动撤销。

晚到的 Provider 结果在交给 04 / 02 前必须重新验证：调用所属 PlanVersion 是否仍可接受、CapabilityVersion / Provider binding 是否仍有效、输入 / Evidence refs 是否仍是当前 Step 预期、当前安全条件是否允许继续使用。语义漂移后晚到的“成功响应”默认不能作为当前合格结果。

Capability 被 SUSPENDED / DEPRECATED 不删除历史 provenance；它影响未来 eligibility 和当前尚未接受的调用结果，不重写已经正式形成的 Domain 历史。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

恢复先按稳定能力语义找回上下文：

```text
CapabilityVersion / ProviderBinding
→ Conformance / current Eligibility
→ input / evidence / security refs
→ existing Invocation result if safe to reuse
→ 07 model / 06 effect child receipts when applicable
→ 04 Step Acceptance / Replan
→ 02 Admission only after revalidation
```

至少验证：Provider 503 后等价 fallback；fallback 非等价时拒绝；Capability schema / semantic drift 触发 Replan；旧 EvidenceCandidate 被新 DocumentVersion 取代后结果晚到；SecurityEpoch 改变；内部 Tool outcome unknown 时 05 不重试；相同 invocation key 在 CapabilityVersion 或输入版本变化时拒绝复用；quality regression 使 eligibility suspend 但不改写历史 Domain fact。
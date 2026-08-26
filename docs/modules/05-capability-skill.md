# 05 Capability & Skill（专业能力与技能）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块解决的是“专业能力怎样成为产品契约”，不是“把所有算法包装成 Tool”

Zuno 会使用事件抽取、事件对齐、争议识别、证据分析、类案检索、法条推荐和其他法律算法。这些能力可能来自课题组研究、规则代码、传统模型、新 LLM 或外部服务。直接让 Runtime 依赖某个脚本或 Provider，短期最省事，长期却会把业务语义和实现版本绑死。

05 的职责是把“能完成什么专业任务”稳定下来，再允许不同 Provider 去实现。Runtime 调用的是专业能力语义，Eval 判断当前实现是否合格，Domain 决定输出能否成为正式事实。

### 最简单的 provider.call() 为什么会慢慢失去边界

一个研究模型刚接入时，最简单方案是写一个 Python wrapper：传入文本，返回 JSON。只要 Demo 跑通，看起来已经是 Skill。

随着模型升级、输入材料类型变化、多个 Provider 共存，问题就出现了：不同实现对“事件”定义是否一致；失败返回空数组是“没有事件”还是“模型故障”；新版字段是否兼容旧调用方；某个 Provider 技术可调用是否意味着质量足够。没有稳定能力语义，Runtime 只能不断理解每个实现的特殊情况。

### Capability = 稳定专业语义

Capability 的核心不是类名，而是一份专业承诺：输入是什么业务含义，输出表达什么，哪些情况算成功、拒绝、不可判定或需要 Review，以及结果可以被哪些后续流程消费。

实现可以变化，但同一 CapabilityVersion 下的语义必须稳定。真正改变专业含义时创建新版本，而不是在旧接口后面偷偷改变“同一个字段是什么意思”。

### Provider 为什么必须和 Capability 分开

一个 Capability 可以由课题组旧模型、现代 LLM、规则系统或外部服务实现。把 Provider identity 从能力语义中分离，Runtime 才能根据当前资格选择实现，而不把业务代码绑定到某个框架或模型家族。

Provider 变化可以是部署、性能或模型升级；Capability 版本变化则表示专业契约变化。两类版本分开以后，回放和 Eval 才能解释质量变化来自哪里。

### Provider Conformance != task quality

Conformance 回答“这个 Provider 是否遵守 Capability 契约”：字段、错误语义、版本、必要来源和行为边界是否一致。它是接入门槛，不是专业质量证明。

所以必须保持 `Provider Conformance != task quality`。一个 Provider 可以完全符合 schema，却在复杂案件上准确率很差；反过来，一个研究脚本可能某项 benchmark 很强，却没有稳定错误语义，不适合直接进入生产调用路径。

### provider execution failure 和 capability semantic drift 为什么是两类故障

Provider 超时、依赖 503、GPU 不可用，属于实现执行失败；如果同一个版本突然改变事件边界、字段含义或输出约束，则属于能力语义漂移，不能通过普通 Retry 掩盖。

```text
provider execution failure
!=
capability semantic drift
```

前者可以 fallback 或 retry，后者应该阻断资格、触发版本升级或重新验证。把两类失败都叫“调用失败”，会让系统在语义已经不可信时继续切换重试。

### Eligibility 为什么不是“服务健康”

Provider 健康只说明技术上能调用。某次任务能否使用，还取决于 CapabilityVersion、Conformance、质量基线、数据限制、当前材料类型和任务风险。

Eligibility 是这些条件的任务级组合。它防止“API 是绿的”被误解成“这个实现适合当前法律任务”。Runtime 可以消费资格，却不应该自己重新实现专业评测逻辑。

### Invocation 为什么需要绑定版本和输入身份

专业输出需要能解释“由哪个 CapabilityVersion、哪个 ProviderVersion、基于哪些材料和参数产生”。否则模型升级后出现质量变化，系统无法重放或归因。

Invocation identity 还帮助处理重复执行和 cache。它不应该和 Runtime Step id 合并，因为同一个 Step 可能多次尝试不同 Provider，而同一 Capability 也可能被不同 Run 调用。

### Fallback 为什么必须保护专业语义

Provider A 不可用时切到 B 看起来只是可用性优化，但 B 必须满足同一 Capability 的最低语义和质量要求。否则“fallback 成功”可能只是换成了一个会返回 JSON、却不适合当前任务的实现。

因此 fallback 候选来自当前资格集合，而不是所有技术兼容 Provider。没有合格实现时，正确结果可能是让 Runtime Replan、进入 Review 或明确 abstain，而不是无限降低标准。

### Cache 为什么不能把专业输出变成永久事实

某些确定性或高重复能力可以缓存，但 cache identity 需要绑定输入版本、Capability / Provider 版本、配置和必要安全 Scope。材料或专业语义变化后，旧结果不能静默复用。

更重要的是，缓存命中只表示“可以复用一次专业计算结果”，仍然不等于 Domain 正式接受。Formal Admission 的业务资格继续由 02 判断。

### Capability、Model 和 Tool 为什么不能混成一个抽象

LLM 是一种计算 Provider，Tool 可能产生现实副作用，Capability 则是专业业务语义。三者有交集，但失败和权威不同。

一个专业能力可以内部调用模型，也可以产生一个 Action Proposal；模型调用事实由 07 记录，现实执行由 06 控制，05 只保证专业输出满足自己的契约。把三者统一成万能 Tool，会让预算、安全、Effect 和专业质量边界互相污染。

### 研究成果怎样进入 Capability，而不是直接进入架构

研究论文或课题组算法首先证明某个局部问题可能可解，不自动证明它已经是稳定产品能力。进入 Zuno 前，需要明确语义、版本、来源、Provider 接口、Conformance 和 Eval。

这样事件抽取、事件对齐、冲突识别等研究资产可以保留学术价值，又不会因为“是我们自己的模型”就跳过产品化门槛。新的 LLM Provider 也可以在同一专业语义下与旧模型公平比较。

### 为什么强模型不能成为所有 Capability 的默认答案

LLM 可以快速覆盖很多专业任务，但成本、延迟、可复现性和结构化稳定性并不总优于专门模型、规则或检索算法。能力层应该允许不同实现按任务价值竞争。

复杂开放判断可能值得更强推理模型，稳定抽取可能更适合小模型或规则。选择依据应该是 Eval 和业务约束，而不是“最新模型能力更强”的抽象印象。

### Provider 退出为什么必须是正常路径

如果某个外部服务停服、研究模型不再维护或质量下降，系统应该能撤销它的 Eligibility，而不要求重写 Runtime 和 Domain。Provider exit 是可替换架构真正成立的测试。

同样，加入新 Provider 也不应该自动获得资格。先证明 Conformance，再证明相应任务质量，最后进入可用集合。

### 什么时候 05 应该更简单

如果系统只有少量稳定内部函数，没有多个实现、版本演进和独立质量门槛，那么 Capability 层可以非常薄，甚至只是清晰的 Python Protocol 和测试集合。

只有研究资产多、Provider 经常变化、需要独立评测和跨 Runtime 复用时，才值得增加 registry、eligibility 和更完整生命周期。能力管理不能为了“平台化”而自我膨胀。

### Capability Version 什么时候应该变，Provider Version 什么时候应该变

如果只是模型权重、部署地址或运行优化改变，而专业输入输出语义保持兼容，通常属于 ProviderVersion 演进；如果“事件”的业务定义、字段含义、错误语义或可接受输出发生变化，则需要新的 CapabilityVersion。

这个区分让上层能够判断兼容性。Runtime 可以在同一 CapabilityVersion 下替换合格 Provider，而不重新理解业务；能力语义真正变化时，上层则明确选择是否迁移，而不是被隐藏升级影响。

版本规则不能只靠 semver 名字，关键是变化是否改变消费者必须理解的专业承诺。

### Deterministic Capability 和 Generative Capability 为什么可以共享能力边界

某些专业任务最适合规则或传统模型，另一些需要 LLM 开放推理。Capability 层不应该预设“专业能力就是 Agent”或“就是模型”。

只要输入输出和失败语义相同，deterministic provider、ML provider 和 LLM provider 可以竞争同一能力资格。这样团队可以用更便宜、更稳定的实现替换昂贵模型，也可以在规则覆盖不足时引入 LLM，而不改变 Runtime 的业务调用方式。

这也是研究工程化的重要价值：比较的是解决同一专业问题的方案，而不是比较框架品牌。

### Qualification 为什么要和 Release 生命周期绑定

一个 Provider 在 Dataset V3 上通过，不代表未来模型、Prompt、ProcessingSpec 或数据分布变化后永久合格。Qualification 需要绑定可复现配置和时间/版本范围，并在重大变化后重新评测。

同时不能把 Eval 服务临时不可用解释成 Provider 自动失败或自动通过。已有 qualification 是否仍在有效期、当前安全政策是否允许、任务是否落在已覆盖 profile，都需要分别判断。

这使 Eligibility 成为“当前任务现在能不能用”的组合，而不是 registry 中一个永远绿色的开关。

### Build / Buy 对专业能力意味着什么

课题组拥有研究成果，不等于所有能力都应该自研。成熟 OCR、通用 embedding、基础分类和模型 Provider 可以优先采购或复用；真正体现法律专业资产的语义、Eval 数据和特定算法可以自有。

判断标准是差异是否长期重要、是否有可维护 Evidence，以及替代成本。如果外部能力已经稳定满足专业契约，自研实现没有明显质量、隐私、成本或可控性收益，就不应为了“技术含量”重复建设。

Capability abstraction 的价值之一正是允许 Buy 和 Build 共存，而不是把所有 Provider 都吸收到一套自研框架里。

### 05 为什么不应该变成中央 Prompt / Plugin 市场

能力注册表很容易膨胀成所有 Prompt、Tool、MCP server 和插件元数据的统一市场。这样做看似平台化，却会把专业契约、模型调用、现实副作用和安全边界混在一个配置中心。

05 只拥有专业 Capability identity、版本、Provider conformance 与资格。Prompt 的具体业务语义跟随使用场景，Tool effect 由 06，模型 transport 由 07，安全策略由 08。保持这个窄边界，才能让能力层真正稳定。

### Capability 的失败语义为什么要允许“不会做”，而不是强迫每个 Provider 给答案

专业系统容易把 Provider success rate 当成目标，于是实现会倾向于任何输入都返回一个结构完整的结果。但某个 Capability 可能只支持特定材料类型、语言、案件阶段或风险等级；超出已验证范围时，最安全的行为是明确 unsupported / insufficient / review required。

这种“有边界的不会做”必须进入 Capability 语义，否则 Runtime 无法区分“任务本来不适用”和“Provider 临时坏了”。前者可能需要换 Capability、Replan 或人工，后者才适合 retry / fallback。同样，Eval 也应该惩罚在未知范围里自信输出，而不是只奖励覆盖率。

Capability 越能精确声明自己的适用范围，上层越不需要依赖模型自报 confidence 来猜是否可信。专业能力的成熟度不在于永远返回答案，而在于知道自己的资格边界。

### 专业能力的组合为什么不应该产生隐藏的“超级 Capability”

一个复杂法律分析可能组合事件抽取、证据比较、法条检索和综合判断。为了调用方便，把整条链包装成一个巨大 Capability 看起来很省事，但会重新隐藏每一步的版本、失败和质量责任。某个子能力升级后，团队也无法判断最终变化来自哪里。

更合理的是只在业务上确实形成稳定整体语义时才提供组合能力，并继续保留关键子能力的 causation。Runtime 可以编排多个 Capability，05 负责每个专业边界的契约和资格；不要因为“一个接口更简单”就牺牲可替换性和可评测性。组合层如果没有独立专业语义，应留在 Runtime Plan，而不是升级成新的长期能力类型。

### 当前、目标与缺口

Current 已有哪些 Capability、Provider、Conformance test 和真实 Eval，必须回到代码和证据；Target 中列出的研究能力 family 不等于它们全部已经产品化或达到质量门槛。

Target 已明确专业语义与 Provider 解耦、Conformance 与质量分开、fallback 受资格约束，以及 Capability 输出仍是 Proposal。Gap 包括字段级版本策略、真实 Provider 兼容、任务级 Eval、cache/fallback 故障测试和哪些研究资产真正值得长期维护。

## Part B — Engineering / Agent Reference

### B1 Scope / Global Invariants

1. Capability = 稳定专业语义；Provider / Skill 是实现。
2. CapabilityVersion 激活后语义不可原地修改。
3. Provider Conformance != task quality。
4. 输出只产生 Proposal / Candidate / Observation / Reference，不直接提交 Domain。
5. Planner 必须知道 supported task class、preconditions、evidence requirement、规模与 side-effect 边界。
6. EvidenceCandidate / CitationLineage 由 03 提供；正式 Evidence / Finding / WorkProduct 由 02 准入。
7. Provider transient failure 可 Retry；semantic / schema / applicability drift 触发 re-resolution / Replan。
8. Provider fallback 必须经过当前 CapabilityVersion 的等价性 /资格证明。
9. 05 内部模型 / Tool 仍受 07 / 06 / 08 控制。
10. Skill 不自动升级为 Canonical Domain Object。
11. Capability 复杂度和质量接受 09 测量。

### B2 Responsibility / Ownership

**Owns**：CapabilityDefinition / CapabilityVersion、semantic purpose、supported task class、input/output contract、preconditions、evidence requirement、uncertainty / failure semantics、ProviderBinding、ConformanceResult、EligibilityDecision、compatibility / deprecation、InvocationIdentity、typed professional outputs。

**Does not own**：Domain Admission、Knowledge Readiness、Plan、Tool Effect、Model routing / usage、Authorization / Approval、Publication。

### B3 Upstream / Downstream

上游：03 DocumentVersion / EvidenceCandidate / CitationLineage / Readiness refs；04 StepRequirement / budget / causation；08 scope / provider / tool security；07 model result；06 controlled tool result。

下游：04 capability metadata / eligibility / typed output；02 Proposal / evidence refs；09 conformance / quality / cost signals。

### B4 Authoritative Facts / Core Objects

CapabilityDefinition、CapabilityVersion、CapabilityRequirement、ProviderBinding、ProviderVersionRef、ConformanceProfile / Result、EligibilityDecision、SkillCompositionRef、CapabilityInvocation、TypedProposal / Candidate / Observation / Reference、CompatibilityPolicy、DeprecationFact。

### B5 Cross-boundary Contracts

#### CapabilityVersion

至少表达 identity、semantic version、purpose、supported task classes、input/output schema refs、preconditions、evidence requirement、uncertainty contract、failure taxonomy、side-effect declaration、cost / latency class、security requirements、compatibility policy。

#### ProviderBinding / Conformance

绑定 CapabilityVersion 与 ProviderVersion / SkillComposition；Conformance 验证 schema、required semantics、deterministic guards、known failures、side-effect declaration 与兼容范围。

#### EligibilityDecision

说明某 CapabilityVersion + ProviderBinding 在指定 environment / task class / scope / quality profile 下当前是 ELIGIBLE / RESTRICTED / INELIGIBLE / SUSPENDED。它不证明某次 Invocation 已成功。

#### CapabilityOutput

绑定 invocation、capability/provider version、normalized input refs、evidence refs、typed payload ref、uncertainty、failure / insufficiency signal、provenance refs。

### B6 Normal Flow

```text
Research Artifact
→ define Capability Contract
→ create immutable CapabilityVersion
→ bind Provider / Skill composition
→ Conformance suite
→ legal/task Evaluation
→ EligibilityDecision
→ 04 resolves capability for StepRequirement
→ CapabilityInvocation
→ internal 03 / 07 / 06 calls through owned boundaries
→ typed output
→ 04 Step Acceptance
→ optional 02 Formal Admission
→ 09 quality/cost evidence
```

### B7 State / Lifecycle

```text
CapabilityVersion: DRAFT → REGISTERED → ACTIVE → DEPRECATED / RETIRED
ProviderBinding: BOUND → CONFORMANCE_PENDING → CONFORMANT / NON_CONFORMANT
Eligibility: UNKNOWN → ELIGIBLE / RESTRICTED / INELIGIBLE; ELIGIBLE → SUSPENDED / SUPERSEDED
Invocation: CREATED → RUNNING → SUCCEEDED / INSUFFICIENT_EVIDENCE / UNSUPPORTED_INPUT / PROVIDER_FAILURE / SEMANTIC_FAILURE
```

最终 enum 名称可调整，但不同语义不得压成同一个 `FAILED`。

### B8 Failure Taxonomy

| 失败 | Owner | 默认动作 | Runtime 含义 |
| --- | --- | --- | --- |
| Provider timeout / 503 | 05 adapter / 07 if model | bounded Retry / equivalent fallback | Plan 通常仍有效 |
| schema mismatch | 05 | reject result | re-resolution / Retry if safe |
| semantic drift | 05 | suspend eligibility | Replan |
| unsupported input | 05 | typed unsupported | Planner 调整 |
| insufficient evidence | 05 + 03 refs | typed insufficiency | more retrieval / Human / Replan |
| quality regression | 05 + 09 | restrict/suspend | future Replan/provider change |
| planner oversized request | 04 + 05 | reject requirement | split / Replan |
| internal Tool unknown | 06 | Reconcile | 05 不重试 Tool |
| security denied | 08 | deny | Replan / stop |

### B9 Retry / Replan / Reconcile / Recovery / Idempotency

Retry 只适用于 semantic contract、输入、Evidence、Eligibility 和 Security 都未变化的 transient execution failure。Replan 用于 capability availability / semantics / preconditions / evidence assumption 失效。

05 不拥有现实 Effect Reconcile；内部 Tool 交 06。恢复依赖 CapabilityVersion + ProviderBinding + InvocationIdentity + input/evidence refs + Eligibility / child receipts，不凭同名函数重放。

缓存和 duplicate suppression 使用独立 capability-invocation namespace，不能与 StepRun、ModelAttempt、ToolAction、Admission 共用 idempotency key。

### B10 Security / Approval / Audit

CapabilityDefinition 声明 security / egress / tool requirements，08 决定当前授权。Provider 不长期持有 Secret。内部高风险 Tool 必须经过 08 + 06；被 Capability 包装不能形成安全旁路。

### B11 Persistence / Transaction Boundaries

是否落 PostgreSQL Registry 取决于是否需要跨进程一致 version / binding / eligibility；无论物理实现如何，immutable version、binding history、eligibility evidence ref 和 invocation causation 必须可恢复。

Registry 不与 Runtime Checkpoint、Domain Store、Model usage、Tool effect 做 2PC。大模型原始 payload、chain-of-thought 和大型中间对象不默认持久化到 Capability Registry。

### B12 Observability / Evaluation

至少观测 capability/version、provider ref、schema / contract hash、precondition outcome、evidence sufficiency、latency、cost、failure class、quality signal、fallback、downstream Step Acceptance / Human Review / Domain Admission refs。

评测明确区分：

```text
Provider 调用成功
!=
Capability contract 满足
!=
专业结果有用
!=
正式业务结果被接受
```

### B13 Current / Target / Gap / Evidence

**Current**：存在 capability / skill / provider / tool / model 的实现表面和 Contract 基础；完整 Registry / Conformance / Eligibility 与质量证明仍是 Gap，具体以 `docs/evidence/` 和代码测试为准。

**Target**：versioned semantic Capability + Provider Conformance + Evaluation + Eligibility + Planner Awareness。

**Gap**：Registry schema、provider equivalence、compatibility / deprecation、legal Eval、Planner resolution、rollback、Research-to-Capability E2E、真实质量 / 成本测量。

**状态**：detail design candidate available；implementation / quality proven not established。

### B14 Code / Database / Migration Constraints

- 不为每个算法建微服务。
- Provider SDK / 模型 SDK / Tool SDK 不直接暴露给所有上层。
- 厂商模型名、函数名、Skill 路径不作为 Capability identity。
- 不因为存在 `skills/` 目录就创建新领域实体。
- Provider fallback 必须是验证过的等价路径。
- 物理拆分继续受 ADR-0012 Evidence Gate。

#### B14.1 Detail Freeze Candidate：CapabilityVersion 字段组

至少包含：`capability_id`、`capability_version`、`semantic_contract_version`、`purpose`、`supported_task_classes`、`input_schema_ref/hash`、`output_schema_ref/hash`、`precondition_spec_ref`、`evidence_requirement_ref`、`uncertainty_contract_ref`、`failure_taxonomy_version`、`side_effect_declaration`、`cost_class`、`latency_class`、`security_requirement_ref`、`compatibility_policy_ref`、`created_at`。

CapabilityVersion 语义不可修改；文字说明修订如果影响 Contract，需要新 version，而不是只改数据库备注。

#### B14.2 Detail Freeze Candidate：ProviderBinding / Conformance 字段组

ProviderBinding 至少包含 `binding_id`、`capability_version_ref`、`provider_type`、`provider_version_ref`、`skill_composition_ref`、`config_version_ref`、`conformance_profile_version`、`bound_at`、`supersedes_binding_ref?`。

ConformanceResult 至少包含 `result_id`、`binding_id`、`suite_version`、`schema_result`、`semantic_guard_results`、`failure_behavior_results`、`side_effect_result`、`tested_at`、`artifact / evidence refs`、`outcome`。

#### B14.3 Detail Freeze Candidate：Eligibility 字段组与 Guard

EligibilityDecision 至少绑定 `eligibility_id`、CapabilityVersion、Binding、environment/profile、task class / scope、required quality floor、ConformanceResult ref、Eval evidence ref、Security / provider qualification refs、outcome、reason、issued_at、expires / review_after。

Guard：Conformance 未通过不能 ELIGIBLE；需要质量门的 Capability 没有匹配 Eval evidence 只能 UNKNOWN / RESTRICTED；ProviderVersion 或 semantic config 变化后旧 Eligibility 不自动继承。

#### B14.4 Detail Freeze Candidate：Invocation / Output 字段组

`CapabilityInvocation` 至少包含 `invocation_id`、CapabilityVersion、Binding、normalized input identity/hash、DocumentVersion / KnowledgeGeneration / EvidenceCandidate refs、run / PlanVersion / StepRun、SecurityEpoch ref、deadline / budget class、started_at / completed_at、result_class。

输出至少绑定 `output_ref`、invocation、typed schema version、payload hash/ref、evidence / provenance refs、uncertainty、failure / insufficiency reason、child ModelCall / ToolEffect refs。输出不可直接携带“domain_admitted=true”。

#### B14.5 Detail Freeze Candidate：Planner Resolution / Fallback

04 提交 CapabilityRequirement：task class、required semantics、input scale、evidence requirement、quality floor、deadline / cost class、side-effect allowance。05 返回一个当前 eligible CapabilityVersion + Binding 或 typed `NO_ELIGIBLE_PROVIDER`。

Fallback 只有在新 Binding 对同一 CapabilityVersion、同一 task requirement 和当前安全约束仍满足时成立；否则返回 requirement unsatisfied 让 04 Replan。05 不把“更弱 Provider”包装成成功。

#### B14.6 Detail Freeze Candidate：Cache / Late Result / Cancellation

Cache key 至少绑定 CapabilityVersion、Binding / ProviderVersion、normalized input hash、relevant DocumentVersion / KnowledgeGeneration / Evidence refs、semantic config version、Security scope freshness class。安全决定本身不一定作为永久 key，但继续使用时重新验收当前授权。

Cancel 只停止后续可取消计算；内部 Model Usage / Tool Effect 按 07 / 06 结算。Late result 交给 04 / 02 前重新检查 PlanVersion、input versions、Capability / Binding Eligibility、Evidence freshness 和当前 Security。

#### B14.7 Detail Freeze Candidate：Schema Evolution / Version Migration

1. Capability semantic change 创建新 CapabilityVersion；禁止原地改 Contract。
2. Provider Binding change 创建新 binding / config version；旧 Invocation 保留历史 refs。
3. Schema 新增 required 字段采用兼容读取 + staged rollout；旧历史输出不能伪造默认专业语义。
4. Eligibility evidence schema 升级保留旧 decision 可解释性。
5. Registry unique constraints 上线前扫描重复 identity / version。
6. Skill / Provider 路径迁移不得改变 Capability identity。
7. 下线旧 Provider 前处理仍在运行 / paused 的 invocation，并保留可读历史。

#### B14.8 Detail Freeze Candidate：Failure Injection / Freeze Evidence

| 场景 | 必须证明 |
| --- | --- |
| Provider transient 503 | 同 semantic contract 下 bounded Retry |
| Provider schema mismatch | result 不进入 Step Acceptance |
| semantic drift | Eligibility suspend + 04 Replan |
| fallback Provider 非等价 | 拒绝静默降级 |
| insufficient evidence | typed insufficiency，不模型补齐 |
| old DocumentVersion result late | freshness check 拒绝当前使用 |
| SecurityEpoch changed | 新受保护使用重新门禁 |
| internal Tool outcome unknown | 05 不自行 Retry Tool |
| same invocation key but CapabilityVersion/input changed | 不复用旧结果 |
| quality regression | future Eligibility 限制，不改写历史 Domain |
| CapabilityVersion upgrade while paused Run exists | old run 可解释，resume 明确兼容或 Replan |
| provider rollback | 不修改历史 Invocation provenance |

## Part C — Cross-Module Consistency（跨模块一致性）

### C1 Completion Proof / Non-proof（完成证明与非证明）

05 的完成证明分层：Provider 调用完成、Capability Contract 满足、当前 Eligibility 允许本次使用。即使三者成立，也只得到合格 Proposal / Candidate / Observation / Reference；04 Step Acceptance 和 02 Admission 仍是独立事实。

### C2 Causation / Version / Freshness Bindings（因果、版本与新鲜度绑定）

Invocation 至少绑定 CapabilityVersion、ProviderBinding、input identity、DocumentVersion / EvidenceCandidate / KnowledgeGeneration refs、Eligibility / SecurityEpoch、run / PlanVersion / StepRun。Capability invocation identity 与 ModelAttempt、ToolAction、StepRun、Admission identity 分开。

### C3 Cancellation / Late Result / Staleness Rules（取消、晚到结果与失效规则）

Cancel 不撤销内部已产生 Model Usage / Tool Effect。晚到结果在 04 / 02 接受前重新校验 Plan、Capability / Provider、输入、Evidence 和 Security。Capability SUSPENDED / DEPRECATED 影响未来资格和未接受晚到结果，不修改历史 Domain fact。

### C4 Recovery Order / Consistency Tests（恢复顺序与一致性验证）

```text
CapabilityVersion / ProviderBinding
→ Conformance / current Eligibility
→ input / evidence / security refs
→ safe existing Invocation result if reusable
→ child 07 model / 06 effect facts
→ 04 Step Acceptance / Replan
→ optional 02 Admission
```

一致性测试至少覆盖 transient failure、非等价 fallback、semantic drift、Evidence freshness、SecurityEpoch change、Tool outcome unknown、versioned cache、quality suspension 和 paused-run compatibility。
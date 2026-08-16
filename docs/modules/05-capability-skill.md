# 05 Capability & Skill（专业能力与技能）

<!-- status: design-baseline-v1; implementation: not-authorized; deepening: cross-module-consistency-v2; detail-design: candidate-v1 -->

## Part A — Human Narrative

### 这个模块保护的是“专业语义”，不是函数名

法律智能系统里，一个函数能被调用并不代表它构成稳定能力。今天叫 `extract_events()`，明天换成另一个模型或规则引擎，如果输入要求、输出含义、证据要求、失败方式和不确定性都改变，上层仍按旧语义使用，就会产生比 API 报错更危险的“静默语义漂移”。

因此 05 的核心是：**Capability = 稳定专业语义**。它定义“这项能力解决什么问题、需要什么输入和证据、输出能被怎样解释、失败时是什么含义”，再允许一个或多个 Provider / Skill 实现这个语义。

### 为什么研究成果不能直接变成生产 Skill

研究代码通常为了验证方法，输入假设、数据格式、容错、版本、权限和异常语义都不完整。把一个 notebook、脚本或 Prompt 文件直接注册成“能力”，Planner 就会开始依赖它，却没有办法知道它在哪些材料、任务和风险条件下可靠。

更稳妥的路径是 Research Artifact → Capability Contract → Versioned Provider → Conformance → Evaluation → Eligibility。研究成果可以很快进入实验，但只有 Contract、测试和质量证据都足够时才成为可被 Runtime 规划依赖的能力。

### 为什么 Capability 和 Provider 必须分开

“事件抽取”是专业语义；某个大模型 Prompt、规则引擎、微调模型或外部服务只是实现方式。Provider 可以替换，但 CapabilityVersion 的语义不能因为实现换了就悄悄变化。

这让 Planner 面对的是稳定边界：它需要“输入一组材料，返回带来源和不确定性的事件候选”，而不是“调用某个厂商模型”。当 Provider 改版时，05 先验证它是否仍满足同一个 Capability Contract。

### Conformance 为什么不是质量证明

Provider Conformance 主要证明结构和最低行为契约成立，例如输入 schema、输出 schema、必填 provenance、错误分类、确定性 guard 和安全边界没有被破坏。

但 **Provider Conformance != task quality**。一个 Provider 可以 100% 返回合法 JSON，却在真实法律材料上经常漏事件、错配主体或错误判断适用性。质量由 09 的 Eval、人工 Reviewer 和真实任务证据证明。

### Planner 为什么必须知道能力边界

如果 Planner 只看到一个“万能分析工具”，很容易生成一个巨大 Step：“阅读全部 300 份材料、抽取事件、判断争议、找法条、写最终意见”。这样的 Step 无法局部验收、无法并行，也无法知道失败应该 Retry 还是 Replan。

05 要向 04 暴露 task class、输入规模边界、所需 Evidence / Readiness、side-effect declaration、成本 / 时延类别和限制，让 Planner 把复杂任务拆成执行器真正能完成和验收的 Step。

### Evidence requirement 为什么属于 Capability Contract

专业能力不是只看文本参数。事实—证据对齐、冲突检测、法条适用性等能力，都可能要求特定 DocumentVersion、EvidenceCandidate、CitationLineage 或 Knowledge Readiness。

所以 Capability Contract 必须说明最低 evidence requirement。输入数据不足时返回 `INSUFFICIENT_EVIDENCE`，而不是让模型“尽量回答”。需要扩大检索范围时由 04 / 03 形成新的任务条件，而不是 05 偷偷读取更多材料。

### 输出为什么只能是 Proposal / Candidate / Observation / Reference

Capability 可以提出 Finding Proposal、Conflict Candidate、ApplicableLaw Candidate 或结构化 Observation，但不能因为专业算法“很确定”就直接写 Canonical Domain State。

02 是正式业务准入边界。05 的输出携带 CapabilityVersion、ProviderVersion、输入与 evidence refs、不确定性和失败信号，供 04 Step Acceptance 和 02 Formal Admission 判断。

### Skill 为什么不是新的业务对象

Skill 更像实现 / 组合方式：一个 Capability 可以由多个 Skills、模型调用、规则函数和检索步骤组成；一个 Skill 也可能服务多个 Capability。把每个 Skill 都升级成正式业务实体会让数据库跟代码目录一起膨胀。

因此 Skill identity 用于实现、部署和 provenance，不自动进入七对象 Canonical Legal Kernel。只有真正拥有长期业务身份和生命周期的概念才进入 02。

### Provider failure 和 semantic drift 为什么不能混在一起

临时 503、超时、限流说明“这次实现没跑起来”，计划可能仍然正确，可以 Retry 或切换经过验证的等价 Provider。

语义漂移则说明实现不再满足原 Capability Contract，例如输出字段含义改变、适用范围缩小、证据 requirement 变化。此时：

```text
provider execution failure
!=
capability semantic drift
```

后者应暂停 Eligibility，通知 04 re-resolve / Replan，而不是简单重试同一个 Step。

### Fallback 为什么必须经过等价性证明

“模型 A 挂了，切模型 B”只有在 Provider B 对当前 CapabilityVersion 的 Conformance、质量下限、安全资格和输入能力都满足时才是 fallback。否则只是换成一个语义不同的实现。

如果替代 Provider 只能完成较弱任务，必须显式改变 task requirement / Plan；不能在 Gateway 或 Capability Adapter 内部静默降级，再把结果包装成原能力成功。

### Capability Eligibility 为什么是动态事实

一个 Provider 曾经通过测试，不代表永远可用。模型版本升级、Prompt 改动、数据政策变化、质量回归、供应商下线或某类输入事故都可能使它从 ELIGIBLE 变成 RESTRICTED / SUSPENDED。

Eligibility 绑定 CapabilityVersion、ProviderVersion、支持的 task / scope、质量证据和必要 Security 条件。历史输出仍保留当时 provenance，未来调用按当前资格选择。

### 为什么 Capability cache 很容易制造旧事实

昂贵专业调用可以缓存，但 cache key 如果只用 input text，就可能把旧 DocumentVersion、旧 KnowledgeGeneration、旧 CapabilityVersion 或旧 Security scope 的结果带进新任务。

缓存必须绑定真正影响专业语义的版本：CapabilityVersion、ProviderVersion、规范化 input refs、Evidence / DocumentVersion / KnowledgeGeneration refs、必要配置与安全范围。结果晚到或缓存命中后，消费者仍要检查当前 Plan 和 Domain freshness。

### 内部模型和内部 Tool 为什么仍然属于别的 Owner

一个 Capability 可以内部调用 07 模型，也可以需要 06 Tool。但“包在 Capability 里”不能让它绕过模型外发、预算、外部 Effect、审批或 Reconciliation。

05 只组合专业语义。模型调用事实仍归 07，现实 Effect 仍归 06，Authorization / Approval 仍归 08。Capability output 通过 refs 关联这些事实。

### Research-to-Capability 为什么需要可回滚版本

研究迭代很快，新的算法未必比旧的稳定。CapabilityVersion 激活后不应该被原地覆盖；升级创建新 version，Provider binding 和 Eligibility 可以逐步切换。

如果评测发现回归，可以停止新版本 Eligibility 并恢复旧的已验证 Provider，而不修改已经由旧版本产生的历史输出和正式 Domain 结果。

### 专业失败为什么必须是 typed failure

`UNSUPPORTED_INPUT`、`INSUFFICIENT_EVIDENCE`、`PROVIDER_FAILURE`、`SCHEMA_MISMATCH`、`SEMANTIC_DRIFT`、`QUALITY_RESTRICTED` 对 Runtime 的含义完全不同。把它们都抛成 Exception，会逼 04 猜 Retry / Replan。

05 应返回稳定 failure class 与必要 reason refs，让 04 能按计划假设判断局部 Retry、扩大检索、Replan、Abstain 或 Human Review。

### 为什么不能每个能力都做成一个微服务

专业能力很多，但逻辑边界不等于部署边界。默认可在同一 Python backend / worker pool 中通过 typed ports 和 versioned registry 组合；只有独立扩缩容、依赖隔离、安全边界或部署生命周期形成证据时，才按 ADR-0012 考虑物理拆分。

研究团队需要的是可替换和可验证，不是服务数量。

### 当前、目标与缺口

Current 仓库已有 capability / skill / tool / model provider 与跨模块 Contract 基础，但完整 Capability Registry、Conformance suite、Eligibility lifecycle 和法律质量证据尚未由专项 Current Evidence 证明。

Target 是稳定 Capability semantic contract + immutable version + Provider binding + Conformance + Eval + Eligibility + Planner Awareness。Gap 包括 Registry、版本兼容、provider equivalence、法律 Eval、Planner resolution、deprecation / rollback、Research Artifact → Capability E2E 和 measurement evidence。

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
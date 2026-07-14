# 05 Memory & Context

updated: 2026-07-14
status: normative-target-module-architecture
module_number: 05
formal_path: `docs/modules/05-memory-context.md`
agent_mirror: `.agent/modules/05-memory-context.md`

> 本文是 Zuno 第 05 个逻辑模块——Memory & Context——唯一的正式 Target 架构主设计。
>
> 本文只描述目标架构、规范性 Contract、状态、失败、恢复、存储和验证要求，不把现有类名、SQLite 表、局部测试或历史 Phase 当成 Current 完成事实。Current、Gap、Measurement 与完成证据由 `docs/status/production-readiness.md` 维护；具体实现、迁移、切流和收口计划必须进入 `.agent/programs/`。

## 0. 文档边界与事实源

本文统一承载：

```text
问题与目标
记忆生命周期与内容类型
Working → Session → Long-term 的沉淀流程
Session Summary、Memory Candidate、Governance 与 Version
Memory Manifest、按需召回和 ContextPack
滑动窗口、Tool Observation 压缩和语义压缩
Reflexion、Consolidation、Utility 与负迁移
状态机、失败、重试、恢复、幂等和并发
安全、隐私删除、审计与可观测性
目标代码、数据库、索引、Contract、测试和完成证据
```

文档边界：

```text
docs/modules/05-memory-context.md
    唯一正式 Target 架构事实源。

.agent/modules/05-memory-context.md
    字节级一致的 Agent 镜像，不是第二份独立架构文档。

.agent/programs/
    Current → Target 的实现、Migration、回填、切流和收口计划。

docs/status/production-readiness.md
    Current、Gap、Measurement Blocked 和完成证据状态。

docs/history/
    已完成或被替代的历史方案，不得重新解释为当前 Target。
```

规范优先级：

```text
全局架构原则
→ 本模块 Target 架构文档
→ 已冻结的跨模块共享 Contract
→ 已确认 Program
→ 代码与 Migration
```

Part I–IV 解释问题、概念、流程和实现表面；Part V–VII 给出规范性状态、Policy、存储和恢复协议；Part VIII 定义 Requirement、测试与完成证据。说明性段落不得覆盖规范性 Contract。

---

# Part I：定位、术语与概念架构

# 1. 为什么需要独立的 Memory & Context 模块

企业 Agent 不能把所有历史消息、Tool Result、检索证据和用户偏好直接拼接进模型上下文，也不能把模型总结出的任何内容直接写成长久事实。否则会出现：

```text
完整会话随着时间无限增长
重要决定被滑动窗口静默淘汰
低价值 Tool Payload 占满 Context Window
旧记忆被当成当前事实
用户偏好、项目约定和企业证据混为一体
单次失败被过度泛化为永久规则
模型可以自行批准、覆盖或删除长期事实
Checkpoint、Conversation、Memory 和 ContextPack 职责重叠
跨租户、跨 Workspace 或已撤销内容被重新召回
压缩后无法证明保留了 Goal、Policy、Evidence 和副作用状态
索引写入成功被误认为 MemoryVersion 已激活
```

一句话定义：

> Memory & Context 是 Zuno 的受治理记忆领域与预算化上下文装配模块。它将跨运行仍有价值的用户事实、任务经历和程序经验版本化保存，并为每次模型调用构造安全、可解释、可重放、可验证的不可变 `ContextPackVersion`。

# 2. 三个正交维度

Zuno 不使用单一“几层记忆”轴描述全部对象。目标模型由三个正交维度组成。

## 2.1 时间生命周期：三层

```text
Working Memory
→ Session Memory
→ Long-term Memory
```

| 层 | 生命周期 | 主要内容 | Canonical Owner |
| --- | --- | --- | --- |
| Working Memory | Action / Step / Run | Goal、Plan、Step、当前 Observation、Budget、Interrupt、Evaluation | Agent Core；控制状态由 LangGraph Checkpointer 持久化 |
| Session Memory | 多个 Run 的连续会话或工作阶段 | Current State、Task Summary、Confirmed Decision、Active Constraint、Open Issue、Artifact/Evidence Ref | Memory & Context；原始消息仍归 Product Surface |
| Long-term Memory | 跨 Session、跨任务 | Episodic、Semantic、Procedural MemoryVersion | Memory & Context |

`Sensory Memory` 不是 Zuno 的 Canonical 持久层。当前用户输入、Tool Observation、Retrieval Observation 和 Runtime Event 是各 Source Owner 的源事实或 Working 输入，不需要另建一套 Sensory Memory 事实库。

## 2.2 长期内容类型：三种

```text
Episodic Memory
    发生过什么。

Semantic Memory
    什么事实在某个 Scope 和有效时间内成立。

Procedural Memory
    在什么条件下建议怎样做。
```

| 类型 | 核心语义 | 典型内容 | 不允许冒充 |
| --- | --- | --- | --- |
| Episodic | 一次具体经历 | Task Signature、关键动作、Outcome、Failure、Recovery、Evidence Ref | 普遍有效规则 |
| Semantic | 稳定事实 | 用户偏好、角色、Workspace 约定、稳定实体属性、有效时间 | 企业知识库原文 |
| Procedural | 可复用策略 | Trigger、Recommended Action、Contraindication、Success Criteria | Skill、Tool、Security Policy 或自动执行权 |

Entity 不是第四种长期 Memory。`EntityFact` 与 `EntityRelation` 是 Semantic Memory 的结构化 Projection；Vector、Graph、Lexical 也是可重建 Projection，不是 Canonical Memory。

## 2.3 压缩强度：四类

```text
C0 Deterministic Lossless
    确定性无损压缩。

C1 Deterministic Lossy
    确定性有损但可解释压缩。

C2 Model-assisted Structured Compression
    弱模型为主的结构化抽取与增量摘要。

C3 Reasoning Consolidation
    强模型辅助的跨经历语义整合、冲突分析与 Reflexion。
```

三层、三种和四类压缩不是平级枚举：

```text
三层回答“活多久”
三种回答“长期记什么”
四类回答“如何变短、变结构化或变稳定”
```

# 3. Context、Memory、Knowledge 和 Checkpoint 的边界

```text
Context != Memory
Memory != Knowledge
Conversation Transcript != Session Summary
Session Summary != Long-term Memory
LangGraph Checkpoint != Memory Database
ContextPack read view, not another memory layer
Index Projection != Canonical Memory Fact
```

## 3.1 Knowledge

Knowledge 是企业文档、DocumentVersion、Evidence、SourceSpan、Citation 和 Retrieval Lineage 的事实 Owner。Memory 可以保存 `knowledge_evidence_ref` 或“用户如何使用某知识”的事实，但不能复制整份企业知识库。

## 3.2 Product Surface

Product Surface 拥有 Conversation、原始用户消息、Assistant 展示消息、附件交互和用户可见的记忆管理入口。Memory 不把原始聊天记录重新定义为自己的事实。

## 3.3 Agent Core

Agent Core 拥有 Run、GoalVersion、PlanVersion、StepRun、Action、Reflection、RunOutcome 和 `ExecutionContextSnapshot`。Working Memory 的控制语义属于 Agent Core；Memory 只通过 Contract 提供 `ContextPackVersion`、Memory Candidate Receipt 和受治理的长期记忆读取。

## 3.4 LangGraph Checkpointer

Checkpointer 保存图控制状态、Node 进度、Interrupt 和恢复所需的序列化状态。它不承担用户偏好、跨任务经验或长期 MemoryVersion 的 Canonical Store。

```text
Checkpoint Commit != Domain Memory Commit
```

## 3.5 ContextPack

ContextPack 是一次模型调用或一个 Step 阶段的不可变预算化读取视图。它可以引用 Policy、Goal、Plan、Session Summary、Memory、Knowledge Evidence、Tool Observation 和 Output Contract，但不拥有这些源事实。

# 4. 模块职责

Memory & Context 负责：

```text
SessionSummaryVersion 和 TaskSummaryVersion
MemoryCaptureIntent 与 MemoryCandidate
Memory Governance、Conflict、Version、Activation、Revoke
Episodic / Semantic / Procedural Memory
MemorySnapshot 与 MemoryManifestSnapshot
按 Scope、时间、类型和 Applicability 召回
ContextCandidateItem 与多级 Fidelity
Context Budget、Protected Set、Atomic Group 与 Packing
ContextPackVersion 与 CompressionTrace
MemoryUseTrace 与 Utility Projection
Reflexion Candidate 接收、验证和晋升
跨 Episode Consolidation
Memory Projection Manifest、Index Acceptance 与 Cutover
Privacy Delete、Retention、Legal Hold Binding 和派生清理
领域事件、审计关联、恢复和 Reconciliation
```

Memory & Context 不负责：

```text
原始 Conversation Message
企业文档、Evidence 和 Citation 的权威内容
Run、Plan、Step、Action 或 RunOutcome
模型 Provider Routing 和 Tokenizer 的权威定义
直接执行 Tool 或外部副作用
审批权限或计算 Security Policy
直接修改 SkillDefinition 或 CapabilityDefinition
保存隐藏思维链
让模型直接批准、激活、覆盖或删除长期 Memory
把 Vector / Graph / Cache 当成事务事实源
```

# 5. Cross-module Ownership

| 对象 | Canonical Owner | Memory 的角色 |
| --- | --- | --- |
| ConversationMessage | Product Surface | 按 Ref 读取，用于 Session Summary |
| ToolObservation / EffectReceipt | Tool Runtime | 归一化为 Digest/Ref，不改写 Outcome |
| Evidence / CitationLineage | Knowledge | 只引用，不复制权威内容 |
| ModelCapabilityProfile / Tokenizer | Model Gateway | 用于预算和模型角色选择 |
| Run / Plan / Step / Reflection / Outcome | Agent Core | 作为候选提取和 Context 构建来源 |
| Authorization / Consent / Security Epoch | Security | 构建和提交时验证 |
| Trace / EvalResult | Observability & Eval | 作为评测、Reflexion 和质量证据 |
| Checkpoint / Queue / Lease / CAS / Object Store | Infrastructure | 作为持久化与执行 Primitive |
| MemoryCandidate / MemoryVersion / ContextPackVersion | Memory & Context | Canonical Owner |

# 6. 核心架构不变量

1. 所有长期 Memory 必须经过 Candidate 和 Governance；不存在模型直写 Active Memory 的正式路径。
2. `MemoryVersion` 激活后不可原地修改；更新创建新版本并显式 Supersede。
3. `ContextPackVersion` 提交后不可原地修改；新召回或新 Observation 创建下一版本。
4. Security / Scope Filter 必须在模型摘要和内容注入前执行。
5. Pending、Rejected、Quarantined、Revoked、Deleted、跨 Scope 的 Memory 不得进入 ContextPack。
6. Working State 不归长期 Memory；Session Summary 不是 Checkpoint 替代品。
7. 单次 Reflexion 默认只足以支持 Episodic Candidate，不能自动晋升 Procedural。
8. Procedural Memory 只能作为 Strategy Hint，不能绕过 Plan、Budget、Security、Approval、Skill 或 Tool Runtime。
9. Context 压缩不得改变 Canonical Memory；Memory Consolidation 不得因当前 Context 不够而删除正式事实。
10. Physical Index Write 不等于 MemoryVersion 可服务；必须遵循 Verification、Manifest、Acceptance、CAS Cutover 和 ServingWatermark。
11. 任何模型都只产生 Proposal；领域状态由确定性校验、Policy 和 Canonical Owner 提交。
12. 源事实可追溯、压缩表示可重建、选择结果可解释、恢复操作可幂等重放。

# 7. 非目标与 Future 边界

近期 Target 不包括：

```text
产品级自治 Multi-Agent Memory Runtime
模型自主管理 Store / Update / Forget 的强化学习策略
直接修改模型权重的 Parametric Memory
跨租户共享长期记忆
无治理的自修改 Prompt 或 Skill
把每个 Memory Event 都做完整 Event Sourcing
默认依赖 Kafka、Kubernetes 或复杂分布式锁
用一份永远增长的 Workspace Summary 代替结构化事实
```

这些能力只有在现有方案通过固定 Eval、隐私、安全、恢复和成本验证后，才可进入 Future Proposal。

---

# Part II：完整运行流程

# 8. Source Facts 与六个运行平面

```text
Source Facts Plane
    Conversation、Knowledge Evidence、Tool Observation、
    Agent Run/Plan/Outcome、Security/Consent、EvalResult。

Ephemeral Runtime Plane
    Working Memory / ExecutionContextSnapshot / Checkpoint。

Session Continuity Plane
    Recent Raw Tail、TaskSummaryVersion、SessionSummaryVersion。

Durable Governed Memory Plane
    MemoryCandidate、MemoryRecord、MemoryVersion。

Projection Plane
    Manifest、Vector、Graph、Lexical、Entity、Utility。

Context Consumption Plane
    ContextCandidate、Selection、Compression、ContextPackVersion。
```

源事实只由各自 Owner 更新。Memory 使用 Ref 和 Snapshot 构造自己的 Candidate、Version 与读取视图。

# 9. Working Memory 如何进入 Session Memory

Working Memory 不会整体搬运到 Session。沉淀流程是：

```text
Working Events / Conversation Delta
→ Source Range Pin
→ Deterministic Pre-filter
→ Session Continuity Extraction Proposal
→ Schema / Coverage / Security Validation
→ SessionSummaryVersion Commit
→ Recent Raw Tail Boundary Update
```

## 9.1 可进入 Session 的内容

```text
Current State
Task Specification
Confirmed Decisions
Active Constraints
Completed Objectives
Open Objectives
Open Issues
Errors & Corrections
Artifact Refs
Evidence Refs
Next Valid Control Point
```

## 9.2 不进入 Session 的内容

```text
隐藏思维链
每次 Reducer 中间值
重复 Token 估算
可由 Artifact 重新读取的大型 Payload
无影响的临时尝试
已被后续 Observation 完全替代的低价值日志
完整 Tool Credential 或 Secret
```

## 9.3 触发条件

Session Summary 不在每轮都调用模型。默认触发模型：

```text
首次达到 initialization_token_threshold

之后满足：
context_growth >= update_token_threshold
AND (
    natural_boundary = true
    OR completed_tool_group_count >= tool_group_threshold
    OR explicit_summary_request = true
)
```

`natural_boundary` 包括：

```text
Assistant 已形成无未完成 Tool Call 的阶段性结果
一个 Objective 完成
进入 Interrupt / Wait
准备 Context Compact
用户明确切换子任务
```

触发参数由 Config Version 管理，并通过 Eval 调整；具体数值不写死为架构事实。

## 9.4 增量更新

```text
Previous SessionSummaryVersion
+ New Source Event Delta
→ SummaryProposal
→ Validation
→ New Immutable SessionSummaryVersion
```

不得每次重新总结整个会话，也不得覆盖旧 SummaryVersion。

# 10. Session Memory 如何进入 Long-term Memory

Session Summary 本身不会直接晋升长期 Memory。长期提取流程：

```text
Session Event / Summary / RunOutcome / User Feedback
→ Capture Policy
→ MemoryExtractionProposal
→ MemoryCandidate
→ Scope Resolution
→ Security / Consent Gate
→ Exact Dedup
→ Semantic Near-duplicate Check
→ Conflict Detection
→ GovernanceDecision
→ MemoryRecord / MemoryVersion
→ Projection Build
→ Verification / Acceptance / Activation
```

只有满足以下条件之一的内容才值得形成 Candidate：

```text
用户明确要求记住
未来其他 Session 仍可能有用
稳定用户事实或偏好
无法从代码、Git、Knowledge 或当前资源重新推导
具有可复用价值的成功或失败经历
有足够证据支持的程序经验
外部最新事实所在位置的 Reference
```

活动列表、完整 PR 列表、临时工作进度、可从代码重建的架构快照，不应进入长期 Memory。

# 11. Long-term Memory 如何重新进入 Working Context

```text
Current Goal / Step / Query
→ Pin MemorySnapshot
→ Load MemoryManifestSnapshot
→ Deterministic Scope / ACL / State / Time Filter
→ Type-specific Retrieval
→ Hybrid Candidate Merge
→ Applicability Validation
→ Conflict / Freshness Handling
→ Context Budget Packing
→ ContextPackVersion
→ Agent Core consumes read view
```

## 11.1 主动召回

Task Start 默认只召回低成本、高权威的小集合：

```text
明确用户偏好
Workspace / Project 约定
Approved Procedural Hint
当前任务强相关的 Semantic Fact
Memory Manifest Topic
```

## 11.2 按需召回

执行中在以下触发下追加召回：

```text
用户引用过去工作
Step Failure 与历史 Failure Signature 相似
Reflection 要求历史案例
Replan 需要旧决策或约束
实体、项目或外部系统 Reference 被提及
Final Gate 发现缺少适用经验
```

## 11.3 分类型 Query

```text
Semantic：
    subject + predicate + scope + effective time

Episodic：
    task signature + environment + failure class + outcome

Procedural：
    trigger predicate + task type + required capability + risk class
```

所有类型不得使用同一个无差别 `top_k` 语义查询。

# 12. Memory Manifest 与懒加载

`MemoryManifestSnapshot` 是小型导航 Projection，不是记忆正文。它包含：

```text
Topic ID
One-line Summary
Memory Kind Count
Latest Effective Time
Sensitivity
Authority Summary
Projection Generation
```

Context Builder 常驻加载 Manifest，而不是全量加载 Memory。详细 Memory 只有在 Query、Scope 和 Applicability 明确匹配时才读取。

Manifest 必须：

```text
有明确 Token Budget
按 Topic 而不是时间流水组织
可由 MemoryVersion 重建
不携带高敏正文
记录 Snapshot / Generation / Content Hash
```

# 13. Context 构建完整流程

```text
REQUESTED
→ PIN_SOURCE_SNAPSHOTS
→ COLLECT_CANDIDATES
→ SECURITY_FILTER
→ NORMALIZE_AND_OFFLOAD
→ DEDUP_AND_CONFLICT
→ PREPARE_REPRESENTATIONS
→ BUILD_PROTECTED_SET
→ PACK_ATOMIC_GROUPS
→ DEGRADE_IF_NEEDED
→ EXACT_TOKEN_VALIDATE
→ POLICY_AND_EVIDENCE_VALIDATE
→ COMMIT_CONTEXT_PACK_VERSION
```

## 13.1 固定快照

至少固定：

```text
ExecutionContextSnapshot
GoalVersion
PlanVersion
EffectiveSecurityEpoch
MemorySnapshot
KnowledgeSnapshot
CapabilitySnapshot
ModelCapabilityProfile
TokenizerVersion
ContextPolicyVersion
```

构建中任一强一致快照变更时，本次 Build 必须 Stale 或重启，不得提交混合代际 Context。

## 13.2 Context 来源

```text
System / Security Policy
Current User Goal
Active Plan / Step Contract
Recent Conversation
Session Summary
Semantic Memory
Procedural Memory
Selected Episodic Example
Knowledge Evidence
Normalized Tool Observation
Capability / Tool State
Approval / Side-effect State
Output Contract
```

# 14. ContextCandidateItem

每个候选必须具备：

```yaml
context_candidate_item:
  context_item_id: string
  source_module: string
  source_type: string
  source_ref: string
  source_version_ref: string
  content_hash: string

  mandatory: bool
  priority_class: string
  atomic_group_id: string | null
  conflict_group_id: string | null

  tenant_id: string
  workspace_id: string | null
  subject_scope_ref: string | null
  classification: string
  effective_security_epoch_ref: string

  authority_score: float
  relevance_score: float
  freshness_score: float
  criticality_score: float
  applicability_score: float
  evidence_strength: float
  conflict_risk: float

  representations: list[ContextRepresentation]
  selected_fidelity: string | null
  selection_state: string
  selection_reason_code: string | null
```

模型可以提出 Relevance、摘要或 Applicability，但 Scope、State、Security、Token、Hash 和 Atomic Group 校验必须确定性执行。

# 15. 五级 Context Fidelity

```text
F0 FULL
    完整原文或完整结构化对象。

F1 NORMALIZED
    去噪、标准化、结构化的等价表示。

F2 EVIDENCE_BOUND_SUMMARY
    带 Source Ref、Coverage 和内容 Hash 的摘要。

F3 REFERENCE_ONLY
    Artifact / Evidence / Memory / Transcript Ref。

F4 EXCLUDED
    本次不进入 Context，保留排除原因。
```

Fidelity 是 Context 表示等级，不是 Memory 状态。正式 MemoryVersion 不因某次 Context 从 F0 降到 F3 而被修改。

# 16. 四类压缩如何交互

## 16.1 C0 Deterministic Lossless

```text
Exact Hash Dedup
重复 Metadata 合并
JSON / Whitespace 标准化
Citation Ref 合并
大型 Payload Object Store Offload
相同 ArtifactRef 去重
Tool Schema 重复消除
```

C0 可以作用于 Working、Session 和 Long-term Projection，不改变语义。

## 16.2 C1 Deterministic Lossy

```text
Sliding Window
旧 Tool Result Clear / Digest
F0 → F1 → F2 → F3 → F4
低价值候选排除
最近 Atomic Tail 保留
Source-specific Quota
```

C1 必须有明确规则、Token 节省量和排除 Trace。

## 16.3 C2 Model-assisted Structured Compression

弱模型默认负责：

```text
Turn Digest
Task Summary
Session Summary
Decision / Constraint Extraction
Memory Candidate Classification
普通 Near-duplicate Proposal
Evidence-bound Summary
```

所有输出必须经过 Schema、Coverage、Source Ref、Security 和 Token 校验。

## 16.4 C3 Reasoning Consolidation

强模型只在需要复杂推理时负责 Proposal：

```text
多 Episode 共同根因
复杂冲突解释
Reflexion Root Cause
Procedural Applicability 与 Contraindication
多次摘要后的语义修复
高风险跨任务 Consolidation
```

C3 不直接提交、激活、删除或修改 MemoryVersion。

# 17. 滑动窗口的正确位置

滑动窗口只负责 Recent Raw Tail，不承担完整 Memory 体系。

正确组合：

```text
Recent Raw Tail
+ SessionSummaryVersion
+ Active Structured State
+ Relevant Long-term Memory
+ Required Knowledge Evidence
+ Protected Policy / Goal / Plan
```

Recent Raw Tail 的边界必须：

```text
满足最小文本交互数
满足最小 Token
不超过 Hard Cap
不拆分 Tool Call / Tool Result
不拆分 Action / Observation / Evaluation
不拆分 Claim / Citation
不跨过不可恢复 Compact Boundary
```

# 18. Tool Observation 压缩

大型 Tool Observation 是 Context 压缩的首要对象。

```text
Raw Observation
→ ObservationNormalizer
→ ObservationDigest
→ ArtifactRef
```

可重新读取的旧 Tool Result 按：

```text
F0 FULL
→ F1 STRUCTURED DIGEST
→ F3 ARTIFACT REF
```

保留至少：

```text
tool_execution_ref
input_hash
outcome
side_effect_state
artifact_ref
evidence_ref
occurred_at
```

不可逆副作用、UNKNOWN Outcome、待 Reconcile 结果不得静默清除。

# 19. Protected Set 与预算

Protected Set 包括：

```text
Security Policy
Current User Goal
Active Plan / Step Contract
Approval Constraint
Unresolved Side-effect State
Output Contract
Required Evidence
Mandatory User Constraint
```

预算：

```text
B_pack =
    model_context_window
  - output_reserve
  - tool_schema_reserve
  - runtime_safety_margin
  - provider_margin
```

分配顺序：

```text
Protected Set
→ Source Minimum Reservation
→ Elastic Shared Pool
```

如果 Protected Set 自身超过预算：

```text
MEM_CONTEXT_MANDATORY_BUDGET_UNSATISFIABLE
```

Agent Core 必须缩小 Step、拆分 Plan、切换可用的大 Context Model、减少 Tool Surface 或 Abstain；不得静默删除 Mandatory Item。

# 20. Packing 算法

第一版采用可解释、可重放的 Atomic-group-aware Deterministic Greedy：

```text
utility =
    relevance
  + authority
  + criticality
  + freshness
  + applicability
  + evidence_strength
  + diversity_gain
  - conflict_risk
  - stale_risk
  - token_cost_penalty
```

顺序：

1. 放入 Protected Set；
2. 满足每个 Source 的最小保留；
3. 以 Atomic Group 为单位排序；
4. 按 Utility / Token Cost 放入；
5. 检查 Diversity、Evidence Coverage 和 Source Cap；
6. 超预算时按 Fidelity Ladder 降级；
7. 以 Model Gateway 提供的 Tokenizer 精确计数；
8. 失败则返回明确 Failure，不提交 ContextPack。

模型可提供 Relevance Proposal，但不能控制 Mandatory、ACL 或最终 Token 判定。

# 21. Session Compact 与 Rehydration

Context 接近上限时的顺序：

```text
C0 去重与 Offload
→ C1 Tool Observation 降级
→ C1 Recent Raw Tail 边界调整
→ C2 使用已有 SessionSummaryVersion
→ C2 生成增量 Summary
→ 按需 Memory 召回与降级
→ 最后才执行模型级 Semantic Compact
```

Compact 后必须重建：

```text
CompactBoundary
+ SessionSummaryVersion
+ Recent Raw Tail
+ Security Policy
+ Current Goal
+ Active Plan / Step
+ Memory Manifest
+ Required Evidence
+ Capability / Tool State
+ Output Contract
```

Summary 不是唯一恢复来源；摘要只是可验证的读取表示。

`CompactionSnapshot` 至少记录：

```yaml
compaction_snapshot:
  compaction_id: string
  source_event_range: string
  source_event_hash: string
  summary_version_ref: string
  recent_tail_start_ref: string

  mandatory_rehydrate_refs: list[str]
  lazy_rehydrate_refs: list[str]
  omitted_source_refs: list[str]
  compression_trace_ref: string

  tokenizer_version: string
  pre_compact_tokens: int
  post_compact_tokens: int
  security_epoch_ref: string
```

# 22. 模型级 Semantic Compact

只有在已有确定性压缩和 Session Summary 仍无法满足预算时使用。

输入必须排除：

```text
隐藏思维链
可通过 Ref 恢复的大型 Payload
压缩后会重新注入的 Policy
无权访问或已撤销内容
```

输出必须结构化保存：

```text
Primary Goal
Current State
Confirmed Decisions
Active Constraints
Completed Work
Errors & Corrections
Open Issues
Pending Tasks
Artifact / Evidence Refs
Next Valid Control Point
```

高风险摘要不得替代原始 Evidence，也不得创建未被 Source Fact 支持的新事实。

# 23. Reflexion 流程

Reflection 属于当前 Run 的质量控制；Reflexion 是跨任务经验 Candidate。

触发条件：

```text
重复相同 Failure
Run Failed / Partial / Abstained
多次 Retry、Repair 或 Replan 后成功
Fallback 恢复成功
用户明确负反馈或正向确认
固定 Eval 发现系统性问题
出现非显然且可复用的成功模式
```

非触发：

```text
一次瞬时网络错误
单纯 Security Block
无证据的根因猜测
未 Reconcile 的副作用 Outcome
普通格式转换
```

流程：

```text
Trigger
→ Evidence Bundle
→ Root Cause Proposal
→ Lesson Proposal
→ Schema Validation
→ Evidence Entailment
→ Capability Feasibility
→ Dedupe / Conflict
→ Applicability
→ Security
→ Governance Review
```

单次结果默认形成 Episodic Candidate。Procedural 晋升要求：

```text
人工批准
OR 多次独立 Episode 支持
OR 固定 Eval 证明
OR 用户 / 管理员明确确认
```

并且必须通过 Safety、Capability、Applicability、Counterexample 和 Revoke 检查。

# 24. Consolidation

Consolidation 不是压缩当前 Context，而是重组长期 Memory。

```text
Select Source MemoryVersions
→ Pin MemorySnapshot
→ Verify Source State
→ Cluster Similar Episodes
→ ConsolidationProposal
→ MemoryCandidate
→ Governance
→ New MemoryVersion
→ Supersede / Keep / Conflict
→ Projection Build
```

允许：

```text
多个 Episodic → Semantic Candidate
多个 Episodic + 验证策略 → Procedural Candidate
重复 Semantic → 新 Version 或 Dedup Decision
```

禁止：

```text
模型直接批准
模型直接删除旧 Version
覆盖 Source Episode
丢失 Evidence / Source Ref
因检索权重低而删除 Canonical Fact
```

# 25. Privacy Delete、Revoke 与 Legal Hold

删除流程：

```text
DeletionRequest
→ Authorization / Identity Scope
→ Legal Hold Check
→ Canonical Record Tombstone / Delete Decision
→ Serving Exclusion
→ Vector / Graph / Lexical / Cache Purge
→ Object / Backup Policy Handling
→ Verification
→ DeletionReceipt
```

`Revoke` 表示不可继续使用但保留合规事实；`Delete` 表示按 Policy 清除或加密销毁；`Supersede` 表示被新版本替代，三者不可混用。

Privacy Delete 必须传播到：

```text
PostgreSQL Canonical Rows
Object Store Payload
Vector Projection
Graph Projection
Lexical Projection
Cache
Manifest
ContextPack Future Selection
Backup / Legal Hold Workflow
```

---

# Part III：状态、失败、恢复与一致性

# 26. MemoryCandidate 状态机

```text
PROPOSED
→ VALIDATING
→ PENDING_REVIEW
→ APPROVED | REJECTED | QUARANTINED | EXPIRED
```

`APPROVED` 只表示 Governance 接受 Candidate；它不等于 MemoryVersion 已索引、激活或可服务。

| Current | Event | Next | 规则 |
| --- | --- | --- | --- |
| PROPOSED | VALIDATION_STARTED | VALIDATING | 固定 Source Snapshot |
| VALIDATING | VALIDATION_PASS | PENDING_REVIEW | 写 Validation Report |
| VALIDATING | VALIDATION_FAIL | REJECTED | 不得创建 Active Version |
| VALIDATING | SECURITY_UNCERTAIN | QUARANTINED | 等待安全处理 |
| PENDING_REVIEW | APPROVE | APPROVED | 生成 Version Intent |
| PENDING_REVIEW | REJECT | REJECTED | 保存 Decision Reason |
| PENDING_REVIEW | TTL_EXPIRED | EXPIRED | 不再参与 Review |
| QUARANTINED | RELEASE | PENDING_REVIEW | 重新验证 Epoch |
| APPROVED | VERSION_COMMITTED | APPROVED | Candidate 保持终态 |

# 27. MemoryVersion 状态机

```text
DRAFT
→ PENDING_INDEX
→ INDEXING
→ VERIFIED
→ ACCEPTED
→ ACTIVE
→ SUPERSEDED | SUSPENDED | REVOKED | DELETED
```

| Current | Event | Next | 规则 |
| --- | --- | --- | --- |
| DRAFT | DOMAIN_COMMIT | PENDING_INDEX | Canonical Row 已提交 |
| PENDING_INDEX | INDEX_DISPATCHED | INDEXING | 写 IndexWriteBatch |
| INDEXING | PHYSICAL_WRITE_RECEIPT | INDEXING | 只证明物理写入 |
| INDEXING | VERIFICATION_PASS | VERIFIED | 校验 Schema/Count/Scope/Lineage |
| VERIFIED | DOMAIN_ACCEPT | ACCEPTED | Memory Owner 决定接受 |
| ACCEPTED | CAS_CUTOVER_PASS | ACTIVE | Serving Generation 更新 |
| ACTIVE | NEW_VERSION_ACTIVE | SUPERSEDED | 保留历史 |
| ACTIVE | NEGATIVE_TRANSFER | SUSPENDED | 不参与召回 |
| ACTIVE | POLICY_REVOKE | REVOKED | 立即停止服务 |
| * | PRIVACY_DELETE_COMPLETE | DELETED | 遵守 Legal Hold |

# 28. SessionSummaryVersion 状态机

```text
PROPOSED
→ VALIDATING
→ ACTIVE
→ SUPERSEDED | TAINTED | REVOKED
```

`TAINTED` 用于 Source Hash、Coverage、Security Epoch 或模型输出错误被事后发现。TAINTED Summary 不得继续作为 Compact Recovery Source。

# 29. ContextPackBuild 状态机

```text
REQUESTED
→ SNAPSHOT_PINNED
→ CANDIDATES_COLLECTED
→ POLICY_FILTERED
→ REPRESENTATIONS_READY
→ PACKED
→ VALIDATING
→ COMMITTED
```

失败终态：

```text
BLOCKED_SECURITY
BUDGET_UNSATISFIABLE
SOURCE_STALE
VALIDATION_FAILED
CANCELLED
```

ContextPack Build 失败不得产生半提交 Pack。

# 30. Projection 状态机

```text
PLANNED
→ WRITING
→ VISIBLE
→ VERIFYING
→ VERIFIED
→ ACCEPTED
→ SERVING
```

Infrastructure 只拥有 Physical Receipt、Visibility、Verification 和 Serving Watermark；Memory Owner 拥有 Manifest、Acceptance 和版本激活。

# 31. Failure Namespace

Memory & Context 使用 `MEM_*` Prefix。

```text
MEM_SCOPE_MISSING
MEM_SECURITY_EPOCH_STALE
MEM_SOURCE_STALE
MEM_SOURCE_HASH_MISMATCH
MEM_CANDIDATE_SCHEMA_INVALID
MEM_CANDIDATE_EVIDENCE_INSUFFICIENT
MEM_CANDIDATE_CONFLICT
MEM_GOVERNANCE_REQUIRED
MEM_GOVERNANCE_REJECTED
MEM_VERSION_GENERATION_CONFLICT
MEM_INDEX_WRITE_FAILED
MEM_INDEX_VISIBILITY_TIMEOUT
MEM_INDEX_VERIFICATION_FAILED
MEM_INDEX_CUTOVER_CONFLICT
MEM_CONTEXT_MANDATORY_BUDGET_UNSATISFIABLE
MEM_CONTEXT_ATOMIC_GROUP_BROKEN
MEM_CONTEXT_TOKEN_COUNT_EXCEEDED
MEM_CONTEXT_EVIDENCE_COVERAGE_FAILED
MEM_CONTEXT_VALIDATION_FAILED
MEM_SUMMARY_COVERAGE_INSUFFICIENT
MEM_SUMMARY_SOURCE_BOUNDARY_UNKNOWN
MEM_REFLEXION_OVERGENERALIZED
MEM_PROCEDURAL_CAPABILITY_UNAVAILABLE
MEM_PRIVACY_DELETE_BLOCKED
MEM_LEGAL_HOLD_BLOCKED
MEM_RECONCILIATION_REQUIRED
MEM_OUTCOME_UNKNOWN
```

# 32. Failure Decision Matrix

| Failure | Retry | Re-extract / Rebuild | Governance | Agent Core Replan |
| --- | --- | --- | --- | --- |
| Provider / transient model failure | 可重试 | 必要时升级模型 | 否 | 通常否 |
| Candidate schema invalid | 参数调整一次 | 是 | 否 | 否 |
| Evidence insufficient | 否 | 补 Evidence 后重建 | 可能 | 复杂任务可能 |
| Scope / Security denied | 否 | 重新授权后重建 | Security | 可能 |
| Context budget unsatisfiable | 否 | 缩小 Step / 换模型后重建 | 否 | 是 |
| Index write transient | 是 | 不重建 Version | 否 | 否 |
| Index verification failed | 有限重试 | 重建 Projection | Domain Acceptance | 否 |
| Version generation conflict | 否 | 读取新 Generation 再决策 | 可能 | 否 |
| Procedural negative transfer | 否 | 重新评估 Lesson | 是 | 当前 Run 可 Replan |
| Privacy delete unknown | 先 Reconcile | 否 | Legal / Security | 否 |

Retry、Rebuild、Re-govern 和 Agent Replan 必须区分。

# 33. 幂等与事务边界

## 33.1 Memory Commit

```text
MemoryCommitIntent
→ Outbox
→ Candidate / Version idempotent commit
→ MemoryCommitReceipt
→ Agent Core binds Receipt
```

`idempotency_key` 至少由：

```text
tenant_id
workspace_id
source_type
source_ref
source_version
capture_policy_version
candidate_kind
```

稳定生成。

## 33.2 Checkpoint 与 Domain Commit

允许的恢复序列：

```text
Checkpoint has Intent, Domain missing
    重放 Domain Commit。

Domain has Candidate, Checkpoint missing Receipt
    根据 Idempotency Key 查找并补绑定。

Projection written, Version not Active
    从 Manifest / Receipt 继续 Verification 和 CAS。

Outcome unknown
    先 Reconcile，不盲目重写或删除。
```

## 33.3 Summary Commit

旧 Active Summary 在新版本完整提交前继续服务。Summary Proposal、Validation 和 Active Pointer Update 使用同一 Domain Transaction 或可恢复 Outbox。

# 34. 并发与 Generation

并发写入必须携带：

```text
expected_record_generation
expected_active_version_id
effective_security_epoch_hash
idempotency_key
```

冲突规则：

```text
同 Record 并发更新
→ CAS 失败
→ 读取最新 Active Version
→ 判断 Dedup / Conflict / Retry Review
```

Consolidation、User Correction、Privacy Delete 和 Automatic Extraction 不允许最后写入者静默覆盖。

# 35. 时间语义

每个 MemoryVersion 区分：

```text
observed_at
    来源事实被观察的时间。

effective_from / effective_to
    事实在业务上生效的时间。

committed_at
    Memory Domain 提交时间。

activated_at
    成为可服务版本的时间。

last_used_at
    Utility Projection 的使用时间。
```

相对日期在持久化前必须转换成绝对时间，并保留用户原始表达 Ref。

Freshness 不能只由 `updated_at` 推断。代码、文件、外部系统当前状态在使用前必须验证；“Memory 记得 X”不等于“X 现在仍成立”。

# 36. 恢复与 Reconciliation

需要以下 Reconciler：

```text
MemoryCommitReconciler
SummaryCommitReconciler
ProjectionReconciler
ContextPackReconciler
DeletionReconciler
UtilityProjectionReconciler
```

每个 Reconciler 必须：

```text
读取 Canonical Fact 和 Receipt
识别 UNKNOWN / ORPHAN / STALE
使用 Stable Idempotency Key
不改变其他模块领域事实
产生 Reconciliation Decision 和 Audit
```

---

# Part IV：领域对象与 Contract

# 37. MemoryCaptureIntent

```yaml
memory_capture_intent:
  capture_intent_id: string
  source_module: string
  source_ref: string
  source_version_ref: string
  source_hash: string
  tenant_id: string
  workspace_id: string | null
  run_id: string | null
  step_run_id: string | null
  requested_kinds: list[str]
  trigger_type: string
  capture_policy_version: string
  effective_security_epoch_ref: string
  idempotency_key: string
```

Intent 证明“需要评估是否形成 Memory”，不证明 Candidate 或 Memory 已创建。

# 38. MemoryCandidate

```yaml
memory_candidate:
  candidate_id: string
  tenant_id: string
  workspace_id: string | null
  subject_ref: string | null

  memory_kind: EPISODIC | SEMANTIC | PROCEDURAL
  use_category: USER | FEEDBACK | PROJECT | REFERENCE
  origin: ORGANIZATION_MANAGED | WORKSPACE_MANAGED | PROJECT_MANAGED |
          USER_EXPLICIT | USER_CORRECTION | SYSTEM_OBSERVED |
          MODEL_EXTRACTED | REFLEXION_DERIVED

  proposed_payload: object
  source_refs: list[string]
  evidence_refs: list[string]
  source_snapshot_ref: string

  observed_at: datetime
  proposed_effective_from: datetime | null
  proposed_effective_to: datetime | null
  proposed_retention_policy_ref: string

  confidence: float
  evidence_strength: float
  sensitivity: string
  conflict_key: string
  dedupe_key: string

  extractor_model_call_ref: string | null
  prompt_version: string | null
  schema_version: string
  hidden_cot: false
  status: string
```

# 39. Typed Payload

## 39.1 EpisodicPayload

```yaml
episodic_payload:
  task_signature: object
  objective_summary: string
  preconditions: list[object]
  key_action_refs: list[string]
  observation_refs: list[string]
  outcome_ref: string
  failure_class: string | null
  recovery_summary: string | null
  artifact_refs: list[string]
  evidence_refs: list[string]
  started_at: datetime
  ended_at: datetime
```

## 39.2 SemanticPayload

```yaml
semantic_payload:
  subject: string
  predicate: string
  value: object
  scope_ref: string
  source_authority: string
  effective_from: datetime
  effective_to: datetime | null
  supersedes_ref: string | null
  conflict_group_id: string | null
```

## 39.3 ProceduralPayload

```yaml
procedural_payload:
  trigger_predicate: object
  recommended_actions: list[object]
  prohibited_actions: list[object]
  applicability_predicate: object
  contraindications: list[object]
  required_capabilities: list[string]
  success_criteria: list[object]
  risk_class: string
  source_episode_refs: list[string]
  counterexample_refs: list[string]
```

# 40. MemoryGovernanceDecision

```yaml
memory_governance_decision:
  decision_id: string
  candidate_id: string
  decision: APPROVE | REJECT | QUARANTINE | REQUEST_MORE_EVIDENCE
  decision_reason_codes: list[string]
  reviewer_type: POLICY | HUMAN | SYSTEM
  reviewer_ref: string
  policy_version: string
  security_decision_ref: string
  decided_at: datetime
  expected_candidate_generation: int
```

模型不得成为 `reviewer_type` 的最终 Owner。

# 41. MemoryRecord 与 MemoryVersion

```yaml
memory_record:
  memory_record_id: string
  tenant_id: string
  workspace_id: string | null
  subject_ref: string | null
  memory_kind: string
  use_category: string
  conflict_key: string
  active_version_id: string | null
  aggregate_generation: int
```

```yaml
memory_version:
  memory_version_id: string
  memory_record_id: string
  version_no: int
  typed_payload: object
  content_hash: string

  source_refs: list[string]
  evidence_refs: list[string]
  source_snapshot_ref: string

  observed_at: datetime
  effective_from: datetime
  effective_to: datetime | null

  authority_level: string
  governance_decision_ref: string
  supersedes_version_ref: string | null

  retention_policy_ref: string
  security_epoch_ref: string
  schema_version: string
  status: string
```

# 42. SessionSummaryVersion

```yaml
session_summary_version:
  summary_version_id: string
  session_id: string
  tenant_id: string
  workspace_id: string | null
  previous_version_ref: string | null

  source_event_start_ref: string
  source_event_end_ref: string
  source_event_hash: string

  current_state: list[object]
  task_specification: list[object]
  confirmed_decisions: list[object]
  active_constraints: list[object]
  completed_objectives: list[object]
  open_objectives: list[object]
  open_issues: list[object]
  errors_and_corrections: list[object]
  artifact_refs: list[string]
  evidence_refs: list[string]
  next_control_point: object | null

  coverage_manifest: object
  omitted_source_refs: list[string]
  model_call_ref: string | null
  prompt_version: string
  schema_version: string
  content_hash: string
  security_epoch_ref: string
  status: string
```

# 43. MemorySnapshot

```yaml
memory_snapshot:
  memory_snapshot_id: string
  tenant_id: string
  workspace_id: string | null
  serving_generation: int
  active_version_refs: list[string]
  manifest_snapshot_ref: string
  projection_manifest_refs: list[string]
  security_epoch_ref: string
  created_at: datetime
  content_hash: string
```

# 44. MemoryManifestSnapshot

```yaml
memory_manifest_snapshot:
  manifest_snapshot_id: string
  memory_snapshot_id: string
  topic_entries:
    - topic_id: string
      label: string
      one_line_summary: string
      memory_kind_counts: object
      latest_effective_at: datetime | null
      sensitivity: string
      authority_summary: string
      topic_version_refs: list[string]
  token_count: int
  content_hash: string
```

# 45. ContextRepresentation

```yaml
context_representation:
  fidelity: F0 | F1 | F2 | F3
  content: object | null
  content_ref: string | null
  source_refs: list[string]
  coverage_manifest: object | null
  token_cost_estimate: int
  representation_hash: string
```

# 46. ContextSelectionDecision

```yaml
context_selection_decision:
  decision_id: string
  context_build_id: string
  context_item_id: string
  selected: bool
  selected_fidelity: string | null
  reason_code: string
  utility_components: object
  token_cost: int
  atomic_group_id: string | null
  policy_version: string
```

# 47. ContextPackVersion

```yaml
context_pack_version:
  context_pack_id: string
  version_no: int
  tenant_id: string
  workspace_id: string | null
  run_id: string
  step_run_id: string | null

  execution_snapshot_ref: string
  goal_version_ref: string
  plan_version_ref: string
  security_epoch_ref: string
  memory_snapshot_ref: string
  knowledge_snapshot_ref: string | null
  capability_snapshot_ref: string | null

  selected_item_refs: list[string]
  selection_decision_refs: list[string]
  compression_trace_ref: string
  exclusion_summary: object

  tokenizer_version: string
  model_capability_profile_ref: string
  input_token_count: int
  output_reserve: int
  tool_schema_reserve: int
  content_hash: string
  committed_at: datetime
```

# 48. MemoryUseTrace 与 MemoryUtilityProjection

```yaml
memory_use_trace:
  memory_use_trace_id: string
  memory_version_id: string
  context_pack_version_ref: string
  run_id: string
  step_run_id: string | null
  selection_reason: string
  adopted_by_agent_core: bool
  influenced_plan: bool
  influenced_action: bool
  outcome_ref: string | null
  eval_result_refs: list[string]
  recorded_at: datetime
```

```yaml
memory_utility_projection:
  memory_version_id: string
  use_count: int
  success_after_use: int
  failure_after_use: int
  negative_transfer_count: int
  last_used_at: datetime | null
  retrieval_weight: float
  suspension_reason: string | null
  projection_generation: int
```

Utility 是 Projection，不回写不可变 MemoryVersion 的事实内容。

# 49. ReflexionCandidate

```yaml
reflexion_candidate:
  reflexion_candidate_id: string
  task_signature: object
  source_run_ref: string
  source_step_refs: list[string]
  run_outcome_ref: string
  acceptance_result_refs: list[string]
  eval_result_refs: list[string]

  observed_problem: string
  root_cause_proposal: string
  lesson_proposal: string
  recommended_action: object
  control_point: string

  applicability_predicate: object
  contraindications: list[object]
  counterexample_refs: list[string]
  required_capabilities: list[string]

  expected_benefit: float
  risk_score: float
  confidence: float
  novelty: float
  evidence_strength: float

  sensitivity: string
  retention_policy_ref: string
  model_call_ref: string
  prompt_version: string
  schema_version: string
  hidden_cot: false
```

# 50. ConsolidationProposal

```yaml
consolidation_proposal:
  consolidation_proposal_id: string
  source_memory_snapshot_ref: string
  source_version_refs: list[string]
  target_kind: SEMANTIC | PROCEDURAL
  proposed_payload: object
  dedupe_analysis: object
  conflict_analysis: object
  applicability_analysis: object
  counterexample_refs: list[string]
  model_call_ref: string | null
  status: string
```

# 51. MemoryCommitReceipt

```yaml
memory_commit_receipt:
  receipt_id: string
  capture_intent_id: string
  candidate_id: string | null
  memory_record_id: string | null
  memory_version_id: string | null
  commit_state: NO_MEMORY | CANDIDATE_COMMITTED | VERSION_COMMITTED
  idempotency_key: string
  domain_generation: int
  committed_at: datetime
```

Receipt 不证明 Index Serving，也不证明未来 Agent 一定会使用该 Memory。

---

# Part V：Policy、模型角色与安全

# 52. Write Policy

Memory Write Policy 决定：

```text
是否值得产生 Candidate
允许的 MemoryKind
允许的 Origin
Scope 和 Subject
Retention
Sensitivity
Human Review Requirement
是否允许自动低风险批准
```

优先级：

```text
Organization Managed Policy
→ Tenant Policy
→ Workspace Policy
→ User Consent
→ Capture Policy
```

低层 Policy 只能收紧，不能放宽 Security 与 Retention。

# 53. 模型角色

| 工作 | 默认执行者 |
| --- | --- |
| Exact Dedup、Scope、ACL、Token、Atomic Group | 确定性系统 |
| Turn / Decision / Constraint Extraction | `EXTRACTOR` 弱模型 |
| Session Incremental Summary | `EXTRACTOR` 或 `EXECUTOR_FAST` |
| Memory Classification | `EXTRACTOR` |
| Relevance Proposal | Reranker 或弱模型 |
|普通 Near-duplicate Proposal | Embedding + 弱模型 |
| 复杂 Conflict、跨 Episode Consolidation | `EXECUTOR_REASONING` / `CRITIC` |
| Reflexion Root Cause | `CRITIC` / `FINAL_CRITIC` |
| Governance、Activation、Delete | 非模型 Owner |

升级链：

```text
EXTRACTOR
→ 调整参数或 Prompt 重试
→ EXECUTOR_REASONING
→ CRITIC 判断 Reject / Re-extract / Request Evidence
```

模型不能：

```text
批准自己的 Candidate
激活 MemoryVersion
修改 Security Epoch
删除或撤销 Memory
自动创建 Skill
绕过 Context Budget
保存隐藏思维链
```

# 54. Security 与 Privacy

每次 Capture、Retrieval、Context Build、Use 和 Delete 都验证：

```text
Tenant
Workspace
Principal / Subject
Purpose
Consent
Data Classification
Effective Security Epoch
Retention
Legal Hold
```

安全门必须先于：

```text
模型摘要
Embedding
Rerank
跨域 Projection
Context 注入
```

敏感 Memory 的 Manifest 只能暴露最小必要 Metadata。

# 55. Prompt Injection 与记忆污染

Memory Candidate 来源中的指令性文本不得自动获得系统指令权威。

处理流程：

```text
Source Classification
→ Instruction / Data Separation
→ Prompt Injection Detection
→ Authority Assignment
→ Candidate Validation
```

Knowledge 文档中的“请忽略系统规则”只能作为数据，不得形成 Procedural Memory。用户明确偏好也不得覆盖组织 Security Policy。

# 56. Freshness 与 Verify-before-use

Memory 记录的是某个时间点的观察或规则。以下内容使用前必须重新验证：

```text
文件路径
函数和 Feature Flag
外部 Dashboard / API
当前团队状态
近期 Deadline
代码行为
权限状态
```

如果当前事实与 Memory 冲突：

```text
当前权威事实优先
→ 创建 Conflict / Correction Candidate
→ 旧 Version Supersede、Suspend 或 Review
```

不得一边使用旧 Memory，一边只在回答中含糊提示“可能过时”。

# 57. Procedural Memory 安全边界

Procedural Memory 只提供：

```text
Strategy Hint
Failure Avoidance Hint
Retrieval Hint
Planning Constraint Proposal
```

不能提供：

```text
Security Override
Approval Grant
Budget Increase
Tool Credential
Side-effect Authorization
PlanVersion Activation
SkillDefinition Mutation
```

Agent Core必须独立判断是否采用，并产生 `MemoryUseTrace`。

# 58. Context Validation

提交前必须验证：

```text
Exact Token Count
Mandatory Set Complete
Atomic Group Complete
Security Epoch Current
Source Snapshot Current
No Pending / Revoked / Deleted Memory
Conflict Policy Satisfied
Citation / Evidence Group Complete
Tool Call / Result Pair Complete
Output Contract Present
Content Hash Stable
```

# 59. Observability

至少记录：

```text
memory_capture_intent_count
candidate_count_by_kind_origin
candidate_validation_failure_rate
governance_approval_rate
dedup_rate
conflict_rate
memory_activation_latency
projection_verification_failure_rate
retrieval_precision_at_k
manifest_hit_rate
memory_useful_use_rate
negative_transfer_rate
stale_memory_rate
session_summary_coverage
summary_compression_ratio
context_pack_token_efficiency
protected_set_budget_failure_rate
fidelity_distribution
context_exclusion_reason_distribution
privacy_delete_completion_latency
reflexion_promotion_rate
procedural_suspension_rate
```

# 60. Eval

固定 Eval 至少覆盖：

```text
Long-term factual recall
Multi-session reasoning
Temporal update
Conflict / Supersede
Abstention when memory missing
Session continuity after compact
Important old decision retention
Irrelevant recent message rejection
Tool payload compression
Procedural applicability
Negative transfer
Privacy isolation
Revoked memory exclusion
Compression faithfulness
Context budget determinism
```

只有在固定数据集上证明 Recall、Faithfulness、Privacy、Negative Transfer 和 Token Efficiency 后，才能提升质量状态。

---

# Part VI：目标实现表面

# 61. 目标内部组件

```text
MemoryCaptureService
SessionContinuityService
SessionSummaryExtractor
SessionSummaryValidator
MemoryCandidateExtractor
MemoryCandidateValidator
MemoryScopeResolver
MemoryDeduplicator
MemoryConflictResolver
MemoryGovernanceService
MemoryRecordRepository
MemoryVersionService
MemoryActivationService
MemorySnapshotService
MemoryManifestBuilder
MemoryRetriever
MemoryApplicabilityEvaluator
ContextCandidateCollector
ContextRepresentationFactory
ContextProtectedSetBuilder
ContextBudgetAllocator
ContextPackingService
ContextValidator
ContextPackRepository
ToolObservationNormalizer
CompactionService
RehydrationService
ReflexionValidationService
MemoryConsolidationWorker
MemoryUseRecorder
MemoryUtilityProjector
MemoryProjectionCoordinator
MemoryDeletionService
MemoryReconciliationService
```

# 62. 目标代码目录

```text
src/backend/zuno/memory/
├── domain/
│   ├── candidates.py
│   ├── records.py
│   ├── versions.py
│   ├── summaries.py
│   ├── snapshots.py
│   ├── context.py
│   ├── reflexion.py
│   ├── consolidation.py
│   ├── deletion.py
│   ├── states.py
│   └── failures.py
├── application/
│   ├── capture_service.py
│   ├── session_continuity_service.py
│   ├── governance_service.py
│   ├── retrieval_service.py
│   ├── context_build_service.py
│   ├── compaction_service.py
│   ├── consolidation_service.py
│   ├── deletion_service.py
│   └── reconciliation_service.py
├── ports/
│   ├── repositories.py
│   ├── model_gateway.py
│   ├── security.py
│   ├── knowledge.py
│   ├── agent_core.py
│   ├── tool_runtime.py
│   ├── projections.py
│   └── observability.py
└── adapters/
    ├── persistence/
    ├── vector/
    ├── graph/
    ├── lexical/
    ├── object_store/
    └── runtime/
```

目录是 Target 规格，不代表 Current 已存在。

# 63. PostgreSQL 表

```text
memory_capture_intents
memory_candidates
memory_candidate_validations
memory_governance_decisions
memory_records
memory_versions
memory_source_bindings
memory_conflicts
memory_revocations
session_summary_versions
memory_snapshots
memory_manifest_snapshots
context_pack_versions
context_selection_decisions
context_compression_traces
memory_use_traces
memory_utility_projections
memory_projection_manifests
memory_commit_receipts
memory_deletion_requests
memory_deletion_receipts
memory_reconciliation_decisions
```

## 63.1 关键约束

```text
memory_records:
    UNIQUE tenant/workspace/conflict_key

memory_versions:
    UNIQUE memory_record_id/version_no
    UNIQUE memory_record_id/content_hash

session_summary_versions:
    UNIQUE session_id/source_event_hash

context_pack_versions:
    UNIQUE context_pack_id/version_no
    UNIQUE run_id/step_run_id/content_hash

memory_capture_intents:
    UNIQUE idempotency_key
```

所有表必须包含 Tenant Scope、Created/Updated Time、Generation、Schema Version 和必要 Security Ref。

# 64. Index 与 Projection

## 64.1 Vector

仅保存：

```text
memory_version_id
tenant_id
workspace_id
memory_kind
embedding
embedding_model_ref
effective_time
authority
status projection
source_generation
```

## 64.2 Graph

```text
Entity
EntityFact
MemoryVersion
ABOUT
SUPPORTED_BY
SUPERSEDES
CONFLICTS_WITH
DERIVED_FROM
```

Graph 不成为 Entity Fact 的权威源。

## 64.3 Lexical

用于：

```text
精确术语
错误消息
外部系统名称
项目代号
用户明确措辞
```

## 64.4 Manifest

`MemoryProjectionManifest` 记录：

```text
domain_generation
version_refs
physical_receipts
verification_refs
acceptance_decision
serving_generation
content_hash
```

# 65. Cross-module Contract

至少需要：

```text
BuildContextRequest / ContextPackReceipt
MemoryCaptureIntent / MemoryCommitReceipt
RetrieveMemoryRequest / MemoryRetrievalResult
SessionSummaryUpdateIntent / SessionSummaryReceipt
ReflexionCandidateEnvelope / ReflexionReviewReceipt
MemoryProjectionRequest / IndexWriteReceipt / ProjectionManifest
MemoryDeletionRequest / MemoryDeletionReceipt
MemoryUseEvent
```

所有跨模块消息使用已冻结的 `CrossModuleEnvelopeV1`，携带 Tenant、Workspace、Run、Step、Idempotency、Security Epoch、Deadline、Classification、Payload Hash 和 Schema Hash。

# 66. API Surface

Product Surface 可以提供：

```text
GET /memory
GET /memory/{record_id}
POST /memory/remember
POST /memory/{record_id}/correct
POST /memory/{record_id}/forget
GET /memory/candidates
POST /memory/candidates/{id}/review
GET /sessions/{id}/summary
GET /runs/{id}/context-packs
```

API 只创建 Intent、Review 或 Delete Request，不允许客户端直接指定 Active Version 或绕过 Governance。

# 67. Config

```text
SessionSummaryPolicyVersion
ContextBudgetPolicyVersion
MemoryCapturePolicyVersion
MemoryGovernancePolicyVersion
MemoryRetrievalPolicyVersion
ConsolidationPolicyVersion
RetentionPolicyVersion
```

配置变更必须版本化，并在 Candidate、Summary、ContextPack 和 Trace 中记录生效版本。

# 68. Infrastructure 边界

PostgreSQL 保存领域事实；Object Store 保存大型不可变 Payload；Vector/Graph/Lexical 保存可重建 Projection；Queue 负责后台 Extraction、Projection、Consolidation 和 Delete 工作；Lease/CAS/Outbox 由 Infrastructure 提供 Primitive。

不默认要求 Memory 模块成为独立微服务。

---

# Part VII：规范性矩阵

# 69. Ownership Matrix

| Fact | Owner | Consumer | 禁止 |
| --- | --- | --- | --- |
| ConversationMessage | Product | Memory / Agent Core | Memory 覆盖原文 |
| ExecutionContextSnapshot | Agent Core | Memory Context Build | Memory 修改 Run State |
| SessionSummaryVersion | Memory | Agent Core / Product | Checkpointer 冒充长期 Summary |
| MemoryVersion | Memory | Agent Core / Product | Model 直接激活 |
| Evidence | Knowledge | Memory / Agent Core | Memory 复制权威正文 |
| ToolOutcome | Tool Runtime | Memory / Agent Core | Summary 改写 Outcome |
| Security Epoch | Security | Memory | Memory 自行放宽 |
| ContextPackVersion | Memory | Agent Core / Model Gateway | Consumer 原地修改 |
| Physical Index Receipt | Infrastructure | Memory | Receipt 冒充 Domain Acceptance |
| EvalResult | Observability & Eval | Memory Governance | Memory 伪造质量结论 |

# 70. Compression Decision Matrix

| 输入 | 首选 | 次选 | 最后手段 |
| --- | --- | --- | --- |
| 重复 Metadata | C0 去重 | — | — |
| 大型 Tool Payload | C0 Offload | C1 Digest / Ref | 重新执行 |
| 旧 Conversation | C1 Sliding Tail | C2 Session Summary | C3 Semantic Compact |
| Session Decision | C2 Structured Extract | 保留 Raw Ref | 人工 Review |
| 多个相似 Episode | Embedding Cluster | C3 Consolidation | 保持独立 |
| 冲突 Semantic Fact | Structured Time/Authority | C3 Conflict Proposal | Governance |
| 低价值召回 Memory | C1 F2→F3→F4 | 调整 Retrieval | 不删除 Canonical |
| Mandatory Set 超预算 | 缩小 Step | 更大 Context Model | Abstain |

# 71. Model Decision Matrix

| 决策 | 模型可提议 | 模型可提交 |
| --- | --- | --- |
| Summary 内容 | 是 | 否 |
| MemoryKind | 是 | 否 |
| Relevance | 是 | 否 |
| Conflict Root Cause | 是 | 否 |
| Governance Approval | 否 | 否 |
| Version Activation | 否 | 否 |
| Privacy Delete | 否 | 否 |
| Procedural Promotion | 是 | 否 |
| Security Scope | 否 | 否 |
| Context Mandatory | 否 | 否 |

# 72. Requirement Enforcement Matrix

下面 60 个 Requirement 是本模块 Target 的稳定验收索引。每个 Requirement 必须映射到 Control、Unit/Integration/Fault/E2E Test 和 Evidence。

| Requirement | 规范 | Control ID | Test IDs | Evidence ID |
| --- | --- | --- | --- | --- |
| ARCH-MEM-001 | Working、Session、Long-term 三层生命周期明确 | RC-MEM-001 | MEM-001-UT / MEM-001-IT | EV-MEM-001 |
| ARCH-MEM-002 | 长期仅 Episodic、Semantic、Procedural 三种 | RC-MEM-002 | MEM-002-UT / MEM-002-IT | EV-MEM-002 |
| ARCH-MEM-003 | Entity/Vector/Graph/Lexical 仅为 Projection | RC-MEM-003 | MEM-003-UT / MEM-003-IT | EV-MEM-003 |
| ARCH-MEM-004 | ContextPack 是不可变 read view | RC-MEM-004 | MEM-004-UT / MEM-004-IT | EV-MEM-004 |
| ARCH-MEM-005 | Working State 归 Agent Core | RC-MEM-005 | MEM-005-UT / MEM-005-IT | EV-MEM-005 |
| ARCH-MEM-006 | Session Summary 与原始消息分离 | RC-MEM-006 | MEM-006-UT / MEM-006-IT | EV-MEM-006 |
| ARCH-MEM-007 | 长期写入必须 Candidate/Governance | RC-MEM-007 | MEM-007-UT / MEM-007-IT | EV-MEM-007 |
| ARCH-MEM-008 | MemoryVersion 不可变版本化 | RC-MEM-008 | MEM-008-UT / MEM-008-IT | EV-MEM-008 |
| ARCH-MEM-009 | ContextPackVersion 不可变 | RC-MEM-009 | MEM-009-UT / MEM-009-IT | EV-MEM-009 |
| ARCH-MEM-010 | Source Fact 与 Memory Fact 可追溯 | RC-MEM-010 | MEM-010-UT / MEM-010-IT | EV-MEM-010 |
| ARCH-MEM-011 | Session Summary 增量更新 | RC-MEM-011 | MEM-011-UT / MEM-011-IT | EV-MEM-011 |
| ARCH-MEM-012 | Summary 有 Coverage 和 Source Hash | RC-MEM-012 | MEM-012-UT / MEM-012-IT | EV-MEM-012 |
| ARCH-MEM-013 | Recent Raw Tail 保留 Atomic Group | RC-MEM-013 | MEM-013-UT / MEM-013-IT | EV-MEM-013 |
| ARCH-MEM-014 | Manifest 小型化和懒加载 | RC-MEM-014 | MEM-014-UT / MEM-014-IT | EV-MEM-014 |
| ARCH-MEM-015 | 按类型检索 | RC-MEM-015 | MEM-015-UT / MEM-015-IT | EV-MEM-015 |
| ARCH-MEM-016 | Scope/ACL 在召回前执行 | RC-MEM-016 | MEM-016-UT / MEM-016-IT | EV-MEM-016 |
| ARCH-MEM-017 | Security 先于模型摘要 | RC-MEM-017 | MEM-017-UT / MEM-017-IT | EV-MEM-017 |
| ARCH-MEM-018 | C0–C3 压缩语义明确 | RC-MEM-018 | MEM-018-UT / MEM-018-IT | EV-MEM-018 |
| ARCH-MEM-019 | F0–F4 Context Fidelity | RC-MEM-019 | MEM-019-UT / MEM-019-IT | EV-MEM-019 |
| ARCH-MEM-020 | Tool Payload 优先压缩 | RC-MEM-020 | MEM-020-UT / MEM-020-IT | EV-MEM-020 |
| ARCH-MEM-021 | Protected Set 不可静默删除 | RC-MEM-021 | MEM-021-UT / MEM-021-IT | EV-MEM-021 |
| ARCH-MEM-022 | Context Budget 可解释和确定性 | RC-MEM-022 | MEM-022-UT / MEM-022-IT | EV-MEM-022 |
| ARCH-MEM-023 | Exact Token Validation | RC-MEM-023 | MEM-023-UT / MEM-023-IT | EV-MEM-023 |
| ARCH-MEM-024 | Compact 后 Rehydration | RC-MEM-024 | MEM-024-UT / MEM-024-IT | EV-MEM-024 |
| ARCH-MEM-025 | Summary 不是唯一恢复源 | RC-MEM-025 | MEM-025-UT / MEM-025-IT | EV-MEM-025 |
| ARCH-MEM-026 | Reflexion 单次默认 Episodic | RC-MEM-026 | MEM-026-UT / MEM-026-IT | EV-MEM-026 |
| ARCH-MEM-027 | Procedural 晋升有证据门槛 | RC-MEM-027 | MEM-027-UT / MEM-027-IT | EV-MEM-027 |
| ARCH-MEM-028 | Procedural 仅 Strategy Hint | RC-MEM-028 | MEM-028-UT / MEM-028-IT | EV-MEM-028 |
| ARCH-MEM-029 | Consolidation 不直接删除 Source | RC-MEM-029 | MEM-029-UT / MEM-029-IT | EV-MEM-029 |
| ARCH-MEM-030 | Utility Projection 与 Fact 分离 | RC-MEM-030 | MEM-030-UT / MEM-030-IT | EV-MEM-030 |
| ARCH-MEM-031 | Negative Transfer 可 Suspend | RC-MEM-031 | MEM-031-UT / MEM-031-IT | EV-MEM-031 |
| ARCH-MEM-032 | Freshness 使用前验证 | RC-MEM-032 | MEM-032-UT / MEM-032-IT | EV-MEM-032 |
| ARCH-MEM-033 | Effective Time 与 Observed Time 分离 | RC-MEM-033 | MEM-033-UT / MEM-033-IT | EV-MEM-033 |
| ARCH-MEM-034 | 冲突不静默覆盖 | RC-MEM-034 | MEM-034-UT / MEM-034-IT | EV-MEM-034 |
| ARCH-MEM-035 | Candidate 状态闭合 | RC-MEM-035 | MEM-035-UT / MEM-035-IT | EV-MEM-035 |
| ARCH-MEM-036 | Version 状态闭合 | RC-MEM-036 | MEM-036-UT / MEM-036-IT | EV-MEM-036 |
| ARCH-MEM-037 | Summary 状态闭合 | RC-MEM-037 | MEM-037-UT / MEM-037-IT | EV-MEM-037 |
| ARCH-MEM-038 | Context Build 状态闭合 | RC-MEM-038 | MEM-038-UT / MEM-038-IT | EV-MEM-038 |
| ARCH-MEM-039 | Projection 发布顺序不可跳过 | RC-MEM-039 | MEM-039-UT / MEM-039-IT | EV-MEM-039 |
| ARCH-MEM-040 | Index Receipt 不等于 Active | RC-MEM-040 | MEM-040-UT / MEM-040-IT | EV-MEM-040 |
| ARCH-MEM-041 | Commit Intent 可幂等重放 | RC-MEM-041 | MEM-041-UT / MEM-041-IT | EV-MEM-041 |
| ARCH-MEM-042 | Checkpoint 与 Domain Commit 可协调恢复 | RC-MEM-042 | MEM-042-UT / MEM-042-IT | EV-MEM-042 |
| ARCH-MEM-043 | 并发更新使用 Generation/CAS | RC-MEM-043 | MEM-043-UT / MEM-043-IT | EV-MEM-043 |
| ARCH-MEM-044 | UNKNOWN 先 Reconcile | RC-MEM-044 | MEM-044-UT / MEM-044-IT | EV-MEM-044 |
| ARCH-MEM-045 | Privacy Delete 全投影传播 | RC-MEM-045 | MEM-045-UT / MEM-045-IT | EV-MEM-045 |
| ARCH-MEM-046 | Legal Hold 阻断删除 | RC-MEM-046 | MEM-046-UT / MEM-046-IT | EV-MEM-046 |
| ARCH-MEM-047 | Prompt Injection 不获得权威 | RC-MEM-047 | MEM-047-UT / MEM-047-IT | EV-MEM-047 |
| ARCH-MEM-048 | 隐藏思维链不持久化 | RC-MEM-048 | MEM-048-UT / MEM-048-IT | EV-MEM-048 |
| ARCH-MEM-049 | 模型只产生 Proposal | RC-MEM-049 | MEM-049-UT / MEM-049-IT | EV-MEM-049 |
| ARCH-MEM-050 | 弱模型默认摘要、强模型复杂整合 | RC-MEM-050 | MEM-050-UT / MEM-050-IT | EV-MEM-050 |
| ARCH-MEM-051 | Model Upgrade 有明确链路 | RC-MEM-051 | MEM-051-UT / MEM-051-IT | EV-MEM-051 |
| ARCH-MEM-052 | Context 选择全量 Trace | RC-MEM-052 | MEM-052-UT / MEM-052-IT | EV-MEM-052 |
| ARCH-MEM-053 | MemoryUseTrace 关联 Outcome/Eval | RC-MEM-053 | MEM-053-UT / MEM-053-IT | EV-MEM-053 |
| ARCH-MEM-054 | 固定 Eval 覆盖长期和压缩质量 | RC-MEM-054 | MEM-054-UT / MEM-054-IT | EV-MEM-054 |
| ARCH-MEM-055 | Canonical Store 使用 PostgreSQL | RC-MEM-055 | MEM-055-UT / MEM-055-IT | EV-MEM-055 |
| ARCH-MEM-056 | 大 Payload 使用 Object Store Ref | RC-MEM-056 | MEM-056-UT / MEM-056-IT | EV-MEM-056 |
| ARCH-MEM-057 | Vector/Graph/Lexical 可重建 | RC-MEM-057 | MEM-057-UT / MEM-057-IT | EV-MEM-057 |
| ARCH-MEM-058 | CrossModuleEnvelope 字段贯通 | RC-MEM-058 | MEM-058-UT / MEM-058-IT | EV-MEM-058 |
| ARCH-MEM-059 | Target 与 Current 状态源分离 | RC-MEM-059 | MEM-059-UT / MEM-059-IT | EV-MEM-059 |
| ARCH-MEM-060 | Production Ready 需要完整工程证据 | RC-MEM-060 | MEM-060-UT / MEM-060-IT | EV-MEM-060 |

---

# Part VIII：测试与完成证据

# 73. Unit Tests

```text
Candidate Schema / Type / Origin
Exact Dedup and Conflict Key
Effective Time Selection
Summary Coverage
Atomic Tail Boundary
Fidelity Conversion
Protected Set
Budget Packing Determinism
Token Count
State Transition Guards
Idempotency Key
Utility Projection
Prompt Injection Classification
```

# 74. Integration Tests

```text
Product Message → SessionSummaryVersion
Agent RunOutcome → MemoryCandidate
Candidate → Governance → MemoryVersion
MemoryVersion → Projection → Activation
Task Start → Manifest → Lazy Retrieval → ContextPack
Compact → Rehydrate → Resume
Reflexion → Episodic → Procedural Promotion
User Correction → Supersede
Security Epoch Change → Context Build Reject
Privacy Delete → All Projection Hidden
```

# 75. Fault Tests

```text
Summary Worker 崩溃
Candidate Commit 后 Checkpoint 崩溃
Index Write 后 ACK 前崩溃
Projection Partial / UNKNOWN
CAS Cutover Conflict
Context Build 中 Security Epoch 变化
Consolidation 并发
Delete Worker 中途崩溃
Backup / Legal Hold 阻断
```

# 76. E2E Scenarios

1. 长会话超过模型窗口后，Goal、已确认决定、关键错误和下一步仍可恢复。
2. 旧 Tool Payload 被压缩为 Ref，但不可逆副作用 Outcome 保留。
3. 用户明确偏好经 Governance 成为 Semantic Memory，并在新 Session 被召回。
4. 单次失败只形成 Episodic；多次验证后才形成 Procedural Hint。
5. Procedural Hint 产生负迁移后自动 Suspend，后续不再召回。
6. Revoked / Deleted Memory 在所有 Projection、Manifest 和 ContextPack 中消失。
7. 跨 Workspace 查询无法看到其他 Scope 的 Metadata 或正文。
8. Context Mandatory Set 超预算时明确失败，不删除 Security Policy。

# 77. Eval Gate

至少建立固定 Case Set，报告：

```text
Memory Recall Precision / Recall
Temporal Update Accuracy
Conflict Resolution Accuracy
Session Continuity Accuracy
Compression Faithfulness
Required Fact Retention
Irrelevant Context Rejection
Token Reduction
Procedural Transfer Success
Negative Transfer Rate
Privacy Leak Rate
Deletion Propagation Completeness
```

没有 fixed benchmark、Trace 和 measured result 时，只能写：

```text
design available
implementation available
measurement blocked
quality not yet proven
```

不得声明 production ready。

# 78. 完成证据

Target 变为 Current 至少需要：

```text
领域对象与 Migration
Canonical PostgreSQL Repository
Unit Test
Integration Test
Fault Injection
E2E
ContextPack Trace
MemoryUseTrace
Privacy Delete Proof
Fixed Eval
Restart / Recovery Evidence
文档与镜像同步
Verifier 和 CI
```

单独存在类名、表名、Mock、Prompt、Vector Collection 或 Markdown 文档，不构成完成证据。

# 79. Program 边界

本文不定义：

```text
具体 Phase
旧表回填顺序
Dual-write 周期
Cutover 日期
Feature Flag 百分比
当前实现文件是否保留
```

后续 Program 必须从 `ARCH-MEM-NNN` Requirement Registry 选择 Requirement，明确 Owner、Migration、测试、Rollback 和 Evidence，不得自行改变本文架构原则。

# 80. 设计依据与取舍

本 Target 吸收以下成熟思想，但不照搬其产品实现：

```text
认知 Agent 架构：
    Working 与 Episodic / Semantic / Procedural 的语义分离。

Virtual Context Management：
    Context Window 与外部持久存储分离，按需换入。

Reflection / Reflexion：
    当前质量判断与跨任务经验候选分离。

长期记忆评测：
    Session、时间更新、冲突、拒答和多会话推理必须独立评估。

工程型 Agent：
    小型 Manifest 常驻、Topic 内容懒加载、
    Session Continuity 与分级 Compact、Rehydration 分离。

企业治理：
    Candidate、Version、Security、Consent、Retention、
    Privacy Delete、Audit 和 Recovery 为强制边界。
```

最终原则：

> Working 负责当前执行，Session 负责连续性，Long-term 负责未来复用；Context 压缩只改变读取视图，Memory Consolidation 才产生新的长期版本；弱模型负责结构化，强模型负责复杂推理，确定性系统和 Governance 决定什么能够成为事实。

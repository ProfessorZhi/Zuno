# 07 Capability / Skill

updated: 2026-07-14
status: normative-target-module-architecture
module_number: 07
formal_path: `docs/modules/07-capability-skill.md`
agent_mirror: `.agent/modules/07-capability-skill.md`

> 本文是 Zuno 第 07 个逻辑模块——Capability / Skill——唯一的正式 Target 架构主设计。
>
> 本文只描述理想目标架构、规范性 Contract 和实现规格，不把当前代码、历史 PHASE、短期迁移或运行证据写成 Target 事实。Current、Gap、Measurement 和完成状态由 `docs/status/production-readiness.md` 维护；Current → Target 的实现、迁移、切流和收口计划必须进入 `.agent/programs/`。

## 0. 文档边界与规范优先级

本文统一承载：

```text
问题、目标与概念架构
Capability / Skill / Provider / Tool 的完整运行流程
版本、生命周期、状态机、失败与恢复
CapabilityProviderBinding 与 ProviderConformance
Availability、Selection、Fallback 与 StepFeasibility 交接
Skill 渐进式加载与供应链治理
Connector Pack、API、CLI、MCP 与通用 Adapter 边界
领域对象、Typed Contract、目标代码、数据库、事务与测试规格
Requirement、Control、Test 与 Evidence 映射
```

文档边界：

```text
docs/modules/07-capability-skill.md
    唯一正式 Target 事实源。

.agent/modules/07-capability-skill.md
    字节级一致的 Agent 镜像，不是第二份独立架构。

docs/status/production-readiness.md
    Current、Gap、Measurement、Blocked 和完成证据状态。

.agent/programs/
    Current → Target 的实现、迁移、切流和收口计划。

docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
    已确认的共享 Owner、Envelope、Security Epoch、Receipt、Failure 和恢复边界。
```

规范优先级：

```text
全局架构原则与已接受 ADR
→ Wave 1 Cross-module Contract Registry
→ 本模块 Target 架构
→ 已确认 Program
→ 代码、Migration 与运行配置
```

本文内部规范层级：

```text
Part I–III
    问题、概念、完整流程和状态恢复的说明性视图。

Part IV–VII
    字段、Owner、状态转换、Policy、持久化和控制矩阵的规范性视图。

Part VIII
    Requirement、测试和完成证据。
```

说明性视图不得覆盖规范性 Contract；发生冲突时按 Part IV–VII 解释，并在同一轮文档修改中消除冲突。


# Part I：定位、术语与概念架构

# 1. 为什么需要 Capability / Skill

企业 Agent 接入的不是一小组固定函数，而是持续变化的知识查询、Memory、Ingestion、Artifact、API、CLI、SDK、MCP、Browser、Database、RPC 和企业工作流。若把所有接入对象直接作为 Tool Schema 暴露给模型，会产生：

```text
Tool 数量和 Schema 持续膨胀
同名 Tool 语义不同、异名 Tool 语义相同
Skill 直接绑定某个 Provider，升级或切换困难
MCP listChanged、OpenAPI 更新或 CLI 版本变化使 Active Plan 漂移
模型把“目录可用”误判为“当前已授权、可执行”
不同 Tenant、App、账号和区域被错误互换
副作用执行 UNKNOWN 后跨 Provider 重试，造成重复效果
Provider 自报能力与真实输入、输出、幂等和 Reconciliation 行为不一致
外部 Skill、Connector Pack 或 Tool Description 成为权限放大与供应链入口
```

一句话定义：

> Capability / Skill 是 Zuno 的能力语义控制面和方法包目录。它管理“系统能做什么、任务应如何做、哪些实现可以提供所需能力、当前哪些候选可进入计划、为什么选择或拒绝某个候选”，但不真实执行 Tool、不批准权限、不消费 Secret、不激活 Plan、不提交外部效果。

# 2. 核心术语

```text
Function Calling
    模型表达结构化 Action Proposal 的协议或语言，不是执行器。

CapabilityDefinition
    稳定的业务能力逻辑身份，例如 collaboration.message.send。

CapabilityVersion
    某一版本能力的 Canonical Input/Output、风险、约束、依赖和验收语义。

CapabilityRequirement
    Skill 或 Plan Step 对业务能力、版本、特性和环境的要求。

SkillDefinition
    稳定的方法包逻辑身份。

SkillVersion
    不可变发布版本，包含 Metadata、Instruction、ResourceManifest、
    CapabilityRequirement、Constraint 和 AcceptanceCriteria。

ToolCapabilityDescriptor
    07 面向 Discovery/Selection 的可发现 Tool 能力描述。

ToolDefinitionRef
    指向 08 Tool Runtime 可执行 ToolDefinitionVersion 的版本化引用。

CapabilityProviderBinding
    精确 CapabilityVersion 与某个 Provider 实现之间的语义和 Contract 映射。

ProviderConformanceRecord
    证明 Binding 在输入、输出、副作用、幂等、错误和恢复方面是否满足 Capability Contract。

CapabilityAvailabilitySnapshot
    某个时间点可用于规划的候选能力与 Provider 投影。

CapabilitySelectionResult
    07 提交的不可变候选选择事实，记录过滤、评分、选中项和 fallback。

ProviderInstanceRef
    指向 08 拥有的业务连接实例，例如某 Tenant、App、Region 和 Identity Mode。

RuntimeEndpointReplicaRef
    08 在同一业务实例池内选择的技术执行副本。

Connector Pack
    可签名、可版本化的安装分发包；包含各模块的声明式配置和扩展，
    本身不是运行时领域事实源。
```

必须保持：

```text
Skill != Capability
Capability != Tool
ToolCapabilityDescriptor != ToolDefinition
Availability != Authorization
Availability != Execution Readiness
Selection != StepFeasibility
Selection != Plan Activation
MCP != Capability
API / CLI / SDK != Capability
Connector Pack != Runtime Authority
```

# 3. Agent 可规划的能力范围

07 可以描述以下业务能力类型：

| CapabilityKind | 示例 | Runtime / 事实 Owner |
| --- | --- | --- |
| `KNOWLEDGE` | 检索、Graph Traversal、Evidence、Citation Check | 03 Knowledge |
| `MEMORY_CONTEXT` | Memory Recall、Context Assembly、Memory Candidate | 05 Memory & Context |
| `INGESTION` | Parse、OCR、Reprocess、等待 Indexable Snapshot | 02 Input / Ingestion |
| `TOOL_ACTION` | API、CLI、MCP Tool、Browser、Filesystem、Database、SaaS | 08 Tool Runtime |
| `ARTIFACT` | 报告、表格、演示、代码补丁、导出 | 对应 Artifact / Agent Core 生命周期 |
| `EXTERNAL_WORKFLOW` | 远端 Job、企业审批流、异步工作流 | 对应领域 Runtime + Agent Interrupt |
| `DOMAIN_OPERATION` | 由其他领域模块提供的受控命令或查询 | 对应领域 Owner |

模型能力不作为 07 的普通 Tool Catalog 真相。04 Model Gateway 拥有 `ModelCapabilityProfile`；07 的 Skill/Requirement 可以声明需要结构化输出、视觉输入或 Tool Calling，但具体 Model Routing 由 04 与 06 协作。

以下对象不是业务 Capability：

```text
Security Gate
Approval Decision
Budget
Trace / Metric / Eval
Checkpoint
Queue / Lease / Fencing
IdempotencyClaim
Plan / Step / RunOutcome
```

# 4. 模块职责

07 负责：

```text
CapabilityDefinition / CapabilityVersion 生命周期
CapabilityRequirement 与 CompatibilityConstraint
SkillDefinition / SkillVersion 生命周期
SkillMetadata / SkillInstruction / SkillResourceManifest
Skill Discovery 与渐进式加载
ToolCapabilityDescriptor 与 ToolDefinitionRef
CapabilityProviderBinding Proposal、验证、激活和撤销
ProviderConformanceRecord
CapabilityAvailabilitySnapshot
CapabilitySelectionResult 与候选拒绝原因
Provider Selection Policy 与 fallback 顺序
Portable Capability 与 Provider-native Capability
Connector Pack 中 07 所属的 Capability / Skill 资产
版本、兼容、Snapshot Pinning、Revocation Propagation
Discovery / Load / Binding / Availability / Selection 事件
```

07 不负责：

```text
TaskContract、Plan、Step、ActionProposal 或 ControlDecision
ToolDefinition、PreparedToolAction、ToolAttempt、EffectReceipt 或 EffectReconciliation
真实 API、CLI、MCP、SDK、Browser、RPC 或数据库执行
Authorization、Approval、CredentialVersion、SecretLease 或 Security Epoch
Model Provider、ModelInvocation、Usage 或 RoutingDecision
Knowledge Evidence、Memory Commit、Ingestion Snapshot 或 Artifact Publication 的领域事实
Queue、Lease、Fencing、IdempotencyClaim、AuditPersistenceReceipt
最终回答、RunOutcome 或产品展示
```

# 5. Cross-module Ownership

| 事实 / Contract | Canonical Owner | 07 可以 | 07 禁止 |
| --- | --- | --- | --- |
| Task、Goal、Plan、Step、ActionProposal、StepFeasibilityDecision | 06 Agent Core | 提供 Requirement、Snapshot、Selection | 激活或修改 Plan |
| KnowledgeVersion、Evidence、CitationLineage | 03 Knowledge | 描述 Knowledge Capability、引用 Port | 伪造 Evidence 或查询内部索引 |
| ModelCapabilityProfile、RoutingDecision、ModelAttempt | 04 Model Gateway | 声明模型能力要求 | 选择具体 Provider/Model 并提交路由事实 |
| ContextPack、MemoryVersion、MemoryCandidate | 05 Memory & Context | 描述 Memory/Context Capability | 直接写长期 Memory |
| ToolDefinition、ProviderInstance、PreparedToolAction、ToolAttempt、EffectReceipt、EffectReconciliation | 08 Tool Runtime | 消费 Descriptor/Health Projection 和保存 Ref | 连接、执行或确认外部效果 |
| Authorization、Approval、CredentialVersion、Revocation、EffectiveSecurityEpoch | 09 Security | 传播约束和引用决定 | 自行授权、批准或持有 Secret |
| Trace、Metric、EvalResult、AuditEvent | 10 Observability & Eval | 产生结构化源事件 | 修改 Eval 或 Audit 接受事实 |
| Transaction、Outbox、Object Store、Queue、Lease、Fencing、SecretLease、IdempotencyClaim | 11 Infrastructure | 使用基础设施 Port | 把物理 Receipt 冒充业务成功 |

# 6. 架构不变量

```text
INV-CAP-01  Capability 使用稳定业务语义身份，不以 Provider Tool 名称作为主身份。
INV-CAP-02  Skill 只描述方法、约束和验收，不直接执行脚本或外部动作。
INV-CAP-03  模型只产生 Proposal，不激活 Definition、Version、Binding、Selection 或 Tool。
INV-CAP-04  Requirement 可以声明兼容范围；Plan 与 Action 必须固定精确版本。
INV-CAP-05  07 选择业务 Provider Instance 或 Pool；08 只在同一业务身份池内选 Replica。
INV-CAP-06  Plan 固定 Planning Availability Snapshot；每个 Action 执行前重新 Preflight。
INV-CAP-07  AVAILABLE 只表示可成为候选，不表示已授权、已批准或可立即执行。
INV-CAP-08  Skill allowed tools/capabilities 只能缩小候选，不能扩大 Security 授权。
INV-CAP-09  Tool Inventory 或 Schema 变化创建新 Version/Generation，不原地改写。
INV-CAP-10  副作用 UNKNOWN 时禁止跨 Provider 盲目 fallback。
INV-CAP-11  核心不硬编码飞书、Slack、GitHub、Jira 等 Provider。
INV-CAP-12  通用 Protocol Adapter + 声明式 Tool Manifest + Connector Pack + 少量 Custom Extension。
INV-CAP-13  Cache、搜索索引和 Health 只是 Projection，不是 Definition/Revocation 事实源。
INV-CAP-14  所有发布、选择、撤销和恢复结果可审计、可版本化、可重放。
INV-CAP-15  Target 文档完成不代表实现、质量或生产就绪。
```

# 7. 逻辑架构

```text
                              06 Agent Core
                                   │
          SkillDiscovery / CapabilityRequirement / Selection Request
                                   │
                                   ▼
                      07 Capability / Skill
┌──────────────────┬────────────────────┬────────────────────┬──────────────────┐
│ Skill Catalog    │ Capability Catalog │ Binding & Conform. │ Availability &   │
│ Version / Load   │ Version / Req.     │ Provider Mapping   │ Selection        │
└──────────────────┴────────────────────┴────────────────────┴──────────────────┘
                                   │
                      ToolDefinitionRef / DomainPortRef
                                   │
          ┌──────────────┬─────────┴─────────┬───────────────┐
          ▼              ▼                   ▼               ▼
      03 Knowledge    05 Memory          08 Tool Runtime  02 Ingestion
                                              │
                          HTTP / CLI / MCP / SDK / RPC / Browser
```


# Part II：完整运行流程

# 8. 总体流程

```text
TaskAnalysisResult
→ Skill Discovery
→ Progressive Skill Loading
→ Capability Requirement Expansion
→ Candidate Discovery
→ Capability Availability Capture
→ Deterministic Hard Filtering
→ Candidate Ranking
→ CapabilitySelectionResult
→ Agent Core Plan Validation / StepFeasibilityDecision
→ ActionProposal
→ 08 PreparedToolAction
→ 09 Authorization / Approval
→ 11 Audit / Idempotency / Secret Lease primitives
→ 08 ToolAttempt / EffectReceipt / Reconciliation
→ 06 Continue / Retry / Fallback / Replan / Wait / Block
```

07 的终点是版本化 `CapabilitySelectionResult` 和引用，不是 Tool Observation。

# 9. Skill Discovery

```text
SkillDiscoveryRequest
→ Resolve visibility scope
→ Read active SkillMetadata projection
→ Filter lifecycle / tenant / workspace / trust / compatibility
→ Score task applicability
→ Return SkillDiscoveryResult
→ Agent Core chooses pinned / automatic / no-skill path
```

`SkillDiscoveryRequest` 至少包含：

```text
task_analysis_ref
goal_version_ref
tenant_id
workspace_id
principal_context_ref
requested_skill_refs
required_output_contract_ref
risk_ceiling
data_classification
token_budget
deadline_at
```

`SkillDiscoveryResult` 必须记录：

```text
discovery_result_id
candidate_skill_version_refs
selected_or_recommended_refs
rejected_candidates[]
no_skill_allowed
policy_snapshot_ref
ranking_method
created_at
valid_until
trace_id
```

Pinned Skill 不可用时，07 返回显式原因；是否等待、采用替代 Skill 或 Replan 由 06 决定。

# 10. Skill 渐进式加载

加载阶段：

```text
METADATA_ONLY
→ INSTRUCTION_REQUESTED
→ INSTRUCTION_READY
→ RESOURCE_PLAN_CREATED
→ RESOURCE_LOADING
→ READY
```

失败/失效：

```text
RESOURCE_MISSING
RESOURCE_HASH_MISMATCH
POLICY_DENIED
VERSION_STALE
VERSION_REVOKED
CONTENT_TOO_LARGE
UNSUPPORTED_MEDIA
QUARANTINED
DEADLINE_EXCEEDED
```

加载原则：

1. 启动和广域 Discovery 只读取 `SkillMetadata`。
2. Skill 成为候选后才读取 `SkillInstruction`。
3. 资源按任务需要、数据等级、Token Budget 和 Resource Manifest 加载。
4. 可执行脚本不作为普通 Resource 执行；必须解析为 `ToolDefinitionRef` 并进入 08。
5. 每次 Load 固定 SkillVersion、Resource Hash、Policy 和 Budget。
6. 大型 Resource 以 Ref 进入 Context，不把完整内容复制进 Graph State。
7. `SkillLoadResult` 可被缓存，但 Reuse 前必须校验 Version、Hash、Scope 和 Security Epoch。

# 11. Capability Requirement Expansion

Skill、Planner 或确定性策略产生的 Requirement 必须归一为：

```text
CapabilityRequirementSet
├── REQUIRED
├── ONE_OF
├── OPTIONAL
├── PROHIBITED
└── FALLBACK_ALLOWED
```

每个 Requirement 至少声明：

```text
capability_semantic_ref
version_range
required_features
input_contract_ref
output_contract_ref
side_effect_ceiling
required_tenant / workspace / region
data_residency
identity_mode
resource_scope
trust_floor
idempotency_requirement
reconciliation_requirement
latency / cost class
fallback_policy
```

`required_capabilities` 表示业务能力需求；`allowed_tools` 仅表示候选范围缩小。二者不能混为一列字符串。

# 12. Provider Inventory 与 Binding Onboarding

接入阶段：

```text
管理员安装或配置 Connector / Provider
→ 08 创建 ToolProviderDefinition / ToolProviderInstance
→ 08 发现或导入 ToolDefinitionVersion
→ 08 发布 ToolInventoryGeneration
→ 07 创建 ToolCapabilityDescriptor
→ 人工 / 规则 / 模型生成 CapabilityProviderBindingProposal
→ Schema Mapping Validation
→ Provider Conformance Test
→ Risk-based Governance Gate
→ CapabilityProviderBinding ACTIVE
```

Proposal 来源：

```text
CURATED
RULE_DERIVED
MODEL_PROPOSED
IMPORTED_CONNECTOR_PACK
```

任何来源都不能绕过验证。

# 13. CapabilityProviderBinding 激活

Binding 激活 Gate：

```text
Stable CapabilityVersion exists
ToolDefinitionRef exact version exists
Canonical input mapping valid
Canonical output mapping valid
Feature coverage explicit
SideEffectClass aligned
Idempotency behavior verified
Effect Receipt strategy verified
Reconciliation behavior verified
Security scope mapping reviewed
Provider trust and provenance valid
Contract Test passed
Required approval completed
```

Provider 只支持 Capability 的部分特性时，Binding 必须声明 Coverage Matrix，不能标记为完全等价。

# 14. Capability Availability Capture

```text
CapabilityRequirementSet
→ Resolve active CapabilityVersion
→ Resolve ACTIVE Binding candidates
→ Read Tool/Domain Provider health projections
→ Check compatibility, visibility, trust and revocation
→ Calculate freshness and TTL
→ Commit CapabilityAvailabilitySnapshot
```

Snapshot Entry 状态：

```text
AVAILABLE
DEGRADED
CONFIG_REQUIRED
UNAVAILABLE
VERSION_INCOMPATIBLE
POLICY_CONSTRAINED
REVOKED
UNKNOWN
```

`AVAILABLE` 的含义仅是“可进入当前规划候选集”。

# 15. Capability Selection

选择分两阶段。

确定性硬过滤：

```text
CapabilityVersion compatibility
Input / Output Contract
Required features and coverage
Tenant / Workspace / Region / Residency
Provider trust and lifecycle
SideEffectClass and risk ceiling
Idempotency and Reconciliation support
Snapshot freshness
ProviderInstance visibility
ToolDefinition exact version and schema hash
```

候选排序：

```text
semantic fit
conformance score
reliability
latency
cost
context schema size
organization preference
recent failure rate
provider diversity
user preference
```

模型可以提供偏好 Proposal，但不得覆盖硬约束。

# 16. StepFeasibility 交接

```text
07 CapabilitySelectionResult
+ 07 CapabilityAvailabilitySnapshot
+ 04 ModelCapabilityProfile
+ 09 Security Decision
+ 06 Budget / Deadline / Resource Claim / Step Contract
→ 06 StepFeasibilityDecision
```

07 不提交 `executable=true/false` 的最终 Step 决定。它只报告：

```text
selected_binding_ref
selected_provider_instance_or_pool_ref
fallback_binding_refs
unmet_capability_requirements
stale_or_revoked_refs
constraint_rejection_reasons
```

# 17. Fallback、Wait 与 Replan

| 情况 | 07 输出 | 最终 Control Owner |
| --- | --- | --- |
| 同 Capability 的兼容 Provider 暂时不可用 | fallback candidates | 06 |
| Binding 不满足 Output Contract | reject candidate | 06 |
| Skill Resource 暂时读取失败 | retry/load failure | 06 选择 wait/retry |
| Capability 永久撤销 | invalidation + alternative candidates | 06 Replan |
| Security deny | 保留候选事实，不改写授权 | 06 Wait/Replan/Abort |
| ToolAttempt `UNKNOWN` | 不提供可立即重试 fallback | 08 Reconcile，06 Wait/Abort |
| Tool 已确认 `NOT_EXECUTED` | 可重新计算 fallback | 06 |
| 新 Provider 改变 Tenant、App、Region 或 Effect Domain | 要求重新 Selection/Prepare/Auth | 06/09 |

Fallback 不得改变 Step Output Contract、风险上限、Tenant、数据驻留或副作用语义。

# 18. Connector Pack 与 Provider 无关核心

核心代码不得出现：

```python
if provider == "feishu":
    ...
```

目标扩展模型：

```text
Zuno Core
├── Capability / Skill contracts
├── Generic Provider descriptors
├── Generic Binding / Conformance
├── Generic Protocol adapters
└── Connector Extension SPI

Connector Packs
├── Collaboration Provider Pack
├── Source Control Provider Pack
├── Ticketing Provider Pack
├── Internal Enterprise Pack
└── Provider-native Pack
```

一个 Connector Pack 可以包含：

```text
connector manifest
07 capability definitions or mappings
07 optional skills
08 provider definitions
08 tool manifests
09 security scope mappings
contract tests
result mappings
reconciliation strategy refs
custom extension refs
```

激活后，各部分成为各模块拥有的独立版本化事实。Connector Pack 本身不能继续充当运行时权威来源。

# 19. Function Calling 与模型可见性

模型可见信息采用四级披露：

```text
Level 0  Capability Metadata
Level 1  Skill Metadata / ToolCapabilityDescriptor summary
Level 2  Selected SkillInstruction / candidate Tool Schema
Level 3  PreparedToolAction reference only; executable details留在 08
```

禁止向模型暴露：

```text
Secret Material
Credential Lease
完整内部 Provider 配置
未授权 Tool Schema
任意 Shell 命令模板
隐藏审批逻辑
完整审计 Payload
```


# Part III：状态、失败、恢复与一致性

# 20. 生命周期总览

```text
CapabilityDefinition
└── CapabilityVersion[]

SkillDefinition
└── SkillVersion[]
    └── SkillResourceManifest

CapabilityVersion
└── CapabilityProviderBinding[]
    └── ProviderConformanceRecord[]

Planning request
└── CapabilityAvailabilitySnapshot
    └── CapabilitySelectionResult
```

Definition 是稳定逻辑身份；Version、Snapshot、Result 和 Conformance 提交后不可原地改写。

# 21. CapabilityVersion 状态机

状态：

```text
DRAFT
VALIDATING
PUBLISHED
ACTIVE
DEPRECATED
SUSPENDED
REVOKED
RETIRED
```

| From | Trigger | Guard | To | 同事务事实 |
| --- | --- | --- | --- | --- |
| `DRAFT` | `SUBMIT_VALIDATION` | Schema、Owner、Contract 完整 | `VALIDATING` | Transition + ValidationRequest |
| `VALIDATING` | `VALIDATION_PASS` | Contract 与兼容检查通过 | `PUBLISHED` | Version + Event |
| `PUBLISHED` | `ACTIVATE` | 同逻辑身份 Active Pointer CAS 成功 | `ACTIVE` | ActivePointer + Outbox |
| `ACTIVE` | `DEPRECATE` | Replacement 可选、Migration Note 完整 | `DEPRECATED` | DeprecationRecord |
| `ACTIVE/DEPRECATED` | `SUSPEND` | 临时风险或质量问题 | `SUSPENDED` | SuspensionRecord |
| 任意非终态 | `REVOKE` | Security/Owner 决定有效 | `REVOKED` | RevocationRecord + InvalidationEvent |
| `DEPRECATED/REVOKED` | `RETIRE` | Retention/引用保护满足 | `RETIRED` | Tombstone |

`REVOKED` 和 `RETIRED` 不可回到 `ACTIVE`；修复必须创建新 Version。

# 22. SkillVersion 状态机

状态：

```text
DRAFT
VALIDATING
APPROVAL_PENDING
PUBLISHED
ACTIVE
DEPRECATED
QUARANTINED
REVOKED
RETIRED
```

`QUARANTINED` 用于来源、签名、恶意 Instruction、资源完整性或权限放大风险。解除隔离必须重新验证并创建新 Governance Decision，不得直接改回 Active。

# 23. CapabilityProviderBinding 状态机

状态：

```text
DISCOVERED
DRAFT
MAPPING_PROPOSED
VALIDATING
APPROVAL_PENDING
ACTIVE
DEGRADED
SUSPENDED
REVOKED
RETIRED
```

| From | Trigger | Guard | To |
| --- | --- | --- | --- |
| `DISCOVERED` | `CREATE_DRAFT` | ToolDefinitionRef 存在 | `DRAFT` |
| `DRAFT` | `PROPOSE_MAPPING` | CapabilityVersion 存在 | `MAPPING_PROPOSED` |
| `MAPPING_PROPOSED` | `START_VALIDATION` | Mapping 可解析 | `VALIDATING` |
| `VALIDATING` | `CONFORMANCE_PASS` | 必要 Test 全通过 | `APPROVAL_PENDING` 或 `ACTIVE` |
| `APPROVAL_PENDING` | `APPROVED` | Approver/Policy 有效 | `ACTIVE` |
| `ACTIVE` | `HEALTH_DEGRADED` | 仍满足最低 Contract | `DEGRADED` |
| `DEGRADED` | `HEALTH_RECOVERED` | Fresh validation | `ACTIVE` |
| 任意可用态 | `SUSPEND/REVOKE` | Owner/Security 决定 | `SUSPENDED/REVOKED` |

模型不能触发 `APPROVED` 或 `ACTIVE`。

# 24. ProviderConformanceRecord 状态机

```text
PENDING
RUNNING
PASSED
FAILED
BLOCKED
EXPIRED
SUPERSEDED
```

Conformance Record 是不可变结果；重新测试创建新 Record。Binding 只能引用未过期、与精确 ToolDefinitionVersion 和测试套件版本匹配的 `PASSED` Record。

# 25. SkillLoad 状态机

```text
REQUESTED
METADATA_READY
INSTRUCTION_READY
RESOURCE_PLANNED
RESOURCE_LOADING
READY
FAILED
INVALIDATED
```

资源缺失、Hash 不匹配、Version 撤销、Security Epoch 失效或 Scope 变化会进入 `FAILED` 或 `INVALIDATED`，不得返回部分内容冒充 READY。

# 26. CapabilityAvailabilitySnapshot 状态机

```text
CAPTURING
READY
PARTIAL
STALE
INVALIDATED
EXPIRED
```

`PARTIAL` 表示部分 Candidate 无法解析，但 Snapshot 仍满足 Policy 允许的最低完备度；Snapshot 必须显式列出缺失项。`STALE` 可用于低风险重新规划参考，不能直接用于高风险 Action Prepare。

# 27. CapabilitySelectionResult Validity

```text
VALID
STALE
REVOKED
SUPERSEDED
UNKNOWN_VALIDITY
```

SelectionResult 不修改自身状态；通过追加 `CapabilityResultValidityRecord` 表达变化。

# 28. Revocation 与失效传播

```text
SkillVersion REVOKED
→ SkillLoadResult REVOKED
→ CapabilityRequirementSet INVALIDATED
→ CapabilitySelectionResult STALE/REVOKED
→ Agent Core StepFeasibility 重新计算
→ Wait / Fallback / Replan / Block

ToolDefinitionVersion REVOKED
→ Binding REVOKED
→ Availability Entry REVOKED
→ SelectionResult REVOKED
→ 08 拒绝 Prepare 或 Execute
→ 06 ControlDecision

ProviderInstance REVOKED
→ ToolExposure invalid
→ Availability invalidated
→ 新执行 fail-closed
```

已经成功完成的历史结果保留审计；是否污染下游结果由 06 的 ResultValidity 和 AnswerPolicy 决定。

# 29. Failure Namespace

07 统一使用 `CAP_*`，Skill 子类使用 `CAP_SKILL_*`。不得复用 `TOOL_*` 表示目录、Binding 或 Selection 失败。

```text
CAP_DEFINITION_NOT_FOUND
CAP_VERSION_UNSUPPORTED
CAP_VERSION_REVOKED
CAP_REQUIREMENT_UNSATISFIED
CAP_BINDING_NOT_FOUND
CAP_BINDING_UNVERIFIED
CAP_CONFORMANCE_FAILED
CAP_PROVIDER_TRUST_UNSATISFIED
CAP_AVAILABILITY_STALE
CAP_AVAILABILITY_INCOMPLETE
CAP_NO_COMPATIBLE_CANDIDATE
CAP_SELECTION_CONSTRAINT_UNSATISFIED
CAP_RESULT_VALIDITY_UNKNOWN
CAP_TOOL_SCHEMA_CHANGED
CAP_PROVIDER_INSTANCE_ROUTE_INVALID
CAP_CONNECTOR_PACK_INVALID
CAP_RECOVERY_INCOMPLETE

CAP_SKILL_NOT_FOUND
CAP_SKILL_VERSION_REVOKED
CAP_SKILL_QUARANTINED
CAP_SKILL_RESOURCE_MISSING
CAP_SKILL_RESOURCE_HASH_MISMATCH
CAP_SKILL_LOAD_BUDGET_EXCEEDED
CAP_SKILL_POLICY_CONFLICT
CAP_SKILL_SCRIPT_RUNTIME_BYPASS
```

# 30. Failure Decision Matrix

| Failure | Retry | Reload / Revalidate | Fallback | Replan | Human / Security |
| --- | --- | --- | --- | --- | --- |
| Registry/DB transient | 07 | 否 | 否 | 否 | 超限告警 |
| Snapshot TTL expired | 否 | Capture 新 Snapshot | 可 | 可能 | 否 |
| Skill Resource transient | 07 | Load 新 Attempt | Skill fallback 可 | 可能 | 按 Policy |
| Resource Hash mismatch | 否 | 新 Version/重新发布 | 否 | 是 | Quarantine |
| Binding Conformance failed | 否 | 修复 Binding 后重测 | 是 | 可能 | 高风险审批 |
| Provider health degraded | 否 | Fresh Health/Snapshot | 是 | 可能 | 否 |
| Tool Schema changed | 否 | 新 Inventory/Binding 验证 | 是 | 是 | 可能 |
| Security deny/revoke | 否 | 09 决定 | 不可绕过 | 是/Block | 09 |
| Tool effect UNKNOWN | 07 不处理 | 08 Reconcile | 禁止立即 fallback | Wait | 可能人工 |
| Capability 永久缺失 | 否 | 否 | 有兼容候选才可 | 是 | 产品提示 |

# 31. Crash Matrix

| 崩溃点 | 恢复规则 |
| --- | --- |
| Resource Object Commit 成功、SkillVersion 提交失败 | Object 进入 orphan scan，按 content hash 删除或重新绑定 |
| SkillVersion 提交成功、Active Pointer 切换失败 | Version 保持 PUBLISHED；CAS 重试或人工处理，不冒充 ACTIVE |
| Active Pointer 成功、Outbox 发布失败 | Outbox Reconciler 重放，Definition/Version 事实保持有效 |
| Binding ACTIVE 提交后事件未发布 | Binding 仍有效，Outbox 重发 invalidation/activation |
| Snapshot 构建一半崩溃 | 未到 READY 的 Snapshot 不可消费；Snapshot Reconciler 终止或重建 |
| SelectionResult 提交后 Binding 被撤销 | 追加 ValidityRecord，通知 06；不覆盖原 Selection |
| Cache 返回已撤销 Version | 以 PostgreSQL/Revocation Generation 为准，Cache 条目失效并告警 |
| Connector Pack 部分安装 | 各模块安装使用 Staging + Activation Barrier；未全部满足不可宣称 Pack ACTIVE |

# 32. Reconciler

```text
SkillResourceOrphanReconciler
SkillVersionActivationReconciler
CapabilityVersionActivationReconciler
BindingConformanceReconciler
BindingRevocationPropagationReconciler
AvailabilitySnapshotReconciler
SelectionValidityReconciler
ToolInventoryBindingReconciler
CapabilityOutboxReconciler
ConnectorPackActivationReconciler
```

每个 Reconciler 必须定义：

```text
scan predicate
claim scope
claim token
fencing epoch
batch size
retry policy
human escalation policy
metric names
reconciliation record
```

# 33. 时间语义

```text
Business Timestamp
    PostgreSQL UTC。

TTL / Expiry / valid_until
    数据库时间比较，Resume 不重置。

Duration
    进程 monotonic clock。

Tool/Provider Lease
    由 08/11 使用数据库时间；07 只消费投影。

Display Time
    用户时区，仅用于展示。
```

Snapshot TTL、Conformance Expiry 和 Approval Expiry 不得混用。等待是否消耗 Run Wall-clock Budget 由 06 BudgetPolicy 决定。


# Part IV：领域对象与 Typed Contract

# 34. 对象分类

| 类型 | 对象 | 规则 |
| --- | --- | --- |
| Aggregate Root | `CapabilityDefinition`、`SkillDefinition` | 通过 Application Service 和 Repository 修改 |
| Version Entity | `CapabilityVersion`、`SkillVersion` | 发布后不可变 |
| Immutable Result | `SkillDiscoveryResult`、`SkillLoadResult`、`ProviderConformanceRecord`、`CapabilityAvailabilitySnapshot`、`CapabilitySelectionResult` | 更正创建新结果或 Validity Record |
| Value Object | `CapabilityRequirement`、`CompatibilityConstraint`、`SkillMetadata`、`SkillInstruction`、`SkillResourceManifest`、`ToolDefinitionRef` | 可哈希、版本化、不得持有 Secret |
| Binding Entity | `CapabilityProviderBinding` | 精确绑定 CapabilityVersion 与 Provider Ref |
| Governance Record | `CapabilityRevocationRecord`、`SkillPublicationDecision`、`SkillQuarantineRecord`、`CapabilityResultValidityRecord` | 追加式、不可覆盖 |
| Infrastructure Record | Outbox、Inbox、ObjectRef、Claim/Fencing Ref | 不冒充业务结果 |

# 35. Storage Mapping

| 对象 | 持久化 | 目标表 / 载体 | 关键约束 |
| --- | --- | --- | --- |
| CapabilityDefinition | Relational Aggregate | `capability_definitions` | `UNIQUE(tenant_scope, semantic_key)` |
| CapabilityVersion | Relational Version | `capability_versions` | `UNIQUE(definition_id, version)` |
| Active Capability Pointer | Relational Pointer | `capability_active_versions` | 每个 scope 最多一个 ACTIVE |
| CapabilityRequirement | Versioned JSON/Relation | `capability_requirements` | 绑定 SkillVersion/Policy |
| Capability Revocation | Append-only | `capability_revocations` | 不能删除历史 |
| SkillDefinition | Relational Aggregate | `skill_definitions` | 稳定 logical key |
| SkillVersion | Relational Version | `skill_versions` | 发布后不可改 |
| SkillResourceManifest | Relational Metadata | `skill_resource_manifests` | Manifest Hash |
| Skill Resource | Object Ref | `skill_resources` + Object Store | content hash |
| Skill Publication Decision | Append-only | `skill_publication_decisions` | approver/policy |
| Skill Quarantine | Append-only | `skill_quarantines` | reason/evidence |
| Skill Discovery Result | Immutable Result | `skill_discovery_results` | task/policy/snapshot refs |
| Skill Load Result | Immutable Result | `skill_load_results` | version/resource hashes |
| CapabilityProviderBinding | Relational Entity | `capability_provider_bindings` | exact refs |
| ProviderConformanceRecord | Immutable Result | `provider_conformance_records` | suite/tool/binding hash |
| Availability Snapshot | Relational Snapshot | `capability_availability_snapshots` | immutable + TTL |
| Availability Entry | Snapshot Child | `capability_availability_entries` | status/reason |
| Selection Result | Immutable Result | `capability_selection_results` | candidates + selected ref |
| Result Validity | Append-only | `capability_result_validity_records` | subject/version |
| Transition Record | Append-only | `capability_transition_records` | generation |
| Domain Event / Outbox | Append-only | `capability_domain_events` / `capability_outbox_events` | sequence/idempotency |

# 36. CapabilityDefinition

```text
capability_definition_id
semantic_key
display_name
description
capability_kind
portability_class
owner_module
tenant_scope
workspace_scope
tags
status
created_at
created_by
aggregate_version
```

`semantic_key` 示例：

```text
collaboration.message.send
knowledge.retrieve_evidence
memory.recall_context
artifact.report.generate
```

Provider-native Capability 使用明确命名空间，例如 `provider.feishu.bitable.record.batch_update`，不得伪装成跨 Provider Portable Capability。

# 37. CapabilityVersion

```text
capability_version_id
capability_definition_id
version
input_contract_ref
input_schema_hash
output_contract_ref
output_schema_hash
required_features
optional_features
side_effect_class
idempotency_requirement
reconciliation_requirement
data_classification_ceiling
compatibility_policy
dependency_requirements
acceptance_contract_ref
status
content_hash
published_at
valid_from
deprecated_at
revoked_at
aggregate_version
```

# 38. CapabilityRequirement

```text
capability_requirement_id
requirement_set_id
mode
capability_semantic_ref
version_range
required_features
input_contract_ref
output_contract_ref
side_effect_ceiling
tenant_constraint
workspace_constraint
region_constraint
data_residency
identity_mode
resource_scope
trust_floor
idempotency_requirement
reconciliation_requirement
latency_class
cost_class
fallback_policy
source_ref
```

`mode`：

```text
REQUIRED
ONE_OF
OPTIONAL
PROHIBITED
FALLBACK_ALLOWED
```

# 39. Skill Contracts

## 39.1 SkillDefinition

```text
skill_definition_id
logical_key
display_name
description
owner
source_type
tenant_scope
workspace_scope
trust_tier
status
aggregate_version
```

## 39.2 SkillVersion

```text
skill_version_id
skill_definition_id
version
metadata_ref
instruction_ref
resource_manifest_ref
requirement_set_ref
acceptance_criteria_ref
compatibility_policy
allowed_capability_constraints
prohibited_capability_constraints
required_memory_scopes
retrieval_profile_ref
data_classification
content_hash
signature_ref
status
published_at
revoked_at
```

## 39.3 SkillMetadata

```text
name
description
applicability
task_patterns
input_contract_summary
output_contract_summary
risk_summary
token_estimate
source_summary
version
```

## 39.4 SkillInstruction

```text
instruction_id
skill_version_id
content_ref
content_hash
instruction_schema_version
step_guidance
decision_constraints
acceptance_guidance
forbidden_actions
```

Instruction 是受治理指导，不是已执行事实，也不能覆盖 Security 或 Agent Core Control。

## 39.5 SkillResourceManifest

```text
manifest_id
skill_version_id
manifest_hash
resources[]
    resource_id
    name
    resource_type
    content_ref
    content_hash
    media_type
    size_bytes
    data_classification
    executable
    tool_definition_ref
    source_ref
    signature_ref
    required
```

当 `executable=true` 时，必须存在 `tool_definition_ref`；Skill Loader 只能返回 Ref。

# 40. ToolCapabilityDescriptor 与 ToolDefinitionRef

```text
ToolCapabilityDescriptor
    descriptor_id
    tool_definition_ref
    provider_definition_ref
    provider_family_id
    protocol_kind
    operation_id
    summary
    input_contract_summary
    output_contract_summary
    side_effect_class
    trust_tier
    feature_flags
    schema_hash
    inventory_generation
    lifecycle_status
```

```text
ToolDefinitionRef
    tool_definition_id
    tool_definition_version
    schema_hash
    inventory_generation
    owner_module = TOOL_RUNTIME
```

07 不保存 endpoint、command、secret、session 或 executable payload。

# 41. CapabilityProviderBinding

```text
binding_id
binding_version
capability_version_ref
provider_binding_kind
tool_definition_ref
domain_port_ref
provider_definition_ref
provider_instance_selector
semantic_mapping_ref
input_mapping_ref
output_mapping_ref
coverage_matrix
unsupported_features
side_effect_compatibility
idempotency_compatibility
reconciliation_compatibility
security_scope_mapping_ref
provider_family_id
backend_system_id
quota_domain_id
effect_domain_id
trust_tier
conformance_record_ref
status
effective_from
effective_until
content_hash
aggregate_version
```

`provider_binding_kind`：

```text
DOMAIN_PORT
TOOL_DEFINITION
ARTIFACT_PRODUCER
EXTERNAL_JOB
```

# 42. ProviderConformanceRecord

```text
conformance_record_id
binding_ref
capability_version_ref
tool_definition_ref
provider_instance_profile_ref
test_suite_version
test_environment_ref
input_conformance
output_conformance
feature_coverage
side_effect_conformance
idempotency_conformance
receipt_conformance
reconciliation_conformance
security_scope_conformance
error_semantics_conformance
result
failure_refs
evidence_refs
tested_at
expires_at
content_hash
```

# 43. CapabilityAvailabilitySnapshot

```text
availability_snapshot_id
request_ref
tenant_id
workspace_id
goal_version_ref
plan_version_ref
policy_snapshot_ref
registry_generation
tool_inventory_generations
security_epoch_ref
captured_at
valid_until
status
completeness
entries[]
```

Entry：

```text
capability_version_ref
binding_ref
provider_instance_or_pool_ref
tool_definition_ref
runtime_health_ref
status
reason_codes
freshness
constraint_summary
fallback_rank
```

# 44. CapabilitySelectionRequest / Result

```text
CapabilitySelectionRequest
    selection_request_id
    run_id
    plan_version_id
    step_definition_id
    requirement_set_ref
    availability_snapshot_ref
    policy_snapshot_ref
    budget_constraints
    risk_ceiling
    deadline_at
```

```text
CapabilitySelectionResult
    selection_result_id
    selection_request_ref
    requirement_set_ref
    availability_snapshot_ref
    selected_capability_version_ref
    selected_binding_ref
    selected_provider_instance_or_pool_ref
    selected_tool_definition_ref
    fallback_binding_refs
    candidate_summaries
    hard_filter_results
    ranking_results
    unmet_requirements
    reason_codes
    validity
    created_at
    valid_until
    trace_id
```

# 45. Skill Discovery / Load Contract

```text
SkillDiscoveryRequest
SkillDiscoveryResult
SkillLoadRequest
SkillLoadPlan
SkillLoadResult
```

`SkillLoadResult` 至少包含：

```text
skill_version_ref
metadata_ref
instruction_ref
loaded_resource_refs
skipped_resource_refs
resource_hashes
token_usage_estimate
policy_snapshot_ref
security_epoch_ref
status
failure_refs
created_at
valid_until
```

# 46. ConnectorPackManifest

`ConnectorPackManifest` 是安装输入，不是运行时权威事实：

```text
pack_id
pack_version
publisher
signature_ref
license
supported_zuno_contract_bundle
provider_definitions[]
tool_manifest_refs[]
capability_mapping_refs[]
skill_refs[]
security_scope_mapping_refs[]
contract_test_refs[]
reconciliation_strategy_refs[]
custom_extension_refs[]
content_hash
```

安装必须把各条目转换为各模块拥有的 Draft/Version/Decision；禁止运行时直接读取任意未激活 Pack 文件决定执行。

# 47. CrossModuleEnvelopeV1

所有跨模块 Request、Result、Invalidation 和 Event 使用 Registry 冻结的 `CrossModuleEnvelopeV1`，至少贯通：

```text
contract_name
contract_version
contract_bundle_version
message_id
producer_module
consumer_module
tenant_id
workspace_id
run_id
step_run_id
correlation_id
causation_id
idempotency_key
aggregate_type
aggregate_id
aggregate_version
expected_generation
effective_security_epoch_ref
effective_security_epoch_hash
principal_context_ref
security_context_ref
authorization_decision_ref
deadline_at
trace_id
data_classification
redaction_decision_ref
audit_requirement_ref
occurred_at
created_at
payload / payload_ref
payload_hash
payload_schema_hash
```

# 48. Typed Ports

```text
CapabilityCatalogPort
SkillCatalogPort
SkillDiscoveryPort
SkillLoadPort
CapabilityAvailabilityPort
CapabilitySelectionPort
CapabilityBindingGovernancePort
ProviderConformancePort
ToolInventoryProjectionPort
ToolRuntimeHealthProjectionPort
SecurityConstraintPort
ModelCapabilityProfilePort
DomainCapabilityPort
CapabilityEventSinkPort
ObjectStorePort
TransactionOutboxPort
```

Port 不暴露其他模块 Repository、数据库 Session、Provider SDK 或 Secret。


# Part V：Policy、版本、安全与 Provider 治理

# 49. Provider Selection Policy

`ProviderSelectionPolicy` 至少定义：

```text
hard_constraints
ranking_weights
organization_preference
user_preference
trust_floor
risk_ceiling
latency_ceiling
cost_ceiling
freshness_requirement
provider_diversity_requirement
fallback_limit
schema_visibility_budget
model_preference_allowed
deterministic_tie_breaker
```

Tie-break 必须确定性，不能依赖无记录的字典顺序或模型随机性。

# 50. Version Range、精确 Pinning 与兼容

```text
Skill / CapabilityRequirement
    可声明 SemVer 或受控 Compatibility Range。

CapabilityProviderBinding
    绑定精确 CapabilityVersion 与精确 ToolDefinitionRef。

CapabilitySelectionResult
    固定精确 CapabilityVersion、BindingVersion、ToolDefinitionRef、Schema Hash。

PlanVersion
    固定 SelectionResult 与 AvailabilitySnapshotRef。

PreparedToolAction
    由 08 再固定 ProviderInstance、ToolDefinitionVersion、Args Hash 与 Runtime Generation。
```

兼容策略必须声明：

```text
BACKWARD_COMPATIBLE
FORWARD_COMPATIBLE
EXACT_ONLY
ADAPTER_REQUIRED
INCOMPATIBLE
```

安全、SideEffectClass、Idempotency、Reconciliation 和数据等级变化视为破坏性变更。

# 51. ProviderInstance、Credential Scope 与 CapabilityConstraint

```text
ProviderInstance
    “连接的是哪个 Tenant、App、Region、Identity 和业务效果域”
    Owner = 08 Tool Runtime

Credential Scope
    “当前 Principal / App 被允许做什么”
    Owner = 09 Security；Secret Lease = 11

CapabilityConstraint
    “当前任务要求什么”
    Owner = 07 Requirement / 06 Task/Step Context
```

不同账号、App 和 Tenant 的映射：

| 概念 | Owner / 表达 |
| --- | --- |
| 外部 Tenant / 企业安装 | 08 ProviderInstance |
| App ID / 非敏感应用身份 | 08 ProviderInstance |
| App Secret / Token | 09 CredentialVersion + 11 SecretLease |
| OAuth Scope / delegated authority | 09 |
| Bot/User identity mode | 08 Instance metadata + 09 authorization |
| Region / Data Residency | 08 Instance metadata + 07 Constraint + 09 Policy |
| 业务 chat/document/resource id | Action 参数或 Canonical Resource ID |
| 07 Selection | 保存 ProviderInstanceRef/PoolRef，不保存 Secret |

07 选择业务路由；08 只在同一 Tenant/App/Identity/Effect Domain 的 Replica Pool 内负载均衡。

# 52. Dynamic Tool Inventory

Tool Inventory 来源：

```text
MCP initialize + tools/list + listChanged
OpenAPI import
CLI Manifest / completion metadata
SDK function registration
Internal RPC schema registry
Browser action manifest
```

变化流程：

```text
08 new ToolInventoryGeneration
→ new ToolDefinitionVersion or revocation
→ ToolInventoryChanged event
→ 07 Binding revalidation / invalidation
→ Availability Snapshot invalidation
→ 06 Wait / Fallback / Replan / Block
```

Active Plan 不允许静默使用新 Schema。

# 53. Skill 与 Connector 供应链

必须检查：

```text
source type
publisher identity
signature
content hash
resource hash
dependency lock
license
allowed URI scheme
path traversal / symlink
external network dependency
embedded executable
malicious instruction
prompt injection
permission amplification
output contract manipulation
data exfiltration instruction
```

Trust Tier：

```text
SYSTEM_SIGNED
TENANT_MANAGED
WORKSPACE_MANAGED
USER_MANAGED
EXTERNAL_VERIFIED
EXTERNAL_UNTRUSTED
```

`EXTERNAL_UNTRUSTED` 不得直接进入 ACTIVE。

# 54. 模型角色

可使用模型的 Proposal 角色：

```text
SKILL_DISCOVERY_ASSIST
CAPABILITY_MAPPING_ASSIST
CAPABILITY_RANKING_ASSIST
SCHEMA_SEMANTIC_MATCH_ASSIST
```

确定性优先：

```text
Schema validation
Version compatibility
Hard constraint filtering
Trust / Tenant / Region filtering
Conformance verification
Hash / Signature check
Lifecycle and revocation
Tie-break and commit
```

模型输出必须经过 Schema Validation，不能直接更新数据库状态。

# 55. Context Budget 与渐进披露

Context Budget 应分别计量：

```text
skill_metadata_tokens
skill_instruction_tokens
skill_resource_tokens
capability_descriptor_tokens
tool_schema_tokens
selection_explanation_tokens
```

优先级：

```text
Required Skill Instruction
→ Required Resource
→ Selected Tool Schema
→ Fallback Descriptor
→ Optional examples
```

预算不足时返回显式 `CAP_SKILL_LOAD_BUDGET_EXCEEDED` 或缩小候选，不得静默截断 AcceptanceCriteria、ForbiddenActions 或 Security Constraint。

# 56. Provider Trust 与 Failure Domain

每个 Binding 至少记录：

```text
provider_family_id
backend_system_id
transport_domain_id
quota_domain_id
credential_domain_id
effect_domain_id
data_residency_domain_id
```

多个 MCP 若共享同一外部 API、Tenant Rate Limit 或 Effect Domain，不得被评分为独立容灾。

# 57. Security Gate 交接

07 只传播：

```text
required_permission_scopes
provider trust requirement
data classification
tenant / workspace / resource scope
side_effect_class
audit requirement
selected ProviderInstanceRef
```

09 产生：

```text
ActionAuthorizationDecision
SecurityApprovalDecision
EffectiveSecurityEpoch
CredentialVersionRef
```

08 在 Prepare/Execute 前校验最新决定。07 的 `AVAILABLE` 和 `selected` 永远不等于 `authorized`。

# 58. 数据、Retention 与删除

Definition/Version/Binding/Selection 需要保留历史审计；Resource Payload 按数据等级和 RetentionPolicy 管理。删除流程：

```text
Domain Tombstone / Revocation
→ stop new selection
→ invalidate projections and caches
→ Infrastructure DeletionRequest
→ Object / Index / Cache target deletion
→ DeletionVerification
→ retain hashes, metadata and audit tombstone
```

Legal Hold 优先于 Purge。删除 Object 内容后，历史 Version 保留不可逆 Tombstone 和 Hash，不伪造仍可加载状态。


# Part VI：目标实现表面

# 59. 目标代码目录

```text
src/backend/zuno/capability/
├── contracts/
│   ├── envelope.py
│   ├── capability.py
│   ├── skill.py
│   ├── binding.py
│   ├── availability.py
│   ├── selection.py
│   ├── conformance.py
│   └── events.py
├── domain/
│   ├── capability_definition.py
│   ├── capability_version.py
│   ├── skill_definition.py
│   ├── skill_version.py
│   ├── provider_binding.py
│   ├── conformance_record.py
│   ├── availability_snapshot.py
│   ├── selection_result.py
│   ├── validity.py
│   └── failure.py
├── application/
│   ├── capability_catalog_service.py
│   ├── skill_catalog_service.py
│   ├── skill_discovery_service.py
│   ├── skill_load_service.py
│   ├── requirement_expansion_service.py
│   ├── binding_governance_service.py
│   ├── conformance_service.py
│   ├── availability_service.py
│   ├── selection_service.py
│   ├── revocation_service.py
│   └── reconciliation_service.py
├── policy/
│   ├── compatibility.py
│   ├── selection.py
│   ├── visibility.py
│   ├── trust.py
│   └── freshness.py
├── adapters/
│   ├── persistence/
│   ├── object_store/
│   ├── tool_runtime_projection/
│   ├── security/
│   ├── model_assist/
│   └── observability/
└── api/
    ├── admin.py
    ├── discovery.py
    └── internal.py
```

08 的 HTTP/CLI/MCP 等执行 Adapter 不放入此目录。

# 60. 目标数据库

```text
capability_definitions
capability_versions
capability_active_versions
capability_requirements
capability_revocations
capability_transition_records

skill_definitions
skill_versions
skill_resource_manifests
skill_resources
skill_publication_decisions
skill_quarantines
skill_discovery_results
skill_load_results

capability_provider_bindings
provider_conformance_records
capability_availability_snapshots
capability_availability_entries
capability_selection_results
capability_result_validity_records

capability_domain_events
capability_outbox_events
capability_inbox_records
capability_reconciliation_records
```

# 61. 关键约束与索引

```text
UNIQUE(capability_definition_id, version)
UNIQUE(skill_definition_id, version)
UNIQUE(capability_version_ref, binding_version)
UNIQUE(binding_ref, tool_definition_ref, test_suite_version, content_hash)
partial UNIQUE(capability_definition_id, scope) WHERE status = ACTIVE
partial UNIQUE(skill_definition_id, scope) WHERE status = ACTIVE
UNIQUE(availability_snapshot_id, capability_version_ref, binding_ref, provider_instance_or_pool_ref)
UNIQUE(selection_request_ref)
UNIQUE(event_id)
UNIQUE(aggregate_type, aggregate_id, transition_sequence)
INDEX(binding status, capability_version_ref)
INDEX(snapshot valid_until, status)
INDEX(selection plan_version_id, step_definition_id)
INDEX(outbox published_at) WHERE published_at IS NULL
```

# 62. 事务边界

```text
Capability Publish
    Version、Transition、Active Pointer、DomainEvent、Outbox 同事务。

Skill Publish
    Version、ResourceManifest、PublicationDecision、Transition、Outbox 同事务；
    Object Payload 在事务前完成不可变提交并以 Hash 引用。

Binding Activation
    ConformanceRecord 已在事务外完成；
    Binding status、Transition、Event、Outbox 同事务。

Availability Capture
    候选计算可在事务外；
    Snapshot、Entries、Completeness、Event 原子提交。

Selection
    Result、Candidate Summary、Policy Ref、Validity seed、Event 原子提交。

Revocation
    RevocationRecord、Version/Binding 状态、Invalidation Event、Outbox 同事务。
```

# 63. Cache 与 Projection

允许：

```text
Skill Metadata search index
Capability semantic search index
Active Version cache
Binding lookup cache
Runtime Health projection
Availability short-TTL cache
```

禁止：

```text
只在 Cache 保存 Revocation
只在向量索引保存 SkillDefinition
从 MCP 当前 list 直接覆盖历史 ToolDefinitionRef
从 Health Cache 推断 Authorization
```

所有 Projection 带 source generation、built_at、valid_until 和 content hash。

# 64. API 表面

Admin API：

```text
create/update draft CapabilityDefinition
publish/deprecate/revoke CapabilityVersion
create/update draft SkillVersion
validate/publish/quarantine/revoke SkillVersion
submit/validate/approve/revoke CapabilityProviderBinding
run/read Provider Conformance
install/inspect Connector Pack
```

Runtime Internal API：

```text
discover_skills
load_skill
resolve_capability_requirements
capture_capability_availability
select_capability_provider
get_selection_validity
invalidate_by_inventory_generation
```

Runtime API 返回 Contract，不暴露 Repository 或 Provider SDK。

# 65. Connector Extension SPI

```text
ConnectorPackImporter
CapabilityMappingProvider
ConformanceTestProvider
SecurityScopeMappingProvider
ResultMappingProvider
ReconciliationStrategyProvider
CustomProtocolExtension
```

Custom Extension 需要：

```text
justification
threat model
sandbox profile
version compatibility
test suite
failure semantics
owner
rollback plan
```

# 66. 通用 Adapter 家族

08 目标通用 Adapter：

```text
HttpApiAdapter
CliAdapter
McpAdapter
SdkFunctionAdapter
RpcAdapter
BrowserAdapter
DatabaseAdapter
LocalFunctionAdapter
```

07 不为每个 CLI/API/MCP 写执行 Adapter。每个操作仍必须有版本化 Manifest/ToolDefinition，由 08 管理。

CLI Manifest 至少声明：

```text
executable allowlist
fixed subcommand
typed argv mapping
working directory policy
environment allowlist
stdin policy
output format
exit-code mapping
timeout
resource limit
side-effect class
idempotency strategy
receipt extraction
reconciliation strategy
```

禁止模型提交任意 Shell 字符串。

# 67. Importer

```text
OpenAPI
→ Draft ToolDefinitionVersion
→ Draft Descriptor / Binding Proposal
→ Contract Test
→ Governance Activation

MCP initialize / tools.list
→ ToolInventoryGeneration
→ Draft ToolDefinitionVersion
→ Binding Proposal
→ Conformance
→ Activation

CLI help / completion / JSON metadata
→ Draft Manifest
→ Manual/Rule review
→ Sandbox Contract Test
→ Activation
```

Importer 只生成 Draft，不产生 ACTIVE。

# 68. Migration 原则

从当前 `SkillCard`、`CapabilityCard`、`ToolCard`、`ToolRequest` 等过渡时：

```text
SkillCard
    拆为 SkillDefinition + SkillVersion + SkillMetadata。

CapabilityCard
    拆为 CapabilityDefinition + CapabilityVersion。

CapabilityRouter
    迁移为 CapabilityDiscovery/Selection，不拥有 StepFeasibility。

ToolCard
    07 保留 ToolCapabilityDescriptor；
    可执行 ToolDefinition 迁移到 08。

ToolRequest
    删除为泛化事实；
    06 使用 ActionProposal，08 使用 PreparedToolAction。

Approval
    迁移到 09 SecurityApprovalDecision。

CredentialRef
    07 只保留 CredentialRequirement；
    CredentialVersionRef 归 09，SecretLease 归 11。

ExecutionAdapter / ResultNormalizer
    迁移到 08。

ToolTrace
    拆为 08 Domain Event 与 10 Trace/Audit Projection。
```

迁移采用：

```text
add new schema
dual read / explicit adapter
backfill versioned facts
cut over producers
drain old readers
remove obsolete contract
```

不得让旧名称继续成为第二事实源。

# 69. Retention、删除与 Legal Hold

```text
Draft / Failed Conformance
    短期保留，支持调试。

Published / Active / Revoked Version
    按审计和引用保留。

Skill Resource Payload
    按数据等级、引用和 Legal Hold。

Availability / Selection
    按 Run、Plan 和审计策略保留。

Transition / Revocation / Governance
    追加式长期保留。
```

# 70. Observability 与 Eval

Trace Span：

```text
skill.discovery
skill.instruction.load
skill.resource.plan
skill.resource.load
skill.resource.integrity_check
capability.requirement.expand
capability.binding.validate
capability.conformance.run
capability.availability.capture
capability.selection
capability.fallback
capability.revocation.propagate
connector.pack.activate
```

指标：

```text
skill_discovery_precision
skill_discovery_recall
wrong_skill_selection_rate
unused_skill_rate
skill_token_overhead
resource_load_efficiency
capability_requirement_unsatisfied_rate
provider_conformance_failure_rate
binding_activation_latency
selection_stability
fallback_success_rate
stale_snapshot_incident_rate
schema_change_invalidation_latency
provider_false_redundancy_rate
malicious_skill_rejection_rate
```

质量证明必须关联 Step Acceptance、Final Gate 或真实业务 Outcome，不能只证明“加载过 Skill”。

# 71. Operations 与 Health

07 运行健康指标：

```text
catalog read latency
discovery latency
load latency
snapshot capture latency
selection latency
active version count
stale binding count
expired conformance count
outbox lag
reconciler backlog
cache generation lag
```

07 不把 08 的 Tool Effect 成功率冒充自身 Selection 正确率；二者通过 Binding/Selection Ref 关联分析。


# Part VII：规范性矩阵与控制闭环

# 72. 通用 Transition Record

```text
transition_id
aggregate_type
aggregate_id
from_status
to_status
trigger_type
trigger_ref
guard_result_ref
reason_code
expected_generation
applied_generation
policy_snapshot_ref
security_epoch_ref
occurred_at
trace_id
```

状态转换必须由确定性 Guard 提交。模型只能提出 reason 或 Proposal。

# 73. Ownership Matrix

| 领域事实 | Owner | 07 消费/产生 | 禁止 |
| --- | --- | --- | --- |
| Skill / Capability Definition、Version | 07 | 产生 | 其他模块直接改 |
| Binding / Conformance | 07 | 产生 | 08 直接激活业务映射 |
| Availability / Selection | 07 | 产生 | 当作 Authorization |
| Plan / Feasibility / ControlDecision | 06 | 消费 | 07 改 Plan |
| ToolDefinition / Instance / Attempt / Effect | 08 | 消费 Ref/Projection | 07 执行 |
| Authorization / Approval / Credential | 09 | 消费 Ref | 07 自批 |
| SecretLease / Claim / Outbox primitive | 11 | 使用 | 冒充业务结果 |
| Trace / Audit / Eval | 10 | 产生源事件 | 修改接受事实 |

# 74. Failure Ownership Matrix

| Failure Category | Fact Owner | Retry/Recovery Owner | 06 Control |
| --- | --- | --- | --- |
| Catalog/Binding/Snapshot/Selection | 07 | 07 | retry/wait/fallback/replan |
| Tool Inventory/Prepare/Effect | 08 | 08 | wait/retry after reconcile/replan |
| Security/Epoch/Approval | 09 | 09 | wait/replan/abort |
| DB/Object/Queue/Lease | 11 | 11 | wait/retry/replan |
| Model Proposal invalid | 04 或 07 边界 | 对应 Owner | repair/escalate |
| Eval/Trace ingest | 10/11 | 对应 Owner | audit policy decides |

# 75. Fallback Eligibility Matrix

| 条件 | 自动列为候选 | 需要重新授权 | 需要 Replan |
| --- | --- | --- | --- |
| 同 CapabilityVersion、同 Tenant/App/Effect Domain、只读 | 是 | 执行前仍重验 | 通常否 |
| 同 CapabilityVersion、不同技术 Replica | 08 内部处理 | 否，若身份不变 | 否 |
| 同 Capability、不同 ProviderInstance 但同身份与 Scope | 可 | 是 | 视 Step |
| 不同 Tenant/App/Region/Identity | 否 | 必须 | 通常是 |
| 风险等级提高 | 否 | 必须 | 是 |
| Output Contract 改变 | 否 | 可能 | 是 |
| ToolAttempt UNKNOWN | 否 | 不适用 | 先 Reconcile |
| 已确认 NOT_EXECUTED | 可重新计算 | 是 | 视兼容性 |

# 76. Freshness Matrix

| 场景 | Planning Snapshot | Action Preflight |
| --- | --- | --- |
| 本地只读 | 短 TTL 可用 | Tool/Version/Scope |
| 远程只读 | 较短 TTL | Health、Epoch、Credential |
| 外部写 | 固定到 Plan | 零陈旧 Tool/Instance/Auth/Credential |
| Destructive | 固定并标高风险 | Approval Hash、Scope、Epoch、Audit、Claim 全重验 |
| 长时间 Resume | 历史 Ref 保留 | 强制新 Preflight，必要时 Replan |

# 77. Conformance Test Matrix

```text
Schema
    canonical input/output mapping, required/optional fields, enum compatibility

Behavior
    success, known failure, timeout, rate limit, partial result

Side Effect
    effect class, idempotency, duplicate request, receipt extraction

Reconciliation
    executed, not executed, unknown, human required

Security
    tenant isolation, scope mapping, redaction, data residency

Lifecycle
    version change, revocation, schema drift, inventory generation

Resilience
    adapter crash, connection loss, response lost, retry boundary
```

# 78. 非法转换与禁止行为

必须拒绝：

```text
REVOKED CapabilityVersion → ACTIVE
RETIRED SkillVersion → ACTIVE
FAILED ConformanceRecord 原地改为 PASSED
模型 Proposal → ACTIVE Binding
Availability AVAILABLE → Authorization ALLOW 推断
SelectionResult → Plan 激活
Tool schema 原地修改而不新建 Version
不同 Tenant/App 的隐式 Provider 切换
Skill Loader 直接运行脚本
ToolAttempt UNKNOWN 后跨 Provider 重试
Cache 值覆盖 PostgreSQL Revocation
Connector Pack 文件直接作为生产运行时真相
```

# 79. Requirement Control Registry

以下 80 条 Control 与 Part VIII 的 Requirement Index 一一对应。


| Control ID | Category | Requirement Summary | Enforcement Ref | Failure Code | Required Tests | Runtime Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `RC-CAP-001` | FOUNDATION | Capability / Skill 是业务能力语义、方法包、版本目录、可用性快照和选择治理模块，不得执行 Tool 或提交其他模块领域事实 | `CapabilityBoundaryGuard` | `CAP_BOUNDARY_VIOLATION` | `CAP-001-UT`, `CAP-001-IT` | `EV-CAP-001` |
| `RC-CAP-002` | FOUNDATION | Capability、Skill、Tool、Function Calling、MCP、API、CLI 和 Provider 必须使用本文的独立定义 | `ConceptTaxonomyValidator` | `CAP_CONCEPT_TAXONOMY_INVALID` | `CAP-002-UT`, `CAP-002-IT` | `EV-CAP-002` |
| `RC-CAP-003` | FOUNDATION | Skill 必须通过 CapabilityRequirement 组合能力，不得把具体执行命令冒充方法步骤 | `SkillRequirementBoundaryGuard` | `CAP_SKILL_DIRECT_EXECUTION_FORBIDDEN` | `CAP-003-UT`, `CAP-003-IT` | `EV-CAP-003` |
| `RC-CAP-004` | FOUNDATION | API、CLI、SDK、MCP、Browser、RPC 是 Provider 或执行协议，不是业务 CapabilityKind | `ProviderProtocolTaxonomyGuard` | `CAP_PROVIDER_PROTOCOL_MISCLASSIFIED` | `CAP-004-UT`, `CAP-004-IT` | `EV-CAP-004` |
| `RC-CAP-005` | FOUNDATION | Security Gate、Approval、Budget、Trace、Checkpoint、Lease 和 IdempotencyClaim 不是业务 Capability | `GovernanceCapabilityExclusionGuard` | `CAP_GOVERNANCE_OBJECT_MISCLASSIFIED` | `CAP-005-UT`, `CAP-005-IT` | `EV-CAP-005` |
| `RC-CAP-006` | FOUNDATION | Capability / Skill 的 Target 主设计只能由单一正式文档承载，Agent 镜像必须字节级一致 | `CapabilityDocMirrorGuard` | `CAP_DOC_MIRROR_MISMATCH` | `CAP-006-UT`, `CAP-006-IT` | `EV-CAP-006` |
| `RC-CAP-007` | FOUNDATION | Current、Gap 和 Measurement 只能由状态事实源维护，Target 文档不得冒充实现完成 | `CurrentTargetSeparationGuard` | `CAP_TARGET_CURRENT_CONFUSION` | `CAP-007-UT`, `CAP-007-IT` | `EV-CAP-007` |
| `RC-CAP-008` | FOUNDATION | 模型只能产生 Discovery、Mapping、Selection 或 Load Proposal，不得激活 Version、Binding 或执行 Tool | `ModelProposalOnlyGuard` | `CAP_MODEL_COMMIT_FORBIDDEN` | `CAP-008-UT`, `CAP-008-IT` | `EV-CAP-008` |
| `RC-CAP-009` | FOUNDATION | 跨模块消息必须使用 CrossModuleEnvelopeV1 并携带版本、Hash、Tenant、Trace 和适用的 Security Epoch | `CapabilityEnvelopeValidator` | `CAP_ENVELOPE_INVALID` | `CAP-009-UT`, `CAP-009-IT`, `CAP-009-FT` | `EV-CAP-009` |
| `RC-CAP-010` | FOUNDATION | 未知 Version、Enum、Hash、Generation、Tenant 或安全上下文必须 fail-closed、quarantine 或返回显式 Blocked | `UnknownContractFailClosedGuard` | `CAP_UNKNOWN_CONTRACT_FAIL_CLOSED` | `CAP-010-UT`, `CAP-010-IT`, `CAP-010-FT` | `EV-CAP-010` |
| `RC-CAP-011` | SKILL | SkillDefinition 是稳定逻辑身份，SkillVersion 发布后不可原地修改 | `SkillVersionImmutabilityGuard` | `CAP_SKILL_VERSION_MUTATION` | `CAP-011-UT`, `CAP-011-IT` | `EV-CAP-011` |
| `RC-CAP-012` | SKILL | SkillVersion 必须结构化保存 Metadata、Instruction、ResourceManifest、CapabilityRequirement 和 AcceptanceCriteria | `SkillVersionSchemaValidator` | `CAP_SKILL_SCHEMA_INVALID` | `CAP-012-UT`, `CAP-012-IT` | `EV-CAP-012` |
| `RC-CAP-013` | SKILL | Skill discovery 只能先暴露 Metadata，Instruction 和 Resource 必须按需渐进加载 | `SkillProgressiveDisclosureGuard` | `CAP_SKILL_EAGER_LOAD_FORBIDDEN` | `CAP-013-UT`, `CAP-013-IT`, `CAP-013-E2E` | `EV-CAP-013` |
| `RC-CAP-014` | SKILL | 每次 Skill discovery 必须产生不可变 SkillDiscoveryResult 并记录候选、拒绝原因和版本 | `SkillDiscoveryResultGuard` | `CAP_SKILL_DISCOVERY_UNAUDITABLE` | `CAP-014-UT`, `CAP-014-IT` | `EV-CAP-014` |
| `RC-CAP-015` | SKILL | 每次 Skill load 必须固定 SkillVersion、资源 Hash、Load Policy 和 Budget | `SkillLoadPinningGuard` | `CAP_SKILL_LOAD_UNPINNED` | `CAP-015-UT`, `CAP-015-IT` | `EV-CAP-015` |
| `RC-CAP-016` | SKILL | Skill Resource 必须按类型、数据等级、完整性、来源和可执行性分类 | `SkillResourceManifestValidator` | `CAP_SKILL_RESOURCE_INVALID` | `CAP-016-UT`, `CAP-016-IT` | `EV-CAP-016` |
| `RC-CAP-017` | SKILL | Skill 中的脚本、Delegate 或可执行资源不得由 Skill Loader 直接运行，必须引用 ToolDefinitionRef | `SkillExecutableResourceGuard` | `CAP_SKILL_SCRIPT_RUNTIME_BYPASS` | `CAP-017-UT`, `CAP-017-IT`, `CAP-017-E2E` | `EV-CAP-017` |
| `RC-CAP-018` | SKILL | Skill allowed_tools 或 allowed_capabilities 只能缩小候选范围，不能扩大授权 | `SkillPermissionNonAmplificationGuard` | `CAP_SKILL_PERMISSION_AMPLIFICATION` | `CAP-018-UT`, `CAP-018-IT` | `EV-CAP-018` |
| `RC-CAP-019` | SKILL | 外部或用户提供的 Skill 默认不可信，必须经过签名、完整性、策略和风险校验 | `SkillSupplyChainGuard` | `CAP_SKILL_UNTRUSTED_SOURCE` | `CAP-019-UT`, `CAP-019-IT` | `EV-CAP-019` |
| `RC-CAP-020` | SKILL | SkillVersion 撤销、隔离或资源失效必须使依赖的 LoadResult 和 SelectionResult 失效并通知 Agent Core | `SkillRevocationPropagationGuard` | `CAP_SKILL_REVOCATION_NOT_PROPAGATED` | `CAP-020-UT`, `CAP-020-IT`, `CAP-020-FT`, `CAP-020-E2E` | `EV-CAP-020` |
| `RC-CAP-021` | BINDING | CapabilityDefinition 必须使用稳定业务语义身份，不得直接使用 Provider Tool 名称作为主身份 | `CapabilitySemanticIdentityGuard` | `CAP_SEMANTIC_IDENTITY_INVALID` | `CAP-021-UT`, `CAP-021-IT` | `EV-CAP-021` |
| `RC-CAP-022` | BINDING | CapabilityVersion 必须定义 Canonical Input/Output Contract、风险、依赖、兼容和验收语义 | `CapabilityVersionSchemaValidator` | `CAP_CAPABILITY_VERSION_INVALID` | `CAP-022-UT`, `CAP-022-IT` | `EV-CAP-022` |
| `RC-CAP-023` | BINDING | Portable Capability 与 Provider-native Capability 必须分离，禁止强行最低公分母映射 | `PortableNativeCapabilityGuard` | `CAP_PORTABLE_NATIVE_COLLISION` | `CAP-023-UT`, `CAP-023-IT` | `EV-CAP-023` |
| `RC-CAP-024` | BINDING | CapabilityProviderBinding 必须把精确 CapabilityVersion 映射到版本化 ToolDefinitionRef 或领域 Port Ref | `ProviderBindingSchemaValidator` | `CAP_BINDING_INVALID` | `CAP-024-UT`, `CAP-024-IT` | `EV-CAP-024` |
| `RC-CAP-025` | BINDING | Binding 可由人工、规则或模型产生 Proposal，但只能由确定性验证和治理 Gate 激活 | `BindingActivationGuard` | `CAP_BINDING_UNVERIFIED_ACTIVATION` | `CAP-025-UT`, `CAP-025-IT`, `CAP-025-FT`, `CAP-025-E2E` | `EV-CAP-025` |
| `RC-CAP-026` | BINDING | 模型生成的 Binding Proposal 不得仅凭语义相似度进入 ACTIVE | `ModelBindingActivationGuard` | `CAP_MODEL_BINDING_ACTIVATION_FORBIDDEN` | `CAP-026-UT`, `CAP-026-IT` | `EV-CAP-026` |
| `RC-CAP-027` | BINDING | ProviderConformanceRecord 必须覆盖输入、输出、副作用、幂等、Reconciliation、安全和错误语义 | `ProviderConformanceGuard` | `CAP_CONFORMANCE_INCOMPLETE` | `CAP-027-UT`, `CAP-027-IT`, `CAP-027-FT` | `EV-CAP-027` |
| `RC-CAP-028` | BINDING | 同名 Tool 不得自动视为同一 Capability，不同名 Tool 也不得因名称不同而自动判为不等价 | `ToolNameEquivalenceGuard` | `CAP_TOOL_NAME_EQUIVALENCE_INVALID` | `CAP-028-UT`, `CAP-028-IT` | `EV-CAP-028` |
| `RC-CAP-029` | BINDING | 一个 Capability 可以绑定多个 Provider，但必须记录 ProviderFamily、Backend、Quota 和 Effect Failure Domain | `ProviderFailureDomainGuard` | `CAP_FAILURE_DOMAIN_MISSING` | `CAP-029-UT`, `CAP-029-IT` | `EV-CAP-029` |
| `RC-CAP-030` | BINDING | Connector Pack 只能作为安装输入，激活后必须拆分为各模块拥有的版本化领域事实 | `ConnectorPackActivationGuard` | `CAP_CONNECTOR_PACK_AUTHORITY_LEAK` | `CAP-030-UT`, `CAP-030-IT` | `EV-CAP-030` |
| `RC-CAP-031` | AVAILABILITY | CapabilityAvailabilitySnapshot 必须是不可变、版本化、带 TTL 和来源 Generation 的规划快照 | `AvailabilitySnapshotGuard` | `CAP_AVAILABILITY_SNAPSHOT_INVALID` | `CAP-031-UT`, `CAP-031-IT`, `CAP-031-FT`, `CAP-031-E2E` | `EV-CAP-031` |
| `RC-CAP-032` | AVAILABILITY | Availability 的 AVAILABLE 只表示可作为候选，不等价于 Authorization、Approval 或 Execution Readiness | `AvailabilityAuthorizationSeparationGuard` | `CAP_AVAILABILITY_AUTHORIZATION_CONFUSION` | `CAP-032-UT`, `CAP-032-IT` | `EV-CAP-032` |
| `RC-CAP-033` | AVAILABILITY | Availability Entry 必须区分 AVAILABLE、DEGRADED、CONFIG_REQUIRED、UNAVAILABLE、VERSION_INCOMPATIBLE、POLICY_CONSTRAINED、REVOKED 和 UNKNOWN | `AvailabilityStatusValidator` | `CAP_AVAILABILITY_STATUS_INVALID` | `CAP-033-UT`, `CAP-033-IT` | `EV-CAP-033` |
| `RC-CAP-034` | AVAILABILITY | PlanVersion 必须固定 CapabilityAvailabilitySnapshotRef，不能在恢复时静默重算并覆盖历史 | `PlanSnapshotPinningGuard` | `CAP_PLAN_SNAPSHOT_UNPINNED` | `CAP-034-UT`, `CAP-034-IT`, `CAP-034-FT`, `CAP-034-E2E` | `EV-CAP-034` |
| `RC-CAP-035` | AVAILABILITY | 每个 Action 执行前必须由 08/09/11 完成最新 Readiness Preflight，07 快照不能替代该检查 | `ExecutionPreflightBoundaryGuard` | `CAP_EXECUTION_PREFLIGHT_BYPASS` | `CAP-035-UT`, `CAP-035-IT`, `CAP-035-FT`, `CAP-035-E2E` | `EV-CAP-035` |
| `RC-CAP-036` | AVAILABILITY | 高风险 Action 对 Schema、Instance、Security Epoch、Credential 和 Approval 的陈旧容忍必须为零或显式 Policy | `HighRiskFreshnessGuard` | `CAP_HIGH_RISK_STALE_STATE` | `CAP-036-UT`, `CAP-036-IT`, `CAP-036-FT` | `EV-CAP-036` |
| `RC-CAP-037` | AVAILABILITY | CapabilitySelectionResult 必须记录候选集、硬过滤、评分、选中 Binding、实例或实例池 Ref 和 fallback 顺序 | `SelectionResultSchemaValidator` | `CAP_SELECTION_RESULT_INVALID` | `CAP-037-UT`, `CAP-037-IT`, `CAP-037-E2E` | `EV-CAP-037` |
| `RC-CAP-038` | AVAILABILITY | 模型可以提出 Provider Preference，但硬过滤、版本兼容和最终 Selection Commit 必须确定性执行 | `DeterministicSelectionGuard` | `CAP_SELECTION_MODEL_COMMIT_FORBIDDEN` | `CAP-038-UT`, `CAP-038-IT` | `EV-CAP-038` |
| `RC-CAP-039` | AVAILABILITY | StepFeasibilityDecision 归 Agent Core；07 只能提供 Requirement、Snapshot、Selection 和未满足约束 | `StepFeasibilityOwnershipGuard` | `CAP_STEP_FEASIBILITY_OWNERSHIP_VIOLATION` | `CAP-039-UT`, `CAP-039-IT`, `CAP-039-FT`, `CAP-039-E2E` | `EV-CAP-039` |
| `RC-CAP-040` | AVAILABILITY | Fallback Candidate 必须保持 Step Output Contract、风险上限、Tenant、数据驻留和副作用语义 | `FallbackCompatibilityGuard` | `CAP_FALLBACK_INCOMPATIBLE` | `CAP-040-UT`, `CAP-040-IT`, `CAP-040-E2E` | `EV-CAP-040` |
| `RC-CAP-041` | VERSIONING | Skill 和 Capability Requirement 可以声明兼容版本范围，Selection 必须解析为精确版本 | `VersionRangeResolutionGuard` | `CAP_VERSION_RANGE_UNRESOLVED` | `CAP-041-UT`, `CAP-041-IT` | `EV-CAP-041` |
| `RC-CAP-042` | VERSIONING | PlanVersion 必须固定精确 CapabilityVersion、BindingVersion、ToolDefinitionRef 和 Schema Hash | `PlanExactVersionPinningGuard` | `CAP_PLAN_VERSION_NOT_EXACT` | `CAP-042-UT`, `CAP-042-IT` | `EV-CAP-042` |
| `RC-CAP-043` | VERSIONING | PreparedToolAction 必须再次固定精确 ToolDefinitionVersion、ProviderInstanceRef 和 Prepared Hash | `PreparedActionPinningBoundaryGuard` | `CAP_PREPARED_ACTION_UNPINNED` | `CAP-043-UT`, `CAP-043-IT`, `CAP-043-FT`, `CAP-043-E2E` | `EV-CAP-043` |
| `RC-CAP-044` | VERSIONING | Tool Inventory 变化必须创建新 Generation 和 ToolDefinitionVersion，不得原地改 Schema | `ToolInventoryGenerationGuard` | `CAP_TOOL_SCHEMA_MUTATED_IN_PLACE` | `CAP-044-UT`, `CAP-044-IT`, `CAP-044-FT`, `CAP-044-E2E` | `EV-CAP-044` |
| `RC-CAP-045` | VERSIONING | MCP listChanged、OpenAPI 更新、CLI Manifest 更新必须触发 Binding 重新验证或失效 | `InventoryChangeInvalidationGuard` | `CAP_INVENTORY_CHANGE_NOT_PROPAGATED` | `CAP-045-UT`, `CAP-045-IT`, `CAP-045-FT`, `CAP-045-E2E` | `EV-CAP-045` |
| `RC-CAP-046` | VERSIONING | Deprecated Version 可按 Policy 服务已固定 Run，但不得用于新的 Selection；Revoked Version 默认立即阻止新执行 | `DeprecationRevocationGuard` | `CAP_VERSION_LIFECYCLE_VIOLATION` | `CAP-046-UT`, `CAP-046-IT` | `EV-CAP-046` |
| `RC-CAP-047` | VERSIONING | 未知或不兼容 ToolDefinitionVersion 必须返回显式 Failure，不得按相近名称猜测替代 | `UnknownToolVersionGuard` | `CAP_TOOL_VERSION_UNKNOWN` | `CAP-047-UT`, `CAP-047-IT` | `EV-CAP-047` |
| `RC-CAP-048` | VERSIONING | Active Plan 引用失效时由 Agent Core 决定 Wait、Fallback、Replan 或 Block，07 不得改写 Plan | `PlanMutationBoundaryGuard` | `CAP_PLAN_MUTATION_FORBIDDEN` | `CAP-048-UT`, `CAP-048-IT`, `CAP-048-FT`, `CAP-048-E2E` | `EV-CAP-048` |
| `RC-CAP-049` | VERSIONING | SelectionResult、LoadResult 和 Snapshot 必须有 ResultValidity，支持 VALID、STALE、REVOKED、SUPERSEDED 和 UNKNOWN_VALIDITY | `CapabilityResultValidityGuard` | `CAP_RESULT_VALIDITY_MISSING` | `CAP-049-UT`, `CAP-049-IT` | `EV-CAP-049` |
| `RC-CAP-050` | VERSIONING | Result reuse 前必须重验 Version、Scope、Security Epoch、Snapshot TTL 和 Resource Integrity | `CapabilityReuseGuard` | `CAP_RESULT_REUSE_INVALID` | `CAP-050-UT`, `CAP-050-IT`, `CAP-050-FT` | `EV-CAP-050` |
| `RC-CAP-051` | SECURITY | ProviderInstance 表示业务连接实例，Credential Scope 表示授权能力，CapabilityConstraint 表示任务要求，三者不得混合 | `InstanceCredentialConstraintGuard` | `CAP_INSTANCE_CREDENTIAL_CONFLATION` | `CAP-051-UT`, `CAP-051-IT` | `EV-CAP-051` |
| `RC-CAP-052` | SECURITY | 07 可以选择 ProviderInstanceRef 或 ProviderPoolRef，但 08 只能在同一业务身份池内选择 RuntimeEndpointReplica | `BusinessRouteReplicaGuard` | `CAP_PROVIDER_INSTANCE_ROUTE_VIOLATION` | `CAP-052-UT`, `CAP-052-IT`, `CAP-052-FT` | `EV-CAP-052` |
| `RC-CAP-053` | SECURITY | 不同 Tenant、App、Region、Identity Mode 或 Effect Domain 之间切换必须重新 Selection、Prepare 和 Authorization | `ProviderIdentitySwitchGuard` | `CAP_PROVIDER_IDENTITY_SWITCH_UNGOVERNED` | `CAP-053-UT`, `CAP-053-IT`, `CAP-053-FT`, `CAP-053-E2E` | `EV-CAP-053` |
| `RC-CAP-054` | SECURITY | 07 不保存 Secret、Token、Credential Material 或可执行 Payload，只保存 Requirement 和 Ref | `CapabilitySecretBoundaryGuard` | `CAP_SECRET_MATERIAL_FORBIDDEN` | `CAP-054-UT`, `CAP-054-IT` | `EV-CAP-054` |
| `RC-CAP-055` | SECURITY | Capability Constraint 必须支持 Tenant、Workspace、Region、Data Residency、Identity Mode、Resource Scope 和 Provider Trust | `CapabilityConstraintValidator` | `CAP_CONSTRAINT_INCOMPLETE` | `CAP-055-UT`, `CAP-055-IT` | `EV-CAP-055` |
| `RC-CAP-056` | SECURITY | Provider Trust、签名、发布者、来源、许可证和供应链证明必须参与 Binding 与 Selection | `ProviderTrustGuard` | `CAP_PROVIDER_TRUST_UNSATISFIED` | `CAP-056-UT`, `CAP-056-IT` | `EV-CAP-056` |
| `RC-CAP-057` | SECURITY | Skill Instruction 与 Security Policy 冲突时 Security 决定优先，Skill 不得改变 Authorization 结果 | `SkillSecurityPrecedenceGuard` | `CAP_SKILL_SECURITY_OVERRIDE` | `CAP-057-UT`, `CAP-057-IT`, `CAP-057-FT` | `EV-CAP-057` |
| `RC-CAP-058` | SECURITY | Read-only、Write、External Effect、Destructive 等风险分类必须与 08/09 的 SideEffectClass 对齐 | `SideEffectClassificationGuard` | `CAP_SIDE_EFFECT_CLASS_MISMATCH` | `CAP-058-UT`, `CAP-058-IT`, `CAP-058-FT`, `CAP-058-E2E` | `EV-CAP-058` |
| `RC-CAP-059` | SECURITY | 数据等级和最小披露必须控制 Skill Metadata、Instruction、Resource 与 Tool Schema 的模型可见性 | `ModelVisibilityDataGuard` | `CAP_MODEL_VISIBILITY_VIOLATION` | `CAP-059-UT`, `CAP-059-IT` | `EV-CAP-059` |
| `RC-CAP-060` | SECURITY | 强制审计要求必须在 Selection 中传播为 Requirement，但持久化 Receipt 和 AuditEvent 分别归 11 与 10 | `AuditOwnershipBoundaryGuard` | `CAP_AUDIT_OWNERSHIP_VIOLATION` | `CAP-060-UT`, `CAP-060-IT`, `CAP-060-FT` | `EV-CAP-060` |
| `RC-CAP-061` | PERSISTENCE | PostgreSQL 保存 07 的定义、版本、Binding、Snapshot、Selection、状态转换和事件事实 | `CapabilityDomainStoreGuard` | `CAP_DOMAIN_STORE_MISSING` | `CAP-061-UT`, `CAP-061-IT` | `EV-CAP-061` |
| `RC-CAP-062` | PERSISTENCE | 大型 Skill Resource 和不可变包内容保存于 Object Store，数据库只保存 Ref、Hash 和 Metadata | `CapabilityLargePayloadGuard` | `CAP_LARGE_PAYLOAD_IN_DB` | `CAP-062-UT`, `CAP-062-IT` | `EV-CAP-062` |
| `RC-CAP-063` | PERSISTENCE | 定义发布、Active Pointer、Transition 和 Outbox 必须在同一事务中提交 | `CapabilityPublishTransactionGuard` | `CAP_PUBLISH_TRANSACTION_INCOMPLETE` | `CAP-063-UT`, `CAP-063-IT`, `CAP-063-FT`, `CAP-063-E2E` | `EV-CAP-063` |
| `RC-CAP-064` | PERSISTENCE | SelectionResult 与其候选摘要、Snapshot Ref、Policy Ref 和 Event 必须原子提交 | `SelectionTransactionGuard` | `CAP_SELECTION_TRANSACTION_INCOMPLETE` | `CAP-064-UT`, `CAP-064-IT`, `CAP-064-FT` | `EV-CAP-064` |
| `RC-CAP-065` | PERSISTENCE | Cache、搜索索引和 Runtime Health 只能作为 Projection，不得成为 Definition、Version 或 Revocation 的事实源 | `CapabilityProjectionAuthorityGuard` | `CAP_PROJECTION_AS_AUTHORITY` | `CAP-065-UT`, `CAP-065-IT` | `EV-CAP-065` |
| `RC-CAP-066` | PERSISTENCE | 所有状态转换必须使用 expected generation/CAS 并产生结构化 Transition Record | `CapabilityTransitionCASGuard` | `CAP_TRANSITION_CONFLICT` | `CAP-066-UT`, `CAP-066-IT` | `EV-CAP-066` |
| `RC-CAP-067` | PERSISTENCE | Outbox 提供 at-least-once 交付，消费者必须按 event_id 幂等 | `CapabilityOutboxGuard` | `CAP_OUTBOX_DELIVERY_INVALID` | `CAP-067-UT`, `CAP-067-IT`, `CAP-067-FT` | `EV-CAP-067` |
| `RC-CAP-068` | PERSISTENCE | 崩溃恢复必须覆盖资源提交、版本发布、Active 切换、Snapshot 构建和撤销传播中断 | `CapabilityCrashRecoveryGuard` | `CAP_RECOVERY_INCOMPLETE` | `CAP-068-UT`, `CAP-068-IT`, `CAP-068-FT`, `CAP-068-E2E` | `EV-CAP-068` |
| `RC-CAP-069` | PERSISTENCE | Capability、Skill、Binding、Snapshot、Selection 和 Outbox 必须有明确 Reconciler、Claim、Fencing 和人工升级 | `CapabilityReconcilerGuard` | `CAP_RECONCILIATION_REQUIRED` | `CAP-069-UT`, `CAP-069-IT`, `CAP-069-FT` | `EV-CAP-069` |
| `RC-CAP-070` | PERSISTENCE | 时间、TTL、Expiry 和 Lease-sensitive 比较必须使用数据库时间；进程内耗时使用 monotonic clock | `CapabilityTimeSemanticsGuard` | `CAP_TIME_SEMANTICS_INVALID` | `CAP-070-UT`, `CAP-070-IT`, `CAP-070-FT`, `CAP-070-E2E` | `EV-CAP-070` |
| `RC-CAP-071` | CONNECTOR | 核心代码不得包含针对飞书、Slack、GitHub、Jira 等具体 Provider 的条件分支 | `ProviderAgnosticCoreGuard` | `CAP_PROVIDER_HARDCODED` | `CAP-071-UT`, `CAP-071-IT` | `EV-CAP-071` |
| `RC-CAP-072` | CONNECTOR | 08 只实现少数通用 HTTP、CLI、MCP、SDK、RPC、Browser、Database 和 LocalFunction Adapter 家族 | `GenericAdapterFamilyGuard` | `CAP_ADAPTER_PROLIFERATION` | `CAP-072-UT`, `CAP-072-IT`, `CAP-072-FT`, `CAP-072-E2E` | `EV-CAP-072` |
| `RC-CAP-073` | CONNECTOR | 每个允许执行的 CLI 操作必须有结构化 Tool Manifest，禁止模型生成任意 Shell 字符串 | `CliManifestGuard` | `CAP_CLI_UNSTRUCTURED_EXECUTION` | `CAP-073-UT`, `CAP-073-IT`, `CAP-073-FT`, `CAP-073-E2E` | `EV-CAP-073` |
| `RC-CAP-074` | CONNECTOR | OpenAPI、MCP tools/list、CLI help 或 completion 可生成 Draft ToolDefinition/Binding Proposal，但不能直接 Active | `GeneratedDraftActivationGuard` | `CAP_GENERATED_DRAFT_ACTIVE` | `CAP-074-UT`, `CAP-074-IT`, `CAP-074-FT`, `CAP-074-E2E` | `EV-CAP-074` |
| `RC-CAP-075` | CONNECTOR | Connector Pack 必须支持 Provider 定义、Tool Manifest、Capability Mapping、Scope Mapping、Contract Test 和 Reconciliation 扩展 | `ConnectorPackSchemaGuard` | `CAP_CONNECTOR_PACK_INVALID` | `CAP-075-UT`, `CAP-075-IT` | `EV-CAP-075` |
| `RC-CAP-076` | CONNECTOR | 只有声明式 Mapping 无法表达的签名、流式、交互式 CLI、认证或 Reconciliation 才允许 Custom Extension | `CustomExtensionEscapeHatchGuard` | `CAP_CUSTOM_EXTENSION_UNJUSTIFIED` | `CAP-076-UT`, `CAP-076-IT` | `EV-CAP-076` |
| `RC-CAP-077` | CONNECTOR | 多 Provider fallback 必须识别共享 Backend、Quota 和 Effect Domain，禁止把同源实现冒充独立容灾 | `ProviderDiversityGuard` | `CAP_FALSE_REDUNDANCY` | `CAP-077-UT`, `CAP-077-IT`, `CAP-077-FT`, `CAP-077-E2E` | `EV-CAP-077` |
| `RC-CAP-078` | CONNECTOR | 副作用 ToolAttempt 为 UNKNOWN 时禁止跨 API、CLI、MCP Provider 盲目重试，必须先由 08 Reconcile | `UnknownEffectFallbackGuard` | `CAP_UNKNOWN_EFFECT_FALLBACK_FORBIDDEN` | `CAP-078-UT`, `CAP-078-IT`, `CAP-078-FT`, `CAP-078-E2E` | `EV-CAP-078` |
| `RC-CAP-079` | CONNECTOR | 07 必须提供 Discovery、Load、Binding、Availability、Selection、Fallback 和 Revocation 的结构化 Trace/Event | `CapabilityObservabilityGuard` | `CAP_TRACE_INCOMPLETE` | `CAP-079-UT`, `CAP-079-IT` | `EV-CAP-079` |
| `RC-CAP-080` | CONNECTOR | Target 转为 Current 必须有代码、Migration、Unit、Integration、Fault、E2E、Trace、Eval 和运行证据 | `CapabilityCompletionEvidenceGuard` | `CAP_COMPLETION_EVIDENCE_INSUFFICIENT` | `CAP-080-UT`, `CAP-080-IT`, `CAP-080-FT`, `CAP-080-E2E` | `EV-CAP-080` |


# Part VIII：测试、Requirement 与完成证据

# 80. Target 测试矩阵

```text
Definition / Version
    publish, activation CAS, deprecate, suspend, revoke, retire, illegal transition

Skill
    discovery precision, pinned skill failure, progressive load, resource hash,
    quarantine, permission non-amplification, executable resource boundary

Binding / Conformance
    curated/rule/model proposal, activation gate, partial coverage,
    same-name mismatch, different-name equivalence, expiry and revalidation

Availability / Selection
    all statuses, partial snapshot, TTL, deterministic filter/rank,
    tie-break, fallback ordering, no-compatible-candidate

Version / Inventory
    exact pinning, range resolution, MCP listChanged, OpenAPI change,
    CLI manifest change, Active Plan invalidation

Provider Instance
    Tenant/App/Region/Identity constraints, replica failover,
    forbidden cross-instance switch, credential boundary

Failure / Recovery
    object orphan, publish crash, outbox replay, snapshot crash,
    stale cache, revocation propagation, all Reconcilers idempotent

Connector
    generic HTTP/CLI/MCP adapters, generated Draft only,
    arbitrary shell rejection, Connector Pack partial activation,
    custom extension justification

Cross-module
    ActionProposal → ToolDefinitionRef → PreparedToolAction,
    Security deny, stale epoch, UNKNOWN effect, NOT_EXECUTED fallback,
    StepFeasibility and Replan ownership

Observability / Eval
    trace completeness, rejection reasons, selection quality,
    unused skill, token overhead, fallback success, schema invalidation latency
```

# 81. Fault Injection

至少覆盖：

```text
PostgreSQL commit success / Outbox publish failure
Object upload success / SkillVersion commit failure
Active Pointer CAS conflict
Binding activation after Conformance expiry
Tool Inventory changes during Plan validation
Provider Instance revoked between Selection and Prepare
Security Epoch changes during long wait
MCP response lost after external side effect
CLI process killed after output before receipt commit
Availability cache returns revoked Binding
Connector Pack activation crashes halfway
Reconciler claim expires and is taken over
```

# 82. 完成证据

Target 变为 Current 至少需要：

```text
代码和目录边界实现
PostgreSQL Migration 与约束
Unit Test
Integration Test
Fault Injection
E2E
真实 API / CLI / MCP Connector Conformance
Trace 与 Metric
Skill discovery / selection Eval
Revocation 与 recovery 运行证据
Security attack / supply-chain test
文档与 Agent 镜像同步
```

推荐状态：

```text
design available
internally consistent
contract-complete
implementation-spec-complete
program-ready
implementation available
measurement blocked
quality not yet proven
production ready
```

本文完成只能声明前五项，不得仅凭文档声明后四项。

# 83. Requirement Index



| ID | Category | Requirement |
| --- | --- | --- |
| `ARCH-CAP-001` | FOUNDATION | Capability / Skill 是业务能力语义、方法包、版本目录、可用性快照和选择治理模块，不得执行 Tool 或提交其他模块领域事实 |
| `ARCH-CAP-002` | FOUNDATION | Capability、Skill、Tool、Function Calling、MCP、API、CLI 和 Provider 必须使用本文的独立定义 |
| `ARCH-CAP-003` | FOUNDATION | Skill 必须通过 CapabilityRequirement 组合能力，不得把具体执行命令冒充方法步骤 |
| `ARCH-CAP-004` | FOUNDATION | API、CLI、SDK、MCP、Browser、RPC 是 Provider 或执行协议，不是业务 CapabilityKind |
| `ARCH-CAP-005` | FOUNDATION | Security Gate、Approval、Budget、Trace、Checkpoint、Lease 和 IdempotencyClaim 不是业务 Capability |
| `ARCH-CAP-006` | FOUNDATION | Capability / Skill 的 Target 主设计只能由单一正式文档承载，Agent 镜像必须字节级一致 |
| `ARCH-CAP-007` | FOUNDATION | Current、Gap 和 Measurement 只能由状态事实源维护，Target 文档不得冒充实现完成 |
| `ARCH-CAP-008` | FOUNDATION | 模型只能产生 Discovery、Mapping、Selection 或 Load Proposal，不得激活 Version、Binding 或执行 Tool |
| `ARCH-CAP-009` | FOUNDATION | 跨模块消息必须使用 CrossModuleEnvelopeV1 并携带版本、Hash、Tenant、Trace 和适用的 Security Epoch |
| `ARCH-CAP-010` | FOUNDATION | 未知 Version、Enum、Hash、Generation、Tenant 或安全上下文必须 fail-closed、quarantine 或返回显式 Blocked |
| `ARCH-CAP-011` | SKILL | SkillDefinition 是稳定逻辑身份，SkillVersion 发布后不可原地修改 |
| `ARCH-CAP-012` | SKILL | SkillVersion 必须结构化保存 Metadata、Instruction、ResourceManifest、CapabilityRequirement 和 AcceptanceCriteria |
| `ARCH-CAP-013` | SKILL | Skill discovery 只能先暴露 Metadata，Instruction 和 Resource 必须按需渐进加载 |
| `ARCH-CAP-014` | SKILL | 每次 Skill discovery 必须产生不可变 SkillDiscoveryResult 并记录候选、拒绝原因和版本 |
| `ARCH-CAP-015` | SKILL | 每次 Skill load 必须固定 SkillVersion、资源 Hash、Load Policy 和 Budget |
| `ARCH-CAP-016` | SKILL | Skill Resource 必须按类型、数据等级、完整性、来源和可执行性分类 |
| `ARCH-CAP-017` | SKILL | Skill 中的脚本、Delegate 或可执行资源不得由 Skill Loader 直接运行，必须引用 ToolDefinitionRef |
| `ARCH-CAP-018` | SKILL | Skill allowed_tools 或 allowed_capabilities 只能缩小候选范围，不能扩大授权 |
| `ARCH-CAP-019` | SKILL | 外部或用户提供的 Skill 默认不可信，必须经过签名、完整性、策略和风险校验 |
| `ARCH-CAP-020` | SKILL | SkillVersion 撤销、隔离或资源失效必须使依赖的 LoadResult 和 SelectionResult 失效并通知 Agent Core |
| `ARCH-CAP-021` | BINDING | CapabilityDefinition 必须使用稳定业务语义身份，不得直接使用 Provider Tool 名称作为主身份 |
| `ARCH-CAP-022` | BINDING | CapabilityVersion 必须定义 Canonical Input/Output Contract、风险、依赖、兼容和验收语义 |
| `ARCH-CAP-023` | BINDING | Portable Capability 与 Provider-native Capability 必须分离，禁止强行最低公分母映射 |
| `ARCH-CAP-024` | BINDING | CapabilityProviderBinding 必须把精确 CapabilityVersion 映射到版本化 ToolDefinitionRef 或领域 Port Ref |
| `ARCH-CAP-025` | BINDING | Binding 可由人工、规则或模型产生 Proposal，但只能由确定性验证和治理 Gate 激活 |
| `ARCH-CAP-026` | BINDING | 模型生成的 Binding Proposal 不得仅凭语义相似度进入 ACTIVE |
| `ARCH-CAP-027` | BINDING | ProviderConformanceRecord 必须覆盖输入、输出、副作用、幂等、Reconciliation、安全和错误语义 |
| `ARCH-CAP-028` | BINDING | 同名 Tool 不得自动视为同一 Capability，不同名 Tool 也不得因名称不同而自动判为不等价 |
| `ARCH-CAP-029` | BINDING | 一个 Capability 可以绑定多个 Provider，但必须记录 ProviderFamily、Backend、Quota 和 Effect Failure Domain |
| `ARCH-CAP-030` | BINDING | Connector Pack 只能作为安装输入，激活后必须拆分为各模块拥有的版本化领域事实 |
| `ARCH-CAP-031` | AVAILABILITY | CapabilityAvailabilitySnapshot 必须是不可变、版本化、带 TTL 和来源 Generation 的规划快照 |
| `ARCH-CAP-032` | AVAILABILITY | Availability 的 AVAILABLE 只表示可作为候选，不等价于 Authorization、Approval 或 Execution Readiness |
| `ARCH-CAP-033` | AVAILABILITY | Availability Entry 必须区分 AVAILABLE、DEGRADED、CONFIG_REQUIRED、UNAVAILABLE、VERSION_INCOMPATIBLE、POLICY_CONSTRAINED、REVOKED 和 UNKNOWN |
| `ARCH-CAP-034` | AVAILABILITY | PlanVersion 必须固定 CapabilityAvailabilitySnapshotRef，不能在恢复时静默重算并覆盖历史 |
| `ARCH-CAP-035` | AVAILABILITY | 每个 Action 执行前必须由 08/09/11 完成最新 Readiness Preflight，07 快照不能替代该检查 |
| `ARCH-CAP-036` | AVAILABILITY | 高风险 Action 对 Schema、Instance、Security Epoch、Credential 和 Approval 的陈旧容忍必须为零或显式 Policy |
| `ARCH-CAP-037` | AVAILABILITY | CapabilitySelectionResult 必须记录候选集、硬过滤、评分、选中 Binding、实例或实例池 Ref 和 fallback 顺序 |
| `ARCH-CAP-038` | AVAILABILITY | 模型可以提出 Provider Preference，但硬过滤、版本兼容和最终 Selection Commit 必须确定性执行 |
| `ARCH-CAP-039` | AVAILABILITY | StepFeasibilityDecision 归 Agent Core；07 只能提供 Requirement、Snapshot、Selection 和未满足约束 |
| `ARCH-CAP-040` | AVAILABILITY | Fallback Candidate 必须保持 Step Output Contract、风险上限、Tenant、数据驻留和副作用语义 |
| `ARCH-CAP-041` | VERSIONING | Skill 和 Capability Requirement 可以声明兼容版本范围，Selection 必须解析为精确版本 |
| `ARCH-CAP-042` | VERSIONING | PlanVersion 必须固定精确 CapabilityVersion、BindingVersion、ToolDefinitionRef 和 Schema Hash |
| `ARCH-CAP-043` | VERSIONING | PreparedToolAction 必须再次固定精确 ToolDefinitionVersion、ProviderInstanceRef 和 Prepared Hash |
| `ARCH-CAP-044` | VERSIONING | Tool Inventory 变化必须创建新 Generation 和 ToolDefinitionVersion，不得原地改 Schema |
| `ARCH-CAP-045` | VERSIONING | MCP listChanged、OpenAPI 更新、CLI Manifest 更新必须触发 Binding 重新验证或失效 |
| `ARCH-CAP-046` | VERSIONING | Deprecated Version 可按 Policy 服务已固定 Run，但不得用于新的 Selection；Revoked Version 默认立即阻止新执行 |
| `ARCH-CAP-047` | VERSIONING | 未知或不兼容 ToolDefinitionVersion 必须返回显式 Failure，不得按相近名称猜测替代 |
| `ARCH-CAP-048` | VERSIONING | Active Plan 引用失效时由 Agent Core 决定 Wait、Fallback、Replan 或 Block，07 不得改写 Plan |
| `ARCH-CAP-049` | VERSIONING | SelectionResult、LoadResult 和 Snapshot 必须有 ResultValidity，支持 VALID、STALE、REVOKED、SUPERSEDED 和 UNKNOWN_VALIDITY |
| `ARCH-CAP-050` | VERSIONING | Result reuse 前必须重验 Version、Scope、Security Epoch、Snapshot TTL 和 Resource Integrity |
| `ARCH-CAP-051` | SECURITY | ProviderInstance 表示业务连接实例，Credential Scope 表示授权能力，CapabilityConstraint 表示任务要求，三者不得混合 |
| `ARCH-CAP-052` | SECURITY | 07 可以选择 ProviderInstanceRef 或 ProviderPoolRef，但 08 只能在同一业务身份池内选择 RuntimeEndpointReplica |
| `ARCH-CAP-053` | SECURITY | 不同 Tenant、App、Region、Identity Mode 或 Effect Domain 之间切换必须重新 Selection、Prepare 和 Authorization |
| `ARCH-CAP-054` | SECURITY | 07 不保存 Secret、Token、Credential Material 或可执行 Payload，只保存 Requirement 和 Ref |
| `ARCH-CAP-055` | SECURITY | Capability Constraint 必须支持 Tenant、Workspace、Region、Data Residency、Identity Mode、Resource Scope 和 Provider Trust |
| `ARCH-CAP-056` | SECURITY | Provider Trust、签名、发布者、来源、许可证和供应链证明必须参与 Binding 与 Selection |
| `ARCH-CAP-057` | SECURITY | Skill Instruction 与 Security Policy 冲突时 Security 决定优先，Skill 不得改变 Authorization 结果 |
| `ARCH-CAP-058` | SECURITY | Read-only、Write、External Effect、Destructive 等风险分类必须与 08/09 的 SideEffectClass 对齐 |
| `ARCH-CAP-059` | SECURITY | 数据等级和最小披露必须控制 Skill Metadata、Instruction、Resource 与 Tool Schema 的模型可见性 |
| `ARCH-CAP-060` | SECURITY | 强制审计要求必须在 Selection 中传播为 Requirement，但持久化 Receipt 和 AuditEvent 分别归 11 与 10 |
| `ARCH-CAP-061` | PERSISTENCE | PostgreSQL 保存 07 的定义、版本、Binding、Snapshot、Selection、状态转换和事件事实 |
| `ARCH-CAP-062` | PERSISTENCE | 大型 Skill Resource 和不可变包内容保存于 Object Store，数据库只保存 Ref、Hash 和 Metadata |
| `ARCH-CAP-063` | PERSISTENCE | 定义发布、Active Pointer、Transition 和 Outbox 必须在同一事务中提交 |
| `ARCH-CAP-064` | PERSISTENCE | SelectionResult 与其候选摘要、Snapshot Ref、Policy Ref 和 Event 必须原子提交 |
| `ARCH-CAP-065` | PERSISTENCE | Cache、搜索索引和 Runtime Health 只能作为 Projection，不得成为 Definition、Version 或 Revocation 的事实源 |
| `ARCH-CAP-066` | PERSISTENCE | 所有状态转换必须使用 expected generation/CAS 并产生结构化 Transition Record |
| `ARCH-CAP-067` | PERSISTENCE | Outbox 提供 at-least-once 交付，消费者必须按 event_id 幂等 |
| `ARCH-CAP-068` | PERSISTENCE | 崩溃恢复必须覆盖资源提交、版本发布、Active 切换、Snapshot 构建和撤销传播中断 |
| `ARCH-CAP-069` | PERSISTENCE | Capability、Skill、Binding、Snapshot、Selection 和 Outbox 必须有明确 Reconciler、Claim、Fencing 和人工升级 |
| `ARCH-CAP-070` | PERSISTENCE | 时间、TTL、Expiry 和 Lease-sensitive 比较必须使用数据库时间；进程内耗时使用 monotonic clock |
| `ARCH-CAP-071` | CONNECTOR | 核心代码不得包含针对飞书、Slack、GitHub、Jira 等具体 Provider 的条件分支 |
| `ARCH-CAP-072` | CONNECTOR | 08 只实现少数通用 HTTP、CLI、MCP、SDK、RPC、Browser、Database 和 LocalFunction Adapter 家族 |
| `ARCH-CAP-073` | CONNECTOR | 每个允许执行的 CLI 操作必须有结构化 Tool Manifest，禁止模型生成任意 Shell 字符串 |
| `ARCH-CAP-074` | CONNECTOR | OpenAPI、MCP tools/list、CLI help 或 completion 可生成 Draft ToolDefinition/Binding Proposal，但不能直接 Active |
| `ARCH-CAP-075` | CONNECTOR | Connector Pack 必须支持 Provider 定义、Tool Manifest、Capability Mapping、Scope Mapping、Contract Test 和 Reconciliation 扩展 |
| `ARCH-CAP-076` | CONNECTOR | 只有声明式 Mapping 无法表达的签名、流式、交互式 CLI、认证或 Reconciliation 才允许 Custom Extension |
| `ARCH-CAP-077` | CONNECTOR | 多 Provider fallback 必须识别共享 Backend、Quota 和 Effect Domain，禁止把同源实现冒充独立容灾 |
| `ARCH-CAP-078` | CONNECTOR | 副作用 ToolAttempt 为 UNKNOWN 时禁止跨 API、CLI、MCP Provider 盲目重试，必须先由 08 Reconcile |
| `ARCH-CAP-079` | CONNECTOR | 07 必须提供 Discovery、Load、Binding、Availability、Selection、Fallback 和 Revocation 的结构化 Trace/Event |
| `ARCH-CAP-080` | CONNECTOR | Target 转为 Current 必须有代码、Migration、Unit、Integration、Fault、E2E、Trace、Eval 和运行证据 |


# 84. 完成状态

本文作为单一正式 Target 架构文档，目标完成状态为：

```text
design available
internally consistent
contract-complete
implementation-spec-complete
program-ready
```

不能由本文单独证明：

```text
implementation available
measurement proven
quality proven
production ready
```

后续 Program 不得自行改变以下已确认原则：

```text
Capability 是业务语义，不是具体 API/CLI/MCP Tool。
Skill 是组合 Capability 的方法包。
07 管理 Definition、Version、Binding、Conformance、Availability 和 Selection。
08 管理 Provider、ToolDefinition、Prepare、Execute、Receipt 和 Reconcile。
09 管理 Authorization、Approval、Credential 和 Revocation。
Requirement 可用版本范围；Plan/Action 必须固定精确版本。
07 选择业务实例或实例池；08 只选择同一身份池的技术 Replica。
Plan 固定规划快照；每个 Action 执行前重新 Preflight。
核心 Provider 无关；使用通用 Adapter、声明式 Manifest、Connector Pack 和少量 Custom Extension。
副作用 UNKNOWN 时禁止跨 Provider 盲目重试。
模型只产生 Proposal，不能激活、授权或执行。
```

# RB-BLUE-REPAIR-001 Architecture Part-A Blue Repair

## 状态

`BLUE_PROPOSAL / COUNTER_RETEST_REOPENED / CANONICAL_SYNC_NOT_APPLIED`

这是对 Round-001 的结构化修复候选，不是 Current Architecture，也不是已实现 Runtime。

## Problem / Goal

候选产品要支持法律案件材料的可追溯分析，但当前事实仍不能证明完整法院 As-Is Workflow、
质量增益或 Native Runtime 必要。Part A 的目标是先建立一个最小、可替换、可审计的边界：

```text
Matter / DocumentVersion / Evidence
→ Proposal / Retrieval / Capability Observation
→ Domain Validation / Review
→ Finding / WorkProduct
```

它不把“法律回答更准”写成 Current，也不要求第一版拥有 Graph、长期 Memory、Persistent
Agent Team 或自研 Native Runtime。

## Product Context

| Surface | 责任 | 不负责 |
|---|---|---|
| WorkBuddy / Dify / Zuno Web 等 Host | 交互、会话和可替换 Runtime Provider | 不拥有 Zuno Canonical Domain Fact |
| Legal Domain Backend | Matter、Evidence、Proposal 验证、Review、版本和审计 | 不负责通用 Agent UI 或任意模型编排 |
| Agent Runtime Provider | Run、Plan、Step、Checkpoint、Resume、预算和协作 | 不直接写 Canonical Legal Fact |
| Knowledge Provider | Raw Artifact 派生索引、Retrieval、引用候选 | 不把相似度命中变成事实 |
| Tool/Sandbox Provider | 授权后的外部 Effect、Receipt 和 Reconciliation | 不绕过 Policy、Approval 或 Domain Owner |

## Architectural Drivers

1. 证据与 Citation 必须可回链，不能只依赖最终 LLM Judge。
2. Canonical Domain State 必须只有一个 Owner，并与 Runtime Control State 分开。
3. 不可逆 Tool Effect 必须有 Approval、Idempotency、EffectReceipt 和 Unknown Outcome 恢复。
4. Graph、Memory、Multi-Agent、Native Runtime 和物理服务数量必须能够被 Benchmark 或 Spike
   删除。
5. Python-only 与 Microservice 是 Target Constraint，但服务数量和 Provider 仍需证据。
6. 历史事实、当前仓库证据和 Target 设计不能互相升级。

## System Context

```text
External Host / Zuno Web / Court or Law-firm System
                     │ API / MCP
                     ▼
             Platform / Domain Boundary
             ├─ Canonical Domain State
             ├─ Proposal Validation / Review
             └─ Audit / Permission
                     │ contracts
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
 Runtime Provider  Knowledge     Tool/Sandbox
 control state     projections   effect receipts
       │             │             │
       └─────────────┼─────────────┘
                     ▼
                 Eval / Trace
```

这是一张逻辑关系图。它不等于最终物理服务数量，也不证明上述 Provider 当前都已经实现。

## Domain Boundary 与 Canonical State

### Canonical Owner

Domain Owner 负责接受经过 Schema、Provenance、Evidence、Permission、Version 和 Review Gate
的 Proposal，形成正式的 Domain Version。Agent、Knowledge、Memory 和外部算法只能产生：

```text
Proposal / Candidate / Observation / Reference / Receipt
```

最低候选 Canonical State：

```text
Matter
DocumentVersion
Evidence
Fact / Claim
Finding
HumanDecision
WorkProduct
```

`Event`、`Conflict`、`Dispute`、`LegalIssue` 和 `ApplicableLaw` 是否都要成为独立 Canonical
Object 仍需根据真实任务和 Mutation/Review 测试决定；不得因为名词出现在文档中就全部冻结。

### State Ownership

| State | Owner | 可接受输入 | Rebuild / Recovery |
|---|---|---|---|
| Canonical Domain State | Domain Service | 已验证 Proposal、Review Decision | 版本化、审计、人工对账 |
| Runtime Control State | Agent Runtime | Plan/Step/Run/Checkpoint | 从 Run/Plan/Checkpoint 恢复，不冒充 Domain Fact |
| Knowledge Projection | Knowledge Service/Worker | Raw Artifact、Domain Reference | 可从 Raw/Canonical Reference 重建 |
| Memory Context | Memory Policy + Provider | Scope-approved Context | Provider 可替换，不能作为 Canonical Fact SoR |
| Tool Effect Receipt | Tool/Sandbox | Authorized Effect Request | Provider Operation ID、Reconcile、人工处理 Unknown |

## Main Runtime

Runtime 的 first-class contract 是 `Run / Plan / Step / Checkpoint / Budget / Review Interrupt`，
不是 `Fact / Finding / HumanDecision`。Runtime 可以根据 EvidenceRequirement、staleness 和
Review 状态规划下一步，但正式 Domain State 仍由 Domain Owner 提交。

Native Domain-aware Runtime 仍是 `DEFERRED/HYPOTHESIS`。如果 WorkBuddy + Legal Backend 或
普通 Workflow 能提供同样的 Domain Conditions、Evidence Gate、Staleness 和 Reconciliation，
Native Runtime 必须删除或外部化。

## Trust Boundary 与 Critical Contracts

### Tool Effect Contract

```text
proposed
→ validated
→ authorized
→ approval_required / ready
→ executing
→ succeeded
   or failed_known
   or outcome_unknown
→ reconciliation
```

`timeout` 不是 `failed_known`。当外部写操作结果未知时，必须先用 `Provider Operation ID`、
EffectReceipt 或 Provider 查询对账；不能盲目重试。

### Tool Gate

```text
Agent Proposal
→ Tool Policy
→ Schema Validation
→ Security Gate
→ Budget Gate
→ Approval Gate
→ Side-effect Classification
→ Execution
→ Observation / Receipt
→ Reconciliation / Audit
```

Policy、Approval、Budget、Secret Scope、Tenant Scope 和 Tool Version 必须绑定到同一 Effect
Request。旧 Approval 不能授权新参数或新 ToolVersion。

## Data / Provider Boundary

| Store / Provider | State class | Owner | Rebuildable | 删除条件 |
|---|---|---|---|---|
| PostgreSQL | Canonical Domain / Control reference | Domain/Runtime Owner | 通过版本和迁移恢复 | 无其他 SoR 依赖时才替换 |
| Object Storage | immutable/raw artifact | Document/Knowledge Owner | 原始材料可重新导入 | 受保留、删除和审计政策约束 |
| Vector Index | derived semantic projection | Knowledge Provider | 从 Raw/Chunk/Embedding 重建 | Hybrid 足够且成本无收益时删除 |
| Lexical Index | derived lexical projection | Knowledge Provider | 从源文档重建 | 任务无 lexical 收益时删除 |
| Graph Projection | derived relationship projection | Knowledge Provider | 从来源关系重建 | Graph Kill Test 不通过时删除 |
| Redis/Queue | ephemeral coordination/delivery | Runtime/Worker Owner | 从 Job/Run/Outbox 重建 | 无实际 TTL/lease/backpressure 需求时删除 |
| Memory Provider | scoped context projection | Memory Policy Owner | 从允许的 Context/Domain Reference 重建 | DB+Checkpoint 满足需求时替换 |

具体 Neo4j、Milvus、Elasticsearch、Redis、RabbitMQ 和 OpenViking 仍是 Provider 候选或历史
上下文，不能仅凭当前仓库组件名升级为历史主链路或 Target 必选项。

## Happy / Failure / Recovery

### Happy Path

```text
Create Matter
→ register DocumentVersion / Raw Artifact
→ ingest / retrieve Evidence Candidate
→ Agent proposes Fact/Event/Finding
→ Domain validates provenance/version/permission
→ Review if required
→ commit Domain Version
→ produce WorkProduct / citation trace
```

### Failure Path

```text
Schema / Permission / Approval stale
→ refused or review

Provider timeout on read
→ bounded retry if transient

External write timeout
→ outcome_unknown
→ reconcile
→ succeeded / failed_known / manual review

Checkpoint complete but Domain commit absent
→ do not claim business completion

Domain commit present but Checkpoint old
→ reconcile generation and suppress duplicate Effect
```

所有异步 Job 必须至少有 Job Identity、Idempotency Key、Attempt、Timeout、Cancellation、Backoff、
Dead-letter/Manual Review 和 Backpressure 语义。具体 MQ Provider 不在本 Part A 冻结。

## Physical Service Boundary

Microservice 是 Owner Target Constraint，但本修复不批准固定五服务。当前最小物理候选为：

```text
Platform / Domain
Agent Runtime
Knowledge Workers / Retrieval
Tool / Sandbox
Eval / Observability Worker
```

每个边界必须有 Independent Scaling、Failure Isolation、Security Isolation、Independent
Deployment、Distinct Availability、Data Ownership 或 Lifecycle 中至少一个强理由；否则允许
合并为模块或 Worker。一个 Agent 不自动成为一个 Service。Kubernetes、Kafka、Database-per-
Service、Saga、2PC 和 Event Sourcing 仍不默认引入。

## Reversal Criteria

以下结果会触发删除或外部化：

- A/B/C 显示 Native Runtime 与 Host+Backend 等价：删除 Native Runtime。
- Graph Kill Test 对主要 Query Class 无 Evidence/Recall 收益：删除 Graph Projection。
- Memory Ablation 显示 Matter DB + Checkpoint 足够：替换 Memory Provider。
- Crash/Effect Test 证明某独立服务无资源、失败或安全隔离收益：合并物理部署。
- Tool/Sandbox 现有 MCP/Provider 已满足 Policy、Receipt、Reconcile 和 Audit：删除重复自研 Runtime。

## 当前 Gate

Part A 已完成结构化 Blue Repair，但没有通过 Counter Retest。`Final P0=12`、`Critical
Closure=0/12`、`Evidence Coverage=0% closure-grade`；因此只能作为 Lab Candidate，不能同步
Canonical Architecture。

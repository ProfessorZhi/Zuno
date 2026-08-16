# ADR 0007：Reuse-first 与可替换能力 Provider 边界

status: accepted-target
decision_date: 2026-08-12
updated: 2026-08-16
scope: Zuno 全局架构、Canonical Taxonomy、Build-vs-Buy 评审和后续 Provider 适配
taxonomy_note: 当前以 ADR-0013 冻结的九模块为准；Memory / Context 是 Optional Provider Boundary，不新增第十逻辑模块。
refinement_note: 2026-08-16 修正旧模块编号，并把长期 Memory 明确收敛为 Zuno-owned policy / typed contract + replaceable provider，而不是由某个 Memory 产品拥有业务事实。

## Context

Zuno 的 Target Architecture 定义了大量 Agent、RAG、Memory、Tool、Security 和 Infrastructure 语义，但项目事实和 Current Evidence 尚不足以证明这些能力都应该由 Zuno 自研、部署或长期维护。

如果继续用“通用开源方案不够企业级”解释自研，会把品牌印象误当成架构证据；如果直接 Fork 一个完整 Agent / RAG / Memory 产品，又可能继承上游 Domain Model、Runtime、Persistence、Security、Failure 和升级路径，形成难以退出的长期 Private Fork。

Memory 尤其容易产生另一种误区：把“有向量库 / 有 OpenViking / 有 Mem0 / 有 Graphiti”直接写成“系统拥有长期记忆”。真正困难的问题不是把文本存进去，而是决定 **什么有资格被记住、谁未来可以召回、何时陈旧、冲突怎么处理、删除和 Legal Hold 怎样作用、记忆能不能进入模型，以及记忆绝不能被误当成法律 Evidence / Domain Truth**。

## Decision

Zuno 正式采用：

> **Reuse First, Build Requires Evidence**

能力采用顺序为：

```text
Complete Product
→ Fork
→ Reuse Subsystem
→ Framework
→ Component
→ Protocol / SDK
→ Build Delta
```

每个候选必须先经过五道 Gate：

```text
G1 Capability Fit
G2 Contract Fit
G3 Modification Surface
G4 Operational / License Fit
G5 Evidence
```

Gate 结果只能是 `PASS`、`FAIL` 或 `UNKNOWN`。`UNKNOWN` 不得被叙事改写为通过，也不得自动触发 `BUILD` 或最终 `ADOPT`。

Zuno 的正式宏观架构为：

```text
Zuno Domain / Control Plane
  Matter / DocumentVersion / Claim / Evidence / Finding
  HumanDecision / WorkProduct
  KnowledgeGeneration / Readiness / EvidenceCandidate
  Plan / PlanVersion / AgentRun / RunOutcome
  Capability Contract / Eligibility
  PreparedAction / EffectReceipt / Reconciliation
  Security Decision / Approval / Audit / Lifecycle
  Eval Contract / Release Evidence
          │
          │ Canonical Contracts
          ▼
Replaceable Capability Providers
  DocumentPipelineBackend
  RetrievalBackend / GraphRetrievalBackend / Reranker
  ContextMemoryBackend
  LangGraph Runtime Provider / Checkpointer
  Connector / MCP Provider
  ModelProvider / EmbeddingProvider / Parser
  Telemetry / Eval Provider
```

Provider 可以负责存储、索引、解析、检索、图遍历、上下文组织、图执行或外部连接，但不得直接提交 Zuno 的 Canonical Business Fact。Provider 的输出必须先被规范化为 `Proposal`、`Observation`、`Candidate`、`Snapshot`、`Reference` 或 Owner-specific `Receipt`，再由对应 Zuno Owner 做版本、权限、质量、状态和审计确认。

## 为什么不把完整产品 Fork 作为默认策略

完整产品 Fork 不是被禁止，而是必须证明修改面可控。若为了满足 Zuno Contract 需要穿透以下五个核心面：

```text
S1 Domain Model
S2 Runtime / State
S3 Persistence
S4 Security
S5 Failure / Effect
```

并且还要长期维护上游升级、部署和回滚，则这通常已经不是轻量二开，而是长期 Private Fork。优先寻找官方 Extension Point、API、SDK、MCP、Provider 或 Adapter 边界；只有这些边界无法满足且 G5 证据证明自建必要时，才进入 Build Delta。

## Canonical Contract 与当前九模块 Owner

- **01 Application & Integration** 拥有 Zuno-side External Request / Invocation / Publication / Delivery 事实；Generic Host 可以拥有最终 UI，但 Provider 不能替 01 宣布 Zuno-side publication complete。
- **02 Legal Domain & Work Product** 拥有 Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct、Formal Admission、AdmissionReceipt 和历史 Citation Binding；Parser、Retriever、Memory、Model 都不能直接写这些 Canonical Facts。
- **03 Knowledge & Evidence** 拥有 KnowledgeGeneration、ReadinessDecision、EvidenceCandidate、CitationLineage、RetrievalRound / assessment 等知识派生语义；Retrieval / Graph / Parser Provider 只提供候选和可重建 projection。
- **04 Agent Runtime & Control** 拥有 AgentRun、PlanVersion、StepRun、RunOutcome、Replan Barrier 和 Runtime completion；LangGraph / Checkpointer 提供图执行与 durable-control primitive，不拥有 Domain completion。
- **05 Capability & Skill** 拥有 Capability semantic contract、CapabilityVersion、ProviderBinding、Conformance、Eligibility 和专业 Proposal；论文算法、模型、规则、外部 API 都只是 Provider / Research Artifact 候选。
- **06 Tool Runtime & Effects** 拥有 PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt 和 external-effect recovery；MCP 只提供工具暴露 / 协议，不拥有授权或现实效果事实。
- **07 Model Gateway** 拥有 ModelRole、RoutingDecision、ModelCallAttempt、Usage / Cost 和 model qualification；LiteLLM / vLLM / 云模型等若采用，只是 Provider。
- **08 Security & Governance** 拥有 AuthorizationDecision、ApprovalDecision、SecurityEpoch、Secret / lifecycle policy、Mandatory Audit requirement；Policy / Secret Provider 不能绕过这个 Owner。
- **09 Observability & Evaluation** 拥有 telemetry / eval projection、DatasetVersion、EvalRun、ReleaseEvidence 和 complexity kill test；LangSmith / OTel / Judge Provider 不能替 Zuno 宣布业务成功或 Production Ready。

## Optional Context / Memory Provider Boundary

Memory / Context 不恢复为第十模块。Zuno 自己拥有 **Memory Policy / Typed Contract / Recall Eligibility**，底层 Provider 承担通用存储、组织和召回。

### 1. 必须先分清五种不同状态

```text
Runtime Checkpoint
!= Working Context
!= Episodic Memory
!= Semantic Memory
!= Procedural Memory
!= Domain Truth / Knowledge Evidence
```

- Runtime Checkpoint：04 的执行控制状态；
- Working Context：本 Run / Step 为完成任务临时需要的上下文；
- Episodic Memory：过去任务中“发生过什么”的结构化记录；
- Semantic Memory：经过资格判断后可长期复用的稳定上下文；
- Procedural Memory：经过 Eval / Review 证明可复用的处理经验或策略候选；
- Context Archive：Provider 可以提供的大规模历史资源、Session、Skill / Resource 层级导航。

这些都不能自动变成 02 Evidence / Finding，也不能替代 03 Knowledge Source Authority。

### 2. Memory 写入采用 Candidate → Admission Policy，而不是 LLM 直接写

目标链路：

```text
Run / Human feedback / Final Reflection
→ MemoryCandidate
→ type classification
→ source / provenance check
→ tenant / user / Matter scope check
→ security / privacy / lifecycle check
→ freshness / temporal validity check
→ conflict / duplicate check
→ consolidation / supersession proposal
→ MemoryWriteDecision
→ Provider persistence
```

模型只能提出 `MemoryCandidate`、分类和 consolidation proposal。它不能因为“这条经验很重要”就自行永久写入，也不能删除与自己冲突的旧记录。

Li & Wu (2025), DOI `10.1002/sdr.70008` 对 generative-agent memory 的分析表明，relevance、recency、importance 是常见记忆检索信号，同时 Prompt 对记忆写入 / 总结 / 召回的控制会影响系统行为。这一研究支持 Zuno 把这些因素变成可审计 feature / policy，而不是藏在一个不可版本化的“记住重要内容”Prompt 里。

### 3. Recall 是 Context Candidate，不是事实证明

长期 Memory Recall 至少绑定：

```text
memory_id / version
memory_type
source refs / provenance
scope
created_at / observed_at
valid_from / valid_to when applicable
importance / confidence when applicable
provider / index generation
security / lifecycle refs
superseded_by / conflict refs
```

召回排序可以综合 semantic relevance、recency、importance 和任务适配度；但任何被召回项只成为 `ContextCandidate`。在正式法律分析里，若它提出了事实性主张，仍必须回到 DocumentVersion / Knowledge / Domain Evidence 路径验证。

### 4. Episodic Memory 不保存隐藏 Chain-of-Thought

推荐结构化保存：

```text
Situation
Task / Plan summary
Accepted actions / observations
Outcome
Failure class
Evidence refs
Human modification / feedback
LessonCandidate
```

不要求保存模型隐藏推理链。Procedural Memory 只有在多次任务、Eval 或人工 Review 证明可复用后才可以晋升，不能把一次 Reflection 自动变成长期策略。

### 5. Forgetting 与删除分开

“从长期 Memory 删除”首先意味着 future recall eligibility 被撤销。物理 bytes 的 purge、备份保留、Audit retention 和 Legal Hold 由 08 的 lifecycle policy 决定。被 Legal Hold 保留的 bytes 不能因此重新获得 recall 资格。

### 6. Provider 角色与候选方向

Provider 选择继续遵守 G1–G5，不在本 ADR 宣布单一胜者：

- OpenViking 类 Context Filesystem：适合层级 Context Archive / progressive context loading 的候选；
- Graphiti 类 temporal graph：适合时间关系 / supersession context projection 的候选；
- Mem0 / LangMem 类 memory framework：适合作为通用记忆 baseline / primitive 候选；
- PostgreSQL / vector / graph 自建：只在 Contract 或运营边界证明必要时建设最小 Build Delta。

这些名称是 `Conditional Candidate`，不是 Current、默认部署或“最优解”。License、私有化、数据出口、性能和 Eval 都必须独立验证。

### 7. Memory cache 必须版本感知

Context / Memory cache 不能只按 query 文本命中。至少绑定 memory version / provider generation、scope、安全 / lifecycle epoch、必要 Domain / Knowledge version 和 retrieval policy version；否则旧 Memory 会跨权限、跨 Matter 或跨新证据继续污染新任务。

### 8. Long-term Memory 继续受 Kill Test

09 至少比较：

```text
No long-term memory
Working context only
Typed episodic memory
Typed episodic + semantic / procedural memory
External Context Provider enabled
```

指标包括 task completion、unsupported claim、stale-memory error、context relevance、human correction、token、latency、cost 和 privacy / scope violation。没有稳定边际收益时，Long-term Memory 必须允许关闭或缩小。

## Security、License、Migration 与 Exit

Provider 适配必须经过 08 Security & Governance 的 Tenant、Matter、Data Classification、Secret、Network、Supply Chain、Permission、Revocation 和 Lifecycle 检查；Provider 的自动 Memory、Connector Permission、Tool Effect 或外部授权不能绕过 Zuno Security Gate。

G4 必须记录许可证、版本、部署模型、数据出口、升级责任、依赖供应链、隔离和退出路径。候选即使功能匹配，也不能因为许可证或运营边界未核验而进入最终 Adopt。

任何未来 Adapter / Provider 计划都必须先定义：输入输出 Contract、版本兼容、失败与重试、幂等 / 对账、数据回迁或退出、Shadow / Benchmark 方式和删除路径。本 ADR 不授权实现这些计划。

## Alternatives

1. **全部 Native Build**：拒绝为默认策略。每项自研都必须承担 G1–G5 证明责任。
2. **Fork 一个完整平台**：保留候选，但 Modification Surface 穿透 S1–S5 时通常不值得。
3. **直接把候选产品当作 Zuno 事实源**：拒绝。Provider 输出不能替代 Domain、Knowledge、Security、Effect、Recovery 或 Eval Contract。
4. **单一 Memory 产品拥有“所有记忆”**：拒绝。Runtime、Context、长期 Memory、Knowledge 和 Domain 的生命周期与权威不同。
5. **能力级 Adapter / Provider**：默认评估路径，因为它保留 Zuno 领域事实和治理语义，同时允许复用成熟子系统。

## Verification

本 ADR 的文档一致性由架构文档集、语义对齐、内部链接和 Repository Verifier 检查；具体候选的 G1–G5 必须由官方资料、源码、测试、License、Spike 和 Benchmark 证据支持后，才可升级决策状态。

本 ADR 是 `accepted-target`，不是 Current、实现证明、论文复现证明或 Production Readiness 证明。
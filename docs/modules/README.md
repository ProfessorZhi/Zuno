# Zuno 模块架构

总体架构已经冻结九个逻辑责任域，模块分解闸门已经打开。本目录现在完成了九个模块的第一轮 **Deep Design V1（深化设计 V1）**：每篇都以 Human-first Part A 解释真实问题、完整流程、异常路径和边界，再用 Part B 的 B1–B14 固定工程责任、状态、失败、恢复、安全、持久化、评测和实现约束。

这仍然不是 Module Detail Freeze（模块细节冻结），也不是 Implementation Authorization（实现授权）。字段级 Contract、最终状态枚举、数据库表、Migration、API 和物理服务只有在后续逐模块 Review 和工程证据充分后才能冻结。

```text
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_deep_design: AVAILABLE_V1
module_deep_design_coverage: 9/9
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

## 九个模块已经完成第一轮深化

| 编号 | 模块 | 深化后首先回答的问题 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration（应用与集成） | 请求怎样进入 Zuno，简单任务为什么可以保持简单，结果由谁发布、交付、失效通知和对接 Host？ | [01](01-application-integration.md) |
| 02 | Legal Domain & Work Product（法律领域与工作成果） | 什么才是正式、长期、可审计的法律业务事实，候选怎样经过准入成为工作成果？ | [02](02-legal-domain-work-product.md) |
| 03 | Knowledge & Evidence（知识与证据） | 哪一版材料现在真的可用于这个任务，知识生成、证据候选和引用怎样构建与恢复？ | [03](03-knowledge-evidence.md) |
| 04 | Agent Runtime & Control（智能体运行与控制） | 复杂任务怎样计划、并行、验收、暂停、重试、重规划、对账和恢复？ | [04](04-agent-runtime-control.md) |
| 05 | Capability & Skill（专业能力与技能） | 论文算法、Prompt、模型和规则怎样成为版本化、可替换、可评测的专业能力？ | [05](05-capability-skill.md) |
| 06 | Tool Runtime & Effects（工具运行与外部效果） | 一个现实动作怎样准备、授权、审批、执行、去重，并在结果未知时对账？ | [06](06-tool-runtime-effects.md) |
| 07 | Model Gateway（模型网关） | 模型怎样按角色、资格、安全、预算和质量统一路由，而不把模型输出变成业务事实？ | [07](07-model-gateway.md) |
| 08 | Security & Governance（安全与治理） | 长任务中谁现在可以做什么、怎样持续授权、审批、使用 Secret、审计和治理数据生命周期？ | [08](08-security-governance.md) |
| 09 | Observability & Evaluation（可观测性与评测） | 系统发生了什么、关键事实怎样关联、复杂度是否真的值得保留、发布质量怎样被证明？ | [09](09-observability-evaluation.md) |

02 / 03 是第一组深挖的事实边界；01 / 04 / 05 / 06 / 07 / 08 / 09 在本轮补齐到同一深度标准。**九篇的“深化完成”只表示设计材料达到可审查状态，不表示实现、测量或生产资格完成。**

## 先从三条真实任务主线理解九个模块

九个模块不是每个请求都必须依次经过的固定流水线。任务越简单，路径越短；只有风险、恢复和长期业务状态要求增加时，才引入更多责任域。

### 主线一：简单法律问答

例如用户问“合同第 8 条写了什么”。应用与集成先明确事项和材料范围，安全与治理给出当前授权，知识与证据确认对应材料对这个任务已经就绪并返回来源，模型网关完成受控生成，应用与集成检查答案资格并发布。

```text
01 请求 / Scope
→ 08 当前授权
→ 03 task-level Readiness + Retrieval
→ 07 受控模型生成
→ 01 Answer Publication
```

这条路径不默认需要 Dynamic Plan、多智能体、长期 Memory 或 GraphRAG。Generic Host（通用 Agent 宿主）只要能遵守同一安全、知识和发布 Contract，也可以承担它。

### 主线二：复杂法律分析

复杂事项包含多版材料、证据依赖、专业分析、并行步骤、人工复核和正式 WorkProduct（工作成果）。

```text
01 请求 / Scope
→ 08 当前授权
→ 03 DocumentVersion 对应的知识就绪 / EvidenceCandidate
→ 04 Plan / Step / Parallel / Join
↔ 05 专业 Capability
↔ 07 模型角色调用
→ 02 Finding Proposal / HumanDecision / Formal Admission
→ AdmissionReceipt + WorkProduct Version
→ 01 Publication / Delivery
```

这里必须保持：Runtime 负责“这次执行怎样继续”，Capability 负责“怎样做专业分析”，Domain 负责“什么最终成为正式法律业务事实”。

### 主线三：带现实副作用的任务

当任务需要向外围法院系统提交、更新或通知，动作候选不能直接执行。

```text
04 / 05 Action Proposal
→ 06 PreparedAction
→ 08 当前 Authorization / Approval / Audit Requirement
→ 06 ToolAttempt
→ EffectReceipt
→ Outcome Unknown 时 Reconciliation
→ 02 必要时 Formal Admission
→ 01 Delivery / Notification
```

现实结果未知时禁止 Blind Retry（盲重试）。这是和普通模型失败最重要的区别之一。

## 九模块之间最重要的事实所有权

模块可以运行在同一个 Python 进程、同一个 PostgreSQL 实例或同一组 Worker 上，但“谁说了算”必须唯一。

| 事实 / 决定 | 权威责任域 | 其他模块最多能做什么 |
| --- | --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 法律领域 | 读取引用、提出候选，不直接改正式状态 |
| Formal Admission、AdmissionReceipt、WorkProductCitationBinding、Domain invalidation truth | 02 法律领域 | 04 用回执恢复；01 做发布和失效交付 |
| KnowledgeGeneration、task-level ReadinessDecision、EvidenceCandidate、CitationLineage | 03 知识与证据 | 02 可以接纳候选为正式 Evidence / 引用 |
| AgentRun、PlanVersion、StepRun、Branch / Join、Budget、Checkpoint、RunOutcome | 04 运行与控制 | 其他模块返回事实 / receipt，不接管计划状态 |
| Capability identity / version、Provider Conformance、Eligibility、专业 Proposal | 05 专业能力 | 04 调度；02 决定是否正式接纳 |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 工具运行 | 08 决定是否允许；外部系统拥有其内部最终事实 |
| Model role mapping、ModelRoutingDecision、ModelCallAttempt、Quota、Usage / Cost | 07 模型网关 | 09 评测；08 决定外发 / Credential policy |
| AuthorizationDecision、Security Epoch、ApprovalDecision、EffectiveLifecycleDecision、Audit Requirement | 08 安全与治理 | 各 Store / 执行边界负责自己的 enforcement fact |
| Trace、Metric、Eval Dataset / Result、Experiment、Release Evaluation Evidence | 09 可观测性与评测 | 各模块提供脱敏事实引用；09 不接管业务真相 |
| External Task Intake、InvocationDecision、AnswerPublicationDecision、Delivery、Invalidation Delivery、Consumer Ack Observation | 01 应用与集成 | 外部 Host 仍拥有自己的最终 UI / 展示事实 |

## 几组绝对不能再次混淆的边界

第一组是 **正式事实与知识派生**：

```text
DocumentVersion canonical identity → 02
KnowledgeGeneration lifecycle      → 03

EvidenceCandidate != Evidence
CitationLineage != WorkProductCitationBinding
KnowledgeGeneration lifecycle != task-level ReadinessDecision
```

知识模块说明“系统加工了哪版材料、现在能检索出什么、候选怎样被找到”；领域模块说明“业务最终接纳了什么、正式成果当时实际引用了什么”。

第二组是 **执行控制与业务提交**：

```text
Checkpoint completed
!=
Domain committed

Formal Admission-required Step
必须有 matching AdmissionReceipt
```

第三组是 **专业分析与现实动作**：

```text
Capability Proposal
!=
PreparedAction
!=
ToolAttempt
!=
EffectReceipt
```

第四组是 **安全决定与执行事实**：

```text
AuthorizationDecision
!=
ApprovalDecision
!=
HumanDecision
```

08 决定“能不能做 / 是否需要批准”，06 / 03 / 07 / 02 等模块证明“是否真的执行”，HumanDecision 是 02 的专业业务决定。

第五组是 **领域失效与外部传播**：

```text
WorkProduct invalidated → 02
Invalidation delivered  → 01
Consumer acknowledged   → 01 的 observation
```

第六组是 **观测与审计**：

```text
Telemetry / Trace
!=
Durable Audit
!=
Business Truth
```

## 全模块共同遵守的架构不变量

1. **模型只产生 Proposal。** 模型、Capability、Retrieval、Memory、Specialist Agent 都不能直接提交 Canonical Domain State。
2. **文件上传不等于知识就绪。** Readiness 是 task scope + DocumentVersion + KnowledgeGeneration + requirement + security 的判断。
3. **原生运行时中的任务一定有 Plan。** 简单 = Deterministic Single-Step；复杂 = Dynamic DAG。
4. **PlanVersion 激活后不可原地修改。** Replan 创建新版本；并行重规划经过 Replan Barrier。
5. **Retry != Replan != Reconcile。** 执行暂时失败才重试；计划假设失效要重规划；现实副作用结果未知要对账。
6. **领域状态与运行控制状态分开。** Domain Store 与 LangGraph Checkpointer 的语义不同，不用 Checkpoint 证明正式提交。
7. **安全是持续门禁。** 新读取、模型外发、Secret、Tool Effect 和 Formal Admission 都消费当前安全决定。
8. **高风险 Effect 必须保护审计与幂等。** Mandatory Audit 要求存在时先取得持久化证明；Outcome Unknown 禁止 Blind Retry。
9. **可观测性不是业务真相。** OTel / LangSmith 等只提供 Projection、diagnosis 和 Eval；关键恢复依赖 Owner facts / receipts。
10. **复杂度必须被测量。** Native Runtime、Long-term Memory、Specialist / Multi-Agent、GraphRAG 都是 measurement-gated / evidence-gated。
11. **逻辑模块不等于微服务。** 默认物理起点仍是 Modular Python Backend + Workers where justified。
12. **Platform / Infrastructure 不是第十个业务模块。** 它提供 PostgreSQL、Object Store、Queue / Worker、Checkpointer adapter、CAS、Lease、Fencing、Clock、Network、Secret Delivery 等原语，但不拥有业务成功事实。
13. **Memory / Context 不是一级模块。** 它是 Optional Provider Boundary，不能覆盖 Domain truth 或安全策略。
14. **Current / Target / Gap 必须分开。** 文档写得完整不证明代码已经实现。

## 每篇模块文档现在采用同一 B1–B14 工程模板

```text
B1  Scope / Global Invariants
B2  Responsibility / Ownership
B3  Upstream / Downstream
B4  Authoritative Facts / Core Objects
B5  Cross-boundary Contracts
B6  Normal Flow
B7  State / Lifecycle
B8  Failure Taxonomy
B9  Retry / Replan / Reconcile / Recovery / Idempotency
B10 Security / Approval / Audit
B11 Persistence / Transaction Boundaries
B12 Observability / Evaluation
B13 Current / Target / Gap / Evidence
B14 Code / Database / Migration Constraints
```

Part A 必须先让人理解“为什么需要这个模块、任务怎样经过它、异常以后发生什么”；Part B 才把同一事实写成可供实现、测试和 Agent 消费的精确规格。Part A 和 Part B 如果无法保持一致，应该暴露 Architecture Gap，而不是分别维护两套事实。

## 推荐的设计依赖顺序与当前进度

设计依赖仍然建议按“先确定真相，再确定可信执行，再确定智能执行，最后组合入口”理解：

```text
Stage 1: 02 法律领域 + 03 知识证据          DEEP DESIGN V1 AVAILABLE
Stage 2: 08 安全治理 + 06 工具外部效果      DEEP DESIGN V1 AVAILABLE
Stage 3: 05 专业能力 + 04 运行控制          DEEP DESIGN V1 AVAILABLE
Stage 4: 07 模型网关 + 09 可观测性评测      DEEP DESIGN V1 AVAILABLE
Final:   01 应用与集成                       DEEP DESIGN V1 AVAILABLE
```

这个顺序是**设计依赖**，不是运行时调用顺序。九篇现在都已经完成第一轮深化，下一步不应再机械扩写，而应进入 Cross-Module Consistency Review（跨模块一致性审查）、场景盘问和字段级模块 Review。

## 下一道门不是“立即实现全部模块”

九模块 Deep Design V1 完成后，仍然保持：

```text
module_detail_freeze: NOT_YET
implementation_authorization: NO
quality_proven: NO
production_readiness: NOT_ESTABLISHED
```

下一步应针对完整 E2E 场景和异常路径盘问：每个事实到底谁创建、谁修改、谁使其失效、谁删除、谁恢复；跨边界 Contract 是否足以支持崩溃恢复；安全和预算能否被旁路；是否存在两个模块都声称拥有同一状态；是否存在同一词在不同文档表达不同含义。

只有具体模块完成字段级 Contract、状态转换、错误语义、持久化、Migration、测试与工程证据 Review 后，才考虑 Module Detail Freeze 或生成对应 Codex 实现任务。

## Platform / Infrastructure 与 Optional Context

Platform / Infrastructure（平台与基础设施）继续是责任层，不是第十个逻辑模块。它提供物理耐久、网络、队列、Worker、检查点、CAS、Lease、Fencing、Secret Delivery、Backup / Restore 等原语；各逻辑模块拥有这些原语承载的业务成功语义。

Memory / Context（记忆与上下文）继续是可选 Provider 边界。Working / Session Context 可以由 Host 或 Runtime 管理；Long-term Memory 只有在消融评测证明收益后才启用，可以由 OpenViking、通用 Host 或其他 Provider 提供。Memory Entry 不能成为 Matter / Evidence / Finding / WorkProduct 的替代真相。

## 状态总结

九个模块的第一轮 Deep Design 已经可用于架构 Review、Codex 任务准备和跨模块盘问；但它们仍属于 Target Design。

`design available` 不等于 `implementation available`；`implementation available` 不等于 `quality proven`；`quality proven` 也不自动等于 `production ready`。
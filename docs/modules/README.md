# Zuno 模块架构

总体架构已经冻结九个逻辑责任域，模块分解闸门已经打开。本目录给出九个模块的 **Design Baseline V1（设计基线 V1）**：边界、事实所有权、主要运行链、失败语义和跨模块 Contract 已经可以作为后续详细设计与实现评审的共同基线，但字段级 Contract、状态枚举、数据库表、Migration 和物理服务仍未冻结。

```text
module_taxonomy: FROZEN
module_design_baseline: AVAILABLE_V1
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

## 先从三条真实任务主线理解九个模块

九个模块不是每个请求都必须依次经过的固定流水线。简单任务应该保持简单，只有业务风险和恢复要求真正增加时，才引入更多责任域。

**简单问答**通常是：应用与集成确认请求范围，安全与治理给出当前授权，知识与证据确认材料可用并检索原文，模型网关完成受控生成，应用与集成检查答案资格并返回。它不默认需要动态规划、多智能体、长期记忆或复杂运行时。

```text
01 应用与集成
→ 08 安全与治理
→ 03 知识与证据
→ 07 模型网关
→ 01 答案发布
```

**复杂法律分析**增加了跨材料版本、证据依赖、专业能力、多步执行、人工复核和正式工作成果。运行控制负责“这次任务怎样继续”，专业能力负责“怎样分析”，法律领域负责“什么最终成为正式业务事实”。

```text
01 请求与范围
→ 08 当前授权
→ 03 材料就绪 / 证据
→ 04 多步运行与控制
↔ 05 专业能力
↔ 07 模型网关
→ 02 正式准入 / 工作成果
→ 01 交付
```

**带现实副作用的任务**还要回答“外部世界究竟发生了什么”。候选动作不能直接执行；执行前要重新授权、必要审批和审计，执行后要保存效果回执，结果未知时进入对账而不是盲目重试。

```text
04 / 05 候选动作
→ 08 授权 / 审批 / 审计要求
→ 06 执行 / 效果回执 / 对账
→ 02 必要时正式准入
→ 01 通知 / 交付
```

## 九个模块分别先回答什么

| 编号 | 模块 | 最先回答的问题 |
| --- | --- | --- |
| 01 | Application & Integration（应用与集成） | 请求怎样进入 Zuno，结果由谁组合、发布、交付和通知？ |
| 02 | Legal Domain & Work Product（法律领域与工作成果） | 什么才是长期、正式、可审计的法律业务事实？ |
| 03 | Knowledge & Evidence（知识与证据） | 哪一版材料现在真的可用于这个任务，证据和引用怎样恢复？ |
| 04 | Agent Runtime & Control（智能体运行与控制） | 复杂任务怎样计划、并行、暂停、重试、重规划和恢复？ |
| 05 | Capability & Skill（专业能力与技能） | 研究算法和模型怎样成为可版本化、可替换、可评测的专业能力？ |
| 06 | Tool Runtime & Effects（工具运行与外部效果） | 外部动作怎样安全执行、去重，并在结果未知时对账？ |
| 07 | Model Gateway（模型网关） | 不同模型怎样按角色、预算、安全和质量要求统一调用？ |
| 08 | Security & Governance（安全与治理） | 现在谁可以对什么做什么、谁批准、数据怎样保留与删除？ |
| 09 | Observability & Evaluation（可观测性与评测） | 系统发生了什么，复杂度是否真的值得保留？ |

## 全模块共同遵守的十条原则

1. **文件上传不等于知识可用。** 正式任务必须知道材料版本、知识生成版本、任务范围和最低能力要求。
2. **模型只产生候选。** 模型、检索、专业能力和专家智能体都不能直接提交正式法律业务状态。
3. **原生运行时中的任务一定有计划。** 简单任务使用确定性单步计划，复杂任务使用动态 DAG；不能通过“直接回答”绕过计划、预算、跟踪、答案策略和运行结果。
4. **领域状态与运行控制状态分开。** PostgreSQL 保存长期业务事实，LangGraph Checkpointer 保存图控制状态；检查点完成不证明领域提交成功。
5. **正式准入需要耐久因果。** 需要正式领域提交的步骤，没有匹配的 `AdmissionReceipt`（正式准入回执）就不能宣布完成。
6. **重试、重规划和对账是三种不同问题。** 执行临时失败才重试；计划假设失效要重规划；现实副作用结果未知要对账。
7. **安全是持续门禁。** 长任务中的新读取、模型外发、秘密使用、工具执行和正式提交必须重新消费当前安全决定。
8. **可观测性不是业务真相。** Trace、Metric 和 LangSmith 适合诊断和评测，不能替代领域事实、授权、效果回执或强制审计。
9. **复杂度必须被测量。** GraphRAG、长期记忆、专业多智能体和原生运行时只有在对照实验中证明收益才保留。
10. **逻辑模块不等于微服务。** 默认仍是模块化 Python 后端加必要 Worker；物理服务拆分受 ADR-0012 的证据门控。

## 事实所有权先定清楚

模块可以共用 Python 进程、数据库实例或 Worker，但不能共用“谁说了算”的语义。

| 事实 / 决定 | 权威责任域 | 其他模块最多能做什么 |
| --- | --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 法律领域 | 读取引用、提出候选，不直接改正式状态 |
| 正式准入、AdmissionReceipt、历史引用绑定、领域失效 | 02 法律领域 | Runtime 读取回执恢复；01 负责失效交付 |
| KnowledgeGeneration、Knowledge Readiness、EvidenceCandidate、CitationLineage | 03 知识与证据 | 02 可把候选准入为正式 Evidence / 引用 |
| AgentRun、PlanVersion、StepRun、Branch/Join、Budget、Checkpoint、RunOutcome | 04 运行与控制 | 其他模块返回事实或回执，不接管计划状态 |
| Capability 定义、版本、Provider Conformance、专业候选结果 | 05 专业能力 | 04 选择和调度；02 决定是否正式接受 |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 工具运行 | 08 决定是否允许；外部系统拥有其内部最终事实 |
| 模型角色映射、路由决定、调用尝试、Quota、Usage / Cost | 07 模型网关 | 09 评测模型质量；08 控制模型外发与凭证 |
| Authorization、Security Epoch、Approval、Lifecycle Policy、Audit Requirement | 08 安全与治理 | 各 Store / 执行边界负责执行并保存自身执行事实 |
| Trace、Metric、Eval Dataset、Evaluation Result、Measurement Evidence | 09 可观测性与评测 | 各模块输出脱敏事实引用；09 不接管业务真相 |
| 请求组合、Zuno 侧答案发布、WorkProduct 交付、失效通知、消费者确认观测 | 01 应用与集成 | 外部 Host 仍拥有自己的最终界面 / 展示决定 |

几个最容易混淆的边界保持不变：检索引用链归知识与证据，正式工作成果的历史引用绑定归法律领域；领域结果已经失效，不等于失效通知已经送达；运行检查点完成，不等于正式领域提交成功；专业能力提出“应该做什么”，工具运行负责“现实动作怎样发生”；Trace 可以帮助诊断，但不能替代耐久审计事实。

## Platform / Infrastructure 与 Memory 不重新变成一级模块

Platform / Infrastructure（平台与基础设施）是责任层，不是第十个逻辑模块。它提供 PostgreSQL、对象存储、队列 / Worker、检查点适配器、CAS、Lease、Fencing、Clock、Index Adapter、Backup / Restore、Network 和 Secret Delivery 等物理原语；上层模块拥有这些原语承载的业务成功语义。

Memory / Context（记忆与上下文）是可选 Provider 边界。Working / Session Context 可由 Host 或运行控制管理；长期记忆只有在消融评测证明收益后才启用，可由 OpenViking、通用宿主或其他 Provider 提供。任何记忆都不能升级为正式业务真相，也不能绕过安全和生命周期政策。

## 推荐的详细设计顺序

详细设计不按编号机械推进，而按“先确定真相，再确定可信执行，再确定智能执行，最后组合入口”的依赖关系推进：

```text
第一阶段：02 法律领域与工作成果 + 03 知识与证据
第二阶段：08 安全与治理 + 06 工具运行与外部效果
第三阶段：05 专业能力与技能 + 04 智能体运行与控制
第四阶段：07 模型网关 + 09 可观测性与评测
最后：01 应用与集成
```

这个顺序是设计依赖，不是运行时调用顺序，更不是服务拓扑。

## 每篇模块文档怎样读

每篇文档都分成两层。Part A 先从真实问题、完整场景、失败和设计理由讲清楚“为什么”；Part B 再给后续工程和 Codex 使用的稳定骨架。

Part B 统一采用以下十四个主题：

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

字段级 Contract、完整状态枚举、ORM、表结构和 API 只有在对应模块详细评审通过后才能冻结。Part B 也不能偷偷新增 Part A 没解释过的重大语义；如果模块深挖发现跨模块矛盾，应回到总体架构或 ADR，而不是在单个模块里自行改全局原则。

## 什么叫“模块设计完成”

文档写满不代表模块完成。一个 Target 要进入 Current，至少需要与风险匹配的代码、Migration、单元测试、集成测试、故障注入、E2E、Trace / Eval 或真实运行证据。模块详细设计结束时还必须能回答：失败怎样传播、谁拥有恢复事实、幂等靠什么、权限变化怎样处理、怎样证明没有旁路，以及哪些能力仍然只是假设。

## 相关入口

- [总体架构](../architecture/architecture.md)：九个责任域为什么存在，以及跨域状态、失败和恢复语义。
- [ADR-0008](../decisions/0008-legal-domain-kernel-and-host-boundary.md)：最小法律领域内核、通用宿主边界和 A/B/C Kill Test。
- [ADR-0012](../decisions/0012-evidence-gated-physical-service-split.md)：为什么九个逻辑模块不能自动变成九个服务。
- [ADR-0013](../decisions/0013-round-02-responsibility-taxonomy.md)：九模块、平台责任层和可选上下文边界。
- [ADR-0014](../decisions/0014-round-02-cross-boundary-authority-and-recovery.md)：准入、引用、生命周期、失效交付和关键恢复。
- [Current Evidence](../evidence/README.md)：代码、测试、运行和评测现在到底证明了什么。
- [Human-first 文档标准](../governance/human-first-documentation-standard.md)：Part A / Part B 的写作约束。

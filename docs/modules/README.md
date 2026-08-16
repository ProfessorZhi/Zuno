# Zuno 模块架构

总体架构已经冻结九个逻辑责任域，Module Decomposition Gate 已打开。本目录现在给出九个模块的**设计骨架**：它们把总体架构的责任边界落到可继续评审的模块层，但还不是字段级冻结、数据库设计或实现授权。

第一次阅读不必从编号顺序开始。更自然的路径是先看“业务事实如何成立”，再看“执行怎样可信”，最后看“系统怎样被调用和观测”：

```text
02 法律领域与工作成果 ── 03 知识与证据
            ↓                    ↓
08 安全与治理 ───────── 06 工具运行与外部效果
            ↓                    ↓
05 专业能力与技能 ───── 04 智能体运行与控制
            ↓                    ↓
07 模型网关 ─────────── 09 可观测性与评测
                     ↓
             01 应用与集成
```

这张图表示**设计依赖**，不是运行时调用顺序，也不意味着这些责任域需要拆成独立服务。

## 九个模块

| 编号 | 模块 | 先回答的问题 | 文档 |
| --- | --- | --- | --- |
| 01 | Application & Integration（应用与集成） | 请求从哪里进入，Zuno 与法院系统或通用宿主怎样组合结果和发布？ | [01](01-application-integration.md) |
| 02 | Legal Domain & Work Product（法律领域与工作成果） | 哪些法律事实、人工决定和正式成果值得长期保存？ | [02](02-legal-domain-work-product.md) |
| 03 | Knowledge & Evidence（知识与证据） | 材料什么时候真的可用于任务，系统怎样恢复证据和引用？ | [03](03-knowledge-evidence.md) |
| 04 | Agent Runtime & Control（智能体运行与控制） | 复杂任务怎样计划、并行、暂停、恢复和重规划？ | [04](04-agent-runtime-control.md) |
| 05 | Capability & Skill（专业能力与技能） | 研究算法、模型和外部能力怎样成为可替换的专业能力？ | [05](05-capability-skill.md) |
| 06 | Tool Runtime & Effects（工具运行与外部效果） | 外部动作怎样授权、执行、去重，并在结果未知时对账？ | [06](06-tool-runtime-effects.md) |
| 07 | Model Gateway（模型网关） | 不同模型怎样按角色、预算、安全和质量要求被统一调用？ | [07](07-model-gateway.md) |
| 08 | Security & Governance（安全与治理） | 谁现在可以做什么，谁批准，数据应保留多久？ | [08](08-security-governance.md) |
| 09 | Observability & Evaluation（可观测性与评测） | 系统怎样被诊断、比较和证明复杂度值得保留？ | [09](09-observability-evaluation.md) |

## 事实所有权先定清楚

模块可以共用 Python 进程、数据库实例或 Worker，但不能共用“谁说了算”的语义。

| 事实 / 问题 | 权威责任域 |
| --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 法律领域与工作成果 |
| 材料处理进度、知识生成版本、Knowledge Readiness、检索候选、CitationLineage | 03 知识与证据 |
| AgentRun、PlanVersion、Step、Budget、Checkpoint、控制恢复 | 04 智能体运行与控制 |
| Capability 定义、版本、Provider Conformance、专业候选结果 | 05 专业能力与技能 |
| PreparedAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 工具运行与外部效果 |
| 模型路由、调用尝试、配额、Usage / Cost Receipt | 07 模型网关 |
| Authorization、Security Epoch、Approval、Lifecycle Policy、Audit Requirement | 08 安全与治理 |
| Trace、Metric、Eval Dataset、Evaluation Result | 09 可观测性与评测 |
| 请求组合、Zuno 侧发布、WorkProduct 交付、失效通知和消费者确认观测 | 01 应用与集成 |

几个最容易混淆的边界继续保持：检索引用链归知识与证据，正式工作成果的历史引用绑定归法律领域；领域结果已经失效，不等于失效通知已经送达；运行检查点已经完成，也不等于正式领域提交已经成功；Trace 可以帮助诊断，但不能替代耐久审计事实。

## 每个模块文档怎样读

每篇文档都分成两层：

- **Part A — Human Narrative**：先从实际问题和场景解释为什么需要这个模块、怎样工作、失败后怎么办，以及为什么不应该把它并入邻居模块。
- **Part B — Engineering / Agent Reference**：把同一设计压缩成 Scope、Ownership、跨边界 Contract、状态、失败、恢复、安全、持久化和证据要求，供后续 Codex、Reviewer 和测试设计使用。

Part B 不能偷偷新增 Part A 没解释过的重大设计；模块深挖如果发现跨模块矛盾，应回到总体架构或 ADR，而不是在某个模块内部自行改掉全局规则。

## 设计骨架与实现的边界

当前这些模块文档的状态统一为：

```text
module_taxonomy: FROZEN
module_design_skeleton: AVAILABLE
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

方向已经可以作为后续模块访谈和详细设计的基线，但以下内容仍需要逐模块确认：具体状态枚举、字段级 Contract、API、ORM、数据库表、Migration、Provider 选择、性能阈值和部署拆分。

`Current` 只能由代码、Migration、Test、Trace、Eval 或运行证据证明。模块文档中的 Target 不因为写得完整就自动变成 Current；当前工程事实统一回到 [Evidence](../evidence/README.md)。

## 相关入口

- [总体架构](../architecture/architecture.md)：九个责任域为什么存在，以及跨域状态、失败和恢复语义。
- [ADR-0008](../decisions/0008-legal-domain-kernel-and-host-boundary.md)：最小法律领域内核与 Host 边界。
- [ADR-0013](../decisions/0013-round-02-responsibility-taxonomy.md)：九模块、平台责任层和可选上下文边界。
- [ADR-0014](../decisions/0014-round-02-cross-boundary-authority-and-recovery.md)：准入、引用、生命周期、失效交付和关键恢复。
- [Current Evidence](../evidence/README.md)：实现和质量现在到底证明了什么。
- [Human-first 文档标准](../governance/human-first-documentation-standard.md)：Part A / Part B 的写作约束。

# Zuno 模块架构

总体架构已经冻结九个逻辑责任域，Module Decomposition Gate 已打开。本目录给出九个模块的 **design skeleton（设计骨架）**：方向、边界和主要事实所有权已经可以作为后续评审基线，但字段级 Contract、数据库、API、部署和实现仍未冻结，也没有自动获得实现授权。

第一次阅读不要先把九个模块想成九个服务。更容易理解的方法，是先看三个真实任务怎样穿过这些责任域。

## 三条主线先把系统串起来

**简单问答**不需要经过所有模块。用户问一份合同里的具体条款时，应用入口确定范围，安全与治理确认当前访问资格，知识与证据确认材料可用并找到依据，模型网关完成受控生成，应用与集成检查结果资格后返回。只要问题本身不需要跨运行的正式领域状态，就没有理由为了“统一架构”强行启动复杂运行时。

```text
01 应用与集成
  → 08 安全与治理
  → 03 知识与证据
  → 07 模型网关
  → 01 发布结果

09 可观测性与评测横向记录和评价
```

**复杂法律分析**会多出计划、专业能力、人工判断和正式成果。材料就绪以后，运行与控制组织多步任务，专业能力产生候选分析，必要时调用模型，最终由法律领域在证据、权限和人审条件成立后完成正式准入；应用与集成再负责把工作成果交付给产品或外部宿主。

```text
01 请求入口
  → 08 当前授权
  → 03 材料与证据
  → 04 多步运行控制
  → 05 专业能力
  ↔ 07 模型网关
  → 02 正式准入 / 工作成果
  → 01 交付与发布

09 负责观测、评测和复杂度证明
```

**带外部副作用的任务**还必须回答现实世界到底发生了什么。专业能力或运行时只能提出候选动作；安全与治理负责当前授权和必要审批，工具运行负责准备、执行、幂等和未知结果对账。若外部动作随后导致正式法律状态变化，再由法律领域独立准入。

```text
04 / 05 候选动作
  → 08 授权 / 审批 / 审计要求
  → 06 执行 / 回执 / 对账
  → 02 必要时正式准入
  → 01 交付或通知
```

这三条主线说明一个重要原则：**九个模块是责任边界，不是每个请求都必须经过的固定流水线。**

## 推荐的设计顺序

详细设计不按编号机械推进。先把长期业务事实和证据边界讲清楚，再讨论可信执行，最后设计组合入口和观测面：

```text
第一组：02 法律领域与工作成果 + 03 知识与证据
第二组：08 安全与治理 + 06 工具运行与外部效果
第三组：05 专业能力与技能 + 04 智能体运行与控制
第四组：07 模型网关 + 09 可观测性与评测
最后：01 应用与集成
```

这是**推荐设计顺序**，不是运行时依赖图。模块可以在同一个 Python 后端、同一个数据库实例或同一组 Worker 中实现；是否拆成独立网络服务仍受物理部署证据门控。

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

模块可以共用代码和基础设施，但不能共用“谁说了算”的语义。

| 事实 / 问题 | 权威责任域 |
| --- | --- |
| Matter、DocumentVersion、Claim、Evidence、Finding、HumanDecision、WorkProduct | 02 法律领域与工作成果 |
| 材料处理进度、知识生成版本、Knowledge Readiness、检索候选、CitationLineage | 03 知识与证据 |
| AgentRun、PlanVersion、Step、Budget、Checkpoint、控制恢复 | 04 智能体运行与控制 |
| Capability 定义、版本、Provider Conformance、专业候选结果 | 05 专业能力与技能 |
| PreparedToolAction、ToolAttempt、EffectReceipt、ReconciliationReceipt | 06 工具运行与外部效果 |
| 模型路由、调用尝试、配额、Usage / Cost Receipt | 07 模型网关 |
| Authorization、Security Epoch、Approval、Lifecycle Policy、Audit Requirement | 08 安全与治理 |
| Trace、Metric、Eval Dataset、Evaluation Result | 09 可观测性与评测 |
| 请求组合、Zuno 侧发布、WorkProduct 交付、失效通知和消费者确认观测 | 01 应用与集成 |

最容易混淆的几条边界继续保持：检索引用链归知识与证据，正式工作成果的历史引用绑定归法律领域；领域结果失效不等于失效通知已经送达；运行检查点完成不等于正式领域提交成功；专业能力提出“应该怎样分析”，工具运行证明“外部动作怎样执行以及发生了什么”；Trace 可以帮助诊断，但不能替代耐久审计事实。

## 模块之外还有什么

**Platform / Infrastructure Responsibility Layer（平台与基础设施责任层）**提供 PostgreSQL、对象存储、队列、Worker、检查点适配器、网络、秘密交付、备份恢复等物理原语，但不拥有第十种业务成功事实。

**Optional Context / Memory Provider Boundary（可选上下文 / 记忆提供方边界）**不是一级逻辑模块。工作上下文可以由宿主或运行控制管理；长期记忆只有在消融评测证明收益后才启用，也可以由 OpenViking 或其他 Provider 提供。

## 每个模块文档怎样读

每篇文档都分成两层：

- **Part A — Human Narrative**：先从实际问题和完整场景解释为什么需要这个模块、正常情况下怎样工作、出问题后怎么办、与邻居模块为什么要分开。
- **Part B — Engineering / Agent Reference**：把同一设计压缩成 Scope、Ownership、跨边界 Contract、状态、失败、恢复、安全、持久化和证据要求，供后续 Codex、Reviewer 和测试设计使用。

Part B 不能偷偷新增 Part A 没解释过的重大设计。模块深挖如果发现跨模块矛盾，应回到总体架构或 ADR，而不是在某个模块内部自行改掉全局规则。

## 设计骨架与实现的边界

当前状态统一为：

```text
module_taxonomy: FROZEN
module_design_skeleton: AVAILABLE
module_detail_freeze: NOT_YET
implementation_authorization: NO
production_readiness: NOT_ESTABLISHED
```

方向已经可以作为后续模块访谈和详细设计的基线，但仍需要逐模块确认：具体状态枚举、字段级 Contract、API、ORM、数据库表、Migration、Provider 选择、性能阈值和物理部署拆分。

`Current` 只能由代码、Migration、Test、Trace、Eval 或运行证据证明。模块文档中的 Target 不因为写得完整就自动变成 Current；当前工程事实统一回到 [Evidence](../evidence/README.md)。

## 相关入口

- [总体架构](../architecture/architecture.md)：九个责任域为什么存在，以及跨域状态、失败和恢复语义。
- [ADR-0008](../decisions/0008-legal-domain-kernel-and-host-boundary.md)：最小法律领域内核与 Host 边界。
- [ADR-0013](../decisions/0013-round-02-responsibility-taxonomy.md)：九模块、平台责任层和可选上下文边界。
- [ADR-0014](../decisions/0014-round-02-cross-boundary-authority-and-recovery.md)：准入、引用、生命周期、失效交付和关键恢复。
- [Current Evidence](../evidence/README.md)：实现和质量现在到底证明了什么。
- [Human-first 文档标准](../governance/human-first-documentation-standard.md)：Part A / Part B 的写作约束。

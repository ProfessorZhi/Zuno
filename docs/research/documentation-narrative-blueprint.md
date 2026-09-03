# Documentation Narrative Blueprint

> status: research-blueprint
> rewrite_authorization: no

本文件保存本轮研究得到的 Human-first 写作蓝图。它指导下一轮 `project / architecture / modules` 重写，但**本身不拥有 Project Truth 或 Architecture Truth**。

## 1. 全局问题

Zuno 文档当前最大的质量问题不是技术深度不足，而是：

> **很多局部论证都正确，但整篇没有让读者持续知道“为什么我们必须走到下一步”。**

因此下一轮不能再做“九模块平均加深”，而应先建立一个 Global Story Spine。

## 2. Project Story

`docs/project/project.md` 应承担真实项目故事，不伪造 Architecture Evolution 为真实历史。

建议叙事主线：

```text
葛季栋 / LIPLAB 长期智慧司法与软件工程研究
→ 多个独立 Research Artifacts
→ 为什么这些局部成果值得进入一个真实工程系统
→ 最简单产品：Generic Agent Host + Legal RAG + Research Models / Skills
→ 这个方案其实能解决大量简单任务
→ 真正不可外包的 Engineering Gap 出现
→ Research Artifact 需要稳定 Capability / Qualification
→ 材料、Evidence、Formal WorkProduct 开始需要长期 Authority
→ Zuno 的边界逐渐收窄到研究能力工程化 + 法律业务权威
→ Pilot / Current / Target / Evidence / Unknown
→ 团队 / 导师 / 个人 Ownership
→ 今天重新做会少造什么
```

Project 文档应自然支撑 3–5 分钟项目介绍，而不是让面试者先背九模块。

## 3. Architecture Story

`docs/architecture/architecture.md` Part A 应讲一次**概念上的架构成长**。

不要第一屏展示九模块表。先假设：

> Generic Host + Legal RAG + 一组 Research Skills。

然后使用同一个法律任务连续推进。

### Scene A — Uploaded != Ready

100 份材料都 HTTP 上传成功，但关键扫描件仍未 OCR。系统第一次发现“文件存在”不等于“当前任务知识完整可用”。先解释这个错误推断，再引出材料版本、派生知识代际与 task readiness。

### Scene B — Implementation != Capability

传统研究模型与新的 LLM 都能返回事件抽取 JSON。Schema 一样仍不能证明它们对“事件”的定义、适用范围与专业质量相同。先解释为什么 Runtime 不应该绑定论文模型，再引出 Capability / Provider / Qualification。

### Scene C — Machine Output != Formal Truth

模型给出风险结论，专业人员修改并采纳。机器结果与正式业务事实开始分裂；新证据进来后，历史存在与当前有效性又继续分裂。

### Scene D — Finished != Still Acceptable

复杂任务运行二十分钟，新材料进入；旧 Plan 的一个高质量分支晚到。此时“计算成功”不等于“结果仍有资格被当前计划接受”，再引出 Runtime control / plan version / late result / replan。

### Scene E — Timeout != Effect Failed

系统向外围法院系统提交动作，HTTP timeout。网络状态不能证明现实动作没发生，blind retry 可能制造重复 Effect。

### Scene F — Authorized Then != Authorized Now

任务启动时合法，在等待期间权限被撤销；后台 Worker 准备外发数据时必须重新消费当前安全事实。

### Scene G — Can Build != Worth Keeping

GraphRAG、Reflection、Multi-Agent、更贵模型都可以加。最后一个问题不是“还能加什么”，而是“什么证据证明复杂机制值得长期存在”。

最后才归纳：这些不同的事实不能互相冒充，因此形成九个逻辑 Ownership boundaries。

## 4. Module Part A

Part A 可以很长。长度必须来自 Context、Story、Causality、Failure、Recovery、Alternative、Trade-off、Evolution 和 Evidence，而不是对象和标题数量。

### 推荐 Opening Scene

| Module | Opening scene / core tension |
| --- | --- |
| 01 Application | Runtime 结束了，但 UI / 外部系统究竟能不能显示“正式完成”？ Product Projection != Owner Truth |
| 02 Legal Domain | 模型结论被专家修改采纳，后来新 Evidence 进入。 Candidate != Formal Fact；History != current validity |
| 03 Knowledge | 100 份文件上传成功，关键扫描件仍未 OCR。 Uploaded != Ready；retrieval miss != fact absent |
| 04 Runtime | 新证据进入后，旧 Plan 的高质量分支晚到。 Finished != still acceptable |
| 05 Capability | 旧研究模型和新 LLM 都做事件抽取。 Implementation != Capability；Conformance != Qualification |
| 06 Effects | POST timeout，不知道外围系统到底执行没有。 Transport != real-world effect |
| 07 Model Gateway | 本地研究模型、私有 LLM、云 Provider 都可调用。 Available != permitted != qualified |
| 08 Security | 10:00 有权限，10:20 执行动作时权限已经撤销。 Auth at start != authorization now |
| 09 Evaluation | GraphRAG / Reflection / 强模型都能加，却不知道谁贡献了收益。 Can build != worth keeping |

这些不是固定章节模板，只是要求每篇先建立读者能看见的真实矛盾。

## 5. Causal Transition

理想 Part A 的段落关系：

```text
我们原本直接做 X
→ 在简单任务里它完全合理
→ 具体场景 Y 出现
→ 最直觉的修复 Z 仍然失败
→ 真正需要分开的其实是两种语义 / 两个 Authority
→ 工程上后来把它叫作某个术语
→ 这个边界又留下一个新问题
→ 下一段自然继续
```

禁止退化成：

```text
### Concept A
定义
### Concept B
定义
### Concept C
定义
```

## 6. Writing Standard V2 候选原则

下一轮 Governance 可以吸收，但不要机械化：

- **Global Story Spine First**：整篇先有主因果链。
- **Research Provenance**：Research Artifact / Capability / Provider / Current 分开。
- **Baseline Before Differentiation**：先诚实写简单方案和成熟平台已经能做什么。
- **Concept Before Name**：现实矛盾先于内部对象名。
- **Failure Before Mechanism**：先解释错误直觉为什么失败。
- **Causal Transition**：章节之间继承未解决问题。
- **Authority Before Plumbing**：先问谁能决定事实，再谈 Receipt / DB / CAS。
- **Can Host != Should Own**：平台能承载不等于平台应该拥有领域语义。
- **Deletion Condition**：复杂机制必须有退出条件。
- **Ownership Honesty**：导师 / 课题组 / 团队 / 个人严格分开。
- **Interview Extractability**：正文中的核心因果段落能自然截成面试答案。
- **Evidence-aware Claims**：没测过就继续写 Hypothesis / Target。

不要新增固定标题数、每段必须几个 why、术语比例、硬字符数等反向激励。

## 7. Human Review Questions

人工验收 Part A 时优先问：

1. 读完前 20% 后，陌生高级工程师是否知道这个模块为什么存在？
2. 删除所有 PascalCase 内部对象名以后，设计因果还能否复述？
3. 上一节是否真的留下了下一节要解决的问题？
4. 复杂方案出现前，是否诚实讲了简单 baseline 为什么可行、又在哪里失败？
5. 文档是在说“平台做不到”，还是准确区分“平台可以 Host / Zuno 必须 Own”？
6. Crash / timeout / permission change 的恢复有没有回到明确 Authority？
7. 如果用户量小十倍、平台能力更强或测量收益不足，哪些层应该删除？
8. 读完以后记住的是几个真实矛盾，还是几十个对象名？

## 8. Rewrite Priority

### P0

`project.md` → overall Architecture Part A → 05 Capability → 03 / 02 / 09。

### P1

`modules/README` → 04 → 06 → 08。

### P2

01 → 07 → Architecture Views → Reference consistency → Governance V2。

目录和 Research Knowledge Base 建立完成前，不把这个 Blueprint 直接写成新的 canonical architecture。

## 9. Academic Research Synthesis — Architecture Story and Architecture Design

> research_date: 2026-09-03
> source: SciSpace semantic search over software-architecture / software-engineering literature
> evidence_scope: indexed metadata and abstracts; this is not a full-text systematic literature review

这轮研究把“怎样讲好架构故事”和“怎样设计好架构”分成两条相互关联、但不能混为一谈的链路。

### 9.1 架构文档的首要对象是 stakeholder concern，不是模块目录

Smolander 与 Päivärinta 对三个软件组织的质性研究指出，不同 stakeholder 使用架构描述的理由并不相同。设计者强调后续设计与实现，其他 stakeholder 更强调沟通、解释与决策。这个结果直接支持 Zuno 当前的 Human / Machine 双视图：同一套架构事实可以有不同阅读路径，但不能维护两套相互竞争的 Architecture Truth。

Clements、Bachmann、Bass、Garlan 等人的 Software Architecture Documentation / Views and Beyond 工作进一步把架构描述组织成多视图问题：先选择与 stakeholder concerns 相关的 view，再补充跨 view 才能表达的信息。对 Zuno 的直接含义是：不要期待一张总图同时解释事实权威、运行控制、失败恢复、部署和演进。`architecture-views.md` 应继续由不同 concern 驱动，而不是追求“一张图讲完”。

Zuno 写作映射：

```text
Stakeholder concern
→ 选择最小必要 view / 场景
→ 解释该 view 能回答什么
→ 明确它不能证明什么
→ 回到 canonical Owner 文档
```

### 9.2 架构故事应保留因果和人的意义，但必须和 evidence / argument 绑定

Rainer 在 human-centric software engineering 的 storytelling 研究中把故事视为对过度抽象的一种补偿方式，并明确指出 storytelling 可以和 evidence、argument 结合。对 Zuno 来说，这不意味着把技术文档小说化，而是要求每个抽象边界保留它出现时的业务因果。

因此 Zuno 的“故事”应该主要由以下元素组成：

```text
Actor / system context
→ concrete trigger
→ current assumption
→ failure or tension
→ decision
→ consequence
→ remaining problem
```

法律案件时间线非常适合承担这条主线，因为材料进入、专业判断、长期运行、权限变化和外部副作用天然具有时间顺序。对象名和 Contract 应在读者已经理解矛盾以后再出现。

Daniel 等人的 viewpoint-driven visual analysis 工作也支持同一原则：可视化应从 concern / viewpoint 出发选择，而不是先选一个通用图形再试图塞入全部信息。

### 9.3 设计架构时先写 quality-attribute scenario，再选 tactic / pattern

SEI 关于 architectural tactics 的工作把质量需求与设计决策联系起来：质量需求需要被写成足够具体的场景，再通过 tactic 连接到设计片段。Márquez 与 Astudillo 2023 年对 IT 专业人员的受控实验进一步显示，在 framework 选择中同时使用 pattern 与 tactic，比只使用 pattern 能更有效地收缩设计空间并得到更精确的选择。

这给 Zuno 一个明确的设计纪律：

```text
Business / professional risk
→ Quality Attribute Scenario
→ Candidate Tactics
→ Candidate Architecture Decisions
→ Trade-off
→ Chosen design
→ Measurement / Evidence
```

禁止从下面这种链路开始：

```text
LangGraph 有 Checkpointer
→ 所以 Zuno 需要 Checkpoint 模块

GraphRAG 很先进
→ 所以 Knowledge 必须 GraphRAG

微服务是成熟架构
→ 所以九个逻辑责任域应该部署成九个服务
```

### 9.4 Zuno 应把“质量属性”翻译成自己的业务风险语言

传统 quality attributes 如 modifiability、performance、availability、security 仍然适用，但 Zuno 的 Architecture Story 还需要先用业务语言表达更贴近法律系统的风险。

例如：

| 业务场景 | 主要架构关注 | 可能的 tactic / boundary |
| --- | --- | --- |
| 新材料进入后旧结论仍被展示为当前有效 | freshness / correctness / traceability | version binding, invalidation, explicit validity state |
| Domain 已正式提交但 Runtime 在 checkpoint 前崩溃 | recoverability / consistency | durable domain receipt, owner-first recovery |
| 外部提交 timeout 后 blind retry | consistency / idempotency / recoverability | logical action identity, reconciliation |
| 长任务执行期间权限被撤销 | security / authorization freshness | continuous authorization, fail-closed effect gate |
| 两个 Provider 都返回相同 schema 但专业语义不同 | substitutability / professional quality | capability contract, qualification evidence |
| GraphRAG / Reflection 增加复杂度但收益未知 | cost / modifiability / evolvability | measurement gate, deletion condition |

这些场景先于 tactic 名称。只有一个设计选择能够明确回答“它改善哪个 scenario、代价是什么、如何测量”，才有资格进入 Target Architecture。

### 9.5 Trade-off 不是文档末尾的礼貌性补充

Bellomo、Gorton、Kazman 对 15 年 ATAM 数据的分析显示，真实项目长期面对多个 quality concerns，而不是单目标优化。对 Zuno 来说，Trade-off 应在设计选择发生的地方同步出现。

例如 Single Controller：

```text
收益：控制状态收敛、PlanVersion authority、late-result 判断更简单
代价：全局控制最终经过一个逻辑写者，吞吐和可用性策略受限
继续使用条件：控制吞吐未成为真实瓶颈，且简化恢复的收益仍高于并行控制收益
升级条件：有 measurement 证明 controller 成为主要瓶颈，再研究 partitioned control
```

这样 Trade-off 会直接约束演进，而不是在文档末尾补一句“增加了一些复杂度”。

### 9.6 Architectural Decision 的对象不仅是结论，还包括 rationale 和 rejected alternatives

Architectural decision documentation 的研究持续强调 rationale、alternatives 与后续可理解性。Zuno 的 ADR 不应只是“采用 X”，而应至少能恢复：

```text
Context / scenario
→ Decision driver
→ Considered alternatives
→ Chosen decision
→ Consequences
→ Evidence or measurement needed
→ Revisit / deletion condition
```

这和当前 `decisions / evidence / governance` 三个域的职责是一致的：ADR 保存长期理由，Evidence 证明 Current，Governance 负责事实边界。论文只能支持这种方法论，不证明任何 Zuno Target 已经实现。

### 9.7 对下一轮正文重写的直接要求

下一轮 `architecture.md` 和 Module Part A 不再只检查“有没有场景”，而检查场景是否真正驱动了设计：

1. 每个重要机制能否追溯到一个具体 business / quality scenario；
2. 该 scenario 的 stimulus、environment、response 和 failure consequence 是否足够清楚；
3. 是否先讨论 simple baseline，再讨论 tactic / boundary；
4. 是否说明至少一个 rejected alternative；
5. 是否说明该设计改善什么，同时牺牲什么；
6. 是否给出 measurement / evidence 或明确 `Measurement Needed`；
7. View / Diagram 是否服务一个明确 concern，而不是把所有对象堆在一张图上；
8. ADR 是否能恢复设计理由，而不仅是最终选择。

这八条是 Human / Architecture Review 的推理要求，不应直接机械化成固定标题或关键词配额。

### 9.8 本轮主要论文

- Kari Smolander, Tero Päivärinta. **Describing and Communicating Software Architecture in Practice: Observations on Stakeholders and Rationale**. CAiSE, 2002. DOI: `10.1007/3-540-47961-9_11`.
- Felix Bachmann, Len Bass, Jeromy Carriere, Paul Clements, David Garlan, James Ivers, Robert L. Nord, Reed Little. **Software Architecture Documentation in Practice: Documenting Architectural Layers**. SEI report, 2000. DOI: `10.21236/ADA377988`.
- Paul C. Clements. **Comparing the SEI's Views and Beyond Approach for Documenting Software Architecture with ANSI-IEEE 1471-2000**. SEI technical note, 2005. DOI: `10.21236/ADA441291`.
- Austen Rainer. **Storytelling in human-centric software engineering research**. EASE, 2021. DOI: `10.1145/3463274.3463803`.
- Donny Thomas Daniel, Egon Wuchner, Michael Stal, Peter Liggesmeyer. **Towards Viewpoint-driven Visual Analysis for Effective Architecture Recovery**. VISSOFT, 2018. DOI: `10.1109/VISSOFT.2018.00024`.
- Felix Bachmann. **Deriving Architectural Tactics: A Step Toward Methodical Architectural Design**. SEI report / repository record. DOI: `10.1184/r1/6573047`.
- Gastón Márquez, Hernán Astudillo. **Selecting Application Frameworks Using Architectural Patterns and Tactics**. SCCC, 2023. DOI: `10.1109/SCCC59417.2023.10315698`.
- Stephany Bellomo, Ian Gorton, Rick Kazman. **Toward Agile Architecture: Insights from 15 Years of ATAM Data**. IEEE Software, 2015. DOI: `10.1109/MS.2015.35`.

这些来源支持“如何推理和表达架构”的方法论。它们不支持任何关于 Zuno 当前性能、Production Readiness、业务效果或个人实现范围的更强事实声明。

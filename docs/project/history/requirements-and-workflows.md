# 历史需求与业务流程恢复

status: canonical-history
canonical_question: 历史项目真实面对什么业务问题和人工流程？
owner: Project History Owner / Business Context
replaces: 旧事实目录中的需求与流程候选

> 本文件把历史事实、架构重建候选和未知事项分开。当前 Target 的 Domain Model、Evidence Requirement、Agent Runtime 或 GraphRAG 不能反向证明历史甲方当时提出过同样的要求。

## CONFIRMED：已经确认的历史锚点

目前能够直接写入历史叙事的业务锚点有限，但很重要：

- 产品属于智慧法院相关体系中的一个产品；
- 法院侧真实人员参与过测试；
- 客户 Demo 后明确反馈回答质量仍需提高；
- 项目进入过 Pilot Validation，但尚未正式生产部署。

这些事实说明项目确实面向真实业务侧进行过阶段性验证，也说明回答质量是客户关注的结果边界；它们不能推出完整的人工流程、标准数据集或质量提升指标。

## RECONSTRUCTED：基于背景的业务问题候选

结合智慧司法公开研究和当前产品方向，可以把下列链路作为 `RECONSTRUCTED_CANDIDATE`，用于下一轮事实恢复和架构 Red Team：

```text
法律 / 案件相关材料进入
  → 人工阅读和定位关键信息
  → 提取事实或事件
  → 对照不同当事人的陈述与证据
  → 发现冲突并形成争议焦点
  → 查找法律依据或类案
  → 形成带来源的分析结果
  → 人工复核或交付
```

这条链路是“法律任务可能需要什么”的工程重建，不是已经确认的 Zuno 历史 SOP。公开论文可以作为研究背景和 Research Transfer，不能作为 Zuno 的产品实现证明。

## TARGET_PROBLEM_MODEL：现在架构要验证的问题

Target 需要验证的不是“是否堆更多 Agent”，而是高风险法律任务是否需要同时处理：

- 多源材料与跨文档证据；
- 事实、事件、陈述和冲突之间的依赖；
- 法律依据的版本、适用性和引用来源；
- 结果是否足够支持一个结论；
- 新证据到来后旧结论是否 stale；
- 哪些结果必须由 Domain Owner 或人复核；
- 外部 Tool 动作是否需要审批、幂等和审计。

这些是 `TARGET_PROBLEM_MODEL`，不能写成“历史甲方已经明确要求全部能力”。每项能力都需要通过真实 QA、Benchmark、User Validation 或故障证据确认是否值得保留。

## UNKNOWN：仍未恢复的历史事实

- 谁提出了第一版需求，业务方当时使用什么原始术语；
- 人工处理什么具体材料，原始输入是卷宗、判决书、法规还是其他资料；
- 人工流程中最耗时、最容易出错的具体步骤；
- 是否存在固定的跨文档核对、证据引用、法条或类案检索流程；
- “回答质量”的正式定义、评分人和验收门槛；
- 法院测试的问题数量、参考答案、参考材料和评价协议；
- 真实 Bad Case，以及后续修改是否真的带来可测量收益。

## 下一步证据入口

优先寻找法院 QA、客户演示材料、页面截图、会议记录、任务记录和真实失败案例。若只能确认“类似流程”，保持 `RECONSTRUCTED_CANDIDATE`；不要因为架构文档已经定义了 Matter、Evidence 或 Finding，就把这些对象倒灌成历史需求。

Target 产品问题和 A/B/C Kill Test 由 [`../architecture/architecture.md`](../architecture/architecture.md) 负责；当前代码证据由 [`../status/current-reality.md`](../status/current-reality.md) 和 [`../../evidence/README.md`](../../evidence/README.md) 负责。

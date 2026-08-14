# 历史需求与业务流程恢复

status: current-fact
canonical_question: 历史项目真实面对什么业务问题和人工流程？
owner: Project Facts Owner / Business Context
source_boundary: 已确认历史锚点与重建候选严格分离

> 本文件把历史事实、架构重建候选和未知事项分开。当前 Target 的 Domain Model、Evidence Requirement、Agent Runtime 或 GraphRAG 不能反向证明历史甲方当时提出过同样的要求。

## USER_CONFIRMED：已经确认的历史锚点

目前能够直接写入历史叙事的业务锚点有限，但很重要：

- 产品属于智慧法院相关体系中的一个产品；
- 法院侧真实人员参与过测试；
- 客户 Demo 后明确反馈回答质量仍需提高；
- 项目进入过 Pilot Validation，但尚未正式生产部署。

这些事实说明项目确实面向真实业务侧进行过阶段性验证，也说明回答质量是客户关注的结果边界；它们不能推出完整的人工流程、标准数据集或质量提升指标。

## RECONSTRUCTED_CANDIDATE：基于背景的业务问题候选

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

## TARGET_ONLY：现在架构要验证的问题

Target 需要验证的不是“是否堆更多 Agent”，而是高风险法律任务是否需要同时处理：

- 多源材料与跨文档证据；
- 事实、事件、陈述和冲突之间的依赖；
- 法律依据的版本、适用性和引用来源；
- 结果是否足够支持一个结论；
- 新证据到来后旧结论是否 stale；
- 哪些结果必须由 Domain Owner 或人复核；
- 外部 Tool 动作是否需要审批、幂等和审计。

这些是 `TARGET_ONLY`，不能写成“历史甲方已经明确要求全部能力”。每项能力都需要通过真实 QA、Benchmark、User Validation 或故障证据确认是否值得保留。

## UNKNOWN：仍未恢复的历史事实

- 谁提出了第一版需求，业务方当时使用什么原始术语；
- 客户原始需求原话；
- 产品主要用户是谁，以及法官、助理、书记员、信息化人员的比例；
- 人工处理什么具体材料，原始输入是卷宗、判决书、法规还是其他资料；
- 具体是否包括法律问答、案件分析、证据分析、争议焦点、法条、类案或文书任务；
- 人工流程中最耗时、最容易出错的具体步骤；
- 是否存在固定的跨文档核对、证据引用、法条或类案检索流程；
- 哪些步骤允许 AI 自动完成，哪些步骤必须人工确认；
- 项目最主要的业务场景和用户问题；
- “回答质量”的正式定义、评分人和验收门槛；
- 法院测试的问题数量、参考答案、参考材料和评价协议；
- 真实 Bad Case，以及后续修改是否真的带来可测量收益。

## UNKNOWN：Agent / Platform 产品形态

以下内容目前没有无歧义的用户确认，统一保持 `UNKNOWN`，具体问题进入
[`confirmation-ledger.md`](confirmation-ledger.md)：

- 项目整体是否是统一 Agent Platform，还是一个司法 Agent 产品；
- 是否存在多个 Agent、Agent Cluster、Coordinator 或 Agent-to-Agent 运行时协作；
- 是否存在 Platform-to-Platform Cooperation、Agent Catalog 或 Agent Studio；
- Agent 是否可以配置 Model、Prompt、Knowledge、Memory、Tool 和 Skill；
- 葛季栋团队的法律算法如何进入 Agent，是否存在能力包以及能力包的正式名称和构成；
- 能力是否可以组合，外部平台如何合作，是否使用 API 或 MCP；
- 是否明确存在知识库、Document Ingestion、Chunk、Embedding、Vector Search、BM25、Hybrid Retrieval、Reranker、Citation、Milvus、Elasticsearch、Neo4j、GraphRAG、Knowledge Graph 或 Similar Case Retrieval。

## 下一步证据入口

优先寻找法院 QA、客户演示材料、页面截图、会议记录、任务记录和真实失败案例。若只能确认“类似流程”，保持 `RECONSTRUCTED_CANDIDATE`；不要因为架构文档已经定义了 Matter、Evidence 或 Finding，就把这些对象倒灌成历史需求。

Target 产品问题和 A/B/C Kill Test 由 [`../architecture/architecture.md`](../architecture/architecture.md) 负责；当前代码证据由 [`../evidence/README.md`](../evidence/README.md) 负责。

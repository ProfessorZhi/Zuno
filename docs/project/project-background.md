# Zuno 项目背景

status: canonical-project-background
canonical_question: Zuno 为什么存在、面向什么业务方向、哪些背景事实今天仍然可以相信？
owner: Project Documentation Owner
source_boundary: 用户确认、公开研究背景和明确未知事项；不把当前 Target 或代码表面反写成历史事实

本文是项目故事的正式入口。它保留已经恢复的背景，同时把“公开研究支持”“用户明确确认”“合理候选”和“仍然未知”分开。历史正式产品名、合同关系和完整第一版需求尚未恢复，因此不使用架构文档补写历史。

## 一句话说明

Zuno 的原始产品方向，是面向天津法院智慧平台场景建设一个法律智能平台，以多个专业 Agent 组织和执行法律任务，并把法律知识、专业智能能力、上下文/Memory、模型、Skill / Tool 与法院业务系统能力组合进完整工作流。它不是整个智慧法院项目，也不能被简化成某一篇论文的 Demo 或一个普通企业 RAG 的别名。

这里需要区分两层：法律智能平台、多专业 Agent 和研究成果产品化属于已经确认的原始产品意图；历史实现中到底完成了几个 Agent、哪些组合能力和多 Agent 协作机制，仍然是 `PARTIALLY_KNOWN` 或 `UNKNOWN`。产品目标明确，不等于历史实现已经完整。

## 项目来源与合作背景

用户确认，项目与南京大学软件学院葛季栋 / LIPLAB 的智慧司法研究和工程背景直接相关，合作侧日常称谓是“智慧法院项目组”。用户进一步确认，项目不是完全脱离课题组研究成果重新开发，而是有意融合葛季栋团队此前积累的多项法律智能研究成果。

南京大学软件学院公开介绍显示，LIPLAB 长期参与天津法院信息化建设，负责部分信息系统研发，尤其涉及智能司法判决辅助技术成果落地。这是公开背景支持，不等于本产品的合同、任务书、部署拓扑或算法集成清单已经公开。[LIPLAB 官方介绍](https://software.nju.edu.cn/szll/yjsds/index.html)

用户确认，项目与天津智慧法院 / 天津法院侧存在合作背景，产品涉及 22 家法院体系中的部分法院。这里的“部分”不能写成全部 22 家法院均使用或正式部署；具体法院名单、直接合同甲方、正式合同、子课题和项目编号仍为 UNKNOWN。

当前仓库使用 `Zuno` 作为产品名称。用户已确认它是智慧法院相关体系中的一个具体产品，不是整个智慧法院项目；历史正式产品名尚未可靠恢复。

## Research → Product 的关系

用户确认的最保守表述是：项目存在把葛季栋团队此前多项法律智能研究成果向产品能力转移、组合或工程化的意图。这个事实不等于每一篇论文、每一个算法、每一个专利都进入了用户参与时期的同一版本，也不等于每项研究都成为 Agent Tool、Knowledge Pipeline 或公开产品 API。

葛季栋官方主页公开列出的研究背景包括多源多态证据链与裁判文书说理、裁判文书文本抽取、相似度分析、法条规范化和案由—法条关联、法条推荐、文本分词，以及 LawBench 等法律语言模型评测研究。[葛季栋官方主页](https://software.nju.edu.cn/gjd/)

其中，Zhang、Li、Sheng、Ge 与 Luo 的 2024 年论文 *Judicial intelligent assistant system: Extracting events from Chinese divorce cases to detect disputes for the judge* 描述了面向中国离婚案件的焦点事件抽取、事件对齐和冲突检测系统。[论文 DOI](https://doi.org/10.1111/exsy.13540)

这些资料属于 `PUBLIC_RESEARCH_CONTEXT`：它们证明相关研究能力链存在，包括 Event Extraction、Event Alignment、Conflict Detection、Dispute Identification、Evidence Chain、裁判文书信息抽取、Case Similarity、Statute Recommendation 和 Legal Text Processing；它们不能证明历史 Zuno 一定实现了 JIA、使用了某个论文模型或达到了论文 Benchmark 指标。具体 Research Inventory → Product Capability 的映射仍待逐项恢复。

## 为什么立项为法律智能 Agent 平台

项目立项存在两个同时成立的驱动力：天津法院侧智慧平台 / 智慧法院建设存在法律智能化产品需求；南京大学软件学院葛季栋 / LIPLAB 已经积累长期智慧司法科研成果，并有将这些成果进一步工程化、产品化的目标。因此，`Court-side Product Need + Research Engineering / Productization` 共同构成项目背景。

从立项目标上，Zuno 就是法律智能平台、多专业 Agent 与可组合法律专业能力的产品方向，不是先做普通 RAG、后来才临时升级成 Agent Platform。第一版需求原话和原始人工 SOP 尚未恢复，所以不能补写具体客户流程；但不能再把“是否从一开始就是 Agent Platform”列为未知。仍然未知的是历史实现成熟度：当时实际有几个 Agent、是否支持 Agent-to-Agent、是否有 Coordinator / Catalog / Studio、能力包如何组成，以及各项研究能力以何种形式接入。

在这个既定产品方向下，系统希望组织专业人员围绕法律材料、事实、事件、证据、法律依据和已有业务上下文完成检索、比对、分析、复核和结果交付；Knowledge、Legal Intelligence、Agent、Context/Memory、Model、Skill / Tool 与法院业务系统能力属于产品目标中的能力边界，不是历史实现清单。

公开司法研究可以解释为什么这些问题值得验证：大量案件文本会增加人工阅读、定位和比对成本，事件与陈述之间可能存在冲突，检索到相关文字也不自动等于法律适用或结论可复核。它们是领域上下文，不是 Zuno 的历史 Bad Case、历史 SOP 或产品指标。

因此，当前项目故事应当这样收敛：Zuno 不是“把 RAG 换成 Agent”这么简单，也不是“把论文直接上线”；它尝试把研究能力、法律专业流程和可控制的 Agent 执行结合起来，服务法院侧及其他法律专业人员的材料处理与分析工作。是否已经支持多个 Agent、Agent 间协作、能力包组合、外部平台合作或完整 Agent Studio，仍是待确认的产品事实。

## 用户与业务范围

目前最可靠的用户表述是法院侧或相关法律专业人员。法官、法官助理、书记员、法院信息化人员、律师或企业法务在历史项目中的具体比例和权限尚未恢复；不能把 Target 用户列表当作历史用户清单。

基于背景可以提出一个业务流程候选：法律或案件材料进入后，系统帮助定位内容、抽取事实或事件、比对多方陈述和证据、分析冲突或争议、检索法律依据或类案，再形成可引用的分析结果并交由人复核。该流程是 `RECONSTRUCTED_CANDIDATE`，不是已确认的历史正式 SOP。

历史第一版需求由谁提出、客户原话、最耗时和最容易出错的步骤、哪些环节允许 AI 自动完成、哪些必须人工确认，以及具体处理卷宗、判决书、法规、证据还是其他材料，均为 UNKNOWN。

## 已恢复的交付阶段

用户确认的阶段链是：已有产品和代码 → Internal Demo → Customer / Smart Court Project Demo → 客户反馈回答质量需要提高 → 继续迭代 → Court-side Testing → Pilot Validation → Production = NO。

这说明项目确实进入过真实业务侧演示、法院侧人员测试和 Pilot Validation；它不证明已经正式生产上线、覆盖全部 22 家法院、满足 SLA，也不提供用户数、运行时长、部署环境或 QPS。客户反馈“回答质量需要提高”目前只有症状，根因、修复和指标仍保留在 UNKNOWN。

## 仍待确认的背景

- 历史正式产品名称、合同甲方、项目编号、子课题和具体法院名单；
- 第一版需求、原始人工流程、主要用户和具体任务材料；
- 研究成果进入哪个版本、以算法、Tool、Skill、Knowledge Pipeline 还是其他形式进入；
- 历史实现中实际完成了几个 Agent、每个 Agent 的正式名称和配置维度；
- 是否已经支持 Agent-to-Agent、Coordinator、Agent Catalog、Agent Studio 或“Agent 集群”；
- Skill / 能力包的准确组成、组合方式和历史正式名称；
- Knowledge / RAG 历史链路是否实际使用了 Chunk、Embedding、BM25、Vector、Hybrid、Reranker、Citation、Milvus、Elasticsearch、Neo4j、GraphRAG、Knowledge Graph 或 Similar Case Retrieval；
- Pilot 的参与法院、用户、任务、时长、环境、验收、SLA、Latency、Cost、HA 和 DR；
- “回答质量需要提高”的真实 Cause → Fix → Metric。

开发参与、个人边界和当前仓库能证明的内容见[开发过程](./development-process.md)。当前代码与测试证据见[Evidence](../evidence/README.md)；总体 Target 设计见[总体架构](../architecture/architecture.md)。这些来源不能互相倒灌。

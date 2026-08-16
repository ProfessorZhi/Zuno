<!--
status: canonical-project-background
canonical_question: Zuno 为什么存在、面向什么业务方向、哪些背景事实今天仍然可以相信？
owner: Project Documentation Owner
source_boundary: 用户回忆、公开研究背景和明确未恢复事项；不把当前 Target 或代码表面反写成历史事实
-->

# Zuno 项目背景

## 1. Zuno 是什么

Zuno 是南京大学软件学院 LIPLAB 面向天津法院智慧平台相关场景建设的法律智能 Agent 平台。它希望把课题组长期积累的智慧司法研究成果工程化，整理成可以被 Agent、业务系统和法律专业人员组合使用的法律智能能力。

Zuno 是智慧法院相关体系中的一个具体产品，不是整个智慧法院项目。今天仓库使用 `Zuno` 作为产品名称，但历史正式产品名称还没有可靠恢复；项目也不能因为进入过法院侧验证，就被描述成已经正式生产上线。

## 2. 为什么会有这个项目

项目有两个同时成立的来源。一方面，天津法院侧智慧平台存在法律智能化需求；另一方面，LIPLAB 和葛季栋团队长期积累了智慧司法研究成果，并尝试把这些成果继续工程化、产品化。项目与天津法院侧的合作背景，和研究成果向具体产品能力的转移，共同构成了 Zuno 的起点。

南京大学软件学院公开介绍显示，LIPLAB 长期参与天津法院信息化建设，负责部分信息系统研发，并涉及智能司法判决辅助技术成果落地。[LIPLAB 官方介绍](https://software.nju.edu.cn/szll/yjsds/index.html)

用户回忆显示，项目与天津法院侧存在合作背景，产品涉及 22 家法院体系中的部分法院。这里的“部分”不能扩展成全部 22 家法院均使用或正式部署；具体参与法院、直接合同甲方、合同或子课题编号仍未恢复。

### 历史起点和“为什么今天仍值得做”不是同一个问题

本节只记录项目为什么历史上出现。至于今天面对已经成熟的通用大模型平台、RAG 框架和 Agent 宿主，Zuno 为什么仍然值得作为独立产品继续建设，需要结合当前已经接受的 Target Architecture 来回答。

这部分单独放在[产品定位、立项逻辑与差异化](./product-positioning-and-value.md)，因为它包含一部分今天的产品与架构判断：通用宿主已经能够承担会话、基础工作流、模型、RAG 和工具，Zuno 真正需要自己长期负责的是法律领域状态、材料版本、正式证据、人工决定、工作成果、失效传播、现实副作用恢复和法律评测等专业语义。

这种区分避免把“今天我们认为合理的架构理由”倒写成“历史客户当时就是这样提出需求的”。

## 3. 原始产品方向

从立项方向上，Zuno 就是法律智能平台、多专业 Agent 和可组合法律专业能力的产品方向，并不是先做一个普通 RAG、后来才把它包装成 Agent Platform。这个判断描述的是原始产品意图，不代表历史版本已经完成了全部目标。

目前没有足够资料恢复历史上实际完成了多少个 Agent、每个 Agent 的正式名称和配置方式，也不能确认是否已经有 Coordinator、Agent-to-Agent 协作、Agent Catalog、Agent Studio 或能力包组合。产品方向已经比较清楚，历史实现的完整程度仍需要单独恢复。

## 4. 研究如何走向产品

项目不是完全脱离课题组研究成果重新开发，而是有意融合葛季栋团队此前积累的多项法律智能研究成果。葛季栋公开主页列出的研究背景涉及多源多态证据链与裁判文书说理、裁判文书文本抽取、相似度分析和法条规范化和案由—法条关联、法条推荐、文本分词以及 LawBench 等法律语言模型评测方向。[葛季栋官方主页](https://software.nju.edu.cn/gjd/)

一个代表性研究例子是 Zhang、Li、Sheng、Ge 与 Luo 的 2024 年论文 *Judicial intelligent assistant system: Extracting events from Chinese divorce cases to detect disputes for the judge*。论文描述了面向中国离婚案件的焦点事件抽取、事件对齐和冲突检测系统。[论文 DOI](https://doi.org/10.1111/exsy.13540)

这些公开材料能够帮助理解 LIPLAB 为什么具备 Event Extraction、Event Alignment、Conflict Detection、Dispute Identification、Evidence Chain、Case Similarity 和 Statute Recommendation 等研究背景，但不能证明历史 Zuno 一定实现了 JIA、使用了某个论文模型，或达到论文中的 Benchmark 指标。具体哪些研究成果进入了哪个产品版本、以算法、Tool、Skill 还是 Knowledge Pipeline 形式进入，目前还没有逐项映射。

今天的 05 Capability & Skill（专业能力与技能）把 Research Artifact → Capability → Provider → Conformance → Eval → Eligibility 设计成目标工程路径，就是为了未来能够回答“某项研究究竟怎样成为可运行产品能力”。这个 Target 设计不能反过来证明历史版本已经按该路径完成工程化。

## 5. 面向什么人和什么工作

目前最稳妥的用户范围是法院侧及相关法律专业人员。法官、法官助理、书记员、法院信息化人员、律师或企业法务在历史项目中的具体比例和权限尚未恢复，因此不能把 Target 用户列表直接当作历史用户清单。

为了理解产品方向，可以把一条可能的工作链概括为：法律或案件材料进入系统后，先定位和抽取事实或事件，再比对多方陈述与证据，分析冲突或争议，检索法律依据或类案，形成带引用的分析结果，最后交由人复核。这是一条帮助理解产品方向的概括，不是已经恢复的历史正式操作流程。

公开司法研究可以解释为什么这类工作值得工程化：案件材料较多时，人工阅读、定位和比对会消耗大量时间；相关文字被检索出来，也不自动意味着它适用于当前争议或能够形成可复核结论。这些是领域背景，不是 Zuno 已经记录的历史 Bad Case、客户原话或产品指标。

## 6. 项目走到了哪一步

目前可以恢复的阶段链是：

```text
已有产品和代码
  → Internal Demo
  → Customer / Smart Court Project Demo
  → 客户反馈：回答质量需要提高
  → 继续迭代
  → Court-side Testing
  → Pilot Validation
  → Production：尚未建立
```

这说明项目经历过内部演示、客户侧或智慧法院项目组演示、法院侧人员测试和 Pilot Validation。客户反馈“回答质量需要提高”目前只能确定为反馈现象，具体是检索、提示词、模型、Memory、Tool、引用还是其他原因，调查过程、修复方式和改善指标都还没有恢复。

没有资料支持把项目描述成正式生产系统，也没有资料支持它覆盖全部 22 家法院或达到某个 SLA。Pilot 的参与法院、用户数、任务量、运行时间、部署环境、验收方式、Latency、QPS、Token、Cost、HA 和 DR 都需要以后根据材料补充。

## 7. 目前仍无法确认的信息

- 历史正式产品名称、第一版需求原文、需求提出者和原始人工流程；
- 具体合同甲方、项目编号、子课题和完整参与法院名单；
- 主要用户究竟是法官、助理、书记员、信息化人员还是其他法律专业人员；
- 历史材料的完整范围，以及用户当时最常提出的问题；
- 哪些研究论文、专利或算法进入了哪个产品版本，以及具体接入形式；
- 历史版本实际完成了多少 Agent，是否支持 Agent 协作、能力包、Studio、Catalog 或外部平台合作；
- 历史 Knowledge / RAG 是否实际使用过 Chunk、Embedding、BM25、Vector、Hybrid、Reranker、Citation、Milvus、Elasticsearch、Neo4j、GraphRAG、Knowledge Graph 或 Similar Case Retrieval；
- Pilot 的参与人员、数据规模、环境、运行时长、评价协议、验收结果和运维指标；
- “回答质量需要提高”的真实原因、调查过程、修改内容和 Cause → Fix → Metric 链路。

这些 Unknown 是后续提高项目可信度最有价值的取证方向。尤其在技术面试里，能够恢复一条真实的 Bad Case → Root Cause → Fix → Metric，以及一项个人任务从需求到验证的完整链路，比继续增加架构术语更有价值。

## 8. 去哪里继续读

- [产品定位、立项逻辑与差异化](./product-positioning-and-value.md)：为什么已经有通用平台仍值得做 Zuno，以及哪些差异仍需测量证明。
- [团队与开发分工](./team-and-contributions.md)：团队规模、用户加入时间和实际参与方向。
- [开发过程](./development-process.md)：从已有产品到 Demo、法院侧测试和 Pilot 的阶段叙事。
- [项目与架构审查问题地图](./review-question-map.md)：Reviewer / 技术面试高频问题应该回到哪个文档回答。
- [总体架构](../architecture/architecture.md)：后续形成的 Target Architecture。
- [当前工程证据](../evidence/README.md)：当前代码、测试、运行和评测能证明什么。
- [Red / Blue 历史](../history/red-blue/README.md)：架构为什么曾经被质疑和调整。
- [项目事实来源说明](../governance/project-fact-provenance.md)：上述表述的来源、事实台账与使用边界。

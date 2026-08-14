# Zuno 项目背景

status: current-fact
canonical_question: 这个历史项目从哪里来、服务什么方向、哪些背景事实可以确认？
owner: Project Facts Owner
source_boundary: 用户确认、公开背景和明确的 UNKNOWN；不替代 Target Architecture

> 本文讲历史项目，不讲当前 Target Architecture。历史项目的正式产品名、合同关系和完整需求没有被完整恢复；缺失处保留 `UNKNOWN`，不使用当前仓库或目标架构补空。

## 1. 项目从哪里来

`USER_CONFIRMED`：这个项目来自南京大学软件学院葛季栋 / LIPLAB 长期参与的智慧司法研发背景，合作侧日常称谓是“智慧法院项目组”。用户进一步确认，项目并不是完全独立于课题组研究成果重新开发，而是融合了葛季栋团队此前积累的多项法律智能研究成果；这确认了 Research transfer / integration intent existed，但不等于每一篇论文、每一个算法或每一个专利都进入了用户参与时期的同一个产品版本。

`PUBLIC_CORROBORATED`：南京大学软件学院公开介绍显示，LIPLAB 长期参与天津法院信息化建设，负责部分信息系统研发，特别涉及智能化司法判决辅助研究成果的落地应用。该公开背景支持研究组与智慧司法、天津法院信息化之间存在长期研究与工程联系，但不直接证明本产品的合同、任务书、部署拓扑或具体集成清单。见[南京大学软件学院 LIPLAB 公开介绍](https://software.nju.edu.cn/szll/yjsds/index.html)。

在本文中，`Zuno` 是当前仓库和本次重构使用的名称。用户确认它对应智慧法院相关体系中的一个产品，而不是整个智慧法院项目；历史正式产品名称已经无法可靠恢复，也不应把 Zuno 反写成当时的正式产品名。

`USER_CONFIRMED`：项目与天津智慧法院 / 天津法院侧存在合作背景，用户所在产品涉及 22 家法院体系中的一部分。这里的“一部分”很重要：具体法院名单、试点法院和直接合同客户都没有恢复。特别是，不能从公开资料推出天津市高级人民法院就是本产品的直接合同客户，也不能写成该产品服务全部 22 家法院。

## 2. 项目服务什么方向

`USER_CONFIRMED`：可以确认的业务方向是智慧法院 / 法律智能相关场景。更细的历史 Scope——例如究竟偏法院内部司法辅助、法律问答、案件分析，还是其中一个更窄的子场景——仍是 `UNKNOWN`。当前能稳定说的是：项目需要面向法院侧或相关专业人员进行演示、测试和试点验证，并且客户明确关注回答质量。

这条事实链不应被夸大为“原始需求已经恢复”。我们还不知道业务方当时使用的原始术语、人工 SOP、最耗时步骤、允许自动化的边界，或回答质量的正式验收标准。

## 3. 团队和开发方式

`USER_CONFIRMED`：历史核心研发规模约为 7–8 人。一名学硕学长承担主要技术负责人角色，并把用户带入项目。这一表述只说明日常技术组织关系，不把他写成正式 CTO、项目总架构师或拥有全部技术决策权的人。

`USER_CONFIRMED`：用户的身份是研究生工程参与者，不是整个项目负责人。团队中可能还包括前端、后端 / Agent、算法 / Legal AI、测试或部署等角色，但精确人数、正式 title、评审方式和责任链仍为 `UNKNOWN`。这些角色是帮助恢复协作结构的候选分类，不是已经确认的人员编制。

## 4. 用户怎样加入

`USER_CONFIRMED`：用户大约在 2026 年 3 月加入。加入时项目不是从零开始：已经有代码，也有一个比较简易的自研前端。用户随后参与 Agent 开发；Memory 是加入后的第一批重要工作之一，并参与了 OpenViking 在 Memory / Context 区域的接入以及 Tool Calling Strategy 相关开发。

`USER_CONFIRMED`：用户在开发过程中学习了 LangGraph 和 GraphRAG，也曾为排查问题进入数据库查看或调试数据。这些事实不能扩大为用户负责完整 Agent Runtime、全部 RAG / GraphRAG、完整 FastAPI 后端、全部数据库、整体架构或生产部署。

## 5. 项目如何被验证

`USER_CONFIRMED`：项目至少经历过内部 Demo、面向智慧法院项目组 / 客户侧的 Demo、法院侧真实人员参与的测试和 Pilot Validation。客户 Demo 后的一个明确反馈是：回答质量仍需要继续提高。这个反馈是当前历史记录中最重要的业务 Evidence Anchor，但具体 Bad Case、根因、修复和指标尚未恢复。

因此，历史交付阶段应当写成：

```text
已有产品和代码
  → 内部 Demo
  → 客户 / 智慧法院项目组 Demo
  → 回答质量反馈
  → 继续迭代
  → 法院侧人员测试
  → Pilot Validation
  → 尚未正式 Production
```

这条链表达的是已恢复的阶段性事实，不是精确日期时间线，也不等于正式验收、稳定 SLA 或全量部署。

## 6. 已知事实与未知事实

### 已确认或已恢复

- `USER_CONFIRMED`：南京大学软件学院葛季栋 / LIPLAB 的长期智慧司法研发背景，以及项目融合团队此前多项法律智能研究成果的意图；
- `PUBLIC_CORROBORATED`：LIPLAB 与天津法院信息化、智能司法辅助研发之间的公开背景联系；
- `USER_CONFIRMED`：合作侧日常称谓“智慧法院项目组”；
- `USER_CONFIRMED`：当前称为 Zuno 的产品属于该体系中的一个产品，不是整个智慧法院项目；
- `USER_CONFIRMED`：与天津智慧法院 / 天津法院侧存在合作背景，涉及 22 家法院体系中的部分法院；
- `USER_CONFIRMED`：用户约于 2026 年 3 月加入已有代码和简易前端的项目；
- `USER_CONFIRMED`：核心研发约 7–8 人，一名学硕学长承担主要技术负责人角色；
- `USER_CONFIRMED`：用户参与 Agent、Memory、OpenViking Memory / Context 接入和 Tool Calling Strategy；
- `USER_CONFIRMED`：存在内部 Demo、客户侧 Demo、法院侧测试和 Pilot Validation；
- `USER_CONFIRMED`：尚未正式生产部署，客户反馈之一是回答质量仍需提高。

### 仍然未知

- 历史正式产品名；
- 合同甲方、子课题和“智慧法院项目组”对应的正式机构；
- 具体法院名单、试点法院和部署位置；
- 原始业务需求、人工 SOP 和回答质量评价协议；
- 历史数据库、完整 Tool 清单、RAG / LangGraph / GraphRAG 主链路；
- 客户 Bad Case 的具体类型、优化 Cause → Fix → Metric；
- 用户的具体文件、API、提交和代码级 Ownership。

## 7. 公开研究的边界

葛季栋 / LIPLAB 相关公开研究属于 `PUBLIC_CORROBORATED` 和 `PUBLIC_RESEARCH_CONTEXT`。它们可以帮助解释为什么后续 Target 会关注事件抽取、事件对齐、冲突检测、争议焦点、事实—法条对应和法律评测，但不能证明历史 Zuno 已经实现这些论文算法，也不能把论文指标写成 Zuno Benchmark。

`PUBLIC_RESEARCH_CONTEXT`：Zhang, Y., Li, C., Sheng, Y., Ge, J., & Luo, B. (2024). *Judicial intelligent assistant system: Extracting events from Chinese divorce cases to detect disputes for the judge*. **Expert Systems**, 41(7), e13540. [DOI: 10.1111/exsy.13540](https://doi.org/10.1111/exsy.13540)。Wiley 论文页面说明，该研究实现了 JIA 系统，用于从中国离婚案件材料中抽取焦点事件、对齐事件并检测当事人陈述之间的冲突。它只能证明相关智慧司法研究成果和能力链存在，不能证明历史 Zuno 一定实现了 JIA，也不能把论文实验指标写成 Zuno 产品指标。

### 7.1 葛季栋官方 Research Inventory

葛季栋官方主页公开列出以下研究和成果背景，均属于 `PUBLIC_RESEARCH_CONTEXT`，不是 Historical Product Feature：

- 国家重点研发计划课题“多源多态证据链构建和裁判文书说理关键技术研究”，编号 `2016YFC0800803`，执行期 2016.7—2020.6；
- 面向裁判文书的证据链关系模型构建方法；
- 基于主题模型的裁判文书相似度分析方法；
- 面向裁判文书的文本信息抽取方法；
- 面向裁判文书的法条名称规范化和案由—法条关联统计方法；
- 基于 LDA 主题模型的法条推荐方法；
- 基于 PageRank 和信息熵的裁判文书文本分词方法；
- `LawBench: Benchmarking Legal Knowledge of Large Language Models`，官方主页列为 EMNLP 2024 研究成果。

来源：[`葛季栋官方主页`](https://software.nju.edu.cn/gjd/)。该页面支持“研究团队曾开展这些方向的研究或成果申报”，但不能证明这些成果全部进入 Zuno、进入同一历史版本，或成为用户参与时期的产品 API、Tool、Agent Capability 或 Knowledge Pipeline。

`PUBLIC_RESEARCH_CONTEXT` 允许我们记录 Event Extraction、Event Alignment、Conflict Detection、Dispute Identification、Evidence Chain、Legal Element Extraction、Fact–Article Mapping、Statute Recommendation 和 Legal LLM Evaluation 等研究上下文；`USER_CONFIRMED` 只确认项目融合了团队此前多项法律智能研究成果。具体融合了哪些论文、专利、算法、Prototype、Product Capability、Tool 或 Knowledge Pipeline，进入 [`confirmation-ledger.md`](confirmation-ledger.md) 等待逐项确认。

历史事实、当前仓库证据和 Target 设计分别由本目录、[`../evidence/README.md`](../evidence/README.md) 和 [`../architecture/architecture.md`](../architecture/architecture.md) 维护。三者不得互相倒灌。

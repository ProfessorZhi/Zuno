# 历史事实确认 Ledger

status: USER_CONFIRMATION_REQUIRED
owner: Project Facts Owner
source_boundary: 只记录待用户逐项确认的问题，不替代 `docs/facts/` 六个事实文件

本台账用于下一轮人工补充历史事实。它不生产事实，也不把候选叙事升级为确认事实。用户没有明确回答前，相关条目的状态保持 `UNKNOWN` 或 `USER_CONFIRMATION_REQUIRED`；`User Answer` 和 `Final Status` 暂不预填。

## 研究成果如何进入产品

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| R-001 | Research inventory | `USER_CONFIRMATION_REQUIRED` | 已确认项目融合葛季栋团队此前多项法律智能研究成果，但具体清单未知 | 请逐项列出论文、专利、算法或原型；分别说明加入你之前、加入你之后、只停留在 Research Prototype、成为 Product Capability / Tool / Knowledge Pipeline 或未进入产品的内容 |  | 用户当前明确确认 |  |

## 原始业务与需求

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| B-001 | 第一版需求 | `USER_CONFIRMATION_REQUIRED` | 谁提出第一版需求、客户原话和原始人工流程未知 | 谁最早提出需求？当时原话是什么？不用系统时具体怎么做？ |  | UNKNOWN |  |
| B-002 | 主要用户 | `USER_CONFIRMATION_REQUIRED` | 法官、法官助理、书记员、法院信息化人员等比例未知 | 谁是主要使用者？不同角色分别做什么？是否有明确比例或主次？ |  | UNKNOWN |  |
| B-003 | 原始材料 | `USER_CONFIRMATION_REQUIRED` | 卷宗、裁判文书、法规、证据、PDF 等具体范围未知 | 用户实际上传或处理哪些材料？文件格式、单案件规模和版本关系是什么？ |  | UNKNOWN |  |
| B-004 | 原始 SOP | `USER_CONFIRMATION_REQUIRED` | “阅读材料—抽取—核对—分析—复核”目前只是 `RECONSTRUCTED_CANDIDATE` | 哪些步骤最耗时、最易错？哪些允许 AI 自动完成？哪些必须人工确认？ |  | UNKNOWN |  |
| B-005 | 质量问题 | `USER_CONFIRMATION_REQUIRED` | 已确认客户说“回答质量需要提高”，具体 Bad Case 和指标未知 | 当时错在哪里：没找到、找到错、跨文档关系错、引用错、推理错还是不可复核？有没有真实样例、修复和结果？ |  | `INC-HIST-001` |  |

## Agent / Platform 产品形态

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| P-001 | 产品边界 | `USER_CONFIRMATION_REQUIRED` | 是否是统一 Agent Platform，还是单一司法 Agent 产品，尚未确认 | 当时对外介绍的是平台、司法产品，还是二者兼有？正式产品名称是什么？ |  | UNKNOWN |  |
| P-002 | 多 Agent | `USER_CONFIRMATION_REQUIRED` | 是否有多个 Agent、Agent Cluster、Coordinator 或运行时 Agent-to-Agent 协作未知 | 当时有几个 Agent？是多个配置还是运行时互相协作？是否存在 Coordinator / Agent-to-Agent？ |  | UNKNOWN |  |
| P-003 | Agent 配置 | `USER_CONFIRMATION_REQUIRED` | Agent Catalog、Agent Studio、Model / Prompt / Knowledge / Memory / Tool / Skill 配置能力未知 | 用户能配置哪些项？是否能组合能力？“能力包”是否存在，正式名称和构成是什么？ |  | UNKNOWN |  |
| P-004 | 研究能力接入 | `USER_CONFIRMATION_REQUIRED` | 法律算法如何进入 Agent、能力包或平台未知 | 算法是 Tool、Knowledge Pipeline、Skill、独立 API 还是其他形式？是否存在平台间合作、API 或历史 MCP？ |  | UNKNOWN |  |

## Knowledge / RAG 历史实现

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| K-001 | 知识检索链路 | `USER_CONFIRMATION_REQUIRED` | 历史是否明确存在知识库、Ingestion、Chunk、Embedding、BM25、Vector、Hybrid、Reranker、Citation、GraphRAG、Knowledge Graph 或 Similar Case Retrieval 未知 | 请只确认实际用过的组件、版本或服务；哪些只是学习、实验、Demo 或当前仓库表面？ |  | UNKNOWN |  |

## 用户个人任务级 Ownership

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| O-001 | Memory 任务 | `USER_CONFIRMATION_REQUIRED` | 已确认 Memory 是早期重要工作，但具体原因、数据、写入和召回时机未知 | 你第一项 Memory 任务是什么？为什么做？保存什么？何时写入、何时召回、输出给谁？ |  | USER_CONFIRMED + UNKNOWN |  |
| O-002 | OpenViking 接入 | `USER_CONFIRMATION_REQUIRED` | 已确认参与 Memory / Context 接入，但引入原因和集成方式未知 | 为什么引入 OpenViking？使用 SDK、API、Adapter 还是其他方式？你具体改了哪一层？ |  | USER_CONFIRMED + UNKNOWN |  |
| O-003 | Agent / Tool 逻辑 | `USER_CONFIRMATION_REQUIRED` | 已确认参与部分 Agent 开发和 Tool Calling Strategy，具体逻辑与真实 Tool 未知 | 具体改过哪些 Agent 输入输出、状态或调用策略？当时有哪些真实 Tool？ |  | USER_CONFIRMED + UNKNOWN |  |
| O-004 | 调试与验证 | `USER_CONFIRMATION_REQUIRED` | 已确认曾查看或调试数据库，SQL、Bug、修复和验证未知 | 看过哪个数据库、为何排查、是否写 SQL？遇到什么 Bug，如何定位、修复和验证？ |  | USER_CONFIRMED + UNKNOWN |  |

## 团队与协作

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| T-001 | 成员与编制 | `USER_CONFIRMATION_REQUIRED` | 核心研发约 7–8 人，但姓名、Title、角色人数、PM 和客户侧人员未知 | 能否按姓名或匿名角色确认前端、Backend、Agent、Legal AI、QA、部署、PM、客户侧各有几人？ |  | USER_CONFIRMED + UNKNOWN |  |
| T-002 | 协作流程 | `USER_CONFIRMATION_REQUIRED` | Review、会议、Issue / Task 管理和接口协作方式未知 | 当时如何分任务、Review、开会、记录 Issue 和联调？请区分记得的事实与猜测。 |  | UNKNOWN |  |

## Demo、测试与 Pilot

| ID | Topic | Current Status | Current Statement | Question To User | User Answer | Evidence | Final Status |
|---|---|---|---|---|---|---|---|
| D-001 | 时间与参与者 | `USER_CONFIRMATION_REQUIRED` | Internal Demo、Customer Demo、Court-side Testing、Pilot 的日期、地点、操作者和观看者未知 | 每阶段大约何时、在哪里、谁操作、谁观看？Court-side Testing / Pilot 涉及哪些法院或人员？ |  | USER_CONFIRMED + UNKNOWN |  |
| D-002 | 测试方法 | `USER_CONFIRMATION_REQUIRED` | 测试材料、题目数量、Reference Answer、Reviewer 和 Evaluation Protocol 未知 | 有没有固定 QA、标准答案、专家评审、打分规则或可复现测试集？ |  | UNKNOWN |  |
| D-003 | Pilot 范围 | `USER_CONFIRMATION_REQUIRED` | Pilot 环境、Endpoint、时长、用户数、验收、SLA、QPS、Latency、Token、Cost、HA、DR 未知 | Pilot 实际在哪里运行、多久、多少用户和任务？是否正式验收？有哪些运行指标或灾备要求？ |  | USER_CONFIRMED Pilot Validation + Production NO |  |

## 使用规则

- 逐项确认后，才把回答写回对应的事实 Owner 文件；不要只更新本台账。
- 用户说“有印象但不确定”时，状态保持 `USER_PARTIAL_RECALL`，不能升级为 `USER_CONFIRMED`。
- 根据背景推演出的流程保持 `RECONSTRUCTED_CANDIDATE`，不能当作历史 SOP。
- 当前仓库只能证明 `CURRENT_REPOSITORY_EVIDENCE`，不能反推历史项目使用。
- 新架构设计属于 `TARGET_ONLY`，不写入历史事实。

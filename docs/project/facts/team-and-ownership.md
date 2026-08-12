# Team and Ownership

## 已确认的团队事实

| Claim | 状态 | 边界 |
|---|---|---|
| 核心研发约 7–8 人 | `[USER_CONFIRMED]` | 这是核心研发规模，不据此推出 LIPLAB 总人数或完整项目团队 |
| 一名学硕学长承担主要技术负责人角色 | `[USER_CONFIRMED]` | 不自动推出正式 title、全部架构决策或生产责任 |
| 用户由该学硕学长带入项目 | `[USER_CONFIRMED]` | 说明加入路径，不证明该学长是合同或产品负责人 |
| 用户是研究生工程参与者 | `[USER_CONFIRMED]` | 不等于项目负责人、客户负责人或整个后端负责人 |

以下仍为 `[UNKNOWN]`：是否包含教师、精确前端/算法人数、是否有独立测试或 DevOps、成员姓名、正式 title、责任链和评审流程。

## 用户本人工作

下表只记录用户明确确认过的参与范围，不扩大为完整 Owner：

| 工作 | 状态 | 保守表述 |
|---|---|---|
| Agent 开发参与 | `[USER_CONFIRMED]` | 参与 Agent 部分开发 |
| Memory 模块 | `[USER_CONFIRMED]` | 第一批重要任务之一是 Memory 模块 |
| OpenViking | `[USER_CONFIRMED]` | 参与 OpenViking 在 Memory / Context 区域的接入 |
| Tool Calling Strategy | `[USER_CONFIRMED]` | 参与工具调用策略相关开发 |
| LangGraph / GraphRAG | `[USER_CONFIRMED]` | 在开发过程中学习相关技术；不等于完整主链路实现 |
| 数据库 | `[USER_CONFIRMED]` | 曾进入数据库查看或调试数据；具体数据库产品、表、SQL 和客户端未知 |

以下不能直接写成用户主责，保持 `[UNKNOWN]`：整个 Agent Runtime、全部 RAG/GraphRAG、全部 FastAPI 后端、全部数据库、全部法律算法、整体架构、生产部署、前端和客户项目管理。

## 四类责任边界

```text
TEAM WORK
    团队共同完成的产品、算法、部署和交付；不能自动归属于用户。

PERSONAL WORK
    用户本人明确参与的 Agent、Memory、OpenViking 接入和 Tool Calling Strategy。

FRAMEWORK PROVIDED
    LangGraph、OpenViking 或其他库提供的通用能力；参与接入不等于用户实现框架。

OTHER TEAM WORK
    技术负责人、前端、算法、后端、测试、部署和客户侧人员的工作；当前大部分细节 UNKNOWN。
```

## 待恢复的 Ownership

| 责任 | 状态 | 需要的证据 |
|---|---|---|
| 产品范围和客户需求 | `[UNKNOWN]` | 会议、任务、邮件或客户反馈 |
| Agent / Workflow 的具体设计与提交 | `[UNKNOWN]` | Git、任务、评审记录 |
| RAG / Retrieval 的具体实现 | `[UNKNOWN]` | 代码、实验、指标 |
| FastAPI/API 的具体实现 | `[UNKNOWN]` | 提交、接口文档、联调记录 |
| 模型选择、训练或 Serving | `[UNKNOWN]` | 配置、训练和部署记录 |
| 发布、基础设施和故障处理 | `[UNKNOWN]` | 部署记录、告警、Runbook |

## 事实 Owner

本文件负责现实团队和个人贡献，不负责未来架构 Ownership。目标 Owner 进入架构专题，候选团队结构和追问进入 [`../../../project-reconstruction-lab/01-facts/`](../../../project-reconstruction-lab/02-history/team-and-ownership.md)。

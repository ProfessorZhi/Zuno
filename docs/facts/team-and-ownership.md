# 团队与个人 Ownership

status: current-fact
canonical_question: 历史项目由谁参与，用户本人实际做了什么？
owner: Project Facts Owner
source_boundary: 用户确认的个人与团队边界；未知细节不补写

## 团队事实

用户确认的核心研发规模约为 7–8 人。一名学硕学长承担主要技术负责人角色，并把用户带入项目。这里的“主要技术负责人”是对日常协作关系的保守描述，不等于正式 CTO、项目总架构师、合同负责人或拥有全部技术决策权。

团队可能涉及前端、后端 / Agent、算法 / Legal AI、测试和部署等角色，但精确人数、成员姓名、正式 Title、责任链、Review 方式和客户侧分工均为 `UNKNOWN`。不要再使用“5 人团队”，也不要把合理的角色候选写成已确认的编制。

## 用户的历史身份

用户是研究生工程参与者，约在 2026 年 3 月由上述学硕学长带入项目。加入时项目已有代码和简易自研前端。用户不是整个项目负责人，不是总架构负责人，也不是 Production Owner。

## 可以确认的个人参与

| 方向 | 状态 | 保守表述 |
|---|---|---|
| Agent | `USER_CONFIRMED` | 参与部分 Agent 开发 |
| Memory | `USER_CONFIRMED` | Memory 是加入后的第一批重要工作之一 |
| OpenViking | `USER_CONFIRMED` | 参与其在 Memory / Context 区域的接入 |
| Tool Calling Strategy | `USER_CONFIRMED` | 参与工具调用策略相关开发 |
| LangGraph / GraphRAG | `USER_CONFIRMED` | 在开发过程中学习相关技术；不能推出完整产品主链路 |
| 数据库 | `USER_CONFIRMED` | 曾进入数据库查看或调试数据；具体产品、表、SQL、客户端未知 |

## 必须保留的责任边界

```text
PERSONAL WORK
    Agent 部分开发、Memory、OpenViking Memory / Context 接入、Tool Calling Strategy。

TEAM WORK
    整体产品、完整后端、RAG / 检索、法律算法、部署、测试和交付；不能自动归属于用户。

FRAMEWORK PROVIDED
    LangGraph、OpenViking 或其他框架提供的通用能力；接入不等于用户实现框架。

OTHER TEAM WORK
    技术负责人、前端、算法、测试、部署和客户侧人员的工作；具体内容继续 UNKNOWN。
```

以下不得写成用户主责：整个 Agent Runtime、全部 RAG / GraphRAG、完整 FastAPI 后端、全部数据库、全部法律算法、整体架构、生产部署、前端或客户项目管理。

## 个人 Ownership 的下一层恢复目标

为了让历史叙事达到代码级可信度，还需要恢复：

```text
接到什么任务
  → 看了哪些模块
  → 改了哪类逻辑
  → 输入输出是什么
  → 遇到什么 Bug
  → 如何调试
  → 如何验证
```

在没有 Git、任务记录、Review 或用户回忆支持前，这些内容保持 `UNKNOWN`，不为了面试完整而补写。

## Owner 边界

本文件只拥有历史团队和个人贡献事实。Target Architecture 的 Domain、Runtime、Knowledge、Security 和 Eval Owner 由 [`../architecture/architecture.md`](../architecture/architecture.md) 统一说明；候选恢复材料仍在 `project-reconstruction-lab/`。

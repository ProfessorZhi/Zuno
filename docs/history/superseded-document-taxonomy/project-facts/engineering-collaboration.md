# Engineering Collaboration

status: canonical-history
canonical_question: 团队怎样拆任务、实现、联调、Review、Demo 和接收反馈？
owner: Project Facts / Team Process
replaces: 无；从 `team-and-ownership.md` 与 `development-evolution.md` 拆出协作过程

## 已确认锚点

| Claim | 状态 | Evidence | Strength | 边界 |
|---|---|---|---|---|
| 核心研发约 7–8 人 | `[USER_CONFIRMED]` | E-USER-003 | E1 | 精确角色和协作流程 UNKNOWN |
| 一名学硕学长承担主要技术负责人角色 | `[USER_CONFIRMED]` | E-USER-003 | E1 | 不自动推出正式 title 或全部 Review 权限 |
| 用户由该学长带入项目并参与已有代码开发 | `[USER_CONFIRMED]` | E-USER-003 | E1 | 具体任务拆分和提交 UNKNOWN |
| 存在内部 Demo、客户 Demo 和法院侧测试 | `[USER_CONFIRMED]` | E-USER-002 | E1 | 精确迭代顺序和会议流程 UNKNOWN |

## 协作过程恢复表

| 环节 | 当前状态 | 需要恢复的事实 |
|---|---|---|
| 需求进入 | `[UNKNOWN]` | 谁提出、以什么材料或会议进入 |
| 技术任务拆分 | `[UNKNOWN]` | 谁拆分、如何分配、是否有任务记录 |
| 个人开发 | `[USER_CONFIRMED]` | 用户参与 Agent、Memory、OpenViking Context/Memory 和 Tool Calling Strategy |
| 前后端联调 | `[UNKNOWN]` | API/JSON 输入输出、联调方式和具体功能 |
| Agent 与 Retrieval/Algorithm/Tool 联调 | `[UNKNOWN]` | Contract、错误处理和版本 |
| Code Review | `[UNKNOWN]` | 是否存在 Review、谁批准、通过标准 |
| Demo 与反馈 | `[USER_CONFIRMED]` | 存在 Demo 和质量反馈；材料与相对顺序 UNKNOWN |

## 三条待恢复 Contract

```text
Frontend ↔ Backend
Agent ↔ Retrieval / Knowledge
Agent ↔ Legal Algorithm / Tool
```

当前不能把 `session/query/answer/citation/status` 这类常见字段写成历史接口；它们只能作为
追问候选，直到有 OpenAPI、前端调用、日志、截图或用户确认。

## 不倒灌 Target

当前 Python/FastAPI、LangGraph、Microservice 和 Multi-Agent 文档只能描述目标或当前仓库
表面，不能证明历史团队按这些边界协作。历史协作应优先由任务记录、提交、聊天、演示和
用户的具体回忆恢复。

## Owner 边界

本文件负责历史协作机制，不负责未来团队 Ownership；个人贡献进入 [`team-and-ownership.md`](team-and-ownership.md)，
架构 Contract 进入 [`../architecture/architecture.md`](../architecture/architecture.md)。

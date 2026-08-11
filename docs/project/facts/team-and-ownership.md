# Team and Ownership

## 现实分工与目标分工必须分开

| 责任 | 现实负责人 | 证据 | 状态 |
|---|---|---|---|
| 需求、产品和范围决策 | 待确认 | 会议、任务、邮件 | `[UNKNOWN]` |
| Agent / Workflow | 待确认 | 代码、提交、评审 | `[UNKNOWN]` |
| Knowledge / Retrieval / RAG | 待确认 | 代码、实验、指标 | `[UNKNOWN]` |
| 模型选择、微调或 Serving | 待确认 | 配置、训练、部署记录 | `[UNKNOWN]` |
| 前后端和 API | 待确认 | 代码、部署 | `[UNKNOWN]` |
| 数据、基础设施、发布和故障 | 待确认 | 发布记录、告警、Runbook | `[UNKNOWN]` |
| 本人实际贡献 | 待确认 | 具体提交、任务和产物 | `[UNKNOWN]` |

## 用户确认的角色边界

| Claim | 状态 | 边界 |
|---|---|---|
| 用户是研究生工程参与者 | `[USER_CONFIRMED]` | 不等于项目商业立项人、客户负责人或整个项目负责人 |
| 用户具体负责过哪些模块、提交和上线动作 | `[UNKNOWN]` | 需要 Git、任务、评审、部署或可复现产物证据 |
| 团队完整人数、成员分工和交付责任链 | `[UNKNOWN]` | 不得从十一份 Target 模块文档推导 |

本文件中的目标 Ownership 只回答“Target 中谁应当拥有事实”；它不能证明历史团队曾按该方式分工。

## 红队必须区分

```text
TEAM WORK
PERSONAL WORK
FRAMEWORK PROVIDED
EXTERNAL TEAM WORK
```

“团队中有人部署了模型”不能写成“本人负责模型部署”；目标模块 Owner 不能自动代表历史团队分工。每一项“我负责”都需要能回答：谁提出需求、谁设计、谁实现关键路径、谁评审、谁发布、谁处理故障、谁能接替维护。

## 当前团队事实

真实团队人数、角色、协作方式和个人贡献目前保持 `[UNKNOWN]`，除非获得用户确认或直接证据。可以在红蓝工作区维护 A/B/C 候选，但候选不能进入简历、Current 或历史叙事。

目标 Ownership 由 [`../architecture/`](../architecture/README.md) 和对应 [`../modules/`](../modules/README.md) 描述；它回答“未来谁应当负责”，不回答“过去谁已经负责”。

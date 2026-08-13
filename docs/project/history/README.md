# 项目历史入口

`docs/project/history/` 只回答一个问题：**历史项目大致发生了什么，哪些内容仍然未知？**

这里的内容来自用户确认、仓库局部证据、公开背景和明确标注的候选恢复。它不拥有 Target Architecture，也不把当前仓库目录反推成完整历史项目。

## 阅读顺序

```text
project-background
  → requirements-and-workflows
  → team-and-ownership
  → development-history
  → incidents-and-improvements
  → delivery-and-usage
  → technology-history
```

## 状态边界

- `USER_CONFIRMED`、`USER_PARTIAL_RECALL`、`PARTIAL_REPOSITORY_EVIDENCE` 和 `PUBLIC_CONTEXT` 只在有对应证据时使用。
- `RECONSTRUCTED_CANDIDATE` 和 `UNKNOWN` 不得写成已发生事实。
- 当前仓库不是完整历史项目；代码、测试和运行证据进入 `docs/project/status/` 与 `docs/evidence/`。
- Target 设计进入 `docs/project/architecture/`；项目重建过程进入 `project-reconstruction-lab/`。

## 历史事实主线

目前可以稳定陈述：项目来自南京大学软件学院葛季栋 / LIPLAB 的长期智慧司法研发背景，日常合作侧称为“智慧法院项目组”，Zuno 是其中一个产品；用户约于 2026 年 3 月加入一个已有代码和简易前端的约 7–8 人核心研发团队，参与 Agent、Memory、OpenViking Memory/Context 和 Tool Calling Strategy。项目有内部 Demo、客户 Demo、法院侧测试和 Pilot Validation，但尚未正式生产部署；客户反馈之一是回答质量仍需提高。

正式产品名、合同主体、具体法院、试点环境、历史技术主链路、具体 Bad Case 和个人代码级 Ownership 继续保持 `UNKNOWN` 或候选状态。

## 事实恢复问题的覆盖

当前 12 个高价值恢复问题已经分别进入正式历史文档，但并不意味着全部已回答：

| 问题 | 正式入口 | 当前状态 |
|---|---|---|
| 项目背景、产品关系、服务方向 | [`project-background.md`](project-background.md) | 已确认背景；正式产品名和合同关系 `UNKNOWN` |
| 加入时间、已有代码、第一批工作、演进顺序 | [`development-history.md`](development-history.md) | 主线已恢复；精确日期和第一条任务 `UNKNOWN` |
| 输入材料、人工流程和痛点 | [`requirements-and-workflows.md`](requirements-and-workflows.md) | 确认锚点；流程为 `RECONSTRUCTED_CANDIDATE` |
| 团队与个人代码级 Ownership | [`team-and-ownership.md`](team-and-ownership.md) | 角色范围已确认；文件、API、Bug 和验证细节 `UNKNOWN` |
| Demo、法院测试、Pilot 和质量反馈 | [`delivery-and-usage.md`](delivery-and-usage.md) | 阶段已确认；QA 协议、Bad Case、指标 `UNKNOWN` |
| 历史技术产品和主链路 | [`technology-history.md`](technology-history.md) | 用户参与边界已确认；具体历史栈大部分 `UNKNOWN` |

其余恢复材料、Evidence ID 和场景化追问继续由 `project-reconstruction-lab/` 与 `docs/evidence/` 维护；本目录不为了消除未知而编造细节。

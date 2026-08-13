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

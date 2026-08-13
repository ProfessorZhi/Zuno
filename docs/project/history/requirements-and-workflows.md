# Requirements and Workflows

status: canonical-history
canonical_question: 真实业务需求、人工流程和产品痛点是什么？
owner: Project Facts / Business Context
replaces: 无；从 `project-background.md` 中拆出业务需求与流程问题

## 事实边界

本文件只记录历史项目实际面对的业务问题和工作流程。Target 的 Domain Model、Evidence
Requirement、Agent Runtime 或 GraphRAG 不能反向证明历史流程。

## 已确认锚点

| Claim | 状态 | Evidence | Strength | 边界 |
|---|---|---|---|---|
| 产品属于智慧法院项目体系中的一个产品 | `[USER_CONFIRMED]` | E-USER-001 | E1 | 不等于完整项目需求已恢复 |
| 法院侧真实人员参与过测试 | `[USER_CONFIRMED]` | E-USER-002 | E1 | 测试任务、角色和数量 UNKNOWN |
| 客户反馈回答质量需要继续提高 | `[USER_CONFIRMED]` | E-USER-002 | E1 | 具体质量问题和人工流程位置 UNKNOWN |

## 业务流程恢复状态

下列链路是待验证的历史候选，不是 Zuno 已确认事实：

```text
案件材料进入
  → 法官/助理阅读材料
  → 提取关键事实或事件
  → 对照双方陈述和证据
  → 识别冲突与争议焦点
  → 查找法条、类案或其他依据
  → 形成可引用的分析结果
  → 人工复核或交付
```

状态：`[RECONSTRUCTED_CANDIDATE]`。JIA 等公开研究说明这种法律任务链具有公开研究背景，
但不能替代 Zuno 自己的需求记录、页面、QA 或用户回忆。

## 仍为 UNKNOWN 的关键事实

- 谁提出了第一版需求，以及业务方使用的原始术语；
- 人工流程中最耗时或最容易出错的具体步骤；
- 是否确实存在跨文档事实核对、证据引用、法条/类案检索等固定操作；
- 产品解决的是法院内部司法辅助、法律问答、案件分析还是其他子场景；
- 业务方如何定义“回答质量”；
- 哪些流程必须人工批准，哪些可以自动化。

## 事实恢复入口

优先寻找需求文档、客户演示材料、法院 QA、页面截图、会议记录和用户的具体场景回忆。
若只能确认“类似流程”，保持 `[RECONSTRUCTED_CANDIDATE]`，不得升级为 `[USER_CONFIRMED]`。

## Owner 边界

本文件负责历史需求和人工流程；跨层 Product / Domain Target 进入 [`../architecture/architecture.md`](../architecture/architecture.md)，
当前状态进入 [`../status/README.md`](../status/README.md)，
候选恢复问题进入 [`../../../project-reconstruction-lab/01-facts/open-questions.md`](../../../project-reconstruction-lab/01-facts/open-questions.md)。

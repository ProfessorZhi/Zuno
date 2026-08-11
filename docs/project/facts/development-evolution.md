# Development Evolution

本文件只记录可证实的开发过程；没有 Git、任务、会议、发布或用户材料支持的阶段，必须标为 `[BLUE_PROPOSAL]` 或 `[UNKNOWN]`。

## 候选演进模型

| 阶段 | 可能目标 | 状态 |
|---|---|---|
| V0 | 业务研究、用户流程和人工基线 | `[BLUE_PROPOSAL]` |
| V1 | 最小 RAG 或单任务 AI 辅助 | `[BLUE_PROPOSAL]` |
| V2 | Hybrid、Rerank、版本、证据和评测 | `[BLUE_PROPOSAL]` |
| V3 | 长任务、Memory 和受控 Agent | `[BLUE_PROPOSAL]` |
| V4 | Tool、权限、审批、幂等和对账 | `[BLUE_PROPOSAL]` |
| V5 | 生产治理、容量、灾备和持续评测 | `[BLUE_PROPOSAL]` |

## 每个阶段必须回答

```text
需求来自谁？
上一阶段哪里失败？
为什么加入新能力？
谁提出、评审、实现和验证？
怎么测试、发布、回滚和处理 Bug？
哪些是 Current，哪些是 Target 或 Future？
```

当前不能把“最终 11 模块 Target”描述为项目第一天就存在。真实 V0/V1/V2 需要通过 Git History、面试原始记录、任务和部署材料重建；如果无法证明，就保持候选阶段。

红蓝攻击材料见 [`../../../project-red-blue/10-delivery-evolution.md`](../../../project-red-blue/10-delivery-evolution.md)，本文件是正式事实 Owner。

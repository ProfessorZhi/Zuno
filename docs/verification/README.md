# 文档验证目录

`docs/verification/` 保存对正式文档、架构 Contract 和工程证据的非规范性验证材料。这里的文件是消费者，不拥有新的架构事实。

正式事实源仍然是：

- `docs/project/architecture/`
- `docs/project/history/`
- `docs/project/status/`
- `docs/decisions/`
- `docs/governance/`

如果验证材料与正式架构冲突，以正式架构为准；如果验证暴露 Gap，应先修改正式事实源，再重新生成验证结果。旧专题和模块原稿在 `docs/history/superseded-document-taxonomy/`，不再是验证入口。

- [Architecture Red Team QA](./interview-qa/README.md)
- [Project Reconstruction & Architecture Lab](../../project-reconstruction-lab/README.md)

`docs/verification/interview-qa/` 是 Zuno 架构红队模拟面试 QA 的唯一维护目录。它按“为什么 → 怎么判断 → 怎么执行 → 失败怎么办 → 如何恢复 → 如何证明有效”的连续追问组织材料，不是第二套架构事实，也不是只罗列术语的题库。

红队发动攻击从 [`deep-dive-chains.md`](./interview-qa/deep-dive-chains.md) 开始；题目、覆盖矩阵和 Gap 报告都是该攻击工具的辅助材料。

`project-reconstruction-lab/` 是更上层的项目重建与架构协作工作区：先采集用户、规模、团队、当前落地和约束，再把产品价值、WorkBuddy 替代、团队协作、架构规模、开发过程、成本、安全和可靠性纳入盘问。它调用 `interview-qa/` 的架构攻击题，但不复制题目，也不拥有正式架构事实。Skill 设计规范位于 Lab 的 `skills/`，正式 Skill 生成仍需遵守当前 Codex 规范。

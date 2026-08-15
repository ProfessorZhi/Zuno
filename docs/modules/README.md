# Zuno 模块设计

Zuno 还没有冻结最终的模块划分。总体架构已经提出若干候选责任域，Round 02 正在继续检查这些边界是否足够稳定、是否真的需要成为独立模块。

因此，当前目录不会提前创建详细模块文档。先把责任边界讲清楚，再决定哪些内容值得拥有独立的状态、Contract、失败恢复和测试证据；这比按照旧目录直接恢复一组模块更可靠。

## 当前状态

```text
模块边界：尚未冻结
候选责任域：10 个
详细模块文档：尚未创建
模块分解闸门：未打开
```

这些状态对应当前的 Architecture Review Protocol。它们说明工作进行到哪里，不是新的架构决定。

## 为什么现在没有详细模块文档

当前还需要回答几类基础问题：哪些责任是 Zuno 必须自己拥有的，哪些可以交给 Generic Host、LangGraph、MCP、OpenViking 或其他 Provider；哪些内容只是 Library、Worker、Platform Responsibility 或 Cross-cutting Concern；哪些边界拥有独立的长期状态、失败模式、安全策略和可验证证据。

在这些问题稳定前，直接创建模块正文会把候选方案误写成既定设计。模块设计应当在 Overall Architecture Freeze Review 完成并明确打开模块分解闸门之后开始。

## 当前候选责任域

下表只帮助读者理解当前讨论范围。它们是候选责任域，不是已经冻结的十个模块，也不是十个服务。

| 候选责任域 | 它主要解决什么问题 |
| --- | --- |
| Product Surface & Agent Portfolio | 用户、法院系统、Host 和 Agent 组合从哪里进入 Zuno。 |
| Legal Domain & Work Product | 哪些法律业务结果、审查决定和工作成果可以长期保存。 |
| Knowledge & Evidence | 材料如何进入系统、变得可检索，并与证据和引用关联。 |
| Agent Runtime & Multi-Agent Orchestration | 复杂任务如何计划、执行、并行和恢复。 |
| Capability / Skill & Tool Runtime | 专业能力和外部工具如何被受控调用。 |
| Model Gateway | 不同模型如何按角色、预算和策略被调用。 |
| Memory & Context | 哪些任务上下文或经验可以在后续工作中复用。 |
| Security & Governance | 身份、权限、审批、秘密和审计如何保护任务。 |
| Observability & Evaluation | 系统如何留下可追踪信息，并判断结果是否达到要求。 |
| Infrastructure & Persistence | 数据持久化、Checkpoint、队列、Worker 和部署如何支撑运行。 |

候选责任域之间可能合并、拆分、外置或删除。尤其要注意，逻辑模块不等于进程、容器、数据库、Worker 或团队；物理部署仍然需要独立证据支持。

## Round 02 正在检查什么

Round 02 还没有 Main Judgment，下面内容都是 Review Questions / Open Concerns，而不是 Accepted Architecture Decision：

- 简单回答和复杂 Agent Runtime 的最终调用权分别属于谁；
- 哪个边界拥有正式引用和历史 WorkProduct 的权威；
- Memory 被删除时，多个副本和 Provider 如何保持一致；
- Domain Commit 与 Runtime Checkpoint 恢复时如何证明业务结果已经成立；
- 已发布结果失效后，外部消费者是否收到通知以及如何记录；
- 关键审计和重建到底依赖哪些事实源；
- Product Surface、Capability / Tool、Memory、Infrastructure 是否真的值得成为独立模块。

这些问题仍回到 [Round 02 原始记录](../history/red-blue/manual-round-02-overall-architecture-freeze-review.md) 审计；当前模块目录不替它们做决定。

## 未来的模块文档怎样读

一个正式模块文档应当先帮助普通工程师理解，再提供工程细节。推荐顺序是：

1. 这个模块解决什么问题；
2. 一个实际业务场景；
3. 它负责什么、不负责什么；
4. 它在 Zuno 整体流程中的位置；
5. 一条正常流程；
6. 最重要的状态；
7. 出问题时如何判断、恢复和交给人处理；
8. 它如何与其他责任域协作。

需要实现或验证时，再进入 Contracts、State Machine、Retry / Replan / Reconcile、Security、Persistence、Observability、Current / Target / Gap 和 Tests / Evidence 等工程参考部分。详细模块文档建立后，必须链接总体架构、项目事实和当前 Evidence，而不是复制它们。

## 相关入口

- [总体架构](../architecture/architecture.md)：解释整个系统为什么这样组合。
- [项目说明](../project/README.md)：解释项目从哪里来、谁参与和怎样发展。
- [当前工程证据](../evidence/README.md)：说明今天的代码和测试证明了什么。
- [Red / Blue 历史](../history/red-blue/README.md)：解释候选边界为什么被持续质疑。
- [Human-first 文档标准](../governance/human-first-documentation-standard.md)：说明四类人类文档与工程文档如何分工。

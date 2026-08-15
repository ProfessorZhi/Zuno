# Zuno 模块设计

Round 02 Main Judgment 已接受新的 Target Responsibility Direction，但总体 Architecture 仍等待 Main Architecture Freeze Review。因此，本目录暂时只保留模块入口，不创建详细模块正文。

## 当前状态

```text
Target Logical Responsibility Modules: 9
Platform / Infrastructure: Responsibility Layer
Optional Context Provider: yes
详细模块文档：尚未创建
MODULE_DECOMPOSITION_GATE: NOT_OPEN
```

九个 Target Logical Modules 是：

| 编号 | 责任域 | 它回答的问题 |
| --- | --- | --- |
| 01 | Application & Integration | 请求、Host/法院系统集成、Agent 定义、调用组合和结果发布从哪里进入？ |
| 02 | Legal Domain & Work Product | 哪些法律业务状态和正式工作结果可以长期保存？ |
| 03 | Knowledge & Evidence | 材料怎样处理、Ready、检索并与证据和引用关联？ |
| 04 | Agent Runtime & Control | 复杂任务怎样计划、执行、并行、重试、重规划和恢复？ |
| 05 | Capability & Skill | 专业法律能力怎样通过可替换 Contract 产生 Proposal？ |
| 06 | Tool Runtime & Effects | 外部查询和副作用怎样获得授权、执行并对账？ |
| 07 | Model Gateway | 模型怎样按角色、Provider、预算和策略调用？ |
| 08 | Security & Governance | 身份、权限、审批、生命周期和审计政策由谁决定？ |
| 09 | Observability & Evaluation | 系统怎样保留诊断信息并判断质量和发布资格？ |

Platform / Infrastructure Responsibility Layer 提供 PostgreSQL、对象存储、队列、Worker、Checkpointer Adapter、网络、秘密交付、备份和恢复等物理原语；它不是第十个业务逻辑模块。Memory / Context 也不再是一级模块，而是可替换的 Optional Context Provider Boundary。逻辑责任不等于进程、容器、数据库、Worker、Network Service 或团队。

## 为什么还没有模块正文

模块正文只有在总体架构冻结并打开模块分解闸门后才建立。每个模块必须先证明自己拥有独立问题域、长期状态或事实、稳定 Contract、失败与恢复语义、安全边界和可验证证据；否则它可能只是 Library、Provider、Worker 或 Cross-cutting Concern。

因此当前不会创建 `01-*.md` 到 `09-*.md`，也不会把本 README 的责任域列表当成已经冻结的最终代码目录。详细设计仍需链接总体架构、项目事实、ADR 和 Evidence，而不是复制它们。

## 相关入口

- [总体架构](../architecture/architecture.md)：解释九个责任域如何组合，以及为什么保留 Platform Layer 和 Optional Context Provider。
- [项目说明](../project/README.md)：解释项目背景、团队与开发过程。
- [当前工程证据](../evidence/README.md)：说明代码、测试和运行证据证明了什么。
- [有效 ADR](../decisions/README.md)：查看长期责任分类和跨边界恢复决定。
- [Red / Blue 历史](../history/red-blue/README.md)：查看这些边界为什么被质询。
- [Human-first 文档标准](../governance/human-first-documentation-standard.md)：查看总体架构和未来模块文档的 Part A / Part B 写法。

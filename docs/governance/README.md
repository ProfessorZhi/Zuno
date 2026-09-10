# Governance — 怎样让 Zuno 的文档长期可信

`docs/governance/` 不拥有 Zuno 的业务 Target。它负责让 Project、Architecture、Modules、Red / Blue、Research、Decisions 和 Evidence 在长期演进中仍能分清来源、责任和事实层级。

治理层回答的是：这句话属于谁？它是 History、Target、Decision、Current 还是 Unknown？两个文档冲突时应回哪一个 Owner？Agent 改文档前必须读什么？一个 Runbook 或测试存在到底能证明什么？

## 顶层文档模型

规范入口：[`documentation-architecture.md`](documentation-architecture.md)。

```text
System & Review
project/ | architecture/ | modules/ | red-blue/

Trust & Evolution
research/ | decisions/ | evidence/ | governance/
```

八个一级目录不代表八个平级 Truth Owner。`red-blue/` 负责压力测试，`research/` 负责上游依据；它们不能覆盖 Project History、Target Architecture 或 Current Evidence。

## Governance 内部结构

当前治理资料按责任理解为四组：

```text
standards / writing & documentation rules
provenance / project facts, ownership, source boundaries
workflows / Agent, GitHub and documentation maintenance process
operations / operational runbooks and recovery profiles
```

历史文件暂时可以继续平铺存在，后续物理分组只做路径整理，不复制第二套事实。

主要入口：

- [`documentation-architecture.md`](documentation-architecture.md) — 整套文档 Owner、阅读路径与迁移规则；
- [`project-fact-provenance.md`](project-fact-provenance.md) — 项目事实来源、允许表述与 Unknown；
- [`repo-ownership-matrix.md`](repo-ownership-matrix.md) — 仓库责任边界；
- [`human-first-documentation-standard.md`](human-first-documentation-standard.md) — Part A 人类技术写作要求；
- [`architecture-narrative-quality-standard.md`](architecture-narrative-quality-standard.md) — Architecture Narrative 质量标准与 Narrative Acceptance Gate；
- [`module-detail-freeze-readiness-review.md`](module-detail-freeze-readiness-review.md) — 九模块 Detail Freeze 前的证据 readiness 审查；不拥有 Target 或 Current；
- [`wave1-cross-module-contract-registry.md`](wave1-cross-module-contract-registry.md) — 跨模块 Contract registry；
- [`terminology.md`](terminology.md) — 跨文档术语；
- [`workflows/agent-workflow.md`](workflows/agent-workflow.md) — 人类与 Agent / GitHub 的协作方式；
- [`operations/`](operations/) — 运行、迁移和恢复 Runbook。

Red / Blue 已独立为 [`../red-blue/`](../red-blue/README.md)。过去的手工 Round 仅保留在其 `archive/legacy/` 中作为历史输入，不再构成正式执行模式或当前 Architecture Truth。

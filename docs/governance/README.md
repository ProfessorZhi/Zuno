# Governance — 怎样让 Zuno 的文档长期可信

`docs/governance/` 不描述 Zuno 的业务运行流程。它约束 Project、Architecture、Modules、Decisions 和 Evidence 怎样被写、被机器读取、被修改和被验证。

治理层回答的是：**这句话谁有资格写？它属于 History、Target 还是 Current？两个文档冲突时信谁？Agent 修改架构时必须先读什么？**

## 六域文档模型

规范入口：[`documentation-architecture.md`](documentation-architecture.md)。

三个系统域：

- `project/` — 真实项目背景、历史、团队和个人参与；
- `architecture/` — 理想总体 Target；
- `modules/` — Target 的责任分解和局部设计。

三个治理域：

- `decisions/` — 保存长期设计理由；
- `evidence/` — 证明 Current；
- `governance/` — 管理来源、Owner、写作、Contract 和机器路由。

## 当前治理资料

- [`project-fact-provenance.md`](project-fact-provenance.md) — 项目事实来源与允许表述；
- [`repo-ownership-matrix.md`](repo-ownership-matrix.md) — 仓库 Owner 边界；
- [`human-first-documentation-standard.md`](human-first-documentation-standard.md) — Part A 人类技术写作要求；
- [`architecture-narrative-quality-standard.md`](architecture-narrative-quality-standard.md) — Architecture Narrative 质量标准；
- [`wave1-cross-module-contract-registry.md`](wave1-cross-module-contract-registry.md) — 当前实施波次的跨模块 Contract registry。

`research/`、`maintenance/` 和 `terminology.md` 目前仍保留原路径以避免断链，但从文档架构上属于参考/运行附件，不是第七、第八个 canonical truth domain。

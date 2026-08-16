# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

```text
docs/project/                 人类可读的项目说明、背景、团队与开发过程
docs/architecture/            总体 Target Architecture 四文件
docs/modules/                 九个 Target 责任域的模块设计入口与 01–09 正文
docs/decisions/               有效 ADR
docs/evidence/                当前可复现证据
docs/history/red-blue/        架构审查过程记录
docs/operations/              当前运维 Runbook / recovery profile
docs/terminology.md           术语
docs/governance/project-fact-provenance.md  项目事实来源边界
docs/governance/human-first-documentation-standard.md  人类文档与工程参考的写作模型
```

## 阅读路径

普通项目阅读：`docs/project/README.md` → `docs/architecture/architecture.md` Part A → `docs/modules/README.md` → 需要的模块 Part A → ADR / Evidence。

总体架构阅读：先读 `docs/architecture/README.md` 和 `architecture.md` 的 Part A；需要实现、测试或审查工程细节时，再读 Part B、ADR、Evidence 和 Governance。

模块设计阅读：先读 `docs/modules/README.md` 的依赖和 Ownership 图，再读目标模块 Part A；进入 Deep Design、Codex Task 或 Review 前再读该模块 Part B、相关 ADR、Current Evidence 和总体 Architecture Part B。

架构复盘再按问题读取 `docs/history/red-blue/` 指定 Round；不要为了理解当前系统而默认加载全部历史对抗记录。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目为什么存在 | `docs/project/project-background.md` |
| 团队怎样组成、用户参与什么 | `docs/project/team-and-contributions.md` |
| 项目怎样开发和交付 | `docs/project/development-process.md` |
| 项目事实的来源和表述边界 | `docs/governance/project-fact-provenance.md` |
| 当前目标架构为什么这样设计 | `docs/architecture/architecture.md` |
| 九个责任域内部怎样工作 | `docs/modules/01-*.md` … `docs/modules/09-*.md` |
| 具体长期设计决策 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 架构曾怎样被质疑和判断 | `docs/history/red-blue/` |
| 当前运维如何执行 | `docs/operations/` |

# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

```text
docs/project/                 人类可读的项目说明、背景、团队与开发过程
docs/architecture/            总体 Target Architecture 四文件
docs/modules/                 模块边界占位
docs/decisions/               有效 ADR
docs/evidence/                当前可复现证据
docs/history/red-blue/        架构审查过程记录
docs/operations/              当前运维 Runbook / recovery profile
docs/terminology.md           术语
docs/governance/project-fact-provenance.md  项目事实来源边界
```

## 阅读路径

普通项目阅读：`docs/project/README.md` → `project-background.md` → `team-and-contributions.md` → `development-process.md` → `docs/architecture/` → `docs/modules/` → `docs/decisions/` → `docs/evidence/`。

架构复盘：先读当前 `docs/architecture/`，再按问题读取 `docs/history/red-blue/` 指定 Round。不要为了理解当前系统而默认加载全部历史对抗记录。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目为什么存在 | `docs/project/project-background.md` |
| 团队怎样组成、用户参与什么 | `docs/project/team-and-contributions.md` |
| 项目怎样开发和交付 | `docs/project/development-process.md` |
| 项目事实的来源和表述边界 | `docs/governance/project-fact-provenance.md` |
| 当前目标架构为什么这样设计 | `docs/architecture/architecture.md` |
| 具体长期设计决策 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 架构曾怎样被质疑和判断 | `docs/history/red-blue/` |
| 当前运维如何执行 | `docs/operations/` |

# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

```text
docs/project/                 项目背景与开发过程
docs/architecture/            总体 Target Architecture 四文件
docs/modules/                 模块边界占位
docs/decisions/               有效 ADR
docs/evidence/                当前可复现证据
docs/history/red-blue/        架构审查过程记录
docs/operations/              当前运维 Runbook / recovery profile
docs/terminology.md           术语
```

## 阅读路径

普通项目阅读：`docs/project/` → `docs/architecture/` → `docs/modules/` → `docs/decisions/` → `docs/evidence/` → `docs/terminology.md`。

架构复盘：先读当前 `docs/architecture/`，再按问题读取 `docs/history/red-blue/` 指定 Round。不要为了理解当前系统而默认加载全部历史对抗记录。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目为什么存在、怎样开发、用户参与什么 | `docs/project/` |
| 当前目标架构为什么这样设计 | `docs/architecture/architecture.md` |
| 具体长期设计决策 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 架构曾怎样被质疑和判断 | `docs/history/red-blue/` |
| 当前运维如何执行 | `docs/operations/` |

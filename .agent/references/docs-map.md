# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

```text
docs/project/                 项目级 Human-first 叙事：README.md + project.md
docs/architecture/            总体 Target Architecture 四文件
docs/modules/                 九个 Target 责任域的 Deep Design V2 与模块入口
docs/decisions/               有效 ADR
docs/evidence/                当前可复现证据
docs/history/red-blue/        架构审查过程记录
docs/operations/              当前运维 Runbook / recovery profile
docs/terminology.md           术语
docs/governance/project-fact-provenance.md  项目事实台账、来源和表述边界
docs/governance/human-first-documentation-standard.md  人类文档与工程参考的写作模型
```

## 阅读路径

普通项目阅读：`docs/project/project.md` → `docs/architecture/architecture.md` Part A → `docs/modules/README.md` → 需要的模块 Part A → ADR / Evidence。

总体架构阅读：先读 `project.md`，明确“为什么 Zuno 值得做、为什么不只用通用平台、哪些差异仍未证明”；再读 `docs/architecture/README.md` 和 `architecture.md` Part A。需要实现、测试或审查工程细节时，再读 Part B、ADR、Evidence 和 Governance。

模块设计阅读：先读 `docs/modules/README.md` 的任务主线、共同不变量和 Ownership，再读目标模块 Part A；进入 Detail Design、Codex Task 或 Review 前再读该模块 Part B 的 B1–B14、Part C、相关 ADR、Current Evidence 和总体 Architecture Part B。

架构评审 / 技术面试覆盖：项目级问题先读 `docs/project/project.md` 的 Reviewer 章节；具体 RAG、Runtime、Domain、Tool、Security、Eval 等问题直接进入对应 Module；“现在实现了吗”进入 Evidence。不要维护第二套问答真相。

当前模块状态是 `Deep Design V2 / Cross-Module Consistency`，九篇 Part A 已深化；字段级 Contract、最终状态枚举、数据库和服务拓扑尚未冻结，也没有自动 Implementation Authorization。

架构复盘再按问题读取 `docs/history/red-blue/` 指定 Round；不要为了理解当前系统而默认加载全部历史对抗记录。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目为什么存在、为什么值得立项、为什么不只用通用平台 | `docs/project/project.md` |
| 项目怎样发展、团队怎样组成、用户参与什么 | `docs/project/project.md` |
| 项目级 Reviewer / 技术面试问题怎样继续深入 | `docs/project/project.md` + 对应 Architecture / Module / Evidence |
| 项目事实的来源和表述边界 | `docs/governance/project-fact-provenance.md` |
| 当前目标架构为什么这样设计 | `docs/architecture/architecture.md` |
| 九个责任域内部怎样工作 | `docs/modules/01-*.md` … `docs/modules/09-*.md` |
| 具体长期设计决策 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 架构曾怎样被质疑和判断 | `docs/history/red-blue/` |
| 当前运维如何执行 | `docs/operations/` |

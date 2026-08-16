# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

```text
docs/project/                 项目级 Human-first 叙事：README.md + project.md
docs/architecture/            总体 Target Architecture 四文件
docs/modules/                 九个 Target 责任域：Deep Design V2 + Detail Design Candidate V1（9/9）
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

总体架构阅读：先读 `project.md`，再读 `docs/architecture/README.md` 和 `architecture.md` Part A。实现、测试或工程审查再读 Architecture Part B、ADR、Evidence 和 Governance。

模块设计阅读：先读 `docs/modules/README.md` 的任务主线、共同不变量和 Ownership，再读目标模块 Part A；进入 Detail Design、Codex Task 或 Review 前再读该模块 B1–B14、Part C、相关 ADR、Current Evidence 和总体 Architecture Part B。

九个模块全部包含 B14.1–B14.8 `Detail Freeze Candidate`。字段、事务 / CAS、Serving / Checkpoint / Registry、Migration、Crash Window 或 Failure Injection 任务必须继续读这些小节，但仍要回到 Evidence 判断 Current；不能把 Candidate 当作数据库或 Runtime 已经实现。

架构评审 / 技术面试：项目级问题先读 `docs/project/project.md` Reviewer 章节；RAG、Runtime、Domain、Tool、Security、Eval 等进入对应 Module；“现在实现了吗”进入 Evidence。

当前状态：九篇 `Deep Design V2 / Cross-Module Consistency` + `Detail Design Candidate V1`；coverage `9/9`；`module_detail_freeze: NOT_YET`；`implementation_authorization: NO`。

架构复盘按问题读取 `docs/history/red-blue/` 指定 Round，不默认加载全部历史记录。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目为什么存在、为什么值得立项、为什么不只用通用平台 | `docs/project/project.md` |
| 项目怎样发展、团队与参与事实 | `docs/project/project.md` |
| 项目级 Reviewer / 技术面试怎样继续深入 | `docs/project/project.md` + 对应 Architecture / Module / Evidence |
| 项目事实来源和表述边界 | `docs/governance/project-fact-provenance.md` |
| 当前目标架构为什么这样设计 | `docs/architecture/architecture.md` |
| 九个责任域内部怎样工作 | `docs/modules/01-*.md` … `docs/modules/09-*.md` |
| 九模块冻结前字段、事务、Crash / Migration 候选 | 对应模块 B14.1–B14.8；受 Architecture / ADR 约束 |
| 具体长期设计决策 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 架构曾怎样被质疑和判断 | `docs/history/red-blue/` |
| 当前运维如何执行 | `docs/operations/` |
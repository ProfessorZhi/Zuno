# Zuno 文档地图

本文只导航，不拥有事实、架构或模块语义。

```text
# Knowledge Plane
docs/project/                 项目级 Human-first Truth：README.md + project.md
docs/research/                研究谱系、Research→Engineering、平台 baseline、Narrative Blueprint
docs/architecture/            总体 Target Architecture 四文件
docs/modules/                 九个 Target 责任域：Deep Design V2 + Detail Design Candidate V1（9/9）

# Control & Maintenance Plane
docs/decisions/               有效 ADR
docs/evidence/                当前可复现证据
docs/governance/              Provenance、Owner、Contract、Human-first 与验收规则
docs/maintenance/             Operations、Agent workflow、History / Red-Blue

docs/terminology.md           术语
```

## 阅读路径

普通项目阅读：`docs/project/project.md` → `docs/research/README.md`（涉及研究来源/平台比较时）→ `docs/architecture/architecture.md` Part A → `docs/modules/README.md` → 需要的模块 Part A → ADR / Evidence。

总体架构阅读：先读 `project.md`，必要时读 Research-to-Engineering / platform baseline，再读 `docs/architecture/README.md` 和 `architecture.md` Part A。实现、测试或工程审查再读 Architecture Part B、ADR、Evidence 和 Governance。

模块设计阅读：先读 `docs/modules/README.md` 的任务主线、共同不变量和 Ownership，再读目标模块 Part A；进入 Detail Design、Codex Task 或 Review 前再读该模块 B1–B14、Part C、相关 ADR、Current Evidence 和总体 Architecture Part B。

九个模块全部包含 B14.1–B14.8 `Detail Freeze Candidate`。字段、事务 / CAS、Serving / Checkpoint / Registry、Migration、Crash Window 或 Failure Injection 任务必须继续读这些小节，但仍要回到 Evidence 判断 Current；不能把 Candidate 当作数据库或 Runtime 已经实现。

架构评审 / 技术面试：项目级问题先读 `docs/project/project.md`；“为什么不是 WorkBuddy / 普通 RAG”“研究成果怎样进入工程”先读 `docs/research/`；RAG、Runtime、Domain、Tool、Security、Eval 等进入对应 Module；“现在实现了吗”进入 Evidence。

架构复盘按问题读取 `docs/maintenance/history/red-blue/` 指定 Round，不默认加载全部历史记录。

## Canonical ownership

| 问题 | Owner |
| --- | --- |
| 项目为什么存在、怎样发展、团队与个人参与 | `docs/project/project.md` |
| 葛季栋/LIPLAB 研究谱系、外部平台基线、Research→Engineering | `docs/research/`（研究依据，不拥有 Current/Target） |
| 项目事实来源和表述边界 | `docs/governance/project-fact-provenance.md` |
| 当前目标架构为什么这样设计 | `docs/architecture/architecture.md` |
| 九个责任域内部怎样工作 | `docs/modules/01-*.md` … `docs/modules/09-*.md` |
| 九模块冻结前字段、事务、Crash / Migration 候选 | 对应模块 B14.1–B14.8；受 Architecture / ADR 约束 |
| 具体长期设计决策 | `docs/decisions/` |
| 当前仓库和运行状态有什么证据 | `docs/evidence/` |
| 文档、事实与 Contract 怎样治理 | `docs/governance/` |
| 架构曾怎样被质疑和判断 | `docs/maintenance/history/red-blue/` |
| 当前运维如何执行 | `docs/maintenance/operations/` |
| 人与 Agent 怎样维护仓库 | `docs/maintenance/agent-workflow/` + `.agent/` |

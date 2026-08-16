# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止。

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| 项目背景、历史事实、立项逻辑、通用平台差异 | `docs/project/project.md`、`project-fact-provenance.md` | Project Documentation |
| 技术面试 / 架构 Reviewer 连续追问 | `docs/project/project.md` Reviewer 章节，再按问题进入 Architecture / Module / Evidence | 对应事实 Owner |
| 个人贡献 | `docs/project/project.md` 第 10 章、历史任务级证据 | Project Documentation；不得由当前 Target 反推 |
| 文档结构、README、Agent 路由 | `workflow.md`、`docs-map.md`、验证地图 | Documentation |
| 阅读总体架构、理解系统 | `docs/project/project.md`、`docs/architecture/README.md`、`architecture.md` Part A | Architecture |
| 总体架构或跨层设计 | `architecture.md` Part A+B、有效 ADR、Evidence、Governance | Architecture |
| 阅读模块、理解责任域 | `docs/modules/README.md`、对应 `docs/modules/0X-*.md` Part A | Module Design |
| Module Deep Design / Review | 总体架构 Part A+B、`docs/modules/README.md`、目标模块 Part A+B+C、ADR、Evidence、Governance | Module Design；不自动授权实现 |
| Module Detail Freeze Review | 上述全部 + 目标模块 B14.1–B14.8 +相邻模块 Candidate +相关 ADR / Evidence | Module Design；当前仅 Detail Candidate |
| 字段、DB / Manifest / Checkpoint / Registry、并发、Migration、Failure Injection 实现任务 | 对应模块 B14.1–B14.8 + 当前代码 / Migration；先确认模块 Detail Freeze 与独立 Implementation Authorization | Architecture + Codex；不得自行改变冻结原则 |
| 实现、测试、Migration、Recovery、Contract、Security | 总体架构 + 对应模块 Deep Design / Detail Candidate + ADR + Evidence + Governance | Architecture / Runtime |
| 架构为什么发生变化 | 当前架构 + `docs/history/red-blue/` 指定 Round | Architecture Review |
| 当前运行、部署、生产准备度 | `docs/evidence/`、`docs/operations/`、代码和测试 | Evidence / Operations |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 + 对应模块 | Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、Evidence、09 模块 | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- Project 如果发现必须新增 / 删除九个逻辑模块、扩大 Canonical Legal Kernel 或改变跨模块 Owner，必须升级 Architecture Gap。
- 模块 Deep Design / Detail Candidate / Freeze Review 如果需要改变总体 Owner、扩大 Canonical Kernel 或修改 Admission / Invalidation / Lifecycle / Security / Effect 等跨模块不变量，停止局部设计并升级 Architecture Gap。
- 九个模块 B14.1–B14.8 都只是冻结前候选。没有 Module Detail Freeze 和明确 Implementation Authorization 时，不创建大规模业务表、Migration 或 Runtime 实现。
- 不允许把某个模块的字段模板机械复制到另一个模块；每个 Owner 的 identity、事务和恢复锚点必须按自身语义设计。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时默认保留，不用磁盘占用作为删除理由。
- 需要删除当前树材料时先列精确 manifest，确认授权和 Git 可追溯性。
- 未经明确授权，不根据 Red / Blue Proposal 或 Candidate 直接实施业务代码。

## 基本流程

```text
read project / current truth
  → distinguish History / Target / Current / Unknown
  → define owner and boundary
  → read overall architecture
  → read target module Deep Design V2 + Part C
  → for field-level questions, read B14.1–B14.8 Detail Candidate
  → read adjacent Owner candidates and Evidence
  → stop if a cross-module architecture gap appears
  → run Module Detail Freeze Review
  → obtain explicit Implementation Authorization
  → generate bounded Codex task
  → implement canonical path
  → migrate callers and tests
  → remove obsolete active path only with evidence
  → focused verify / full CI as required
  → commit + push
```
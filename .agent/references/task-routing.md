# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止。

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| 项目背景、历史事实、立项逻辑、通用平台差异 | `docs/project/project.md`、`project-fact-provenance.md` | Project Documentation |
| 技术面试 / 架构 Reviewer 连续追问 | `docs/project/project.md` 的 Reviewer 章节，再按问题进入 Architecture / Module / Evidence | 对应事实 Owner |
| 个人贡献 | `docs/project/project.md` 第 10 章、历史任务级证据 | Project Documentation；不得由当前 Target 反推 |
| 文档结构、README、Agent 路由 | `workflow.md`、`docs-map.md`、验证地图 | Documentation |
| 阅读总体架构、理解系统 | `docs/project/project.md`、`docs/architecture/README.md`、`architecture.md` Part A | Architecture |
| 总体架构或跨层设计 | `architecture.md` Part A + Part B、有效 ADR、Evidence、Governance | Architecture |
| 阅读模块、理解责任域 | `docs/modules/README.md`、对应 `docs/modules/0X-*.md` Part A | Module Design |
| Module Deep Design / Review | 总体架构 Part A+B、`docs/modules/README.md`、目标模块 Part A+B+C、相关 ADR、Evidence、Governance | Module Design；不自动授权实现 |
| 实现、测试、Migration、Recovery、Contract、Security | 总体架构 + 对应模块 Deep Design V2 + ADR + Evidence + Governance | Architecture / Runtime |
| 架构为什么发生变化 | 当前架构 + `docs/history/red-blue/` 指定 Round | Architecture Review |
| 当前运行、部署、生产准备度 | `docs/evidence/`、`docs/operations/`、代码和测试 | Evidence / Operations |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 + 对应模块 | Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、Evidence、09 模块 | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- Project 如果发现必须新增 / 删除九个逻辑模块、扩大 Canonical Legal Kernel 或改变跨模块 Owner，不允许在 Project 里直接改架构，必须升级为 Architecture Gap。
- 模块 Deep Design 发现需要新增 / 删除逻辑模块、改变总体 Owner、扩大 Canonical Legal Kernel 或修改 Admission / Invalidation / Lifecycle / Security 等跨模块不变量时，停止模块局部设计并升级为 Architecture Gap。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时，默认保留，不用磁盘占用作为删除理由。
- 需要删除当前树材料时先列精确 manifest，确认用户授权和 Git 可追溯性。
- 未经明确授权，不根据 Red / Blue Proposal 或 module design baseline 实施业务代码。

## 基本流程

```text
read project / current truth
  → distinguish History / Target / Current / Unknown
  → define owner and boundary
  → read overall architecture
  → read module Deep Design V2 when relevant
  → stop if a cross-module architecture gap appears
  → implement canonical path only after explicit gate
  → migrate callers and tests
  → remove obsolete active path
  → focused verify
  → commit + push
```

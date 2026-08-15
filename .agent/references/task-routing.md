# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止。

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| 项目背景、历史事实、个人贡献 | `docs/project/README.md`、`project-background.md`、`team-and-contributions.md`、`development-process.md` | Project Documentation |
| 文档结构、README、Agent 路由 | `workflow.md`、`docs-map.md`、验证地图 | Documentation |
| 阅读架构、理解系统 | `docs/architecture/README.md`、`architecture.md` Part A | Architecture |
| 总体架构或跨层设计 | `docs/architecture/architecture.md` Part A + Part B、有效 ADR、Evidence、Governance | Architecture |
| Module Design | 已冻结总体架构、`docs/modules/README.md`、相关 ADR、Evidence 和 Governance | Module Design；不自动授权实现 |
| 实现、测试、Migration、Recovery、Contract、Security | `architecture.md` Part A + Part B、有效 ADR、Evidence、Governance | Architecture / Runtime |
| 架构为什么发生变化 | 当前架构 + `docs/history/red-blue/` 指定 Round | Architecture Review |
| 当前运行、部署、生产准备度 | `docs/evidence/`、`docs/operations/`、代码和测试 | Evidence / Operations |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 | Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、Evidence | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时，默认保留，不用磁盘占用作为删除理由。
- 需要删除当前树材料时先列精确 manifest，确认用户授权和 Git 可追溯性。
- 未经明确授权，不根据 Red / Blue Proposal 实施架构变化。

## 基本流程

```text
read current truth
  → define owner and boundary
  → implement canonical path
  → migrate callers and tests
  → remove obsolete active path
  → focused verify
  → commit + push
```

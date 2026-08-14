# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止，不保存历史施工细节。

## 路由表

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| `docs/`、`.agent/`、History、README | `workflow.md`、`docs-map.md`、`verification-map.md` | 文档治理 |
| 项目事实、历史恢复、个人贡献 | `docs/facts/`、`docs/history/`、`project-reconstruction-lab/README.md` | Project History Owner |
| 架构 Red/Blue | `project-reconstruction-lab/WORKFLOW.md`、`docs/architecture/`、ADR、facts | Architecture Owner |
| 当前运行/部署审计 | `docs/facts/current-state.md`、`docs/evidence/`、代码和测试 | Facts/Evidence Owner |
| Target 状态 | `docs/architecture/`、ADR、治理 | Architecture Owner |
| Production Readiness | `docs/facts/current-state.md`、`docs/evidence/` | Facts/Evidence Owner |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client / UI |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 | 对应 Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、`docs/evidence/` | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时，默认保留，不用数量或磁盘占用作为删除理由。
- 需要旧兼容入口才能通过测试时，迁移调用方或重写测试，不恢复旧 Canonical facade。
- 当前 Lab 只有 `WORKFLOW.md` 和三个仓库内本地 Skill；它们通过 `.agent/system.yaml` 注册，任务匹配时直接读取，不自动导出。没有 active Round。未得到用户明确授权前，不得创建 Session、Question Set、Candidate Branch 或新的架构修改。

## 基本流程

```text
read current truth
  → define owner and contract
  → implement canonical path
  → migrate callers and tests
  → remove old active path
  → focused verify
  → commit + push
```

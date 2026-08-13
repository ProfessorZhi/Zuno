# 任务路由

本文只决定先读什么、走哪条 Owner 路径和何时停止，不保存历史施工细节。

## 路由表

| 任务 | 先读 | 主要 Owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| `docs/`、`.agent/`、History、README | `workflow.md`、`docs-map.md`、`verification-map.md` | 文档治理 |
| 项目事实、历史恢复、个人贡献 | `project-reconstruction-lab/README.md`、`docs/project/history/`、事实证据 | Project History Owner |
| 架构 Red/Blue | `project-reconstruction-lab/05-red-blue/README.md`、`principles.md`、`workflow-status.md`、`docs/project/architecture/`、ADR、status | Architecture Owner |
| 当前运行/部署审计 | `docs/project/status/current-reality.md`、`docs/evidence/`、代码和测试 | Status/Evidence Owner |
| Target 状态或 Production Readiness | `docs/project/status/`、ADR、治理 | Status/Evidence Owner |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client / UI |
| `src/backend/zuno` | `code-map.md`、`debugging.md`、总体架构 | 对应 Runtime Owner |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md`、`docs/evidence/` | Eval Owner |

## 停止条件

- 目标会改变业务 API、数据库 Schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证。
- 发现未提交资产、未进入 main 的 Commit 或未归属文件时，默认保留，不用数量或磁盘占用作为删除理由。
- 需要旧兼容入口才能通过测试时，迁移调用方或重写测试，不恢复旧 Canonical facade。
- 当前 Red/Blue 为 `RESET`，active protocol 为 `NONE`；Round-007 已在启动前取消。下一代 Protocol 未设计前不得创建 Session、Question Set、Candidate Branch 或新的架构修改。

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

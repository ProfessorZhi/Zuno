# 任务路由

本文只决定先读什么、走哪条 owner 路径和何时停止，不保存历史施工细节。

## 路由表

| 任务 | 先读 | 主要 owner |
| --- | --- | --- |
| 范围不清、只读盘点 | `AGENTS.md`、`docs-map.md`、`code-map.md` | 只读审计 |
| `docs/`、`.agent/`、history、README | `workflow.md`、`docs-map.md`、`verification-map.md` | 文档治理 |
| 项目重建、Red/Blue、Round Protocol | `project-reconstruction-lab/README.md`、`05-red-blue/round-protocol-v4.1.md`、`current-program.md` | Architecture Workflow Owner |
| `apps/web` | `apps/web/AGENTS.md`、`code-map.md` | Product client / UI |
| `src/backend/zuno` | `code-map.md`、`debugging.md` | 对应模块 owner |
| API / DTO / 前后端契约 | `code-map.md`、Product Surface module doc | Product Surface |
| Agent Runtime / Multi-Agent | `docs/project/agents/agent-platform.md`、`multi-agent-runtime.md`、`code-map.md` | Agent Runtime |
| Domain / lifecycle | `docs/project/domain/legal-domain-model.md`、`domain-state-lifecycle.md` | Domain Owner |
| Service / Security / persistence | `docs/project/services/`、`docs/project/security/`、`docs/project/data/`、`debugging.md` | Service / Security / Data |
| eval / dataset / metric | `tools/evals/zuno/AGENTS.md`、`verification-map.md` | Eval owner |

## 停止条件

- 目标仍会改变业务 API、数据库 schema、依赖、安全边界或 Target→Current 语义时，先停在设计和验证，不猜测。
- 发现未提交资产、未进入 main 的 commit 或未归属文件时，默认保留，不用数量或磁盘占用作为删除理由。
- 需要旧兼容入口才能通过测试时，迁移调用方或重写测试；不恢复 facade。

## 基本流程

```text
read current truth
  -> define owner and contract
  -> implement canonical path
  -> migrate callers and tests
  -> remove old path
  -> focused verify
  -> commit + push
```

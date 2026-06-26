# 任务路由

本文件替代旧 skill 目录。它是仓库内的轻量任务路由表，不再模拟外部插件结构。

## 任务路由层

这一层只回答“这类任务应该先读什么、按什么流程做”，不保存长篇设计正文。

## 路由规则

| 任务类型 | 必读参考 | 执行流程 |
| --- | --- | --- |
| 范围不清楚、只读盘点 | `docs/architecture/*`、`.agent/references/docs-map.md`、`.agent/references/code-map.md` | 只读审计，不修改、不提交 |
| 文档、`.agent`、references、history | `.agent/references/docs-map.md`、`.agent/references/workflow.md` | 文档维护流程 |
| 目录移动、归档、ignore、缓存清理 | `.agent/references/docs-map.md`、`.agent/references/code-map.md` | 仓库卫生流程 |
| `apps/web` | `apps/web/AGENTS.md`、`.agent/references/code-map.md` | 前端变更流程 |
| `src/backend/zuno` | `src/backend/zuno/AGENTS.md`、`.agent/references/runtime-call-chain.md` | 后端变更流程 |
| API / DTO / 前后端 contract | `.agent/references/code-map.md`、`.agent/references/runtime-call-chain.md` | API contract 流程 |
| 架构替换 | `.agent/architecture/near-term/`、`.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`、`.agent/references/workflow.md` | 架构重构流程 |
| eval tooling / datasets / metrics | `tools/evals/zuno/AGENTS.md`、`.agent/references/verification-map.md` | eval 变更流程 |

## 语言规则

前台文档默认中文。新增或重写 `docs/`、`.agent/` Markdown 时，目标、边界、步骤、验收和状态说明必须使用中文。历史档案可保留原文。

## 停止条件

遇到以下情况停止并返回证据：

- 任务要求修改 forbidden path。
- 必须把 Target 写成 Current 才能通过。
- 目录移动会丢失历史证据。
- 验证失败但根因不清楚。
- 用户目标不清晰，且不同选择会改变修改范围。

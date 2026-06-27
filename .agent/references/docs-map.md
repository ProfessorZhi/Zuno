# 文档地图

## 正式人类入口

- `README.md`：仓库总览和首读路径。
- `docs/README.md`：文档入口。
- `docs/architecture/current-architecture.md`：当前仓库事实。
- `docs/architecture/target-architecture.md`：近期目标摘要。
- `docs/architecture/roadmap.md`：当前状态和下一步。
- `docs/evidence/public-demo.md`：精选公开证据入口。
- `docs/evidence/eval-baselines.md`：Eval baseline 状态。
- `docs/reference/terminology.md`：公共术语表。
- `docs/architecture/decisions/`：仍然有效的正式 ADR。
- `docs/history/`：历史档案。

## Agent 工作流入口

- `AGENTS.md`：仓库级 Agent 总入口。
- `.agent/README.md`：Agent 工作流库说明。
- `.agent/references/task-routing.md`：任务路由入口。
- `.agent/references/workflow.md`：执行步骤、停止条件、验证和收尾。
- `.agent/references/`：精简导航、任务路由、工作流和查表层。
- `.agent/programs/current.md`：当前执行状态。
- `.agent/programs/implementation-roadmap.md`：当前执行计划总目录。
- `.agent/programs/PHASE*.md`：当前计划的平铺 phase 文件；每个新 program 从 `PHASE01` 开始。
- `.agent/programs/closure-checklist.md`：当前 phase 收口清单。
- `.agent/architecture/near-term/`：近期目标架构详细设计。
- `.agent/architecture/future/`：长期方向，不是当前实现目标。
- `.agent/templates/`：可复用提示和报告。
- `.agent/scripts/`：验证器和本地操作辅助。

## 边界

`docs/` 放稳定结论；`.agent/` 放可执行工作流和设计阶段细节；`docs/history/` 放过时或已完成材料。

## 前台瘦身规则

保留小前台：

- `docs/`：current architecture、target architecture、roadmap、decisions、evidence、terminology、history index。
- `.agent/`：workflow README、current program、near-term target design、references、scripts、templates。
- `docs/history/`：old lessons、old phases、retired plans、old audits/specs/runbooks/prototypes、replaced fragments、completed programs。

不要把 history folder、临时截图、generated cache、旧 phase fragment、旧 UI prototype 重新提升到前台。

## 目标架构视觉参考

- `.agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html`：canonical Target / Proposed visual blueprint。
- `.agent/architecture/near-term/01-target-runtime-architecture.md`
- `.agent/architecture/near-term/02-context-memory-architecture.md`
- `.agent/architecture/near-term/03-capability-tool-retrieval-architecture.md`
- `.agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md`
- `.agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md`

HTML 是 Target / Proposed，不是 Current Truth，也不是 `docs/` 前台路径。

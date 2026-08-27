# Current Program

state: `no-active`
active_program: `none`
queued_program: `none`

当前没有 active implementation 或 architecture review program。项目故事由 `docs/project/` 维护，总体架构由 `docs/architecture/` 维护，Red / Blue 原始审查记录由 `docs/maintenance/history/red-blue/` 维护。

## 当前边界

- 不自动创建新的 Round、Session、Question Set、Candidate Branch 或 Architecture Revision。
- 不把历史 Round、Target 文档、Mock、测试或目录存在写成 Current、Measured 或 Production Ready。
- 不修改业务 Runtime、数据库、Migration、UI、Dependencies 或 Production Infra，除非有独立明确任务。
- 新架构审查必须由用户明确激活；接受后的变化必须由独立任务写回 `docs/architecture/` 或 `docs/decisions/`。

## Red / Blue 工作空间边界

Red / Blue 当前没有常驻的独立 Lab Workspace。明确启动一次审查时，运行态工作空间属于 `.agent/programs/`；机器路由由 `.agent/system.yaml` 与 `.agent/references/` 负责，人类可读流程由 `docs/maintenance/agent-workflow/` 解释。Round 结束后，原始问答、裁决与历史快照进入 `docs/maintenance/history/red-blue/`，而被接受的架构变化必须单独进入 Architecture / Module / ADR。

```text
Project Story                      docs/project/                              CANONICAL
Overall Architecture               docs/architecture/                         CANONICAL TARGET
Research Reference                 docs/research/                             NON-CANONICAL INPUT
Architecture Review Runtime        .agent/programs/                           ACTIVE ONLY WHEN EXPLICITLY STARTED
Architecture Review Workflow       docs/maintenance/agent-workflow/           HUMAN PROCESS
Architecture Review History        docs/maintenance/history/red-blue/         HISTORY / NON-CANONICAL
Current Evidence                   docs/evidence/                             CURRENT EVIDENCE
Production Readiness               NOT_ESTABLISHED
Active Round                       NONE
```

旧 Program、Lab Workspace 和旧协议通过 Git history 追溯，不恢复到 current tree。旧 Program1 已 `SUPERSEDED / RETIRED`。

# Current Program

state: `no-active`
active_program: `none`
queued_program: `none`

当前没有 active implementation 或 architecture design program。项目故事由 `docs/project/` 维护，总体架构由 `docs/architecture/` 维护；Red / Blue Interview Harness 已独立到 `.agent/red-blue/`，其当前 Round 状态见 `.agent/red-blue/current.md`。

## 当前边界

- 不自动创建新的 implementation / design Program、Candidate Branch 或 Architecture Revision。
- 不把历史 Round、Target 文档、Mock、测试或目录存在写成 Current、Measured 或 Production Ready。
- 不修改业务 Runtime、数据库、Migration、UI、Dependencies 或 Production Infra，除非有独立明确任务。
- 新架构设计 Program 必须由用户明确激活；Red / Blue Round 由 `.agent/red-blue/current.md` 独立管理。

```text
Project Story                      docs/project/                              CANONICAL
Overall Architecture               docs/architecture/                         CANONICAL TARGET
Research Reference                 docs/research/                             NON-CANONICAL INPUT
Implementation / Design Program    .agent/programs/                           ACTIVE ONLY WHEN EXPLICITLY STARTED
Red / Blue Interview Harness       .agent/red-blue/                           SEPARATE RUNTIME
Red / Blue Human Workflow          docs/maintenance/red-blue/                 HUMAN PROCESS
Red / Blue History                 docs/maintenance/history/red-blue/         HISTORY / NON-CANONICAL
Current Evidence                   docs/evidence/                             CURRENT EVIDENCE
Production Readiness               NOT_ESTABLISHED
Active Program                     NONE
```

旧 Program、Lab Workspace 和旧协议通过 Git history 追溯，不恢复到 current tree。旧 Program1 已 `SUPERSEDED / RETIRED`。
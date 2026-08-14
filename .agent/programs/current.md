# Current Program

state: `no-active`
active_program: `none`
queued_program: `none`

最近完成的 Program 已收口 Round-006 Operational Pilot 与 V4.2 profile；当前 Lab 已完成轻量化
重建。上一代协议、Bootstrap、Reset 和工程辅助材料不再是 active tree；正式 Round 统一归档在
`docs/history/red-blue/`，当前唯一 Workflow 是 `project-reconstruction-lab/WORKFLOW.md`。

当前没有 active 或 queued Program；下一代 Red/Blue Protocol 和 Architecture Revision 都没有自动启动。

## Scope

本文件只描述当前执行状态，不保存历史施工材料。当前允许：

- 读取 `docs/facts/`、`docs/architecture/`、ADR、治理、Evidence 和指定历史归档；
+ 使用 `project-reconstruction-lab/WORKFLOW.md` 做默认手动审查；只有用户或上层 Coordinator 明确指定名称时，才读取三个本地 Skill；
- 为新的审查建立单独 Program，但必须先通过架构审查和用户 Gate。

当前禁止：

- 自动创建新的 Round、Session、Question Set、Candidate Branch 或 Architecture Revision；
- 把历史 Round、Target 文档、Mock、测试或目录存在写成 Current、Measured 或 Production Ready；
- 修改业务 Runtime、Facts、ADR、Schema、Migration、UI、Dependencies 或 Production Infra，除非另有明确任务。

## Current handoff

```text
Repository Closure                  CLOSED
Local Workspace Closure             CLOSED
Canonical Facts Taxonomy             DONE
Canonical Architecture               ACCEPTED_TARGET / NOT_CHANGED_IN_THIS_TASK
Implementation Evidence Track        INDEPENDENT / NOT_AN_ARCHITECTURE_GATE
Red/Blue Lab                         LIGHTWEIGHT_RECONSTRUCTION
Active Workflow                      project-reconstruction-lab/WORKFLOW.md
Formal Round Owner                   docs/history/red-blue/
Active Round                         NONE
Round-007                            CANCELLED_BEFORE_START
Production Readiness                 NOT_ESTABLISHED
```

`IMPLEMENTATION-EVIDENCE-CYCLE-001` 是独立 Evidence Track，不是 Architecture Review 的自动前置
条件。正式 Round 只从 `docs/history/red-blue/README.md` 读取；旧协议和流程工程通过 Git history
追溯。用户没有明确授权前，不创建新的 Session、题集或 Candidate。

旧 Program1 已 `SUPERSEDED / RETIRED`，不得恢复或重新激活。

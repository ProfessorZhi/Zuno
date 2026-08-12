# Current Program Reference

state: `active-design-program`
active_program: `PROJECT-ARCHITECTURE-RECONSTRUCTION-V1`
queued_program: `none`
program_class: `architecture-review-and-reconstruction`

当前 active 的是设计/审查 Program，不是 implementation program。详细执行契约见
`.agent/programs/current.md`；项目级工作流和候选材料见
`project-reconstruction-lab/README.md`。

## 当前边界

- Canonical Facts V1 已形成，本轮不继续增加 Facts 分类；
- Track A 继续恢复事实深度，但不把候选记忆直接写成事实；
- Track B 从真实问题重新攻击 Product、Domain、Runtime、Knowledge、Service、Data、Security 和 Eval；
- Python-only 与 Microservice 是 Owner Target Constraint，但具体服务数量和边界仍在审查；
- 本 Program 不修改业务 Runtime、UI、Schema/Migration、依赖或生产 Infra；
- User Architecture Gate 已批准 Part-A Target，Canonical Sync 已应用；Implementation Task
  Candidate 仅进入 `READY_FOR_TASK_DEFINITION`，本 Program 仍不得修改 Runtime 或创建 active
  implementation Program。
- `ZUNO-RED-BLUE-WORKFLOW-V2 / ROUND-001` 已生成并完成 100 题记录；其原始 P0/Critical
  Closure 仍保持 OPEN，但经 Gate Realignment 后 Part-A Target 已被批准并完成 Canonical Sync。
- `RB-BLUE-REPAIR-001` 已完成 Root-Cause Clustering、Part-A Repair 和 Counter Retest；
  Round-002 具备启动条件但保持 `READY_NOT_STARTED`；I/E/X Closure 继续作为后续轨道推进。
- 当前 Evidence Closure 会话为 `RB-EVIDENCE-CLOSURE-001`；它复用已有 focused verifier/test，
  不修改 Runtime/UI/Schema/Migration/生产 Infra。当前 Final P0 为 12，Closure-grade evidence
  为 0/12，Counter Retest 尚未执行，Canonical Docs 不得同步。
- 当前已执行 `RB-P0-V4-EXECUTION-001`：6 项 V4 verification/emulator records、5 项 V3
  current/narrow records；Red 接受为 Closure 的数量为 0，Q066 为 BLOCKED_EXTERNAL，Q039-B
  为 V5 benchmark gap，12 个原始 P0 仍 OPEN。
- 当前 Gate Realignment 会话为 `RB-GATE-REALIGNMENT-001`：A-P0=0、I-P0=11、E-P0=1、
  X-P0=1；用户 Gate 已 `APPROVED`，Canonical Sync 已应用为 `ACCEPTED_TARGET`。该分类不关闭
  原始 P0，也不激活 Implementation Program。

## 当前交接

```text
Repository Closure                  CLOSED
Local Workspace Closure             CLOSED
Repository Fresh-State Reset        CLOSED
Canonical Facts Taxonomy V1         DONE
Fact Depth Recovery                 IN_PROGRESS
Product / Architecture Reconstruction IN_PROGRESS
Red / Blue / Interview Review       READY / IN_PROGRESS
Canonical Architecture Sync         APPLIED / ACCEPTED_TARGET
Implementation Program              READY_FOR_TASK_DEFINITION (not active)
```

Canonical Runtime Program V1 已完成并归档。可读历史摘要位于：

- `docs/history/architecture-evolution.md`
- `docs/history/program-history.md`

完整原始材料不在当前树；需要考古时使用 GitHub commit history。

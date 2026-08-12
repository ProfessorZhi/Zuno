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
- 未通过 User Architecture Gate 前不生成 implementation task。
- `ZUNO-RED-BLUE-WORKFLOW-V2 / ROUND-001` 已生成并完成 100 题记录；当前为
  `NOT_PASSED_PENDING_USER_GATE`，P0 Critical Gate 保持 OPEN，Canonical Docs 未同步。

## 当前交接

```text
Repository Closure                  CLOSED
Local Workspace Closure             CLOSED
Repository Fresh-State Reset        CLOSED
Canonical Facts Taxonomy V1         DONE
Fact Depth Recovery                 IN_PROGRESS
Product / Architecture Reconstruction IN_PROGRESS
Red / Blue / Interview Review       READY / IN_PROGRESS
Canonical Architecture Sync         AFTER USER ARCHITECTURE GATE
Implementation Program              NOT_STARTED
```

Canonical Runtime Program V1 已完成并归档。可读历史摘要位于：

- `docs/history/architecture-evolution.md`
- `docs/history/program-history.md`

完整原始材料不在当前树；需要考古时使用 GitHub commit history。

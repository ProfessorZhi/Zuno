# Current Program Reference

state: `no-active`
active_program: `none`
queued_program: `none`

最近完成的是 Red/Blue Workspace Reset；上一代 Round-006 closure 与 V4.2 execution profile
consolidation 保持为历史完成记录。
详细执行契约见
`.agent/programs/current.md`；项目级工作流和实施证据见
`project-reconstruction-lab/README.md`。

## 最近完成 Program 边界

- 当前事实入口已收敛到 `docs/facts/`；历史背景和开发过程统一归档到 `docs/history/`，本轮不继续增加事实分类；
- Track A 继续恢复事实深度，但不把候选记忆直接写成事实；
- Track B 从真实问题重新攻击 Product、Domain、Runtime、Knowledge、Service、Data、Security 和 Eval；
- Python-only 与 Microservice 是 Owner Target Constraint，但具体服务数量和边界仍在审查；
- 本 V4.2 Bootstrap 只修改 Workflow、Governance、Lab Protocol、Session Contract、Prompt、
  Context Packet、Verifier、Routing 和 Docs Tests；Round-006 已在 3 个 Live Turn 后因 Workflow
  Execution Blocker 中止收口，不再继续运行，也不修改 Runtime、
  Facts、ADR、Schema、Migration、UI、Dependencies 或 Production Infra；
- Architecture Review Track 与 Implementation Evidence Track 并行；Wave-001 不再是 Round-006
  的自动前置 Gate，Architecture Score 也不能替代实现证据。
- `ZUNO-RED-BLUE-WORKFLOW-V2 / ROUND-001` 已生成并完成 100 题记录；其原始 P0/Critical
  Closure 仍保持 OPEN，但经 Gate Realignment 后 Part-A Target 已被批准并完成 Canonical Sync。
- `RB-BLUE-REPAIR-001` 已完成 Root-Cause Clustering、Part-A Repair 和 Counter Retest；
  `RB-WORKFLOW-V3-ROUND-002` 已完成 100Q、评分、决策、Delta 和 Canonical Sync；I/E/X
  Closure 继续作为后续轨道推进。
- 当前 Evidence Closure 会话为 `RB-EVIDENCE-CLOSURE-001`；它复用已有 focused verifier/test，
  不修改 Runtime/UI/Schema/Migration/生产 Infra。当前 Final P0 为 12，Closure-grade evidence
  为 0/12，Counter Retest 尚未执行，Canonical Docs 不得同步。
- 当前已执行 `RB-P0-V4-EXECUTION-001`：6 项 V4 verification/emulator records、5 项 V3
  current/narrow records；Red 接受为 Closure 的数量为 0，Q066 为 BLOCKED_EXTERNAL，Q039-B
  为 V5 benchmark gap，12 个原始 P0 仍 OPEN。
- 当前 Gate Realignment 会话为 `RB-GATE-REALIGNMENT-001`：A-P0=0、I-P0=11、E-P0=1、
  X-P0=1；用户 Gate 已 `APPROVED`，Canonical Sync 已应用为 `ACCEPTED_TARGET`。该分类不关闭
  原始 P0；Wave-001 也不会把实现证据升级为 Production Ready。

## 当前交接

```text
Repository Closure                  CLOSED
Local Workspace Closure             CLOSED
Repository Fresh-State Reset        CLOSED
Canonical Facts Taxonomy V1         DONE
Fact Depth Recovery                 OPEN EVIDENCE GAP / NO ACTIVE PROGRAM
Product / Architecture Reconstruction OPEN CANDIDATE / NO ACTIVE PROGRAM
Red / Blue / Interview Review       RESET / NO ACTIVE PROTOCOL
Canonical Architecture Sync         APPLIED / ACCEPTED_TARGET (V3.1.3 Round-005 review)
Implementation Evidence Wave-001   COMPLETE (TASK-001 / TASK-003; independent Track B)
V3 Round-003                       COMPLETE; V3.1.1 normalization COMPLETE; V3.1.2 Round-004 COMPLETE; V3.1.3 Round-005 COMPLETE; V3.1.3.1 Semantic Audit COMPLETE
V4.1 Workflow Bootstrap            HISTORICAL / IMMUTABLE
V4.2 Workflow Bootstrap            ACCEPTED_WITH_DEBT / EXTERNAL_VERDICT_PROVIDED
Round-006                         ABORTED_OPERATIONAL_PILOT / WORKFLOW_EXECUTION_BLOCKER; 3 LIVE TURNS; SCORE INVALID; CANDIDATE NONE
V4.2 default profile              BATCH_ADVERSARIAL
V4.2 experimental profile         LIVE_ADAPTIVE
Round-007                         CANCELLED_BEFORE_START
Round-006 closure                 COMPLETE
V4.2 batch profile consolidation  COMPLETE / HISTORY
Architecture Readability Gate    IN_PROGRESS
Next Red/Blue Protocol            NOT_DESIGNED
```

Canonical Runtime Program V1 已完成并归档。可读历史摘要位于：

- `docs/history/architecture-evolution.md`
- `docs/history/program-history.md`

完整原始材料不在当前树；需要考古时使用 GitHub commit history。

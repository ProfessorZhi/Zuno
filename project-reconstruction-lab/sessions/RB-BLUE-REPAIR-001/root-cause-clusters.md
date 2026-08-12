# RB-BLUE-REPAIR-001 Root-Cause Clusters

## 解释规则

本表把 Round-001 的 100 个问题按主要根因归并，而不是逐题写补丁。`Initial P0/P1` 是
Round-001 的原始记录；它被保留为历史结果。`Final Severity` 是基于 Blue Answer 和 Red
Impact Assessment 的重分类，不代表问题已经关闭。

| Cluster | Root Cause | Questions | Initial P0/P1 | Final P0/P1/P2/P3 | Blue Repair |
|---|---|---|---:|---:|---|
| RC-001 | Product Problem / Domain Boundary | Q001–Q011 | 7 / 4 | 1 / 5 / 5 / 0 | 用真实法院任务、最小 Domain Contract 和 Host+Backend 基线约束产品差异 |
| RC-002 | Canonical Ownership / Governance | Q012–Q020 | 5 / 4 | 1 / 3 / 2 / 3 | 建立 Owner、Proposal、State、Decision 和 User Gate 关系 |
| RC-003 | Runtime Control / Planning | Q021–Q035 | 7 / 8 | 1 / 8 / 4 / 2 | 分离 Run/Plan/Step/Checkpoint 与 Domain State，收缩默认 Replan/Multi-Agent |
| RC-004 | Knowledge / Graph / Memory Evidence | Q036–Q050 | 8 / 7 | 1 / 6 / 7 / 1 | Graph、Memory、Legal Capability 变为 Conditional Provider，统一 Evidence Contract |
| RC-005 | Data / State / Consistency | Q051–Q060 | 7 / 3 | 1 / 7 / 1 / 1 | 明确 SoR、Projection、Raw Artifact、Cache、版本和重建能力 |
| RC-006 | Tool Effect / Sandbox / Security | Q061–Q070 | 7 / 3 | 6 / 1 / 2 / 1 | 强制 Policy/Approval/Effect Receipt/Unknown Reconciliation 状态链 |
| RC-007 | Failure / Retry / Recovery | Q071–Q080 | 7 / 3 | 0 / 8 / 2 / 0 | 统一错误分类、Lease、Retry、Cancellation、Reconcile 和恢复 Contract |
| RC-008 | Physical Service / Deployment Boundary | Q081–Q088 | 2 / 6 | 0 / 2 / 5 / 1 | 保留 Microservice Target，拒绝 11=11；以 workload/failure/security/lifecycle 证明边界 |
| RC-009 | Eval / Benchmark / Observability | Q089–Q095 | 3 / 4 | 0 / 4 / 3 / 0 | 将每个架构 Claim 绑定 Benchmark、Trace、Release Gate 和删除条件 |
| RC-010 | Positioning / Personal Evidence / Round Governance | Q096–Q100 | 5 / 0 | 1 / 2 / 1 / 1 | 继续区分 Historical、Current、Target；不以分数绕过 User Gate |

总计：初始 `P0=58 / P1=42`；重分类后 `P0=12 / P1=46 / P2=32 / P3=10`。

## 根因结论

58 个初始 P0 并不等于 58 个独立 Critical Architecture Defect。它主要反映 Round-001 把
所有问题都设为 P0/P1，导致严重度饱和。真正需要 Critical Gate 的 12 个最终 P0 集中在：

```text
Canonical State Owner
Runtime/Domain State separation
HITL / Approval Gate
Evidence / Citation integrity
PlanVersion concurrency
Tool authorization
Irreversible Effect
Effect reconciliation
Sandbox boundary
Context / Tool security
Recovery state ownership
```

这次重分类降低了严重度噪声，但没有关闭这些 P0。每个 Final P0 仍需要实际 Contract、
Fault/ Security/Eval Evidence 和 Counter Retest。

## Cluster 到 Repair Change

| Change | Clusters | Repair intent | 状态 |
|---|---|---|---|
| BR-001 | RC-001, RC-002 | Part-A Problem、Domain Boundary、Canonical Owner | PROPOSED |
| BR-002 | RC-003 | Runtime Control 与 Domain State 分离 | PROPOSED |
| BR-003 | RC-004 | Knowledge/Evidence/Graph/Memory Provider Contract | PROPOSED |
| BR-004 | RC-005 | SoR、Projection、Artifact、Cache 和一致性 | PROPOSED |
| BR-005 | RC-006 | Tool Effect、Approval、Sandbox、Unknown Outcome | PROPOSED |
| BR-006 | RC-007 | Failure taxonomy、Retry、Recovery、Idempotency | PROPOSED |
| BR-007 | RC-008 | Service Boundary 与 Deployment Profile | PROPOSED |
| BR-008 | RC-009, RC-010 | Eval/Governance/Personal Evidence Gate | PROPOSED |

所有 Change 仍未通过 User Architecture Gate，不能同步 `docs/`。

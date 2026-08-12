# ROUND-001 Blue Change Set

本文件只保存 Blue Reconstruction Proposal。当前 `User Gate=PENDING`、`Sync Status=NOT_APPLIED`，因此没有任何内容写回 `docs/project/`，也没有生成 implementation task。

## CHANGE-001

Source Cluster IDs: CLUSTER-001, CLUSTER-002, CLUSTER-005
Before: Zuno/Native Runtime/Legal Domain 作为整体产品差异候选。
Attack: WorkBuddy + Legal Backend、普通 Workflow 和 JSON + PostgreSQL 可能已经足够。
Decision: REFINE / DEFER
After: 保留 Host-agnostic 最小 Domain Contract 候选；Native Domain-aware Runtime、完整 Kernel、长期 Memory 保持 DEFERRED/HYPOTHESIS，等待 A/B/C 和 Domain mutation/review/stale 测试。
New Complexity: 需要 A/B/C harness、Contract/Owner test、退出适配。
Removed Complexity: 不默认自建完整 Host、Native Runtime、所有 Legal Objects。
Canonical Paths: `docs/project/domain/`, `docs/project/agents/`, `docs/project/eval/`, ADR-0008
Evidence Needed: A/B/C、Kill Domain/Runtime、事实工作流、review/stale trace。
Validation Run: NOT_RUN
Validation Not Run: Runtime benchmark、Domain E2E、用户 Architecture Gate。
Rollback: 删除 Native Runtime/Kernel candidate，保留 Provider Contract 和 Host integration。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-002

Source Cluster IDs: CLUSTER-004, CLUSTER-005
Before: GraphRAG、Graph、Memory 可被技术名称误认为默认关键路径。
Attack: Hybrid RAG、Matter DB + Checkpoint 和普通 Workflow 可能同等有效。
Decision: REFINE / DEFER
After: Graph 是 Conditional Provider；Memory 是 policy/contract + replaceable provider；所有收益必须按 Query Class/Scope/Task 做消融。
New Complexity: Benchmark dataset、projection rebuild 和 provider conformance。
Removed Complexity: Always-on Graph、无证据 Long-term Memory。
Canonical Paths: `docs/project/knowledge/`, `docs/project/agents/`, `docs/project/eval/`, ADR-0006/0008
Evidence Needed: Graph Kill、Memory ablation、permission/stale/rebuild tests。
Validation Run: NOT_RUN
Validation Not Run: 真实法律 QA、成本/延迟、Graph 错边 fault test。
Rollback: 固定 Hybrid/DB+Checkpoint，删除 Graph/Memory Provider。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-003

Source Cluster IDs: CLUSTER-003, CLUSTER-006, CLUSTER-008
Before: Runtime/Domain/Queue/Tool 的状态边界只在 Target 文档中描述。
Attack: partial commit、unknown effect、duplicate job 和 checkpoint mismatch 会造成业务错误。
Decision: REFINE / BUILD DELTA PROPOSAL
After: 固定 Domain State、Runtime Control、Job Delivery、Effect Receipt 四类状态；要求 generation、idempotency、provider operation ID、lease、reconcile 和 fault tests。
New Complexity: Recovery contract、fault injection、trace fields。
Removed Complexity: checkpoint/queue 作为唯一事实源的隐含假设。
Canonical Paths: `docs/project/data/`, `docs/project/services/`, `docs/project/agents/`, ADR-0010
Evidence Needed: crash matrix、outbox/lease/effect/reconcile E2E。
Validation Run: NOT_RUN
Validation Not Run: 任何业务 Runtime 修改和实际故障演练。
Rollback: 只保留设计/Gaps，不进入生产代码；失败时收缩为同步/人工对账。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-004

Source Cluster IDs: CLUSTER-007, CLUSTER-009, CLUSTER-010
Before: Tool/Sandbox、Service Count、Deployment Profile 由候选拓扑描述。
Attack: 合并服务可能足够；Sandbox/secret/permission/Production 证据缺失。
Decision: KEEP CONTRACT / DEFER PHYSICAL TOPOLOGY
After: 保留 Tool Effect/Sandbox Security Contract；五服务只作为 Candidate，按 workload/failure/security/lifecycle 证据合并或拆分；Compose 不升级 Production。
New Complexity: security tests、service boundary matrix、profile evidence。
Removed Complexity: 11 modules=11 services、Compose=Production、K8s default。
Canonical Paths: `docs/project/services/`, `docs/project/security/`, `docs/project/deployment/`, ADR-0010
Evidence Needed: sandbox escape/egress/secret/revocation、resource profile、HA/DR/trace。
Validation Run: NOT_RUN
Validation Not Run: no runtime/deployment implementation in this Round。
Rollback: merge deployables while preserving logical owner/effect receipt contracts。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## CHANGE-005

Source Cluster IDs: CLUSTER-011, CLUSTER-012, CLUSTER-013
Before: 文档/研究/个人贡献容易被读者当成统一事实。
Attack: Public research、历史参与、Target ownership 和个人实现边界混淆。
Decision: KEEP GOVERNANCE / FACT RECOVERY
After: 每个 Candidate 绑定 Evidence State、Evidence ID、Scope、Cannot Infer；Provider 需 License/Fit/Exit；个人贡献继续由 User/Artifact Gate 决定。
New Complexity: Round traceability、Complexity Cards、License ledger。
Removed Complexity: “公开仓库可商用”“参与过即负责”“Target 即 Current”的隐含叙事。
Canonical Paths: `docs/project/facts/`, `docs/governance/`, `docs/decisions/`, Lab only until User Gate
Evidence Needed: old artifacts, official licenses, user confirmations, verifier evidence。
Validation Run: NOT_RUN
Validation Not Run: Fact Recovery and Build-vs-Buy review。
Rollback: 保持 UNKNOWN/DEFERRED，不删除历史材料。
User Gate: PENDING
Sync Status: NOT_APPLIED
Applied Commit SHA: NONE
Retest IDs: NONE

## Canonical Write Gate

```text
Question traceability + Red objection + Blue answer + Red score
  + Decision + Open risk + Required evidence + User Gate
  → only then Canonical Sync
```

本轮所有 Change 都是 `NOT_APPLIED`；不存在 Canonical Docs Changed，也不存在由 Round 自动产生的架构事实。

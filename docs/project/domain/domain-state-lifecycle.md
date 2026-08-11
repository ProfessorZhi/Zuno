# Domain State Lifecycle：新证据如何改变业务状态？

status: normative-target
canonical_question: Domain State 如何版本化、失效、审核、提交和恢复？
owner: Platform / Domain Service
replaces: old module domain-state sections (Superseded)

## Version and authority

Canonical Store 保存当前状态、不可变版本、provenance、dependency reference、review/audit 和必要 outbox。Provider 结果先进入 quarantine/proposal；Schema、权限、Evidence gate、CAS/version guard 和 Human Review 决定是否提交。

## New Evidence protocol

```text
EvidenceVersion committed
  → dependency lookup
  → affected Claim/Fact/Finding = STALE or REVIEW_REQUIRED
  → bounded re-evaluation job
  → new Proposal / Run
  → Domain Owner + Human Review
  → new Canonical Version
```

冲突、争议、适用法和相似案件是 derived result；策略可以选择重算、要求人工复核或保持旧版本并显示 stale。不得把新证据自动写成新的法律结论，也不得默认全量重算。

## Failure and recovery

- Domain transaction 成功、queue publish 未确认：outbox/retry，不能重复业务提交。
- Provider 返回未知结果：Receipt/Operation ID + reconciliation；不能盲目重试副作用。
- Runtime checkpoint 完成、Domain commit 缺失：以 DomainGeneration 为准恢复。
- HumanDecision 改变依据：下游 Finding/WorkProduct 标 stale，按 policy 创建新 Run。

默认不引入 Event Sourcing；PostgreSQL current state + version + dependency + audit 足够作为第一阶段 Target。若未来需要完整事件重放，必须另立 ADR。

## Current / Target / Gap

- Current：PostgreSQL migrations、outbox、generation/checkpoint 相关基础设施存在，但法律状态闭环未被 E2E 证明。
- Target：DomainGeneration 与 Runtime/CheckpointGeneration 分离，并可 reconciliation。
- Gap：新证据 stale propagation、跨服务 CAS、outbox/inbox 和 crash recovery evidence。

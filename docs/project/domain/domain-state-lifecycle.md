# Domain State Lifecycle：新证据如何改变业务状态？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: Domain State 如何版本化、失效、审核、提交和恢复？
owner: Platform / Domain Service
replaces: old module domain-state sections (Superseded)

## Part A — Architecture Narrative

Domain State 的生命周期回答一个业务问题：当案件材料变化、人工决定变化或一次长任务中断时，
系统如何知道原来的法律结论还能不能继续使用。Canonical Store 保存当前业务事实及其版本，
而 Agent checkpoint 只说明执行走到哪里；两者分开，才能在恢复时优先相信已经提交的业务状态，
而不是相信一个可能过期的控制快照。

以“新证据推翻旧事实”为例，EvidenceVersion 先被接受，再沿 dependency 找到受影响的 Claim、
Fact、Conflict、ApplicableLaw 或 Finding，并把它们标记为 stale 或 review_required。系统可以
启动有界重算、等待人工决定或保持旧版本但显式告知过期；只有新的 Proposal 通过 Domain Owner
和必要 Human Review，才产生新的 Canonical Version。这个流程避免全量重算，也避免旧 Finding
在新材料出现后继续伪装成当前事实。

主要失败包括 Domain commit 成功但队列确认丢失、checkpoint 显示完成但 Domain transaction
未提交，以及并行分支依据了不同 DomainVersion。恢复必须使用 generation/version/CAS 和
幂等标识进行对账。PostgreSQL current state + version 足以作为 Target 起点；Event Sourcing、
2PC 或 Saga 只有在重放、跨边界一致性或运营证据证明必要时才进入候选。
若更简单的 current-state + outbox/reconciliation 已经通过同一恢复测试，则应删除额外事件日志
或分布式事务复杂度。

## Part B — Detailed Architecture Specification

### Version and recovery contract

`DomainVersion` 是业务事实版本，`PlanVersion` 在激活后不可变，`CheckpointGeneration` 只表示
Runtime 控制位置。新 Evidence 通过 dependency lookup 产生 stale/review_required，再由 bounded
re-evaluation 和 Domain Owner 形成新版本。Domain commit、outbox publish、checkpoint、provider
receipt 各自可重试但必须幂等；未知副作用先 reconciliation，不能盲 retry。崩溃恢复必须比较
DomainGeneration 与 CheckpointGeneration，冲突则 quarantine/replan/manual review。

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

## PlanVersion / DomainVersion contract

`DomainVersion` 表示 Canonical 业务状态；`PlanVersion` 在激活后不可变。Replan 必须创建新的
`PlanVersion`，并在并行分支汇合前建立 barrier。每个 Step 记录读取的 DomainVersion/Snapshot；
提交时发现版本变化，必须选择冲突、重试、重新规划或 abstain/request-more-evidence，不能静默覆盖。

New Evidence 提交后，按依赖把受影响的 Fact、Conflict、Dispute、ApplicableLaw 和 Finding 标记
为 `STALE` 或 `REVIEW_REQUIRED`。只有 bounded re-evaluation 与 Domain Owner 验证完成后，才可
形成新的 Canonical Version 或触发新的 Agent Run。

## Current / Target / Gap

- Current：PostgreSQL migrations、outbox、generation/checkpoint 相关基础设施存在，但法律状态闭环未被 E2E 证明。
- Target：DomainGeneration 与 Runtime/CheckpointGeneration 分离，并可 reconciliation。
- Gap：新证据 stale propagation、跨服务 CAS、outbox/inbox 和 crash recovery evidence。

# Implementation Track

## 状态

```text
Track: READY_AFTER_USER_GATE
Active implementation program: NOT_STARTED
Task candidates: 6
Runtime changes in this session: NONE
```

I-P0 的“阻塞”是实施完成阻塞，不是 Target 设计阻塞。只有 User Architecture Gate 通过并
完成 Canonical Sync 后，候选任务才可以转成 active implementation Program。

## 任务候选

| Candidate | P0 | 目标 | 当前证据边界 | 禁止越界 |
|---|---|---|---|---|
| TASK-CANDIDATE-001 | Q005 | Domain Owner mutation/version contract | 当前无 Canonical persistence | 不把 model spike 当实现 |
| TASK-CANDIDATE-002 | Q053 | Plan/Domain optimistic concurrency/replan | 当前无联合写回 | 不宣称无 lost update |
| TASK-CANDIDATE-003 | Q039-C | Citation provenance guard | wrong-span 当前 XFAIL | 不把 missing-citation gate 当完整绑定 |
| TASK-CANDIDATE-004 | Q061 | execute-time authorization/revocation | 当前只有 contract/batch | 不绕过 Security/Approval |
| TASK-CANDIDATE-005 | Q063/Q064/Q070 | Effect receipt、unknown reconcile、audit chain | emulator/read-only 为窄证据 | 不宣称第三方 exactly-once |
| TASK-CANDIDATE-006 | Q016/Q097 | cross-state recovery reconciliation | 当前无四方 state store | 不把 checkpoint 当 Domain Fact |

## 激活条件

每个任务激活前必须有：Canonical Owner、Target Contract、Allowed/Forbidden Scope、状态迁移、
失败/Retry/Recovery/Idempotency、Security、Observability、Migration、Rollback 和 focused
acceptance tests。任务候选存在不等于 Implementation Complete。

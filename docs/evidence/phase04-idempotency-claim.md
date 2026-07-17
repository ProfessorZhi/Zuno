# PHASE04 Idempotency Claim 证据

phase_id: PHASE04
task_id: P04-T04
date: 2026-07-17
status: implementation_available
P04-T04: completed
same_key_same_hash: passed
same_key_different_hash: passed
renew: passed
expiry: passed
stale_generation_reject: passed
result_replay: passed
owner_crash: passed_process_exit_reclaim
tenant_isolation: passed
high_concurrency_single_winner: passed
owner_generation_expiry_fencing: passed
abort_reclaim: passed
worker_heartbeat_supervision: passed
busy_owner_reject: passed
effect_reconciliation_after_process_exit: passed
lost_completion_no_reexecution: passed
process_cancellation_propagates: passed

## 边界

本证据关闭 P04-T04，但不关闭 PHASE04。Idempotency Claim Service 只拥有 request hash、owner、generation、expiry、status 和 result ref 等基础设施事实。

Idempotency Claim != Domain Success。`completed` 只表示同一 canonical request hash 可以重放先前 result ref；领域 Owner 仍拥有结果含义与有效性，外部 effect 是否已发生必须由调用方提供的 reconciliation 查询判断。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，镜像 `postgres:16` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Lifecycle verifier | `python tools/scripts/verify_phase04_idempotency_claim.py` |
| Owner crash verifier | `python tools/scripts/verify_phase04_idempotency_owner_crash.py` |
| Tenant verifier | `python tools/scripts/verify_phase04_idempotency_tenant_isolation.py` |
| Supervision verifier | `python tools/scripts/verify_phase04_idempotency_supervision.py` |

## 已验证行为

- Claim 使用 PHASE03 canonical SHA-256，只持久化 request hash，不保存 request payload 或 Secret。
- 同 tenant/scope/key 与相同 hash 返回 active claim 或 completed result；不同 hash fail closed。
- 12 个并发 contender 收敛到一个 PostgreSQL row、一个 `acquired=true` winner、一个 owner 和一个 generation。
- transaction-local tenant 参与唯一边界；不同 tenant 可以安全复用 scope/key，同 tenant hash conflict 仍拒绝。
- live owner 可以 renew；错误 owner、错误 generation、过期 owner 都不能 renew 或 complete。
- `complete_idempotency` 同时校验 tenant、owner、generation、`in_progress`、未过期和非空 result ref。
- generation-fenced `abort_idempotency` 把确定未产生 effect 的失败转为可立即接管的 expired claim；旧 owner 不能 abort 新 generation。
- `IdempotencyWorkerSupervisor` 以独立 heartbeat 续租长任务；跨越初始 TTL 后 contender 仍只能读取原 live owner。
- live claim 被其他 owner 持有时 supervisor 抛出 busy error，不执行 operation。
- worker operation 确定失败且 reconciliation 返回空时立即 abort；replacement 在下一 generation 执行并完成。
- `KeyboardInterrupt/SystemExit` 等进程级取消不转成普通成功或 abort；取消沿调用栈传播，unknown-effect Claim 保持 `in_progress` 供后续对账。
- worker 子进程在同一事务提交 Claim 与 Outbox effect 后、Claim completion 前退出；replacement 过期接管后由 reconciliation 找回 event id，完成 Claim 且 operation 调用次数为零。
- 旧 worker 在 replacement generation 完成后不能提交 stale result。
- completed result 由后续 supervisor 直接 replay，不再次执行 operation。

## 命令与结果

```text
python tools/scripts/verify_phase04_idempotency_claim.py
PHASE04 idempotency claim verification passed.

python tools/scripts/verify_phase04_idempotency_owner_crash.py
PHASE04 idempotency owner crash verification passed.

python tools/scripts/verify_phase04_idempotency_tenant_isolation.py
PHASE04 idempotency tenant isolation verification passed.

python tools/scripts/verify_phase04_idempotency_supervision.py
PHASE04 idempotency supervision verification passed.
```

```text
pytest -q tests/integration/test_phase04_postgres_foundation.py tests/integration/test_phase04_idempotency_owner_crash.py tests/integration/test_phase04_idempotency_tenant_isolation.py tests/integration/test_phase04_idempotency_supervision.py -p no:cacheprovider
13 passed
```

## 状态结论

- P04-T04 的 Mandatory Scope 已有代码、真实 PostgreSQL 测试、进程退出故障与可复现 Evidence。
- P04-T04 状态为 `completed`。
- PHASE04 仍由其他 Work Package、官方 Checkpointer、完整 Backup/Restore/Replay、组合故障和 Coordinator approval 阻塞。

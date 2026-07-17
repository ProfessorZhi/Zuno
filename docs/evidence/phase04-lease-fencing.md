# PHASE04 Lease/Fencing 证据

phase_id: PHASE04
task_id: P04-T05
date: 2026-07-17
status: implementation_available
P04-T05: completed
lease_acquire: passed
heartbeat_renew: passed
duplicate_worker_reject: passed
expiry_transfer: passed
cancel_transfer: passed
late_fencing_token_reject: passed
database_clock_deadline: passed
same_owner_idempotent_acquire: passed
explicit_transfer: passed
fenced_commit_same_transaction: passed
worker_heartbeat_scheduler: passed
crash_handoff: passed
network_partition_heartbeat_loss: passed
pause_gc_delay: passed
cancel_transfer_race: passed
clock_tolerance: passed

## 边界

本证据关闭 P04-T05，但不关闭 PHASE04。Lease/Fencing 只拥有 worker 对 resource 的临时执行权、epoch 与 fencing token；不能代表领域结果成功。

领域 Owner 必须通过 `LeaseWorkerCoordinator.commit()` 在同一个 PostgreSQL 事务内先执行 `assert_fence(... FOR UPDATE)` 再写结果。只在业务写之前的另一个事务检查 token 不能满足本证据边界。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL | `zuno-postgres`，镜像 `postgres:16` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Network fault | 本地 TCP blackhole proxy 阻断 worker 到 PostgreSQL 的双向流量 |
| Primitive verifier | `python tools/scripts/verify_phase04_lease_fencing.py` |
| Coordination verifier | `python tools/scripts/verify_phase04_lease_worker_coordination.py` |
| 集成测试 | `pytest -q tests/integration/test_phase04_lease_worker_coordination.py tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider` |

## 已验证行为

- acquire、renew、expiry、cancel 与 transfer 的 deadline 全部由 PostgreSQL `now()` 计算，不依赖 worker 本地时钟。
- 同 owner 对 live lease 的 reacquire 保持 lease id/epoch，只延长 deadline；其他 owner 不能获取 live lease。
- 显式 `transfer_lease()` 校验完整旧 token，切换 owner/lease id 并把 epoch 加一；旧 token 随即失效。
- `assert_fence()` 校验 resource/owner/lease id/epoch/数据库 deadline/clock tolerance，并用 `FOR UPDATE` 将 fence 与后续业务写锁在同一事务。
- clock tolerance 大于剩余 lease lifetime 时提前 fail closed。
- `LeaseWorkerCoordinator` 用独立 heartbeat 跨越初始 TTL，期间 contender 不能接管，最终 fenced Outbox 写入提交。
- worker 暂停超过 TTL 后 replacement 接管并递增 epoch，旧 worker late result 被拒绝。
- worker 子进程持久化 lease 后退出；deadline 后 replacement 接管，崩溃 worker token 不能提交。
- cancel 与 transfer 并发竞争只有一个 PostgreSQL row-lock winner，最终收敛到新 owner 和下一 epoch。
- TCP blackhole 阻断 PostgreSQL heartbeat 后，partitioned worker 在有界时间内 fail closed；恢复并 handoff 后旧 token 不能提交，新 token 可以 fenced commit。
- verifier 重复运行后删除临时 lease/outbox rows，不遗留测试事实。

## 命令与结果

```text
python tools/scripts/verify_phase04_lease_fencing.py
PHASE04 lease/fencing verification passed.

python tools/scripts/verify_phase04_lease_worker_coordination.py
PHASE04 lease worker coordination verification passed.
```

```text
pytest -q tests/integration/test_phase04_lease_worker_coordination.py -p no:cacheprovider
1 passed

pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider
10 passed
```

## 状态结论

- P04-T05 Mandatory Scope 的代码、真实 PostgreSQL concurrency/fault tests 与可复现 Evidence 已齐全。
- P04-T05 状态为 `completed`。
- PHASE04 仍由其他 Work Package、官方 Checkpointer、完整 Backup/Restore/Replay、组合故障和 Coordinator approval 阻塞。

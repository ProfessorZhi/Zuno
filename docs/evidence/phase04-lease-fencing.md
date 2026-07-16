# PHASE04 Lease/Fencing Evidence

phase_id: PHASE04
task_id: P04-T05
date: 2026-07-16
status: partial_implementation_available
lease_acquire: passed
heartbeat_renew: passed
duplicate_worker_reject: passed
expiry_transfer: passed
cancel_transfer: passed
late_fencing_token_reject: passed

## 边界

本证据证明真实 PostgreSQL 上的 Lease/Fencing 子集：worker 可以获取 lease、续租、取消 lease；重复 worker 不能接管未过期 lease；lease 过期或取消后，新 worker 接管会递增 epoch；旧 worker 的 fencing token 在转移后不能再通过写入前检查。

这不关闭 P04-T05，也不关闭 PHASE04。Lease/Fencing 只证明基础设施所有权和 epoch 边界，不能代表领域结果成功。

## 环境

| 项目 | 值 |
| --- | --- |
| PostgreSQL service | `zuno-postgres`, image `postgres:16` |
| Database URL | `postgresql+psycopg://postgres:postgres@localhost:5432/zuno` |
| Verification command | `python tools/scripts/verify_phase04_lease_fencing.py` |
| Integration test | `pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider` |

## 已验证行为

- `acquire_lease()` 为资源创建 `FencingToken`，并能通过 `assert_fence()`。
- `renew_lease()` 只允许当前 owner、lease_id 和 epoch 续租，且保持 token identity 不变。
- 另一个 worker 不能接管未过期 lease。
- lease 过期后，新 worker 接管同一资源并递增 epoch。
- 旧 token 在转移后被 `assert_fence()` 拒绝，不能代表 late result 写入权限。
- 旧 token 在转移后不能续租。
- `cancel_lease()` 让当前 token 立即失效，后续接管递增 epoch。
- 已取消 token 不能重复取消。

## 命令与结果

```text
python tools/scripts/verify_phase04_lease_fencing.py
PHASE04 lease/fencing verification passed.
```

```text
pytest -q tests/integration/test_phase04_postgres_foundation.py -p no:cacheprovider
8 passed
```

## 剩余缺口

- 尚未证明真实 worker 进程崩溃后的 handoff。
- 尚未证明 network partition、pause/GC delay 和 cancel race。
- 尚未实现独立 heartbeat scheduler 或 worker coordination runtime。
- 尚未证明跨模块业务写入在所有路径都强制调用 `assert_fence()`。
- P04-T05 仍是 `ready`，不是 completed。

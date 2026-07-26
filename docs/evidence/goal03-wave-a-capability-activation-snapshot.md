# Goal03 Wave A Capability Activation Snapshot Evidence

状态：局部实现证据，不是 Wave A completed 证明。

## 目标

本证据覆盖 PHASE14 的 Installation / Activation CAS 与 AvailabilitySnapshot eligibility 纵切：

- Capability Installation 激活和撤销必须带 `expected_generation`。
- 当前 generation 从 `capability_transition_events` 推导，stale generation fail closed。
- Activation / Revocation 更新 installation 状态并写入 transition event。
- AvailabilitySnapshot 只包含 `ACTIVE` installation 绑定的 `ACTIVE` provider binding。
- Revocation 后同一候选不再进入 snapshot hash。

## 默认调用链

```text
CapabilityRepository.install_capability
→ CapabilityRepository.activate_installation
→ CapabilityRepository.append_transition_event
→ capability_transition_events CAS generation
→ capability_installations status/policy epoch update

CapabilityRepository.create_availability_snapshot
→ filter ACTIVE installation + ACTIVE binding
→ immutable capability_availability_snapshots row
```

## 代码证据

- `src/backend/zuno/platform/database/capability/domain.py`
- `src/backend/zuno/platform/database/capability/__init__.py`
- `tests/integration/test_goal03_wave_a_persistence.py`

## 验证

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py -p no:cacheprovider
```

结果：

```text
5 passed
```

## 边界

本证据证明 PHASE14 的 durable installation activation CAS、revocation 和 snapshot eligibility 进入 PostgreSQL repository 路径。

本证据不单独证明完整 PHASE14 completed；完整 progressive loading budget、supply-chain crash recovery、legacy registry cutover 和 Planner 端到端 snapshot-only 路径仍需 Closure Gate 汇总证明。

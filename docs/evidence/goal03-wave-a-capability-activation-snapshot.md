# Goal03 Wave A Capability Activation Snapshot Evidence

状态：局部实现证据，不是 Wave A completed 证明。

## 目标

本证据覆盖 PHASE14 的 Installation / Activation CAS 与 AvailabilitySnapshot eligibility 纵切：

- Capability Installation 激活和撤销必须带 `expected_generation`。
- 当前 generation 从 `capability_transition_events` 推导，stale generation fail closed。
- Activation / Revocation 更新 installation 状态并写入 transition event。
- Installation 创建前必须已有同 tenant 的 `ACTIVE` CapabilityDefinition、`ACTIVE` CapabilityVersion 和 `ACTIVE` ProviderBinding；未完成 conformance 的 binding 不能形成 ACTIVE installation 事实。
- AvailabilitySnapshot 只包含 `ACTIVE` installation 绑定的 `ACTIVE` provider binding。
- Revocation 后同一候选不再进入 snapshot hash。
- Activation / Revocation transition 与 PHASE04 统一 `infra_outbox_events` 同事务提交，topic 为 `capability.transition.committed`，供 Agent Core 或外部 worker crash 后按 ordering key 幂等恢复。

## 默认调用链

```text
CapabilityRepository.install_capability
→ active verified binding guard
→ CapabilityRepository.activate_installation
→ CapabilityRepository.append_transition_event
→ capability_transition_events CAS generation
→ capability_installations status/policy epoch update

CapabilityRepository.create_availability_snapshot
→ filter ACTIVE installation + ACTIVE binding
→ immutable capability_availability_snapshots row

CapabilityRepository.append_transition_event
→ capability_transition_events insert
→ InfrastructureRepository.enqueue_outbox(topic=capability.transition.committed)
→ pending ordered outbox event for Agent Core consumption
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

Focused rerun after transition outbox wiring:

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase14_capability_installation_activation_uses_cas_and_revocation_filters_snapshot -p no:cacheprovider
python -m pytest -q tests/api/test_goal03_capability_route.py -p no:cacheprovider
python -m compileall -q src/backend/zuno/platform/database/capability
git diff --check
```

结果：

```text
1 passed
2 passed, 1 warning
compileall passed
git diff --check passed with LF/CRLF warnings only
```

## 边界

本证据证明 PHASE14 的 durable installation active binding guard、activation CAS、revocation、transition outbox dispatch 和 snapshot eligibility 进入 PostgreSQL repository 路径。

本证据不单独证明完整 PHASE14 completed；完整 cross-worker supply-chain crash recovery、legacy compatibility facade retirement 和所有 Planner 端到端 snapshot-only 路径仍需 Closure Gate 汇总证明。

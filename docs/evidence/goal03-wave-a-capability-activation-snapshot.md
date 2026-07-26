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
- Capability transition outbox claim 会按同 tenant + ordering key 阻塞前序未 `published` 的事件；activation crash 后重新 pending 时，不允许先 claim 后续 revocation。
- Capability transition 事件已证明可以经历 claim、publish failure、retry claim、complete，并由 Agent Core consumer inbox 用 message id + payload hash 去重。
- AvailabilitySnapshot 在同一 workspace 内还会按 runtime health、quota remaining 和 capacity remaining 过滤候选；degraded / quota exhausted / capacity exhausted 不能进入 snapshot hash。

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
→ filter runtime health / quota / capacity signals
→ immutable capability_availability_snapshots row

CapabilityRepository.append_transition_event
→ capability_transition_events insert
→ InfrastructureRepository.enqueue_outbox(topic=capability.transition.committed)
→ pending ordered outbox event for Agent Core consumption
→ InfrastructureRepository.claim_outbox ordered predecessor guard
→ record_outbox_publish_failure / retry claim / complete_outbox
→ record_inbox_receipt(consumer=Agent Core) idempotent redelivery guard
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

Focused rerun after ordered transition crash recovery guard:

```powershell
python -m pytest -q tests/integration/test_goal03_wave_a_persistence.py::test_phase14_capability_installation_activation_uses_cas_and_revocation_filters_snapshot -p no:cacheprovider
python -m pytest -q tests/integration/test_phase04_postgres_foundation.py::test_outbox_claim_and_inbox_hash_conflict tests/integration/test_phase04_postgres_foundation.py::test_outbox_ordering_watermark_buffers_and_releases_contiguous_messages -p no:cacheprovider
python -m compileall -q src/backend/zuno/platform/database tests/integration/test_goal03_wave_a_persistence.py
```

结果：

```text
1 passed
2 passed
compileall passed
```

## 边界

本证据证明 PHASE14 的 durable installation active binding guard、activation CAS、revocation、transition outbox dispatch、ordered retry / Agent Core inbox 去重恢复和 snapshot eligibility 进入 PostgreSQL repository 路径。

本证据不单独证明完整 PHASE14 completed；legacy compatibility facade retirement 和所有 Planner 端到端 snapshot-only 路径仍需 Closure Gate 汇总证明。

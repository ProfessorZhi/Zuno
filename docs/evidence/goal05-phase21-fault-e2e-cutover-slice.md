# Goal05 PHASE21 Fault / Recovery Slice Evidence

status: in_progress
date: 2026-07-29
branch: codex/goal05-phase15-sandbox-repair

## Scope

本证据只记录 PHASE21 的一个真实修复切片：Capability exposure 的攻击面约束，以及 Agent recovery 的 crash matrix。它不声明 PHASE21 完成，不声明 full E2E / cutover / rollback / load / soak / removal candidate closure。

已完成：

- 新增 `src/backend/zuno/capability/conformance.py`。
- `CapabilityRouter` 在默认 `planner_exposure` 生成后，执行 fail-closed conformance 校验。
- exposure 仅允许已授权 capability 摘要进入 planner trace。
- `required_roles`、`credential_policy`、`dependency_probe` 等敏感字段不得泄漏到 planner exposure。
- task goal 中出现 prompt injection 标记时，只记录攻击痕迹，不改变授权边界。
- 新增 `Phase21CrashRecoveryMatrix`，复用现有 `ParallelRecoveryPlanner` 评估 crash / replay / late result 场景。
- crash matrix 覆盖 domain commit before checkpoint、dispatch commit before send、result before reducer、publisher restart、consumer restart、late branch result。
- late result 会被 fenced，不会直接覆盖当前 execution epoch。
- 新增 fault tests 覆盖 capability attack conformance 与 crash recovery matrix。

## Verification

```text
docker version --format '{{.Server.Version}}'
docker info --format '{{.SecurityOptions}}'
pytest -q tests/fault/capability/test_phase21_capability_attack_conformance.py tests/fault/agent/test_phase21_crash_recovery_matrix.py -p no:cacheprovider
pytest -q tests/capability/test_capability_skill_layer.py tests/agent/dag/test_phase17_dispatch_commit.py tests/agent/dag/test_phase17_parallel_recovery.py tests/agent/dag/test_phase17_readyset_admission.py -p no:cacheprovider
pytest -q tests/agent/runtime/test_runtime_restart_persistence.py tests/agent/runtime/test_runtime_interrupt_resume.py tests/agent/runtime/test_runtime_real_execution.py -p no:cacheprovider
pytest -q tests/fault/security/test_phase05_security_pre_effect_faults.py tests/fault/security/test_phase05_security_sink_fail_closed.py tests/security/test_phase05_security_eval_gate.py -p no:cacheprovider
```

## Result

```text
29.4.0
[name=seccomp,profile=builtin name=cgroupns]
5 passed
20 passed
7 passed
6 passed
```

## Boundary

本切片只证明 Capability / Agent 两条默认路径的攻击面约束和 crash 恢复语义继续可执行。PHASE21 其余 E2E、Web/Desktop、Delete/Restore、Load/Soak、Canary/Cutover 与 PHASE22 cleanup 仍待完成。

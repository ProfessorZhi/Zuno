# PHASE04 Checkpoint Boundary 与版本 Fail-closed 证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-18
status: implementation_available_for_checkpoint_boundary_version_subscope

## Result

- checkpoint_domain_fact_separation: passed
- schema_registry_domain_checkpoint_owner: passed
- infrastructure_checkpoint_receipt_not_domain_success: passed
- checkpoint_service_capability_boundary: passed
- checkpoint_version_fail_closed: passed
- unknown_checkpoint_adapter_version_rejected: passed
- unknown_checkpoint_schema_version_rejected: passed
- official_checkpointer_runtime_boundary: passed
- phase_completion: blocked_cross_domain_replay_and_approval

## Command

```powershell
python tools/scripts/verify_phase04_checkpoint_boundary_version.py
```

Result: passed.

```powershell
pytest -q tests/repo/test_phase04_checkpoint_boundary_version.py -p no:cacheprovider
```

Result: passed.

## Boundary

本证据证明 `ARCH-INFRA-021` 和 `ARCH-INFRA-023` 的当前边界子范围：`agent_runtime_checkpoints` 归 Agent Core，`infra_checkpoints` 是 Infrastructure primitive receipt；Contract Registry 明确 `Checkpoint Commit != Domain Commit`，database README 禁止把 checkpoint receipt 解释为领域成功。

本证据也证明 `CHECKPOINT` capability 的 adapter/schema version 进入 `UpgradeCompatibilityProfileV1`，unknown adapter/schema major version 默认 fail closed；official LangGraph PostgreSQL Checkpointer runtime 已由独立 evidence 证明，但 Checkpoint receipt 仍只属于 Infrastructure / Agent Core 恢复边界，不成为领域成功事实。

本证据不证明跨领域 replay final cutover 或 PHASE04 closure。

# PHASE04 Backup Scope 与服务边界证据

phase_id: PHASE04
task_id: P04-T07
date: 2026-07-18
status: implementation_available_for_backup_service_boundary_subscope

## Result

- backup_scope_profile: passed
- backup_rpo_source_coverage: passed
- backup_encryption_requirement_defined: passed
- backup_verification_command_boundary: passed
- backup_evidence_ref_existence: passed
- service_boundary_profile: passed
- postgresql_rabbitmq_object_checkpoint_boundary: passed
- checkpoint_backup_restore_boundary: passed
- product_projection_replay_boundary: passed
- phase_completion: blocked_cross_domain_replay_and_approval

## Command

```powershell
python tools/scripts/verify_phase04_backup_service_boundaries.py
```

Result: passed.

```powershell
pytest -q tests/repo/test_phase04_backup_service_boundaries.py -p no:cacheprovider
```

Result: passed.

## Boundary

本证据证明 `docs/governance/infrastructure-dr-profile.yaml` 已经为 PostgreSQL、Object Manifest/MinIO、RabbitMQ Outbox/Inbox、official Checkpointer、Product Projection Replay 和 PITR 明确定义 backup scope、RPO source、encryption requirement、verification command 和 evidence ref。

本证据也证明 `InfrastructureCapabilityProfileV1` / `DataServiceCapabilityV1` 中 PostgreSQL、RabbitMQ、Object Store 和 Checkpoint Store 的 typed boundary 已经机器可验证；其中 Checkpoint Store 明确保留 `official_adapter_not_yet_installed` unsupported semantic。

它不证明生产 encrypted backup、跨领域 replay final cutover 或 PHASE04 closure，也不关闭 PHASE04。

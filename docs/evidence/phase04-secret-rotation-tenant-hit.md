# PHASE04 Secret Rotation / Cross-Tenant Hit Evidence

## Scope

本证据只覆盖 Infrastructure 子范围：

- `ARCH-INFRA-035`：Encryption / Secret Rotation 可回滚；
- `ARCH-INFRA-058`：Cross-tenant hit quarantine / fail-closed。

它不证明生产 KMS、真实凭据材料托管、PITR、official LangGraph PostgreSQL Checkpointer、完整 Backup/Restore/Replay 或 PHASE04 closure。

## Environment

- Database：真实 PostgreSQL，本地 `zuno-postgres`；
- Migration head：`20260718_15`；
- Runtime path：`InfrastructureUnitOfWork` + PostgreSQL tables；
- Secret material policy：只持久化 `SecretRef`、version、KMS ref、config hash、payload hash、lease receipt，不持久化 plaintext secret material。

## Commands

```powershell
python tools/scripts/verify_phase04_secret_rotation_tenant_hit.py
pytest -q tests/integration/test_phase04_secret_rotation_tenant_hit.py -p no:cacheprovider
```

## Results

- secret_rotation_schema: passed
- secret_material_payload_rejected: passed
- secret_version_activation: passed
- secret_lease_uses_active_generation: passed
- cross_tenant_secret_lease_rejected: passed
- rollback_restores_previous_secret_version: passed
- stale_secret_rotation_generation_rejected: passed
- relational_cross_tenant_hit_fail_closed: passed
- object_cross_tenant_hit_quarantined: passed
- cross_tenant_hit_receipt_durable: passed
- phase_completion: blocked_official_checkpointer_and_product_projection_replay

## Boundary

`infra_secret_versions`、`infra_secret_rotation_heads` 和 `infra_secret_leases` 证明 Infrastructure 当前有可回滚的 secret version activation / rollback / lease receipt 边界，并且 lease 不携带 secret material。

`infra_cross_tenant_hits` 证明运行时 gate 在发现跨租户命中时 fail closed 或 quarantine，并把 hit 事实持久化供审计与对账使用。

该证据不能替代真实生产 KMS、PITR WAL 演练、official Checkpointer restore 或完整跨服务恢复 cutover。

# PHASE01 Program Risk Register

phase_id: PHASE01
task_id: P01-T06
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
status_boundary: "未知项必须写 blocked/needs-evidence，不通过猜测关闭。"
unassigned P0: none

| risk_id | severity | owner | source | risk | dependency / next phase | status |
| --- | --- | --- | --- | --- | --- | --- |
| P01-R001 | P0 | Infrastructure | `current-persistence-inventory.md` | PostgreSQL is Target but real PostgreSQL domain UoW, lock/isolation, migration upgrade/downgrade and crash recovery evidence are missing. | PHASE04 | needs-evidence |
| P01-R002 | P0 | Infrastructure | `current-persistence-inventory.md` | RabbitMQ and Outbox/Inbox are Target; current evidence is local queue/fake worker chain. | PHASE04 | needs-evidence |
| P01-R003 | P0 | Infrastructure / Knowledge | `current-persistence-inventory.md` | MinIO/S3, external vector/graph/search and backup/restore are declared but not proven Current. | PHASE04, PHASE11, PHASE12 | needs-evidence |
| P01-R004 | P0 | Repository Governance | `legacy-bypass-inventory.yaml` | `legacy_aliases.py` and production `legacy` path remain active; final canonical tree cannot close until removed. | PHASE02, P22-T03 | assigned |
| P01-R005 | P0 | Model Gateway | `legacy-bypass-inventory.yaml` | Direct OpenAI/Anthropic/DashScope/provider calls still bypass Model Gateway. | PHASE07 | assigned |
| P01-R006 | P0 | Tool Runtime / Security | `legacy-bypass-inventory.yaml` | Direct MCP, httpx and subprocess tool paths exist outside canonical Tool Runtime/Security gate. | PHASE05, PHASE15, PHASE16 | assigned |
| P01-R007 | P0 | Product Surface | `current-runtime-inventory.md` | API services still orchestrate workspace runtime and tool approval directly instead of thin Product Command/Query ports. | PHASE09 | assigned |
| P01-R008 | P0 | Frontend / Product Surface | `frontend-current-inventory.md` | Web/Desktop lack real browser/desktop E2E for SSE resume, reauthorization, cursor expiry, multi approval and UNKNOWN UI. | PHASE10, PHASE21 | needs-evidence |
| P01-R009 | P1 | Observability & Eval | `docs/status/production-readiness.md` | Fixed benchmark and comparable measured runs remain blocked; quality cannot be proven. | PHASE20, PHASE22 | needs-evidence |
| P01-R010 | P1 | Memory & Context | `requirement-ledger.yaml` | Memory module Target requirements exist, but Memory context governance is not Current until code/tests/evidence map them. | PHASE13 | assigned |
| P01-R011 | P1 | Security | `docs/governance/wave1-cross-module-contract-registry.md` | Wave 1 contracts are CONFIRMED_TARGET, not Runtime Current; security epoch/audit/secret lease must be implemented before side effects. | PHASE03, PHASE05 | assigned |
| P01-R012 | P1 | Release / Operations | `current-persistence-inventory.md` | Backup/restore/PITR and cross-service recovery set validation are not implemented evidence. | PHASE04, PHASE21 | needs-evidence |

## Parallelism Boundaries

- PHASE02 may parallelize compatibility matrix, feature flag registry, allowlist inventory and rollback playbook only when they do not edit the same registry or removal gate.
- PHASE03 may split contracts by owner, but canonical serialization, hash, version compatibility and shared bundle export are serial closure items.
- PHASE04 must serialize Alembic revision chain, PostgreSQL domain schema, UoW, Outbox/Inbox, Idempotency, Lease/Fencing and Checkpointer boundaries unless a unique owner is assigned.

## Stop Conditions Carried Forward

- Real PostgreSQL integration environment missing blocks PHASE04 completion.
- Any need to change shared Contract field semantics, module ownership or fixed Agent Core principles must stop affected tasks.
- Any test that can only pass with fake Evidence, Receipt, Citation or success status must be blocked.

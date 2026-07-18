# PHASE04 Adapter Conformance Profile Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_ids:
  - ARCH-INFRA-061
  - ARCH-INFRA-062
status: implementation_available
date: 2026-07-18

## Boundary

This evidence proves that PHASE04 infrastructure adapters use a shared, typed conformance profile for `DEVELOPER_CI` and `SERVER_PRODUCT` deployment classes. Profiles are derived from the Infrastructure Capability Profile, so service kinds and supported or unsupported semantics have one typed source.

It does not prove that every future enterprise adapter is implemented. Official LangGraph PostgreSQL Checkpointer, PITR, complete projection replay and full PHASE04 recovery remain blocked or target_not_current.

## Verification Results

- adapter_conformance_profile_contract: passed
- developer_ci_server_product_same_suite: passed
- service_kind_coverage_parity: passed
- supported_semantics_shared: passed
- unsupported_semantics_shared: passed
- unsupported_local_semantic_fail_fast: passed
- required_test_refs_exist: passed
- evidence_refs_exist: passed
- conformance_suite_version_hash_changes: passed
- invalid_content_hash_rejected: passed

## Commands

```powershell
python tools/scripts/verify_phase04_adapter_conformance_profiles.py
```

Expected result:

```text
PHASE04 adapter conformance profile verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_adapter_conformance_profiles.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `AdapterConformanceProfileV1` records adapter name, service kind, deployment class, supported semantics, unsupported semantics, fail-fast policy, conformance suite version, required tests, evidence ref and canonical content hash.
- Developer CI and Server Product profiles use the same conformance suite version.
- Unsupported local semantics fail fast instead of silently degrading to local-only behavior.
- Profile hash changes when the conformance suite version changes.

## Remaining Target

- Future enterprise-only adapters must pass this same profile before being promoted.
- Official LangGraph PostgreSQL Checkpointer remains blocked by the dependency Stop Condition.
- Complete PHASE04 Backup/Restore/PITR/Product Projection Replay and combined-service fault evidence remain incomplete.

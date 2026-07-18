# PHASE04 Upgrade Compatibility Profile Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_id: ARCH-INFRA-060
status: implementation_available
date: 2026-07-17

## Boundary

This evidence proves that PHASE04 infrastructure typed services expose an explicit upgrade compatibility profile. It is derived from `InfrastructureCapabilityProfileV1` / `DataServiceCapabilityV1`, so service kinds, adapter versions and schema or contract versions have a single typed source.

It does not prove live rolling upgrade, official Checkpointer integration, or full recovery replay. Official LangGraph PostgreSQL Checkpointer, PITR and complete projection replay remain PHASE04 blockers.

## Verification Results

- upgrade_compatibility_profile_contract: passed
- every_typed_service_has_upgrade_profile: passed
- adapter_and_schema_versions_explicit: passed
- read_write_rollback_windows_explicit: passed
- unknown_version_fail_closed: passed
- profile_version_hash_changes: passed
- invalid_profile_hash_rejected: passed
- evidence_refs_exist: passed

## Commands

```powershell
python tools/scripts/verify_phase04_upgrade_compatibility_profiles.py
```

Expected result:

```text
PHASE04 upgrade compatibility profile verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_upgrade_compatibility_profiles.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `UpgradeCompatibilityProfileV1` records current adapter version, current schema or contract version, explicit read/write/rollback compatible versions, unsupported versions, fail-closed unknown-version actions, evidence ref, runtime status and canonical content hash.
- `tools/scripts/verify_phase04_upgrade_compatibility_profiles.py` derives profiles for every service kind declared by the Infrastructure Capability Profile.
- Unknown adapter or schema versions are not accepted as compatible unless they are present in the explicit compatibility window.
- Compatibility profile hash changes when a version field changes.

## Remaining Target

- Runtime rolling upgrade and downgrade drills for every deployed adapter are not proven by this evidence.
- Official LangGraph PostgreSQL Checkpointer remains blocked by the dependency Stop Condition.
- Complete PHASE04 Backup/Restore/PITR/Product Projection Replay and combined-service fault evidence remain incomplete.

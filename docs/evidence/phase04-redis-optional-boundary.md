# PHASE04 Redis Optional Boundary Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_id: ARCH-INFRA-045
status: implementation_available
date: 2026-07-18

## Boundary

This evidence proves the PHASE04 Redis boundary: Redis is represented only as an optional `CACHE` acceleration service in the Infrastructure Capability Profile. It is non-authoritative, rebuildable from source, and excluded from the PHASE04 required real-service set and release provenance adapter bundle.

It does not prove Redis high availability, Redis failover, Redis rate-limit acceleration, or enterprise Redis deployment. Those remain future optional or later-phase targets.

## Verification Results

- redis_cache_capability_present: passed
- redis_cache_non_authoritative: passed
- redis_cache_rebuildable: passed
- redis_cache_optional_acceleration_only: passed
- redis_not_required_real_service: passed
- redis_not_required_release_adapter: passed
- redis_backup_restore_class_rebuild_from_source: passed

## Commands

```powershell
python tools/scripts/verify_phase04_redis_optional_boundary.py
```

Expected result:

```text
PHASE04 Redis optional boundary verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_redis_optional_boundary.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `DataServiceCapabilityV1` cache entry uses `service_kind="CACHE"` and `adapter_name="redis-optional-cache"`.
- Redis cache is `authoritative=false`, `rebuildable=true`, `consistency_model="rebuildable"` and `backup_restore_class="rebuild-from-source"`.
- Redis is not listed in `verify_phase04_complete_infrastructure.py` required real services.
- Redis is not listed in the PHASE04 release provenance required infrastructure services or adapter versions.

## Remaining Target

- Redis HA, failover, rate limiting, TLS/mTLS and enterprise cache deployment are not proven by this evidence.
- Redis must not become a unique source of final domain state in later phases.
- Official LangGraph PostgreSQL Checkpointer and full PHASE04 recovery evidence remain blockers.

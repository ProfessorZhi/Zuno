# PHASE04 Release Provenance Manifest Evidence

phase_id: PHASE04
task_id: P04-T07
requirement_id: ARCH-INFRA-063
status: implementation_available
date: 2026-07-18

## Boundary

This evidence proves that PHASE04 infrastructure release provenance is machine-verifiable for the local real PostgreSQL, RabbitMQ and MinIO services. The manifest binds source commit, running infrastructure image ids, Compose network and port refs, configuration hash, Alembic migration versions, adapter versions, data-service compatibility evidence and provenance evidence refs.

It does not prove a production application image release, signed supply-chain release, official LangGraph PostgreSQL Checkpointer integration, PITR, or full PHASE04 recovery replay.

## Verification Results

- release_manifest_contract: passed
- source_commit_bound: passed
- running_image_digest_bound: passed
- compose_network_refs_bound: passed
- config_versions_bound: passed
- migration_versions_bound: passed
- adapter_versions_bound: passed
- compatibility_evidence_bound: passed
- provenance_refs_exist: passed
- signature_ref_hash_bound: passed
- rollback_ref_self_rejected: passed
- manifest_hash_changes_on_commit_change: passed

## Commands

```powershell
python tools/scripts/verify_phase04_release_provenance_manifest.py
```

Expected result:

```text
PHASE04 release provenance manifest verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_release_provenance_manifest.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `ReleaseManifestV1` binds source commit, infrastructure image digest bundle, SBOM/config ref, signature hash, config versions, migration versions, adapter versions, data-service compatibility ref, rollback ref, network refs and provenance refs.
- `tools/scripts/verify_phase04_release_provenance_manifest.py` checks the three real local services are running healthy and match Compose network, port and image declarations.
- The manifest content hash changes when the source commit changes.
- A release manifest cannot use itself as the rollback release.

## Remaining Target

- Full production application image digest, external SBOM generation and supply-chain signing remain outside this PHASE04 infrastructure provenance subset.
- Official LangGraph PostgreSQL Checkpointer remains blocked by the dependency Stop Condition.
- Complete PHASE04 Backup/Restore/PITR/Product Projection Replay and combined-service fault evidence remain incomplete.

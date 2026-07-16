# PHASE04 MinIO Object Store Evidence

phase_id: PHASE04
task_id: P04-T06
date: 2026-07-16
status: partial_implementation_available
object_staging: passed
hash_mismatch_fail_closed: passed
commit_visibility: passed
delete: passed
restore: passed
storage_restart: passed
retention: not_yet_proven
legal_hold: not_yet_proven
lifecycle: not_yet_proven

## Boundary

This evidence proves a real MinIO object store subset only. It does not close P04-T06 and does not close PHASE04.

Object Commit != Domain Success. Object visibility is a physical receipt; Product, Input, Knowledge, Agent Core or Tool domain success remains owned by the relevant domain transaction and final gate.

## Environment

| Item | Value |
| --- | --- |
| Docker service | `zuno-minio` |
| Image | `minio/minio:RELEASE.2023-03-20T20-16-18Z` |
| Endpoint | `localhost:9000` |
| Verification command | `python tools/scripts/verify_phase04_minio_object_store.py` |
| Storage restart verification | `python tools/scripts/verify_phase04_minio_storage_restart.py` |
| Integration test | `pytest -q tests/integration/test_phase04_minio_object_store.py -p no:cacheprovider` |

## Verified Behavior

- Creates an isolated real MinIO bucket for each run.
- Stages object content under `_staging/<sha256>/...` with SHA-256 metadata.
- Fails closed when commit receives an expected hash that does not match staged bytes.
- Commits by copying staged content to the visible object key and deleting the staged object.
- Reads the committed object and verifies the exact bytes.
- Creates an explicit restore point copy before deletion.
- Deletes the visible object and verifies it is no longer readable.
- Restores the object from the restore point and verifies content hash and bytes.
- Restarts the real `zuno-minio` container and verifies both committed object bytes and restore point bytes remain readable with unchanged hash receipts.
- Removes temporary objects and bucket after the run.

## Commands And Results

```text
python tools/scripts/verify_phase04_minio_object_store.py
PHASE04 MinIO object store verification passed.
```

```text
python tools/scripts/verify_phase04_minio_storage_restart.py
PHASE04 MinIO storage restart verification passed.
```

```text
pytest -q tests/integration/test_phase04_minio_object_store.py -p no:cacheprovider
1 passed
```

## Remaining Gap

- Retention, legal hold, authorization hooks and lifecycle are not yet proven.
- Multipart/partial upload, visibility lag, lost response and reconciliation are not yet proven.
- Object Manifest is not yet integrated with PostgreSQL domain transaction and backup/restore recovery set.
- P04-T06 remains `ready`, not completed.

# PHASE04 MinIO Object Store Evidence

phase_id: PHASE04
task_id: P04-T06
date: 2026-07-17
status: partial_implementation_available
object_staging: passed
hash_mismatch_fail_closed: passed
commit_visibility: passed
visibility_lag: passed
duplicate_upload: passed
multipart_upload: passed
partial_upload_abort: passed
lost_response_reconciliation: passed
duplicate_complete_reconciliation: passed
orphan_reconciliation: passed
delete: passed
missing_object: passed
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
- Re-staging the same object content converges on the same deterministic staged object name and hash receipt.
- 在真实 MinIO 中完成两段 S3 multipart upload，第一段为 5 MiB，并校验最终 bytes 与 SHA-256 receipt。
- 单段未完成上传保持不可读；持久 upload-session 候选仍 active 时不清理，失活后通过精确 key 对账并 abort orphan upload。
- 模拟 MinIO 已完成 multipart upload、但 transport 响应丢失；Adapter 通过对象 size 与 SHA-256 恢复 staged receipt，不盲目重传。
- 服务端已完成后重复 complete，仍收敛到同一个 staged receipt。
- 持久 upload-session registry 提供对账候选；MinIO 只证明物理 upload/object 状态，不拥有 session liveness。
- Keeps the future visible object key unreadable until commit succeeds.
- Fails closed when reading a missing object.
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
2 passed
```

## Remaining Gap

- Retention, legal hold, authorization hooks and lifecycle are not yet proven.
- Object Manifest is not yet integrated with PostgreSQL domain transaction and backup/restore recovery set.
- P04-T06 remains `ready`, not completed.

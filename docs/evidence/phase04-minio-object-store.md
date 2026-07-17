# PHASE04 MinIO Object Store Evidence

phase_id: PHASE04
task_id: P04-T06
date: 2026-07-17
status: minio_subscope_implementation_available
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
authorization_hook: passed_fail_closed
permission_deny: passed
retention: passed_governance
legal_hold: passed
lifecycle: passed_staging_expiration
postgres_manifest_receipt_adoption: passed
raw_content_sha256_reconciliation: passed
domain_manifest_atomicity: passed
post_physical_commit_crash_recovery: passed
committed_read_gate: passed
object_hash_quarantine: passed
logical_delete_before_physical_purge: passed
minio_subscope_completion: proven
p04_t06_completion: blocked_official_checkpointer

## 边界

本证据完整证明 P04-T06 的真实 MinIO/S3-compatible Object Store 子范围达到 `implementation available`。P04-T06 仍不能关闭，因为官方 LangGraph PostgreSQL Checkpointer 是同一 Work Package 的另一项强制子范围，当前受关键依赖 Stop Condition 阻塞；PHASE04 因此仍未关闭。

Object Commit != Domain Success。Object Commit 不等于 Domain Success。Object visibility 只是物理 receipt；Product、Input、Knowledge、Agent Core 或 Tool 的领域成功仍由对应领域事务与 Final Gate 持有。

## Environment

| Item | Value |
| --- | --- |
| Docker service | `zuno-minio` |
| Image | `minio/minio:RELEASE.2023-03-20T20-16-18Z` |
| Endpoint | `localhost:9000` |
| Verification command | `python tools/scripts/verify_phase04_minio_object_store.py` |
| Storage restart verification | `python tools/scripts/verify_phase04_minio_storage_restart.py` |
| Integration test | `pytest -q tests/integration/test_phase04_minio_object_store.py -p no:cacheprovider` |
| Manifest adoption command | `python tools/scripts/verify_phase04_minio_manifest_adoption.py` |
| Durable adapter SHA-256 | `6e4009b4d29ac4d6decc02adac0b2f60a3c9e3584b1f2740ce54a26eecfb0b71` |
| PostgreSQL repository SHA-256 | `453040efb5d690aa338df4c6bcdc72545eafe63bc7e3a334e33e81dd5b3df8e5` |
| Manifest verifier SHA-256 | `b73a6591f4a4da6f247a04b93f619ff8a15dc995efccb4a5690bcef81899a7aa` |
| Compose SHA-256 | `fb53082b499ec5363591562d8a67d663c4430e13bd26903a136f4677df9e1d23` |

## Verified Behavior

- Creates an isolated real MinIO bucket for each run.
- Stages object content under `_staging/<sha256>/...` with SHA-256 metadata.
- Re-staging the same object content converges on the same deterministic staged object name and hash receipt.
- 在真实 MinIO 中完成两段 S3 multipart upload，第一段为 5 MiB，并校验最终 bytes 与 SHA-256 receipt。
- 单段未完成上传保持不可读；持久 upload-session 候选仍 active 时不清理，失活后通过精确 key 对账并 abort orphan upload。
- 模拟 MinIO 已完成 multipart upload、但 transport 响应丢失；Adapter 通过对象 size 与 SHA-256 恢复 staged receipt，不盲目重传。
- 服务端已完成后重复 complete，仍收敛到同一个 staged receipt。
- 持久 upload-session registry 提供对账候选；MinIO 只证明物理 upload/object 状态，不拥有 session liveness。
- 在 Object Lock bucket 中保存 committed version id，并为精确 version 写入 `GOVERNANCE` retention 与 legal hold。
- legal hold 启用时 exact-version purge 被真实 MinIO 拒绝；解除 legal hold 后，未到期 retention 仍继续拒绝 purge。
- `_staging/` lifecycle expiration rule 写入真实 MinIO 并读回相同 prefix 与 7 天期限；旧 MinIO 不支持的 incomplete-upload lifecycle action 不被伪造，partial upload 继续由显式 reconciler 清理。
- authorization hook 在发起 S3 I/O 前拒绝 `object:read`，hook 异常或非 `True` 结果均 fail closed。
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
- `SessionObjectManifest` 把 MinIO receipt 的原始 bytes SHA-256、size、owner 和 visibility 与真实 Input `knowledge_file` 领域行写入同一个 Domain UoW；commit 前 crash 时两者共同回滚。
- MinIO 已提交可见对象、但 PostgreSQL 更新前 crash 时，Manifest 保持 `staged`，`read_committed` 继续拒绝读取；reconciler 重新读取真实 bytes 并按 SHA-256/size 收敛到 `visible`。
- 领域 `success` 与 `visible` Manifest 的最终事务在 commit 前 crash 时共同回滚；物理 Object receipt 不会自动推进领域成功。
- 同 object ref 跨 owner/hash/size 边界时持久进入 `quarantined`；篡改真实 MinIO bytes 后 committed read fail closed，且 quarantine 不因普通重试自动解除。
- 删除流程先把 PostgreSQL Manifest 改为 `deleted`、撤销逻辑可见性，再执行 MinIO 物理删除；恢复后 Manifest 为 `restored` 并重新校验 bytes/hash。

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
3 passed
```

```text
python tools/scripts/verify_phase04_minio_manifest_adoption.py
PHASE04 MinIO manifest adoption verification passed.
```

```text
pytest -q tests/integration/test_phase04_postgres_foundation.py tests/integration/test_phase04_minio_object_store.py tests/integration/test_phase04_minio_manifest_adoption.py -p no:cacheprovider
14 passed in 6.70s
```

## Remaining Gap

- Security Policy 决策仍归 PHASE05 Security Owner；本证据只证明 Infrastructure authorization hook 的 fail-closed 执行边界。
- 官方 LangGraph PostgreSQL Checkpointer 依赖尚未批准并接入；P04-T06 保持 `blocked`，不以自定义 `infra_checkpoints` primitive 冒充完成。

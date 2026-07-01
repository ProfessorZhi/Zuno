# PHASE03 ObjectStore Abstraction 与 Binary Input

status: pending
program: zuno-enterprise-ingestion-async-infrastructure-v1
phase: PHASE03_object-store-abstraction-and-binary-input
mode: tdd-implementation

## 目标

把 `LocalObjectStore.save_text()` 升级为 `ObjectStore` abstraction，支持 text 和 bytes，能保存 source raw file、Document IR artifact、parse diagnostics artifact、workspace artifact content，并提供 sha256 verification。Object Store 是大对象和原始证据落点，Postgres / SQLite 只保存 metadata 和状态事实。

## 范围

- 定义 `ObjectStore` protocol：`save_bytes`、`save_text`、`read_bytes`、`read_text`、`open_stream`、`get_metadata`、`verify_sha256`。
- `LocalObjectStore` 支持 binary safe path、content hash、metadata、missing object error。
- 为 MinIO / S3 adapter boundary 预留 dependency probe / target-blocked evidence。
- `/workspace/file` 继续兼容现有 text upload，同时内部可保存 bytes。

## 禁止范围

- 不要求真实 MinIO / S3 服务。
- 不引入 multipart upload 或分片大文件实现，除非 tests 明确需要。
- 不把对象内容塞回 DB 大字段作为事实源。
- 不改变现有 text fixture 的读取兼容性。

## 验收闸门

- `LocalObjectStore.save_bytes()` 和 `read_bytes()` round-trip 通过。
- `save_text()` 基于 bytes 实现，sha256 与真实 bytes 一致。
- `verify_sha256()` 能发现 object tamper / missing。
- Workspace file register 保持现有 API 兼容，并能返回 durable object metadata。
- MinIO / S3 boundary 无配置时稳定 target-blocked。

## 验证命令

```powershell
pytest -q tests/knowledge/test_enterprise_ingestion_storage_contract.py -p no:cacheprovider
pytest -q tests/api/test_workspace_durable_ingest_runtime.py -p no:cacheprovider
git diff --check
```

## 需要先读取

- `src/backend/zuno/knowledge/storage/local_object_store.py`
- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 需要修改的文件

- `src/backend/zuno/knowledge/storage/local_object_store.py`
- `src/backend/zuno/knowledge/storage/contracts.py`
- `src/backend/zuno/knowledge/storage/__init__.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `tests/knowledge/test_enterprise_ingestion_storage_contract.py`
- `tests/api/test_workspace_durable_ingest_runtime.py`

## 执行拆解

1. 写 failing test：binary object round-trip。
2. 写 failing test：sha256 verification catches tamper。
3. 实现 `ObjectStore` protocol 和 LocalObjectStore bytes API。
4. 将 `save_text()` 改为复用 `save_bytes()`。
5. 保持 workspace durable ingest tests green。
6. 记录 PHASE03 evidence。

## 多 agent 分工

- Storage Agent：审 object key、hash 和 metadata。
- API Agent：审 `/workspace/file` additive compatibility。
- Verification Agent：跑 object store / durable ingest tests。

## 需要返回的证据

- binary fixture path、sha256、metadata。
- tamper / missing object failure message。
- API response shape 差异。

## 停止条件

- 需要真实 MinIO / S3 才能完成本 phase。
- Binary API 会破坏现有 text source object 路径。
- 对象路径可能逃逸 workspace/object root。

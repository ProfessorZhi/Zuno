# Input Runtime Batch Evidence

status: implementation_available

本证据覆盖 `ARCH-ING-001` 到 `ARCH-ING-080`。范围是 Input / Document Ingestion 模块的 runtime batch 边界：原始 SourceObject 不可变保存、对象提交校验、ParseJob 生命周期、ParserWorker 成功与 blocked 路径、SourceSpan provenance、handoff envelope、queue/outbox/reconciler 边界、缓存/格式/删除/容量/安全/Trace/API 证据门。

## Current Boundary

- 代码：`src/backend/zuno/knowledge/ingestion/runtime_batch.py`
- 既有 ingestion contract：`src/backend/zuno/knowledge/ingestion/contracts.py`
- 既有 async runtime：`src/backend/zuno/knowledge/ingestion/async_runtime.py`
- 既有 storage contract：`src/backend/zuno/knowledge/storage/contracts.py`
- 测试：`tests/knowledge/test_input_runtime_batch.py`
- 验证器：`tools/scripts/verify_input_runtime_batch.py`

## Verified Behavior

- LocalObjectStore 保存原始文本和 blocked 图像对象，并验证 SHA-256、size、mime type。
- SQLiteDurableIngestionStore 保存 SourceObject、WorkspaceFile、ParseJobSnapshot 和解析 provenance。
- ParserWorker 覆盖 text/markdown succeeded path 与 image/png blocked path。
- blocked path 不发布 `index_requested` handoff。
- IngestionReconciler、LocalQueueBackend outbox、RabbitMQ target-blocked probe 和 Redis fallback boundary 均被验证。
- ParseAttemptControl 验证 lease/fencing/late result 语义。
- Transform、quality gate、format preservation、delete receipts、legal hold、capacity reservation、parser security profile、handoff payload hash 和 schema hash 均被 verifier 固定。

## Commands

在 `integration/phase01-full` 分支运行：

```powershell
python -m py_compile src/backend/zuno/knowledge/ingestion/runtime_batch.py tools/scripts/verify_input_runtime_batch.py
pytest -q tests/knowledge/test_input_runtime_batch.py -p no:cacheprovider
python tools/scripts/verify_input_runtime_batch.py
```

结果：

```text
5 passed
Input runtime batch verification passed: 80 requirements, source_verified=True, parse=succeeded, blocked=blocked.
```

## Limit

这只代表 Input / Document Ingestion runtime batch 需求达到 `implementation_available`。它不代表 PHASE11、PHASE04 或整个 Program 已关闭，也不把本地 SQLite / LocalQueue / LocalObjectStore 冒充为生产级分布式依赖。

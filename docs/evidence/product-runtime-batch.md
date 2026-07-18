# Product Runtime Batch Evidence

## Scope

本证据覆盖 `ARCH-PRODUCT-001` 到 `ARCH-PRODUCT-080`。本批证明 Product Surface 北向产品边界达到 `implementation_available`：统一 Web/Desktop/External API Contract、Product 不成为第二 Controller、Command Journal、CommandReceipt、幂等冲突、Projection/AuthorizedView/SSE/Cursor、Interrupt/Signal/Approval/UNKNOWN Effect、RunOutcome、Upload/Parse/Index/Searchable、Artifact/Publication/Delivery/Render/Read、全链路授权、ActionToken、Sanitization、Sandbox、Desktop typed IPC、External API replay protection、Delete/Correction/Retention、SLO 和 Target-to-Current evidence gate 均可机器验证。它不代表 PHASE05 或全 Program 关闭。

## Implemented Runtime Surface

- `src/backend/zuno/product/runtime_batch.py`
- `src/backend/zuno/api/dto/workspace.py`
- `src/backend/zuno/api/services/workspace_task_runtime.py`
- `apps/web/src/apis/workspace.ts`
- `tools/scripts/verify_product_runtime_batch.py`
- `tests/api/test_product_runtime_batch.py`

## Reproducible Commands

```powershell
python -m py_compile src/backend/zuno/product/runtime_batch.py tools/scripts/verify_product_runtime_batch.py
pytest -q tests/api/test_product_runtime_batch.py -p no:cacheprovider
python tools/scripts/verify_product_runtime_batch.py
```

## Results

- `python -m py_compile ...` passed.
- `pytest -q tests/api/test_product_runtime_batch.py -p no:cacheprovider` passed: `5 passed`.
- `python tools/scripts/verify_product_runtime_batch.py` passed: `80 requirements`, `3 receipts`, `4 stream events`, `7 run outcomes`.

## Current Boundary

`validate_product_runtime_batch_from_repo()` reads the frontend workspace API and validates the Product Surface fixture against backend DTO and shared envelope contracts. Negative tests prove CommandReceipt cannot claim domain success, heartbeat cannot imply success, expired ActionToken fails closed and frontend forbidden secret fields are rejected.

# Platform Vendor 边界

PHASE02 status: target-owner-reserved

## 当前角色

`platform/vendor/` 是第三方 shim 的目标 owner。PHASE02 只建立 README 和 import guard，不搬迁当前 `fastapi_jwt_auth` 兼容实现。

当前事实是：`fastapi_jwt_auth` 仍通过 `zuno.compatibility.vendor.fastapi_jwt_auth` 保护旧 import path，物理位置仍在 `platform/compatibility/vendor/fastapi_jwt_auth`。

## Target role

目标状态下，第三方 shim 放在 `platform/vendor/`，legacy import registry 放在 `platform/compatibility/`。迁移必须先保持 `zuno.compatibility.vendor.fastapi_jwt_auth` 兼容路径，再把实际实现移动到本目录。

## 允许新增内容

- README、import guard 和 vendor 迁移说明。
- 未来通过兼容 re-export 保护旧路径后的第三方 shim。

## 禁止事项

- 禁止在 PHASE02 直接移动 `fastapi_jwt_auth` 实现。
- 禁止把 legacy alias registry 写入 `platform/vendor/`。
- 禁止把新的 vendor shim 写入 compatibility。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `pytest -q tests/api/test_fastapi_jwt_auth_compat.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`

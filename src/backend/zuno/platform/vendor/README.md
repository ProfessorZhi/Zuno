# Platform Vendor 边界

PHASE22 status: canonical-owner-active (P22-T03 Wave 1)

## 当前角色

`platform/vendor/` 是第三方 shim 的 canonical owner。`fastapi_jwt_auth` 已从 `platform/compatibility/vendor/fastapi_jwt_auth` 物理迁移到 `platform/vendor/fastapi_jwt_auth`，canonical import path 为 `zuno.platform.vendor.fastapi_jwt_auth`。

## Target role

第三方 shim 只允许放在本目录；legacy import registry 由 `platform/compatibility/` 持有（PHASE22 Wave 1 删除兼容目录后该目录不再存在）。

## 允许新增内容

- 第三方 shim 实现、README、import guard 与迁移说明。
- 通过 canonical import path 暴露的 public surface。

## 禁止事项

- 禁止把 legacy alias registry 写入 `platform/vendor/`。
- 禁止恢复 `platform/compatibility/vendor/fastapi_jwt_auth/` 或 `src/backend/fastapi_jwt_auth/` 顶层 public shell。
- 禁止在 shim 包内写业务逻辑。

## Focused tests

- `python tools/scripts/verify_repo_structure.py`
- `python tools/scripts/verify_phase22_cleanup_boundary.py`
- `pytest -q tests/api/test_fastapi_jwt_auth_compat.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider`

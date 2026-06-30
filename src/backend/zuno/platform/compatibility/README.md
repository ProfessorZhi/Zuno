# Zuno Compatibility

## 当前角色

分类：`compatibility-shell`

`compatibility/` 收纳迁移兼容边界：历史 alias、当前已存在的 vendor 兼容路径、退休 public import 的替代入口。它存在是为了减少顶层目录噪音，同时保留可测试的迁移路径。

PHASE02 之后，本目录的目标收缩为 legacy import registry only。当前允许范围只有 `legacy_aliases.py`、`legacy/` 和已经被 tests 保护的 `vendor/fastapi_jwt_auth` 兼容路径。

## Target role

目标是让 `src/backend/zuno` 顶层不再暴露 `legacy/`、`vendor/` 以及只剩历史 import 语义的目录或 `.py` alias 文件。旧 public import path 由 `legacy_aliases.py` 注册，不再占用包根目录。

第三方 shim 的目标 owner 是 `platform/vendor`。`fastapi_jwt_auth` 仍在 `platform/compatibility/vendor/fastapi_jwt_auth`，只是因为当前旧 import path 还由 `tests/api/test_fastapi_jwt_auth_compat.py` 保护；物理迁移必须先提供兼容 re-export 证据。

## 禁止事项

- 禁止把新的业务逻辑写进 compatibility。
- 禁止把 compatibility 写成目标架构主路径。
- 禁止把新的 vendor shim 写入 compatibility。
- 禁止恢复 `src/backend/fastapi_jwt_auth/` 顶层 public shell。

## Focused tests

- `pytest -q tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`

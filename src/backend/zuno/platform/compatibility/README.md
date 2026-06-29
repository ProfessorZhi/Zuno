# Zuno Compatibility

## 当前角色

分类：`compatibility-shell`

`compatibility/` 收纳迁移兼容边界：历史 alias、vendored dependency、退休 public import 的替代入口。它存在是为了减少顶层目录噪音，同时保留可测试的迁移路径。

## Target role

目标是让 `src/backend/zuno` 顶层不再暴露 `legacy/`、`vendor/` 以及只剩历史 import 语义的目录或 `.py` alias 文件。目录型兼容材料统一进入 `compatibility/legacy/` 或 `compatibility/vendor/`；旧 public import path 由 `legacy_aliases.py` 注册，不再占用包根目录。

## 禁止事项

- 禁止把新的业务逻辑写进 compatibility。
- 禁止把 compatibility 写成目标架构主路径。
- 禁止恢复 `src/backend/fastapi_jwt_auth/` 顶层 public shell。

## Focused tests

- `pytest -q tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider`
- `python tools/scripts/verify_repo_structure.py`

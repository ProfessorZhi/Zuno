# PHASE07：FastAPI JWT Compat Retirement Plan

> 状态：first slice complete。`src/backend/fastapi_jwt_auth/` 顶层 compatibility shell 已退休。

## 背景

`src/backend/fastapi_jwt_auth/` 曾经是旧 public import 的 compatibility shell。它让代码可以继续使用：

```python
from fastapi_jwt_auth import AuthJWT
```

但这会让 `src/backend` 顶层同时出现 `zuno/` 和 `fastapi_jwt_auth/`，第一次打开目录时不够清楚。

## 当前落地

当前 runtime 已改为直接使用内部兼容边界：

```python
from zuno.compatibility.vendor.fastapi_jwt_auth import AuthJWT
from zuno.compatibility.vendor.fastapi_jwt_auth.exceptions import AuthJWTException
```

vendored package 现在位于：

```text
src/backend/zuno/compatibility/vendor/fastapi_jwt_auth/
```

`src/backend/fastapi_jwt_auth/` 已删除，并由 `tests/api/test_fastapi_jwt_auth_compat.py` 固定为 retirement guard。

## 迁移内容

- `src/backend/zuno/main.py`、user API 和 autobuild websocket 已改用 `zuno.compatibility.vendor.fastapi_jwt_auth`。
- vendored package 内部 import 已改为相对 import，不再依赖 public `fastapi_jwt_auth.*` 包名。
- `tests/api/test_fastapi_jwt_auth_compat.py` 从“public shell 存在”改为“public shell 不存在，runtime vendored import 可用”。
- `tools/scripts/verify_repo_structure.py` 和 repo tests 禁止 `src/backend/fastapi_jwt_auth/` 回潮。

## 禁止

- 禁止恢复 `src/backend/fastapi_jwt_auth/` 顶层目录。
- 禁止恢复 runtime 中的 `from fastapi_jwt_auth ...` import。
- 禁止把 vendored dependency 写成目标业务层；它只能存在于 `compatibility/vendor/`。

## 验证

```powershell
git diff --check
pytest -q tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```

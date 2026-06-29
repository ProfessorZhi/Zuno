# PHASE07：FastAPI JWT Compat Retirement Plan

> 状态：in progress。目标是处理 `src/backend/fastapi_jwt_auth/` 为什么挡在 `src/backend` 顶层，以及如何安全退休或降噪。

## 背景

`src/backend/fastapi_jwt_auth/` 当前是 tracked compatibility shell。它把旧 public import：

```python
from fastapi_jwt_auth import AuthJWT
```

转接到：

```text
src/backend/zuno/vendor/fastapi_jwt_auth/
```

因此它不是本地产物，不能直接删除。

当前落地状态：

- `src/backend/fastapi_jwt_auth/` 已收敛为单文件 compatibility shell，只保留 `__init__.py`。
- `__init__.py` 显式把 `fastapi_jwt_auth.config`、`fastapi_jwt_auth.exceptions`、`fastapi_jwt_auth.auth_config`、`fastapi_jwt_auth.auth_jwt` alias 到 `zuno.vendor.fastapi_jwt_auth.*`。
- 这样既减少顶层视觉噪音，又避免同一 vendored 源码在 public name 和 `zuno.vendor` name 下重复加载导致 class identity 漂移。

## 当前引用证据

当前 `rg fastapi_jwt_auth` 显示它仍被这些 runtime / compat 路径使用：

| path | usage |
| --- | --- |
| `src/backend/zuno/main.py` | imports `AuthJWT` and `AuthJWTException`。 |
| `src/backend/zuno/api/services/user.py` | imports `AuthJWT`。 |
| `src/backend/zuno/api/v1/user.py` | imports `AuthJWT`。 |
| `src/backend/zuno/services/autobuild/build.py` | imports `AuthJWT`。 |
| `src/backend/zuno/vendor/fastapi_jwt_auth/*.py` | vendored package 内部仍按 public package name 互相 import。 |
| `tests/api/test_fastapi_jwt_auth_compat.py` | 固定 public import compatibility 行为。 |

这说明 `src/backend/fastapi_jwt_auth/` 当前是有意保留的 compatibility shell，不是可直接删除的临时目录。

## 目标

给出可执行路线：

1. 识别所有 `fastapi_jwt_auth` public import。
2. 判断能否改为 `zuno.vendor.fastapi_jwt_auth` 或内部 auth facade。
3. 如果不能改，给 compatibility shell 加强说明并把它纳入 repo structure contract。
4. 如果能改，拆成小切片迁移 import、更新 tests、再删除顶层 compat shell。

## 推荐切片

1. 已完成：保留 shell，并把它收敛为单文件 `__init__.py`，用 module alias 明确说明它不是业务目录。
2. 新建或确认内部 auth facade，例如 `zuno/platform/security.py` 或 `zuno/api/dependencies.py`，承接 application code 的 AuthJWT 依赖。
3. 逐个迁移 application imports，不改 vendored package 内部 import。
4. 如果 vendored package 可以脱离 public package name，再评估删除 shell。
5. 删除前必须让 `tests/api/test_fastapi_jwt_auth_compat.py` 改成 retirement guard，而不是直接删测试。

## 当前不能删除的原因

- runtime application 仍直接使用 `from fastapi_jwt_auth import AuthJWT` 或 `from fastapi_jwt_auth.exceptions import AuthJWTException`。
- vendored package 内部仍使用 `from fastapi_jwt_auth.auth_config import AuthConfig`、`from fastapi_jwt_auth.config import LoadConfig` 和 `from fastapi_jwt_auth.exceptions import ...`。
- 直接删除顶层 shell 会让 runtime import 和 vendored internal import 同时失效；下一步必须先建立内部 auth facade，并证明 vendored package 不再依赖 public package name。

## 验收

- `tests/api/test_fastapi_jwt_auth_compat.py` 的存在理由写清楚。
- `fastapi_jwt_auth` 不能再被误判为“乱放的业务目录”。
- retirement path 必须有测试和回滚。
- `tests/api/test_fastapi_jwt_auth_compat.py` 必须证明 shell 只有一个 Python 文件，并证明 public submodule 实际解析到 vendored package。

## 禁止

- 不直接删除 `src/backend/fastapi_jwt_auth/`。
- 不破坏 `from fastapi_jwt_auth import AuthJWT`，除非同一 phase 内完成替代和测试。

## 验证

```powershell
git diff --check
pytest -q tests/api/test_fastapi_jwt_auth_compat.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
```

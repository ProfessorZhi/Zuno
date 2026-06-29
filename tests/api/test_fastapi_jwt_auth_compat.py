import importlib
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
COMPAT_ROOT = BACKEND_ROOT / "fastapi_jwt_auth"
VENDORED_ROOT = (
    BACKEND_ROOT / "zuno" / "compatibility" / "vendor" / "fastapi_jwt_auth"
)


def _ensure_backend_path() -> None:
    backend = str(BACKEND_ROOT)
    if backend not in sys.path:
        sys.path.insert(0, backend)


def test_fastapi_jwt_auth_public_shell_is_retired() -> None:
    assert not COMPAT_ROOT.exists()


def test_fastapi_jwt_auth_runtime_imports_use_vendored_package() -> None:
    _ensure_backend_path()

    from zuno.compatibility.vendor.fastapi_jwt_auth import AuthJWT
    from zuno.compatibility.vendor.fastapi_jwt_auth.auth_config import (
        AuthConfig as VendoredAuthConfig,
    )
    from zuno.compatibility.vendor.fastapi_jwt_auth.auth_jwt import (
        AuthJWT as VendoredAuthJWT,
    )
    from zuno.compatibility.vendor.fastapi_jwt_auth.config import (
        LoadConfig as VendoredLoadConfig,
    )
    from zuno.compatibility.vendor.fastapi_jwt_auth.exceptions import (
        AuthJWTException as VendoredAuthJWTException,
    )

    assert AuthJWT is VendoredAuthJWT
    assert VendoredAuthConfig.__module__.startswith(
        "zuno.compatibility.vendor.fastapi_jwt_auth"
    )
    assert VendoredLoadConfig.__module__.startswith(
        "zuno.compatibility.vendor.fastapi_jwt_auth"
    )
    assert VendoredAuthJWTException.__module__.startswith(
        "zuno.compatibility.vendor.fastapi_jwt_auth"
    )
    vendored_auth_jwt_module = importlib.import_module(VendoredAuthJWT.__module__)
    assert Path(vendored_auth_jwt_module.__file__).resolve().is_relative_to(
        VENDORED_ROOT
    )

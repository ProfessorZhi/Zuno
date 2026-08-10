import importlib
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
RETIRED_ROOT = BACKEND_ROOT / "fastapi_jwt_auth"
VENDORED_ROOT = BACKEND_ROOT / "zuno" / "platform" / "vendor" / "fastapi_jwt_auth"


def _ensure_backend_path() -> None:
    backend = str(BACKEND_ROOT)
    if backend not in sys.path:
        sys.path.insert(0, backend)


def test_fastapi_jwt_auth_public_shell_is_absent() -> None:
    assert not RETIRED_ROOT.exists()


def test_fastapi_jwt_auth_runtime_imports_use_vendor_package() -> None:
    _ensure_backend_path()
    from zuno.platform.vendor.fastapi_jwt_auth import AuthJWT
    from zuno.platform.vendor.fastapi_jwt_auth.auth_config import AuthConfig
    from zuno.platform.vendor.fastapi_jwt_auth.auth_jwt import AuthJWT as VendoredAuthJWT
    from zuno.platform.vendor.fastapi_jwt_auth.config import LoadConfig
    from zuno.platform.vendor.fastapi_jwt_auth.exceptions import AuthJWTException

    assert AuthJWT is VendoredAuthJWT
    for exported in (AuthConfig, VendoredAuthJWT, LoadConfig, AuthJWTException):
        assert exported.__module__.startswith("zuno.platform.vendor.fastapi_jwt_auth")
    module = importlib.import_module(VendoredAuthJWT.__module__)
    assert Path(module.__file__).resolve().is_relative_to(VENDORED_ROOT)

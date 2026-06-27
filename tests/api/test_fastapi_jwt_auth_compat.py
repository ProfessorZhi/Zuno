from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
COMPAT_ROOT = BACKEND_ROOT / "fastapi_jwt_auth"


def _ensure_backend_path() -> None:
    backend = str(BACKEND_ROOT)
    if backend not in sys.path:
        sys.path.insert(0, backend)


def test_fastapi_jwt_auth_public_submodules_are_static_files() -> None:
    for module_name in ["auth_jwt.py", "auth_config.py", "config.py", "exceptions.py"]:
        assert (COMPAT_ROOT / module_name).is_file()


def test_fastapi_jwt_auth_public_submodules_export_vendored_objects() -> None:
    _ensure_backend_path()

    from fastapi_jwt_auth import AuthJWT
    from fastapi_jwt_auth.auth_config import AuthConfig
    from fastapi_jwt_auth.config import LoadConfig
    from fastapi_jwt_auth.exceptions import AuthJWTException
    from zuno.vendor.fastapi_jwt_auth.auth_config import AuthConfig as VendoredAuthConfig
    from zuno.vendor.fastapi_jwt_auth.auth_jwt import AuthJWT as VendoredAuthJWT
    from zuno.vendor.fastapi_jwt_auth.config import LoadConfig as VendoredLoadConfig
    from zuno.vendor.fastapi_jwt_auth.exceptions import AuthJWTException as VendoredAuthJWTException

    assert AuthJWT is VendoredAuthJWT
    assert AuthConfig is VendoredAuthConfig
    assert LoadConfig is VendoredLoadConfig
    assert AuthJWTException is VendoredAuthJWTException

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"
COMPAT_ROOT = BACKEND_ROOT / "fastapi_jwt_auth"


def _ensure_backend_path() -> None:
    backend = str(BACKEND_ROOT)
    if backend not in sys.path:
        sys.path.insert(0, backend)


def test_fastapi_jwt_auth_compat_shell_is_single_file() -> None:
    assert sorted(path.name for path in COMPAT_ROOT.glob("*.py")) == ["__init__.py"]


def test_fastapi_jwt_auth_public_submodules_export_vendored_objects() -> None:
    _ensure_backend_path()

    from fastapi_jwt_auth import AuthJWT
    import fastapi_jwt_auth.auth_config as public_auth_config_module
    import fastapi_jwt_auth.auth_jwt as public_auth_jwt_module
    import fastapi_jwt_auth.config as public_config_module
    import fastapi_jwt_auth.exceptions as public_exceptions_module
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
    for public_module in [
        public_auth_config_module,
        public_auth_jwt_module,
        public_config_module,
        public_exceptions_module,
    ]:
        assert Path(public_module.__file__).resolve().is_relative_to(
            BACKEND_ROOT / "zuno" / "vendor" / "fastapi_jwt_auth"
        )

"""Vendored FastAPI JWT package exposed through a thin compatibility shell."""

from pathlib import Path
from pkgutil import extend_path

__version__ = "0.5.0"

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_VENDORED_ROOT = _PACKAGE_ROOT.parent / "zuno" / "vendor" / "fastapi_jwt_auth"
if _VENDORED_ROOT.exists():
    vendored_path = str(_VENDORED_ROOT)
    if vendored_path not in __path__:
        __path__.append(vendored_path)

from .auth_jwt import AuthJWT

__all__ = ["AuthJWT", "__version__"]

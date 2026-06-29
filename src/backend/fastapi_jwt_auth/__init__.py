"""Single-file compatibility shell for the vendored FastAPI JWT package."""

from importlib import import_module
from pathlib import Path
import sys

__version__ = "0.5.0"

_PACKAGE_ROOT = Path(__file__).resolve().parent
_VENDORED_ROOT = _PACKAGE_ROOT.parent / "zuno" / "vendor" / "fastapi_jwt_auth"
__path__ = [str(_PACKAGE_ROOT)]
if _VENDORED_ROOT.exists():
    vendored_path = str(_VENDORED_ROOT)
    __path__.append(vendored_path)

for _submodule in ["config", "exceptions", "auth_config", "auth_jwt"]:
    sys.modules[f"{__name__}.{_submodule}"] = import_module(
        f"zuno.vendor.fastapi_jwt_auth.{_submodule}"
    )

AuthJWT = sys.modules[f"{__name__}.auth_jwt"].AuthJWT

__all__ = ["AuthJWT", "__version__"]

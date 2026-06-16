from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_ZUNO_API_ROOT = _PACKAGE_ROOT.parents[1] / "zuno" / "api"
if _ZUNO_API_ROOT.exists():
    zuno_api_root = str(_ZUNO_API_ROOT)
    if zuno_api_root not in __path__:
        __path__.append(zuno_api_root)

__all__: list[str] = []

from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_ZUNO_SERVICES_ROOT = _PACKAGE_ROOT.parents[1] / "zuno" / "services"
if _ZUNO_SERVICES_ROOT.exists():
    zuno_services_root = str(_ZUNO_SERVICES_ROOT)
    if zuno_services_root not in __path__:
        __path__.append(zuno_services_root)

__all__: list[str] = []

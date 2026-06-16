from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_ZUNO_DAO_ROOT = _PACKAGE_ROOT.parents[2] / "zuno" / "database" / "dao"
if _ZUNO_DAO_ROOT.exists():
    zuno_dao_root = str(_ZUNO_DAO_ROOT)
    if zuno_dao_root not in __path__:
        __path__.append(zuno_dao_root)

__all__: list[str] = []

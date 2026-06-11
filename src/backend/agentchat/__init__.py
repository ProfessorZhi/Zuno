from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_LEGACY_ROOT = _PACKAGE_ROOT.parent / "zuno" / "legacy" / "agentchat"
if _LEGACY_ROOT.exists():
    legacy_path = str(_LEGACY_ROOT)
    if legacy_path not in __path__:
        __path__.append(legacy_path)

__all__: list[str] = []

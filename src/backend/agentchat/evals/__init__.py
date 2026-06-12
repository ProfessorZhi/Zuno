from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_TOOLS_EVALS_ROOT = _PACKAGE_ROOT.parents[3] / "tools" / "evals" / "zuno"
if _TOOLS_EVALS_ROOT.exists():
    tools_evals_path = str(_TOOLS_EVALS_ROOT)
    if tools_evals_path not in __path__:
        __path__.append(tools_evals_path)

__all__: list[str] = []

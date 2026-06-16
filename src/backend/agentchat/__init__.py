import sys
from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

def _find_repo_root(package_root: Path) -> Path:
    for parent in package_root.parents:
        if (parent / "docs" / "architecture").exists() and (parent / "README.md").exists():
            return parent
    return package_root.parents[-1]


_PACKAGE_ROOT = Path(__file__).resolve().parent
_REPO_ROOT = _find_repo_root(_PACKAGE_ROOT)

_LEGACY_ROOT = _PACKAGE_ROOT.parent / "zuno" / "legacy" / "agentchat"
if _LEGACY_ROOT.exists():
    legacy_path = str(_LEGACY_ROOT)
    if legacy_path not in __path__:
        __path__.append(legacy_path)

_TOOLS_EVALS_ROOT = _REPO_ROOT / "tools" / "evals" / "zuno"
if _TOOLS_EVALS_ROOT.exists():
    tools_evals_path = str(_TOOLS_EVALS_ROOT)
    if tools_evals_path not in __path__:
        __path__.append(tools_evals_path)

__all__: list[str] = []

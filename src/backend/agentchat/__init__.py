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
_SERVICE_API_ROOT = _REPO_ROOT / "services" / "api" / "src"
if (_SERVICE_API_ROOT / "agentchat" / "__init__.py").exists():
    service_api_root_str = str(_SERVICE_API_ROOT)
    if service_api_root_str not in sys.path:
        sys.path.insert(0, service_api_root_str)

    service_package_root = _SERVICE_API_ROOT / "agentchat"
    service_package_root_str = str(service_package_root)
    if service_package_root_str not in __path__:
        __path__.append(service_package_root_str)

_LEGACY_ROOT = _PACKAGE_ROOT.parent / "zuno" / "legacy" / "agentchat"
if _LEGACY_ROOT.exists():
    legacy_path = str(_LEGACY_ROOT)
    if legacy_path not in __path__:
        __path__.append(legacy_path)

__all__: list[str] = []

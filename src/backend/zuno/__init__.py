"""Top-level package marker for zuno.

Keep this package boundary lightweight. Runtime entrypoints should be imported
from their explicit modules instead of relying on package-level wildcard
re-exports.
"""

from __future__ import annotations

import sys
from pathlib import Path
from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)


def _find_repo_root(package_root: Path) -> Path:
    for parent in package_root.parents:
        if (parent / "docs" / "architecture").exists() and (parent / "README.md").exists():
            return parent
    return package_root.parents[-1]


def _find_service_api_root(package_root: Path) -> Path | None:
    repo_root = _find_repo_root(package_root)
    repo_service_root = repo_root / "services" / "api" / "src"
    if (repo_service_root / "zuno" / "main.py").exists():
        return repo_service_root

    for parent in package_root.parents:
        sibling_service_root = parent / "src"
        if (sibling_service_root / "zuno" / "main.py").exists():
            return sibling_service_root
    return None


_PACKAGE_ROOT = Path(__file__).resolve().parent
_SERVICE_API_ROOT = _find_service_api_root(_PACKAGE_ROOT)

if _SERVICE_API_ROOT and (_SERVICE_API_ROOT / "zuno" / "main.py").exists():
    service_api_root_str = str(_SERVICE_API_ROOT)
    if service_api_root_str not in sys.path:
        sys.path.insert(0, service_api_root_str)

    service_package_root = _SERVICE_API_ROOT / "zuno"
    service_package_root_str = str(service_package_root)
    if service_package_root_str not in __path__:
        __path__.append(service_package_root_str)

__all__: list[str] = []

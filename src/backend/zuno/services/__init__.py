from importlib import import_module
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

if (_SERVICE_API_ROOT / "zuno" / "services" / "__init__.py").exists():
    service_api_root_str = str(_SERVICE_API_ROOT)
    if service_api_root_str not in sys.path:
        sys.path.insert(0, service_api_root_str)

    service_package_root = _SERVICE_API_ROOT / "zuno" / "services"
    service_package_root_str = str(service_package_root)
    if service_package_root_str not in __path__:
        __path__.append(service_package_root_str)

_SUBMODULES = {
    "capability_registry",
    "cli_tool_discovery",
    "convert_files",
    "domain_pack",
    "execution_policy",
    "graphrag",
    "mcp",
    "mcp_openai",
    "memory",
    "pipeline",
    "queue",
    "rag",
    "redis",
    "retrieval",
    "runtime_registry",
    "simple_api_tool",
    "storage",
    "tool_connectivity_service",
    "tool_creation_service",
    "user_defined_tool_runtime",
    "workspace",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name: str):
    if name in _SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

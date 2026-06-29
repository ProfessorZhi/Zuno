"""Register lazy legacy ``zuno.*`` import aliases without root files."""

from __future__ import annotations

import importlib
import importlib.abc
import importlib.machinery
from pathlib import Path
import sys
import types
from types import ModuleType


_PACKAGE_ALIASES = {
    "compatibility": ("zuno.platform.compatibility", "platform/compatibility"),
    "config": ("zuno.platform.config", "platform/config"),
    "core": ("zuno.agent.core", "agent/core"),
    "database": ("zuno.platform.database", "platform/database"),
    "resources": ("zuno.platform.resources", "platform/resources"),
    "schema": ("zuno.api.dto", "api/dto"),
    "services": ("zuno.platform.services", "platform/services"),
    "tools": ("zuno.capability.tools", "capability/tools"),
    "utils": ("zuno.platform.common", "platform/common"),
    "middleware": ("zuno.platform.middleware", "platform/middleware"),
}

_MODULE_ALIASES = {
    "settings": "zuno.platform.settings",
}

_EXACT_SUBMODULE_ALIASES = {
    "middleware.trace_id_middleware": "zuno.platform.middleware.trace_id_middleware",
    "middleware.white_list_middleware": "zuno.platform.middleware.white_list_middleware",
    "mcp_servers.arxiv": "zuno.capability.mcp.servers.arxiv",
    "mcp_servers.lark_mcp": "zuno.capability.mcp.servers.lark_mcp",
    "mcp_servers.qa_echo": "zuno.capability.mcp.servers.qa_echo",
    "mcp_servers.remote_proxy": "zuno.capability.mcp.servers.remote_proxy",
    "mcp_servers.weather": "zuno.capability.mcp.servers.weather",
    "mcp_servers.arxiv.mcp_arxiv": "zuno.capability.mcp.servers.arxiv.mcp_arxiv",
    "mcp_servers.lark_mcp.main": "zuno.capability.mcp.servers.lark_mcp.main",
    "mcp_servers.qa_echo.main": "zuno.capability.mcp.servers.qa_echo.main",
    "mcp_servers.remote_proxy.main": "zuno.capability.mcp.servers.remote_proxy.main",
    "mcp_servers.weather.mcp_weather": "zuno.capability.mcp.servers.weather.mcp_weather",
}


def register_legacy_aliases(package_name: str = "zuno") -> None:
    """Install lazy import rules for old public paths."""

    package_root = Path(__file__).resolve().parents[2]
    for finder in sys.meta_path:
        if (
            isinstance(finder, _LegacyAliasFinder)
            and finder.package_name == package_name
            and finder.package_root == package_root
        ):
            return
    sys.meta_path.insert(0, _LegacyAliasFinder(package_name, package_root))


class _LegacyAliasFinder(importlib.abc.MetaPathFinder):
    def __init__(self, package_name: str, package_root: Path) -> None:
        self.package_name = package_name
        self.package_root = package_root

    def find_spec(
        self,
        fullname: str,
        path: object | None = None,
        target: ModuleType | None = None,
    ) -> importlib.machinery.ModuleSpec | None:
        prefix = f"{self.package_name}."
        if not fullname.startswith(prefix):
            return None

        alias = fullname[len(prefix):]
        if alias in _MODULE_ALIASES:
            return importlib.machinery.ModuleSpec(
                fullname,
                _TargetModuleAliasLoader(_MODULE_ALIASES[alias]),
                is_package=False,
            )
        if alias in _EXACT_SUBMODULE_ALIASES:
            return importlib.machinery.ModuleSpec(
                fullname,
                _TargetModuleAliasLoader(_EXACT_SUBMODULE_ALIASES[alias]),
                is_package=False,
            )
        if alias in _PACKAGE_ALIASES:
            target_name, relative_path = _PACKAGE_ALIASES[alias]
            return importlib.machinery.ModuleSpec(
                fullname,
                _PackageAliasLoader(
                    alias_name=fullname,
                    target_name=target_name,
                    path=self.package_root / relative_path,
                ),
                is_package=True,
            )
        if alias == "evals":
            return importlib.machinery.ModuleSpec(
                fullname,
                _NamespaceAliasLoader(
                    alias_name=fullname,
                    path=self.package_root.parents[2] / "tools" / "evals" / "zuno",
                ),
                is_package=True,
            )
        if alias == "mcp_servers":
            return importlib.machinery.ModuleSpec(
                fullname,
                _NamespaceAliasLoader(
                    alias_name=fullname,
                    path=self.package_root / "capability" / "mcp" / "servers",
                    all_names=["arxiv", "lark_mcp", "qa_echo", "remote_proxy", "weather"],
                ),
                is_package=True,
            )
        return None


class _PackageAliasLoader(importlib.abc.Loader):
    def __init__(self, *, alias_name: str, target_name: str, path: Path) -> None:
        self.alias_name = alias_name
        self.target_name = target_name
        self.path = path

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        module = types.ModuleType(self.alias_name)
        module.__doc__ = f"Compatibility alias for legacy ``{self.alias_name}`` imports."
        module.__package__ = self.alias_name
        module.__path__ = [str(self.path)] if self.path.is_dir() else []
        module.__file__ = str(self.path / "__init__.py")
        module.__all__ = []

        def __getattr__(name: str):
            target_module = importlib.import_module(self.target_name)
            return getattr(target_module, name)

        module.__getattr__ = __getattr__  # type: ignore[attr-defined]
        return module

    def exec_module(self, module: ModuleType) -> None:
        return None


class _NamespaceAliasLoader(importlib.abc.Loader):
    def __init__(
        self,
        *,
        alias_name: str,
        path: Path,
        all_names: list[str] | None = None,
    ) -> None:
        self.alias_name = alias_name
        self.path = path
        self.all_names = all_names or []

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        module = types.ModuleType(self.alias_name)
        module.__doc__ = f"Compatibility namespace for legacy ``{self.alias_name}`` imports."
        module.__package__ = self.alias_name
        module.__path__ = [str(self.path)] if self.path.is_dir() else []
        module.__file__ = None
        module.__all__ = list(self.all_names)
        return module

    def exec_module(self, module: ModuleType) -> None:
        return None


class _TargetModuleAliasLoader(importlib.abc.Loader):
    def __init__(self, target_name: str) -> None:
        self.target_name = target_name

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> ModuleType:
        return importlib.import_module(self.target_name)

    def exec_module(self, module: ModuleType) -> None:
        return None

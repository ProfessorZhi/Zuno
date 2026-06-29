"""Compatibility module for legacy ``zuno.mcp_servers`` imports.

MCP server implementations live under ``zuno.capability.mcp.servers``. This
module keeps old import paths alive without keeping a visible top-level
``mcp_servers/`` directory in the backend tree.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

_TARGET = Path(__file__).resolve().parent / "capability" / "mcp" / "servers"
__path__ = [str(_TARGET)] if _TARGET.is_dir() else []

__all__ = ["arxiv", "lark_mcp", "qa_echo", "remote_proxy", "weather"]


def _alias(alias: str, target: str):
    module = importlib.import_module(target)
    sys.modules[alias] = module
    return module


for _name in __all__:
    _alias(f"{__name__}.{_name}", f"zuno.capability.mcp.servers.{_name}")

for _alias_name, _target_name in {
    "arxiv.mcp_arxiv": "arxiv.mcp_arxiv",
    "lark_mcp.main": "lark_mcp.main",
    "qa_echo.main": "qa_echo.main",
    "remote_proxy.main": "remote_proxy.main",
    "weather.mcp_weather": "weather.mcp_weather",
}.items():
    _alias(
        f"{__name__}.{_alias_name}",
        f"zuno.capability.mcp.servers.{_target_name}",
    )

"""Compatibility package for legacy ``zuno.mcp_servers`` imports.

MCP server implementations now live under ``zuno.capability.mcp.servers``.
This package only extends module lookup so old import paths continue to work.
"""

from __future__ import annotations

import importlib
from pathlib import Path
import sys

_TARGET = Path(__file__).resolve().parents[1] / "capability" / "mcp" / "servers"
if _TARGET.is_dir():
    __path__.append(str(_TARGET))  # type: ignore[name-defined]

__all__ = ["arxiv", "lark_mcp", "qa_echo", "remote_proxy", "weather"]

for _name in __all__:
    _module = importlib.import_module(f"zuno.capability.mcp.servers.{_name}")
    sys.modules[f"{__name__}.{_name}"] = _module

_remote_proxy_main = importlib.import_module(
    "zuno.capability.mcp.servers.remote_proxy.main"
)
sys.modules[f"{__name__}.remote_proxy.main"] = _remote_proxy_main

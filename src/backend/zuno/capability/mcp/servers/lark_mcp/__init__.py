"""Lark MCP server package.

The upstream server code imports itself as ``lark_mcp``. Keep that package
alias while the implementation lives under ``zuno.capability.mcp.servers``.
"""

from __future__ import annotations

import sys

sys.modules.setdefault("lark_mcp", sys.modules[__name__])

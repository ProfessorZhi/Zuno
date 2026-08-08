"""PHASE22 (Slice C) — fixture: Product direct → MCP tool.

Must STILL be flagged as ``REAL_PRODUCT_BYPASS``. A Product Adapter
that calls an MCP tool directly bypasses the ToolInvocationGateway.

The hardened verifier must surface this as a tool bypass finding
regardless of the local binding name (``mcp`` / ``foo`` / ``binding``).
"""


class McpShim:
    """A minimal stand-in for an MCP tool / client."""

    async def ainvoke(self, args):
        return args


class ProductDirectMcpAdapter:
    """Product Adapter that reaches into MCP via a renamed binding."""

    def __init__(self):
        # The local binding ``self._binding`` is an MCP tool shim —
        # there is NO gateway between the Product Adapter and the
        # tool. Even with renamed identifiers the call must be
        # flagged.
        self._binding = McpShim()

    async def run(self, payload):
        return await self._binding.ainvoke(payload)
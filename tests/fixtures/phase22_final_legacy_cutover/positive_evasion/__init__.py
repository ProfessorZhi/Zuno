"""Package marker for the PHASE22 (Slice B) positive-evasion fixtures.

Exposes a single ``direct_mcp`` symbol so the renamed-import fixture
can rebind it under an alias. The hardened detector walks import
aliases, so a renamed import must still be flagged as a direct MCP
bypass.
"""


class _McpShim:
    """Minimal stand-in for an MCP tool object: exposes ``ainvoke``."""

    async def ainvoke(self, args):
        return args


# The hardened detector treats any chained ``<...>.ainvoke`` call as
# potentially direct MCP bypass when the import alias chain resolves
# to a symbol that ends with ``mcp``. The local binding name is NOT
# inspected, so this fixture remains a positive evasion test.
direct_mcp = _McpShim()
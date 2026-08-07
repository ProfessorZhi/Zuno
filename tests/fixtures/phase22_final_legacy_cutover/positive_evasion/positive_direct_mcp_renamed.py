"""PHASE22 (Slice B) — positive fixture: direct MCP bypass renamed to a
benign identifier (``foo``) must STILL be detected.

The original detector relied on substring matches against the literal
"mcp" identifier. This fixture renames the MCP helper to ``foo`` and
imports it via a chained alias. The hardened detector must walk the
intra-file import alias map and flag any direct call that resolves to
an MCP helper, regardless of the local binding name.
"""


from fixtures.phase22_final_legacy_cutover.positive_evasion import (  # noqa: E402
    direct_mcp as foo,
)


class DirectMcpRenamed:
    """Product Adapter that reaches into MCP via a renamed binding."""

    def __init__(self) -> None:
        self._binding = foo

    async def run(self, payload):
        # The local binding ``self._binding`` is imported under the
        # alias ``foo``. The hardened detector must walk the alias back
        # to the MCP import and flag the call as a direct MCP bypass.
        return await self._binding.ainvoke(payload)
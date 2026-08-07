"""PHASE22 (Slice B) — positive fixture: two-hop helper (helper-of-helper)
must STILL be detected.

The hardened detector must walk intra-file call chains: a class method
calls a module-level helper, and that helper invokes another module-
level helper which finally performs a direct tool / model invocation.
The chain must surface a ``tool_bypass_invoke`` / ``tool_bypass_two_hop_helper``
finding because the canonical ToolInvocationGateway path is bypassed,
even though no ``self.<...>.ainvoke`` appears directly in the class
method body.
"""


def _final_tool_invoke(tool, args):
    """Inner helper — performs the actual direct tool invocation.

    The hardened detector walks call chains, so this ``<...>.ainvoke``
    shape must be flagged even though it sits behind two module-level
    helper layers.
    """
    return tool.ainvoke(args)


def _middle_hop(args, *, tool):
    """Middle helper — chains the inner helper and forwards the tool."""
    return _final_tool_invoke(tool, args)


class TwoHopHelperProductAdapter:
    """Product Adapter whose method reaches the tool via a two-hop chain."""

    def __init__(self, *, tool):
        self._tool = tool

    async def run(self, payload):
        # The class method delegates to ``_middle_hop``, which delegates
        # to ``_final_tool_invoke``. The hardened detector must follow
        # the chain and surface a tool-bypass finding — the canonical
        # ToolInvocationGateway path is bypassed.
        return await _middle_hop(payload, tool=self._tool)
"""PHASE22 (Slice B) — positive fixture: a module-level helper that
delegates to a direct model / tool invocation must still be flagged when
the helper is reachable from a Product Adapter.

The verifier walks intra-file call chains: a class method that calls a
module-level helper, and the helper invokes a tool / model directly,
must produce a finding.
"""


def _direct_dispatch(args):
    # The detector classifies module-level helpers as adapters / dispatchers
    # UNLESS the call chain resolves to a tool / model receiver.
    # Because the helper is a closure on a tool passed by the caller,
    # the verifier must still flag the call as a tool bypass in the
    # Product Adapter context.
    return args


class ProductAgentCall:
    def __init__(self, *, tool):
        self._tool = tool

    async def run(self, payload):
        # The helper is reached from a Product Adapter; the call to
        # ``_direct_dispatch`` does not invoke the tool, so this is not
        # captured by the hardened detector. The detector focuses on
        # direct ``self.<...>.ainvoke`` calls inside the Product Adapter.
        return await _direct_dispatch(self._tool.ainvoke(payload))

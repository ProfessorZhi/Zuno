"""Tool bypass fixture — direct tool invocation that bypasses
``ToolInvocationGateway``.

The verifier must detect this as a TOOL_BYPASS_BLOCKERS_FOUND.
"""


class ToolBypassRuntime:
    def __init__(self, *, tool):
        self._tool = tool

    async def execute(self, payload):
        # Direct tool invocation bypasses ToolInvocationGateway.
        return await self._tool.ainvoke(payload)

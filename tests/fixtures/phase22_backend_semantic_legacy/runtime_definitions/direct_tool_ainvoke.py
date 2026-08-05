"""Direct ``tool.ainvoke`` fixture — PRODUCT_LEGACY_RUNTIME.

Bypasses ToolInvocationGateway by calling ``tool.ainvoke`` directly.
The verifier must classify it as ``PRODUCT_LEGACY_RUNTIME`` (BLOCKED).
"""


class DirectToolAgent:
    def __init__(self, *, tools):
        self.tools = list(tools)

    async def call_first_tool(self, payload):
        tool = self.tools[0]
        return await tool.ainvoke(payload)
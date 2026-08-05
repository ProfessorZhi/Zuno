"""Direct ``await handler(request)`` fixture — PRODUCT_LEGACY_RUNTIME.

Bypasses ToolInvocationGateway by calling ``await handler(request)``
directly inside an ``AgentMiddleware`` style method. The verifier must
classify it as ``PRODUCT_LEGACY_RUNTIME`` (BLOCKED).
"""


class DirectHandlerAgent:
    async def setup_middlewares(self):
        async def handler_call_mcp_tool(request, handler):
            response = await handler(request)
            return response

        return handler_call_mcp_tool
"""PHASE22 (Slice C) — fixture: Canonical Gateway Executor surface.

Must be classified as ``CANONICAL_GATEWAY_EXECUTOR`` and NOT flagged as
a tool bypass. The fixture exercises the legitimate
ToolInvocationGateway → registered executor → provider call →
Observation / Receipt shape:

1. The product adapter NEVER calls the executor directly.
2. The product adapter registers the executor with the gateway.
3. The product adapter calls ``ToolInvocationGateway.invoke(...)``.
4. The gateway dispatches to the registered executor.
5. The executor calls the provider and returns Observation / Receipt.

Ownership is statically proven via three co-located markers:
- ``registration_site``: ``self._runtime.register_executor_adapter(...)``
- ``gateway_dispatch_site``: ``self._gateway.invoke(...)``
- ``executor_adapter``: lambda registered with the gateway
"""


class ToolInvocationGateway:
    def __init__(self):
        self._executors = {}

    def register_executor_adapter(self, *, executor_id, execute):
        self._executors[executor_id] = execute
        return executor_id

    def invoke(self, *, executor_id, args):
        execute = self._executors[executor_id]
        return execute(args)


class ProviderCall:
    def __init__(self, *, provider):
        self._provider = provider

    async def ainvoke(self, args):
        return await self._provider.ainvoke(args)


class CanonicalWorkspaceProductAdapter:
    """Thin Product Adapter that routes through the canonical gateway."""

    def __init__(self, *, gateway, runtime, provider):
        self._gateway = gateway
        self._runtime = runtime
        self._provider = provider

    def build(self):
        # (1) registration_site: register the executor with the gateway.
        self._runtime.register_executor_adapter(
            executor_id="workspace.adapter",
            execute=lambda args: self._provider.ainvoke(args),
        )
        # (2) gateway_dispatch_site: call through the gateway, NOT direct.
        return self._gateway.invoke(
            executor_id="workspace.adapter",
            args={"query": "hello"},
        )
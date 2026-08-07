"""PHASE22 (Slice C) — fixture: Product direct → registered executor.

Must STILL be flagged as ``REAL_PRODUCT_BYPASS`` even when the call
target is a registered executor. A Product Adapter that calls a
registered executor directly bypasses the ToolInvocationGateway — the
ownership proof is incomplete (no ``gateway_dispatch_site`` between
the Product Adapter and the registered executor).

The hardened verifier must surface this as a tool bypass finding.
"""


class RegisteredExecutor:
    def __init__(self):
        self._registry = {}

    def register(self, *, executor_id, execute):
        self._registry[executor_id] = execute
        return executor_id

    async def ainvoke(self, executor_id, args):
        return self._registry[executor_id](args)


class ProductDirectExecutorAdapter:
    """Product Adapter that calls a registered executor directly."""

    def __init__(self, *, executor):
        self._executor = executor
        # registration_site is present (executor is registered), but
        # there is NO gateway_dispatch_site between the Product
        # Adapter and the executor.
        self._executor.register(
            executor_id="direct.executor",
            execute=lambda args: args,
        )

    async def run(self, payload):
        # No gateway between Product Adapter and registered executor.
        return await self._executor.ainvoke("direct.executor", payload)
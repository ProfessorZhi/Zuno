"""Clean runtime fixture — a thin Product Adapter that delegates to
the canonical runtime. The verifier must classify this as a clean
shape in the CLEAN fixture file.
"""


class CleanRuntimeAdapter:
    """Thin Product Adapter — delegates to SingleControllerRuntimeHarness."""

    def __init__(self, *, unified_runtime):
        self._unified = unified_runtime

    async def ainvoke(self, messages):
        return self._unified.start({"messages": messages})

    async def astream(self, messages):
        for event in self._unified.stream({"messages": messages}):
            yield event

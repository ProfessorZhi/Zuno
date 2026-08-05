"""Versioned public API caller — must NOT be misclassified as legacy.

The verifier must NOT flag versioned public API names that just happen
to contain the word "agent" or "runtime".
"""


class WorkSpaceSimpleAgentV2:
    """Versioned public API that is the canonical adapter."""

    def __init__(self, *, unified_runtime):
        self._unified = unified_runtime

    async def ainvoke(self, messages):
        return self._unified.start({"messages": messages})


class UnifiedAgentRuntimeServiceV2:
    """Versioned public API for the canonical runtime service."""

    def start(self, request):
        return {"started": True, "request": request}

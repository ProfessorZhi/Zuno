"""PHASE22 (Slice B) — negative fixture: a call through the canonical
executor adapter must NOT be flagged.

The canonical adapter registration is the allowed path through the Tool
Control Plane; the verifier must exempt it from the tool-bypass
detector.
"""


class CanonicalWorkspaceProductAdapter:
    """Thin Product Adapter that delegates to the canonical executor
    adapter registration. Must remain undetected by the name-free
    detector.
    """

    def __init__(self, *, runtime, tenant_id, workspace_id):
        self._runtime = runtime
        self._tenant_id = tenant_id
        self._workspace_id = workspace_id

    def build(self, bindings):
        # Canonical call shape: the adapter registers the executor
        # through the Tool Control Plane. The detector MUST NOT flag
        # ``register_executor_adapter`` or the executor adapters it
        # constructs.
        _ = self._runtime.register_executor_adapter(
            executor_id="workspace.adapter",
            execute=lambda args: args,
        )
        return self._runtime

"""PHASE22 (Slice C) — fixture: unknown dynamic executor (UNRESOLVED).

The verifier cannot statically prove the runtime type that ``getattr``
resolves to. Even when the resolved attribute is then dispatched
through a canonical-looking call shape, the dynamic dispatch site
itself must surface ``AUDIT_UNRESOLVED``.

The hardened verifier must NOT default-safe this file. Any successful
classification here would be unverifiable ownership — the audit cannot
claim the file is a legitimate canonical executor without runtime
evidence.
"""


class DynamicExecutorLoader:
    def __init__(self, *, tool, attribute_name):
        self._tool = tool
        self._attribute_name = attribute_name

    async def run(self, payload):
        # Dynamic dispatch — the verifier cannot statically prove the
        # attribute is a canonical executor adapter.
        method = getattr(self._tool, self._attribute_name)
        return await method(payload)
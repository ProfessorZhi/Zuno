"""PHASE22 (Slice B) — positive fixture: rename evasion must still be
detected.

The original detector looked for ``self.tool.ainvoke`` and ``handler``;
this fixture renames the receiver to ``binding`` and the helper to
``executor`` and must STILL be flagged as a tool bypass.
"""


class RenamedToolBypass:
    def __init__(self, *, binding):
        self._binding = binding

    async def run(self, payload):
        # Receiver name is ``binding``, not ``tool`` — must still be flagged.
        return await self._binding.ainvoke(payload)

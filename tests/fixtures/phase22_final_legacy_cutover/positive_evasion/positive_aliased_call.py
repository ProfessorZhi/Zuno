"""PHASE22 (Slice B) — positive fixture: alias call must still be detected.

The detector builds an intra-file alias map. ``binder = self.tool;
binder.ainvoke(args)`` must be flagged because ``binder`` resolves to
``self.tool``.
"""


class AliasedToolBypass:
    def __init__(self, *, tool):
        self.tool = tool

    async def run(self, payload):
        binder = self.tool
        return await binder.ainvoke(payload)

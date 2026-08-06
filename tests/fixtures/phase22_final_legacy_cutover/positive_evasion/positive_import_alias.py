"""PHASE22 (Slice B) — positive fixture: import alias must still be
detected.

The detector walks alias names. A function imported as ``from x import
call_me as alias`` and called via ``alias.ainvoke(args)`` must surface
a finding.
"""


from fixtures.phase22_final_legacy_cutover.positive_evasion.helpers import (  # noqa: E402
    RenamedInvoker as alias_invoker,
)


class AliasToolBypass:
    def __init__(self) -> None:
        self.binding = alias_invoker()

    async def run(self, payload):
        # The detector should walk through the alias to the underlying
        # ``ainvoke`` call and flag it.
        return await self.binding.ainvoke(payload)

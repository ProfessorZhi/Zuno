"""PHASE22 (Slice C) — negative fixture: unrelated ``getattr`` and
unrelated ``invoke`` MUST NOT be falsely correlated.

The file contains:

  - ``func_a`` performs a ``getattr`` lookup but does NOT dispatch
    the result (just returns the value).
  - ``func_b`` performs a tool ``ainvoke`` call but does NOT derive
    the receiver from a ``getattr`` result.

The previous file-wide detector correlated these two unrelated
patterns and produced a false-positive ``unresolved_file_rename``
finding. The hardened, function-scoped detector MUST leave this file
alone on the getattr-correlation path: neither function shows a
``getattr``→``dispatch`` chain.

This file does not match the canonical executor adapter naming
contract (it is a regular Product Adapter stub), but it also does
not exhibit dynamic dispatch. The verifier must not invent a
correlation between the two unrelated call sites.
"""


def func_a(*, client, key):
    """Pure config lookup — ``getattr`` is used but not dispatched."""
    config = getattr(client, key)
    return config


class ProductAdapterWithoutDynamicDispatch:
    """A Product Adapter that has tool calls but does NOT derive them
    from ``getattr`` results. The hardened verifier must not flag
    this file as ``unresolved_file_rename`` due to getattr / invoke
    cross-function correlation.
    """

    def __init__(self, *, tool):
        self._tool = tool

    async def run(self, payload):
        # Plain tool call, no getattr, no alias chain.
        return await self._tool.ainvoke(payload)
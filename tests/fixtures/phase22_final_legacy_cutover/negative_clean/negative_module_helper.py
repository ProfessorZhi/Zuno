"""PHASE22 (Slice B) — negative fixture: a module-level helper that is
NOT a tool / model call must remain undetected.

The detector must NOT flag this file. There are no chain-attribute
``invoke`` / ``ainvoke`` / ``stream`` / ``astream`` calls in the
fixture. The helper is a pure utility function that does not perform
any tool / model / provider invocation.
"""


def _normalize_response(raw):
    """Pure function — no chained attribute invoke. Must NOT be flagged."""
    return raw


class ProductAdapterWithHelper:
    def __init__(self, *, model):
        self._model = model

    async def answer(self, query):
        # The helper is a pure function, no chain-invoke. The detector
        # must leave it alone.
        raw = self._model.complete(query)
        return _normalize_response(raw)

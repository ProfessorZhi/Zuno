"""Candidate runtime class with no canonical_delegate evidence.

This fixture is the *fail-closed* shape. When a Production Entry Point
constructs it, the verifier cannot find ``canonical_delegate`` evidence
in the class methods and therefore must classify it as ``UNRESOLVED``
instead of silently allowing it.

It is used by the alias / qualified / assignment / factory fixtures that
demonstrate the fail-closed decision tree.
"""


class WorkSpaceSimpleAgent:
    """Thin facade that DOES NOT delegate to the canonical runtime.

    The class looks like a Product Adapter (no graph construction, no
    direct model/tool call) but it does NOT call into any canonical
    runtime symbol. The verifier must classify it as ``UNRESOLVED``
    whenever a Production Entry Point constructs it.
    """

    def __init__(self, *, model_config, user_id, session_id):
        self._model_config = model_config
        self._user_id = user_id
        self._session_id = session_id

    async def ainvoke(self, messages):
        return {
            "messages": messages,
            "user_id": self._user_id,
            "session_id": self._session_id,
        }

    async def astream(self, messages):
        yield {
            "messages": messages,
            "user_id": self._user_id,
            "session_id": self._session_id,
        }

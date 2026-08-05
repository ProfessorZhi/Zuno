"""Production candidate class with NO canonical_delegate — UNRESOLVED.

The class methods do NOT call into any canonical runtime symbol. They
also do NOT call ``create_agent`` / ``model.ainvoke`` / ``tool.ainvoke``
or await ``handler``. There is no graph construction. The class is
reachable by a Production Entry Point. The verifier must classify it
as ``UNRESOLVED`` because nothing proves canonical delegation.
"""


class WorkSpaceSimpleAgent:
    """Stub class with no execution evidence and no canonical delegate."""

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

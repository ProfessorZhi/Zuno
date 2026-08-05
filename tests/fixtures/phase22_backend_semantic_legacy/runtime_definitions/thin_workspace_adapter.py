"""Thin WorkSpaceSimpleAgent Product Adapter fixture.

A future cutover shape: ``WorkSpaceSimpleAgent`` keeps the public
``ainvoke`` / ``astream`` surface, but every method delegates to the
canonical ``UnifiedAgentRuntimeService``. It does not construct its own
graph, does not directly invoke a model, does not directly invoke a tool,
and does not own Plan / Trace / Final Gate / RunOutcome.

This file exists purely as a verifier fixture. It is NOT imported by
production code.
"""


class WorkSpaceSimpleAgent:
    """Thin Product Adapter that delegates to UnifiedAgentRuntimeService."""

    def __init__(self, *, unified_runtime, model_config, user_id, session_id):
        self._unified = unified_runtime
        self._model_config = model_config
        self._user_id = user_id
        self._session_id = session_id

    async def ainvoke(self, messages):
        request = self._build_start_request(messages)
        return self._unified.start(request)

    async def astream(self, messages):
        request = self._build_start_request(messages)
        for event in self._unified.stream(request):
            yield event

    def _build_start_request(self, messages):
        return {
            "messages": messages,
            "user_id": self._user_id,
            "session_id": self._session_id,
        }
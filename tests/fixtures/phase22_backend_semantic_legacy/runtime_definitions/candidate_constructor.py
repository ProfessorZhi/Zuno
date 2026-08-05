"""Candidate runtime class used by the alias / qualified / factory fixtures.

The verifier classifies candidates in
``tests/fixtures/phase22_backend_semantic_legacy/production_callers/`` by
constructing this class via different caller shapes. The class itself has
the canonical delegate shape so when a caller successfully resolves to
``WorkSpaceSimpleAgent`` AND uses the canonical runtime pattern, the
verifier classifies it as ``PRODUCT_ADAPTER``. When the caller shape
cannot be statically resolved, the verifier classifies the class as
``UNRESOLVED`` (fail-closed).
"""


class WorkSpaceSimpleAgent:
    """Canonical adapter shape — delegates to a runtime dependency."""

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

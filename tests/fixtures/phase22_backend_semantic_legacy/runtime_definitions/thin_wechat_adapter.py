"""Canonical WeChat thin adapter fixture — PRODUCT_ADAPTER (ALLOWED).

PHASE22-PR135 cutover shape: the adapter builds a canonical
``WorkspaceAgentRuntime``, routes every tool through the gateway-bound
adapter registry, and maps the canonical run snapshot back to the WeChat
message contract. ``final_answer`` is a channel-message local derived from
``snapshot`` — a read of the canonical run outcome, not Product Run
ownership. The verifier must classify it as ``PRODUCT_ADAPTER``.
"""


class WeChatAgent:
    def __init__(self, *, user_id: str, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
        self._runtime = None

    async def init_wechat_agent(self):
        from zuno.platform.services.workspace.single_controller_runtime import (
            WorkspaceAgentRuntime,
        )

        self._runtime = WorkspaceAgentRuntime(
            model=None,
            bindings=[],
            tenant_id="tenant:fixture",
            workspace_id="workspace:fixture",
            principal_id=self.user_id,
        )
        return self._runtime

    def _final_answer(self, snapshot) -> str:
        response_content = ""
        for obs in snapshot.observations:
            if obs.kind == "model":
                grounded = str(obs.metadata.get("final_answer") or "")
                if grounded:
                    response_content = grounded
        return response_content

    async def astream(self, messages):
        snapshot = await self._runtime.start({"goal": messages[-1].content})
        final_answer = self._final_answer(snapshot).strip() or "fallback text"
        yield {
            "event": "task_result",
            "data": {"message": final_answer},
        }

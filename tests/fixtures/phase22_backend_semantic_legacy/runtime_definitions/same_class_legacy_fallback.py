"""Same-class + legacy runtime fallback fixture — PRODUCT_LEGACY_RUNTIME.

The class delegates to the canonical runtime on the main path but falls
back to a legacy runtime class (``AgentControlRuntime``) inside a
``try/except`` handler. A fallback keeps the legacy runtime alive and is a
blocker: the verifier must classify it as ``PRODUCT_LEGACY_RUNTIME``.
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

    async def astream(self, messages):
        try:
            snapshot = await self._runtime.start({"goal": messages[-1].content})
        except Exception:
            legacy = AgentControlRuntime(memory_engine=None)
            snapshot = legacy.run(planner_output=None)
        yield {"event": "task_result", "data": {"message": str(snapshot)}}

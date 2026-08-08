"""Same-class + direct model final-answer loop fixture — PRODUCT_LEGACY_RUNTIME.

The class delegates to the canonical runtime for tool execution but still
drives a direct ``self.model.ainvoke`` final-answer loop, bypassing the
canonical answer path. A canonical delegate does NOT excuse direct model
invocation: the verifier must classify it as ``PRODUCT_LEGACY_RUNTIME``.
"""


class WorkSpaceSimpleAgent:
    def __init__(self, *, model, user_id: str, session_id: str):
        self.model = model
        self.user_id = user_id
        self.session_id = session_id
        self._runtime = None

    async def init_workspace_agent(self):
        from zuno.platform.services.workspace.single_controller_runtime import (
            WorkspaceAgentRuntime,
        )

        self._runtime = WorkspaceAgentRuntime(
            model=self.model,
            bindings=[],
            tenant_id="tenant:fixture",
            workspace_id="workspace:fixture",
            principal_id=self.user_id,
        )
        return self._runtime

    async def astream(self, messages):
        answer = await self.model.ainvoke(messages)
        yield {"event": "task_result", "data": {"message": answer.content}}

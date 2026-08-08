"""Same-class + direct tool fixture — PRODUCT_LEGACY_RUNTIME (BLOCKED).

The class carries a canonical delegate on the init path but still invokes
``tool.ainvoke`` directly in the run path. A canonical delegate does NOT
excuse direct tool execution: the verifier must classify it as
``PRODUCT_LEGACY_RUNTIME``.
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

    async def run_tool(self, tool, args):
        return await tool.ainvoke(args)

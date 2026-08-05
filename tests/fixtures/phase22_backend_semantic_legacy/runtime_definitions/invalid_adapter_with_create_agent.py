"""Invalid WorkSpaceSimpleAgent fixture.

This fixture intentionally keeps the legacy ``create_agent`` call inside
the class methods. The verifier must classify it as ``PRODUCT_LEGACY_RUNTIME``
because the class still owns an independent LangGraph / LangChain Agent
Graph and bypasses the canonical runtime.
"""


def create_agent(*, model, tools, system_prompt, middleware, state_schema):
    """Marker for the verifier — represents ``langchain.agents.create_agent``."""
    return {"model": model, "tools": tools, "system_prompt": system_prompt}


class WorkSpaceSimpleAgent:
    """Legacy-shape class that still owns an independent graph."""

    def __init__(self, *, model, tools):
        self.model = model
        self.tools = tools

    def setup_react_agent(self):
        return create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt="you are a workspace agent",
            middleware=[],
            state_schema=None,
        )

    async def ainvoke(self, messages):
        return await self.setup_react_agent().ainvoke(messages)
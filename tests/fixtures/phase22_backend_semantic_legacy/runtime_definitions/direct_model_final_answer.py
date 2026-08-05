"""Direct model final answer fixture — PRODUCT_LEGACY_RUNTIME.

Drives a final answer by calling ``model.ainvoke`` directly, bypassing
the canonical runtime. The verifier must classify it as
``PRODUCT_LEGACY_RUNTIME`` (BLOCKED).
"""


class DirectModelFinalAnswerAgent:
    def __init__(self, *, model):
        self.model = model

    async def ainvoke(self, messages):
        return await self.model.ainvoke(messages)
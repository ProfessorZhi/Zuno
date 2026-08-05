"""Allowlisted active bypass — even with an allowlist comment, the
structural pattern must still be flagged.

The verifier must NOT special-case ``# allowlist`` comments. A direct
tool invocation is a blocking finding regardless of allowlist comments.
"""


class ActiveBypassRuntime:
    def __init__(self, *, tool):
        # allowlist: tool_bypass_direct — direct tool invocation approved
        self._tool = tool

    async def execute(self, payload):
        return await self._tool.ainvoke(payload)
